"""
PostGIS Adapter for Chora.

Requires `psycopg` (or `asyncpg`) and `SQLAlchemy` + `GeoAlchemy2`.
"""
from typing import Iterator, Any
from datetime import datetime

from chora.adapters.base import GraphAdapter
from chora.core import (
    PlatialGraph, PlatialNode, PlatialEdge,
    NodeId, EdgeId, NodeType, EdgeType
)
from chora.core.exceptions import AdapterError, ConnectionError, NodeNotFoundError


class PostGISAdapter(GraphAdapter):
    """
    Adapter for PostGIS-enabled PostgreSQL database.
    
    Maps spatial extents to Geometry columns and other nodes to relational tables.
    Uses SQLAlchemy ORM with GeoAlchemy2 for spatial operations.
    """
    
    def __init__(self, dsn: str):
        try:
            import psycopg
            import sqlalchemy
            from geoalchemy2 import Geometry
        except ImportError:
            raise AdapterError(
                "PostGIS dependencies not installed. "
                "Run `pip install psycopg sqlalchemy geoalchemy2`."
            )
        self._dsn = dsn
        self._engine = None
        self._Session = None
        self._tables_created = False

    def connect(self) -> None:
        """Establish database connection and create tables if needed."""
        from sqlalchemy import create_engine
        from sqlalchemy.orm import sessionmaker
        try:
            self._engine = create_engine(self._dsn)
            self._Session = sessionmaker(bind=self._engine)
            with self._engine.connect() as conn:
                pass  # Verify connection
            
            # Create tables on first connection
            if not self._tables_created:
                self._create_tables()
                self._tables_created = True
        except Exception as e:
            raise ConnectionError(f"Failed to connect to PostGIS: {e}")

    def disconnect(self) -> None:
        """Close connection."""
        if self._engine:
            self._engine.dispose()
            self._engine = None
            self._Session = None

    def _create_tables(self) -> None:
        """Create ORM tables if they don't exist."""
        from sqlalchemy import (
            MetaData, Table, Column, String, Float, DateTime, 
            ForeignKey, Text, JSON
        )
        from geoalchemy2 import Geometry
        
        metadata = MetaData()
        
        # Nodes table
        self._nodes_table = Table(
            'chora_nodes', metadata,
            Column('id', String(128), primary_key=True),
            Column('node_type', String(64), nullable=False),
            Column('name', String(256)),
            Column('created_at', DateTime, default=datetime.now),
            Column('properties', JSON),
            Column('geometry', Geometry('GEOMETRY', srid=4326), nullable=True)
        )
        
        # Edges table
        self._edges_table = Table(
            'chora_edges', metadata,
            Column('id', String(128), primary_key=True),
            Column('source_id', String(128), ForeignKey('chora_nodes.id')),
            Column('target_id', String(128), ForeignKey('chora_nodes.id')),
            Column('edge_type', String(64), nullable=False),
            Column('weight', Float, default=1.0),
            Column('created_at', DateTime, default=datetime.now),
            Column('properties', JSON)
        )
        
        metadata.create_all(self._engine)

    def save_graph(self, graph: PlatialGraph) -> None:
        """Save entire graph to relational tables."""
        if not self._engine:
            raise ConnectionError("Not connected")
        
        # Save all nodes
        for node in graph.nodes():
            self.add_node(node)
        
        # Save all edges
        for edge in graph.edges():
            self.add_edge(edge)

    def load_graph(self, name: str) -> PlatialGraph:
        """Load graph from relational tables."""
        if not self._engine:
            raise ConnectionError("Not connected")
        
        graph = PlatialGraph(name=name)
        
        # Load all nodes
        for node in self.query_nodes():
            graph.add_node(node)
        
        # Load all edges
        for edge in self.query_edges():
            try:
                graph.add_edge(edge)
            except Exception:
                pass  # Skip edges with missing nodes
        
        return graph

    def add_node(self, node: PlatialNode) -> NodeId:
        """Add a single node to the database."""
        if not self._engine:
            raise ConnectionError("Not connected")
        
        from sqlalchemy import insert
        from shapely import to_wkb
        
        # Extract geometry if present
        geometry_wkb = None
        if hasattr(node, 'geometry') and node.geometry is not None:
            geometry_wkb = to_wkb(node.geometry, hex=True)
        
        with self._engine.connect() as conn:
            stmt = self._nodes_table.insert().values(
                id=str(node.id),
                node_type=node.node_type.name,
                name=getattr(node, 'name', ''),
                geometry=geometry_wkb,
                properties=self._node_to_dict(node)
            ).prefix_with('OR REPLACE')
            conn.execute(stmt)
            conn.commit()
        
        return node.id

    def get_node(self, node_id: NodeId) -> PlatialNode:
        """Retrieve a node by ID."""
        if not self._engine:
            raise ConnectionError("Not connected")
        
        from sqlalchemy import select
        
        with self._engine.connect() as conn:
            stmt = select(self._nodes_table).where(
                self._nodes_table.c.id == str(node_id)
            )
            result = conn.execute(stmt).fetchone()
            
            if not result:
                raise NodeNotFoundError(f"Node {node_id} not found")
            
            return self._row_to_node(result)

    def delete_node(self, node_id: NodeId) -> None:
        """Delete a node by ID."""
        if not self._engine:
            raise ConnectionError("Not connected")
        
        from sqlalchemy import delete
        
        with self._engine.connect() as conn:
            # Delete connected edges first
            stmt = delete(self._edges_table).where(
                (self._edges_table.c.source_id == str(node_id)) |
                (self._edges_table.c.target_id == str(node_id))
            )
            conn.execute(stmt)
            
            # Delete node
            stmt = delete(self._nodes_table).where(
                self._nodes_table.c.id == str(node_id)
            )
            conn.execute(stmt)
            conn.commit()

    def add_edge(self, edge: PlatialEdge) -> EdgeId:
        """Add a single edge to the database."""
        if not self._engine:
            raise ConnectionError("Not connected")
        
        with self._engine.connect() as conn:
            stmt = self._edges_table.insert().values(
                id=str(edge.id),
                source_id=str(edge.source_id),
                target_id=str(edge.target_id),
                edge_type=edge.edge_type.name,
                weight=edge.weight,
                properties=self._edge_to_dict(edge)
            ).prefix_with('OR REPLACE')
            conn.execute(stmt)
            conn.commit()
        
        return edge.id

    def get_edge(self, edge_id: EdgeId) -> PlatialEdge:
        """Retrieve an edge by ID."""
        if not self._engine:
            raise ConnectionError("Not connected")
        
        from sqlalchemy import select
        
        with self._engine.connect() as conn:
            stmt = select(self._edges_table).where(
                self._edges_table.c.id == str(edge_id)
            )
            result = conn.execute(stmt).fetchone()
            
            if not result:
                raise AdapterError(f"Edge {edge_id} not found")
            
            return self._row_to_edge(result)

    def delete_edge(self, edge_id: EdgeId) -> None:
        """Delete an edge by ID."""
        if not self._engine:
            raise ConnectionError("Not connected")
        
        from sqlalchemy import delete
        
        with self._engine.connect() as conn:
            stmt = delete(self._edges_table).where(
                self._edges_table.c.id == str(edge_id)
            )
            conn.execute(stmt)
            conn.commit()

    def query_nodes(self, **criteria) -> Iterator[PlatialNode]:
        """Query nodes by criteria."""
        if not self._engine:
            raise ConnectionError("Not connected")
        
        from sqlalchemy import select
        
        stmt = select(self._nodes_table)
        
        # Apply filters
        if 'node_type' in criteria:
            stmt = stmt.where(
                self._nodes_table.c.node_type == criteria['node_type'].name
            )
        if 'name' in criteria:
            stmt = stmt.where(
                self._nodes_table.c.name == criteria['name']
            )
        
        with self._engine.connect() as conn:
            result = conn.execute(stmt)
            for row in result:
                yield self._row_to_node(row)

    def query_edges(self, **criteria) -> Iterator[PlatialEdge]:
        """Query edges by criteria."""
        if not self._engine:
            raise ConnectionError("Not connected")
        
        from sqlalchemy import select
        
        stmt = select(self._edges_table)
        
        # Apply filters
        if 'edge_type' in criteria:
            stmt = stmt.where(
                self._edges_table.c.edge_type == criteria['edge_type'].name
            )
        if 'source_id' in criteria:
            stmt = stmt.where(
                self._edges_table.c.source_id == str(criteria['source_id'])
            )
        if 'target_id' in criteria:
            stmt = stmt.where(
                self._edges_table.c.target_id == str(criteria['target_id'])
            )
        
        with self._engine.connect() as conn:
            result = conn.execute(stmt)
            for row in result:
                yield self._row_to_edge(row)

    # -------------------------------------------------------------------------
    # Spatial Query Methods
    # -------------------------------------------------------------------------

    def query_within_bounds(
        self, 
        min_lon: float, min_lat: float,
        max_lon: float, max_lat: float
    ) -> Iterator[PlatialNode]:
        """Query nodes within a bounding box."""
        if not self._engine:
            raise ConnectionError("Not connected")
        
        from sqlalchemy import select, func
        
        with self._engine.connect() as conn:
            stmt = select(self._nodes_table).where(
                func.ST_Intersects(
                    self._nodes_table.c.geometry,
                    func.ST_MakeEnvelope(min_lon, min_lat, max_lon, max_lat, 4326)
                )
            )
            result = conn.execute(stmt)
            for row in result:
                yield self._row_to_node(row)

    def query_within_distance(
        self,
        lon: float, lat: float,
        distance_meters: float
    ) -> Iterator[PlatialNode]:
        """Query nodes within a distance from a point."""
        if not self._engine:
            raise ConnectionError("Not connected")
        
        from sqlalchemy import select, func
        
        point = func.ST_SetSRID(func.ST_MakePoint(lon, lat), 4326)
        
        with self._engine.connect() as conn:
            stmt = select(self._nodes_table).where(
                func.ST_DWithin(
                    func.ST_Transform(self._nodes_table.c.geometry, 3857),
                    func.ST_Transform(point, 3857),
                    distance_meters
                )
            )
            result = conn.execute(stmt)
            for row in result:
                yield self._row_to_node(row)

    # -------------------------------------------------------------------------
    # Internal Helper Methods
    # -------------------------------------------------------------------------

    def _node_to_dict(self, node: PlatialNode) -> dict:
        """Convert node to properties dict."""
        props = {}
        for attr in ['agent_id', 'extent_id', 'start_time', 'end_time', 'value']:
            if hasattr(node, attr):
                val = getattr(node, attr)
                if isinstance(val, datetime):
                    props[attr] = val.isoformat()
                elif val is not None:
                    props[attr] = str(val)
        return props

    def _edge_to_dict(self, edge: PlatialEdge) -> dict:
        """Convert edge to properties dict."""
        return {
            'temporal_validity': getattr(edge, 'temporal_validity', None)
        }

    def _row_to_node(self, row) -> PlatialNode:
        """Convert database row to PlatialNode."""
        from chora.core.node import PlatialNode
        return PlatialNode.from_dict({
            'id': row.id,
            'node_type': row.node_type,
            'name': row.name,
            'properties': row.properties
        })

    def _row_to_edge(self, row) -> PlatialEdge:
        """Convert database row to PlatialEdge."""
        return PlatialEdge(
            source_id=NodeId(row.source_id),
            target_id=NodeId(row.target_id),
            edge_type=EdgeType[row.edge_type],
            weight=row.weight
        )
