"""
PostGIS Adapter for Chora.

Requires `psycopg` (or `asyncpg`) and `SQLAlchemy` + `GeoAlchemy2`.
"""
from typing import Iterator

from chora.adapters.base import GraphAdapter
from chora.core import (
    PlatialGraph, PlatialNode, PlatialEdge,
    NodeId, EdgeId
)
from chora.core.exceptions import AdapterError, ConnectionError

class PostGISAdapter(GraphAdapter):
    """
    Adapter for PostGIS-enabled PostgreSQL database.
    
    Maps spatial extents to Geometry columns and other nodes to relational tables.
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

    def connect(self) -> None:
        """Establish database connection."""
        from sqlalchemy import create_engine
        try:
            self._engine = create_engine(self._dsn)
            with self._engine.connect() as conn:
                pass # Verify connection
        except Exception as e:
            raise ConnectionError(f"Failed to connect to PostGIS: {e}")

    def disconnect(self) -> None:
        """Close connection."""
        if self._engine:
            self._engine.dispose()
            self._engine = None

    def save_graph(self, graph: PlatialGraph) -> None:
        """Save graph to relational tables."""
        if not self._engine:
            raise ConnectionError("Not connected")
        # STUB: Implementation would map nodes/edges to ORM models
        pass

    def load_graph(self, name: str) -> PlatialGraph:
        """Load graph from relational tables."""
        # STUB
        return PlatialGraph(name=name)

    # Required abstract methods
    def add_node(self, node: PlatialNode) -> NodeId: return node.id
    def delete_node(self, node_id: NodeId) -> None: pass
    def get_node(self, node_id: NodeId) -> PlatialNode: raise NotImplementedError
        
    def add_edge(self, edge: PlatialEdge) -> EdgeId: return edge.id
    def delete_edge(self, edge_id: EdgeId) -> None: pass
    def get_edge(self, edge_id: EdgeId) -> PlatialEdge: raise NotImplementedError
    
    def query_nodes(self, **criteria) -> Iterator[PlatialNode]: yield from []
    def query_edges(self, **criteria) -> Iterator[PlatialEdge]: yield from []
