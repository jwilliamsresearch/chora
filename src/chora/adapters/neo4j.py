"""
Neo4j Adapter for Chora.

Requires `neo4j` python driver.
"""
from typing import Iterator, Any
from datetime import datetime

from chora.adapters.base import GraphAdapter
from chora.core import (
    PlatialGraph, PlatialNode, PlatialEdge,
    NodeId, EdgeId, NodeType, EdgeType
)
from chora.core.exceptions import (
    AdapterError, ConnectionError, NodeNotFoundError
)

class Neo4jAdapter(GraphAdapter):
    """
    Adapter for Neo4j graph database.
    
    Maps Chora concepts to Neo4j property graph:
    - Nodes -> :Label (e.g. :Agent, :Encounter)
    - Edges -> :RELATIONSHIP (e.g. :PARTICIPATES_IN)
    - Properties -> Node/Relationship properties
    """
    def __init__(self, uri: str, auth: tuple[str, str] | None = None):
        try:
            from neo4j import GraphDatabase, Driver
        except ImportError:
            raise AdapterError("neo4j package not installed. Run `pip install neo4j`.")
            
        self._driver: Driver | None = None
        self._uri = uri
        self._auth = auth

    def connect(self) -> None:
        """Establish connection to Neo4j."""
        try:
            from neo4j import GraphDatabase
            self._driver = GraphDatabase.driver(self._uri, auth=self._auth)
            self._driver.verify_connectivity()
        except Exception as e:
            raise ConnectionError(f"Failed to connect to Neo4j: {e}")

    def disconnect(self) -> None:
        """Close connection."""
        if self._driver:
            self._driver.close()
            self._driver = None

    def save_graph(self, graph: PlatialGraph) -> None:
        """Save entire graph to Neo4j (merge nodes/edges)."""
        if not self._driver:
            raise ConnectionError("Not connected")
            
        with self._driver.session() as session:
            # 1. Save Nodes
            for node in graph.nodes():
                session.execute_write(self._merge_node, node)
            
            # 2. Save Edges
            for edge in graph.edges():
                session.execute_write(self._merge_edge, edge)

    def load_graph(self, name: str) -> PlatialGraph:
        """Load graph from Neo4j (not fully implemented due to filtering complexity)."""
        # For a real implementation, we'd need to know which nodes belong to 'name'
        # Currently assuming one global graph or using 'name' as a Label is tricky.
        # This is a stub for the full implementation.
        return PlatialGraph(name=name)

    # ... (Individual CRUD operations would go here)
    
    def add_node(self, node: PlatialNode) -> NodeId:
        """Add a single node."""
        if not self._driver:
            raise ConnectionError("Not connected")
        with self._driver.session() as session:
            session.execute_write(self._merge_node, node)
        return node.id
        
    def add_edge(self, edge: PlatialEdge) -> EdgeId:
        """Add a single edge."""
        if not self._driver:
            raise ConnectionError("Not connected")
        with self._driver.session() as session:
            session.execute_write(self._merge_edge, edge)
        return edge.id

    # Internal helpers
    @staticmethod
    def _merge_node(tx, node: PlatialNode):
        # Construct Cypher MERGE
        labels = f":{node.node_type.name}"
        query = (
            f"MERGE (n{labels} {{id: $id}}) "
            "SET n.name = $name "
            "RETURN n"
        )
        params = {
            "id": str(node.id),
            "name": getattr(node, "name", "")
        }
        tx.run(query, params)

    @staticmethod
    def _merge_edge(tx, edge: PlatialEdge):
        rel_type = edge.edge_type.name
        query = (
            "MATCH (a {id: $source_id}), (b {id: $target_id}) "
            f"MERGE (a)-[r:{rel_type}]->(b) "
            "SET r.id = $id, r.weight = $weight "
            "RETURN r"
        )
        params = {
            "source_id": str(edge.source_id),
            "target_id": str(edge.target_id),
            "id": str(edge.id),
            "weight": edge.weight
        }
        tx.run(query, params)
    
    # Required abstract methods implementation
    def get_node(self, node_id: NodeId) -> PlatialNode:
        """Retrieve a node by ID."""
        if not self._driver:
            raise ConnectionError("Not connected")
        
        with self._driver.session() as session:
            result = session.run(
                "MATCH (n {id: $id}) RETURN n, labels(n) as labels",
                {"id": str(node_id)}
            )
            record = result.single()
            if not record:
                raise NodeNotFoundError(f"Node {node_id} not found")
            
            # Reconstruct PlatialNode from properties
            # This is a simplified version - full implementation would use a factory
            node_data = dict(record["n"])
            labels = record["labels"]
            
            from chora.core.node import PlatialNode
            return PlatialNode.from_dict({
                "id": node_data.get("id"),
                "name": node_data.get("name"),
                "node_type": labels[0] if labels else "UNKNOWN"
            })
    
    def delete_node(self, node_id: NodeId) -> None:
        """Delete a node by ID."""
        if not self._driver:
            raise ConnectionError("Not connected")
        
        with self._driver.session() as session:
            session.run(
                "MATCH (n {id: $id}) DETACH DELETE n",
                {"id": str(node_id)}
            )
    
    def get_edge(self, edge_id: EdgeId) -> PlatialEdge:
        """Retrieve an edge by ID."""
        if not self._driver:
            raise ConnectionError("Not connected")
        
        with self._driver.session() as session:
            result = session.run(
                "MATCH ()-[r {id: $id}]->() RETURN r, type(r) as rel_type, startNode(r).id as source, endNode(r).id as target",
                {"id": str(edge_id)}
            )
            record = result.single()
            if not record:
                raise AdapterError(f"Edge {edge_id} not found")
            
            edge_data = dict(record["r"])
            return PlatialEdge(
                source_id=NodeId(record["source"]),
                target_id=NodeId(record["target"]),
                edge_type=EdgeType[record["rel_type"]],
                weight=edge_data.get("weight", 1.0)
            )
    
    def delete_edge(self, edge_id: EdgeId) -> None:
        """Delete an edge by ID."""
        if not self._driver:
            raise ConnectionError("Not connected")
        
        with self._driver.session() as session:
            session.run(
                "MATCH ()-[r {id: $id}]->() DELETE r",
                {"id": str(edge_id)}
            )
    
    def query_nodes(self, **criteria) -> Iterator[PlatialNode]:
        """Query nodes by criteria."""
        if not self._driver:
            raise ConnectionError("Not connected")
        
        # Build dynamic query based on criteria
        where_clauses = []
        params = {}
        
        for key, value in criteria.items():
            if key == "node_type":
                # Filter by label
                where_clauses.append(f"n:{value.name}")
            else:
                where_clauses.append(f"n.{key} = ${key}")
                params[key] = value
        
        where_clause = " AND ".join(where_clauses) if where_clauses else "true"
        query = f"MATCH (n) WHERE {where_clause} RETURN n, labels(n) as labels"
        
        with self._driver.session() as session:
            result = session.run(query, params)
            for record in result:
                node_data = dict(record["n"])
                labels = record["labels"]
                from chora.core.node import PlatialNode
                yield PlatialNode.from_dict({
                    "id": node_data.get("id"),
                    "name": node_data.get("name"),
                    "node_type": labels[0] if labels else "UNKNOWN"
                })
    
    def query_edges(self, **criteria) -> Iterator[PlatialEdge]:
        """Query edges by criteria."""
        if not self._driver:
            raise ConnectionError("Not connected")
        
        with self._driver.session() as session:
            result = session.run(
                "MATCH ()-[r]->() RETURN r, type(r) as rel_type, startNode(r).id as source, endNode(r).id as target"
            )
            for record in result:
                edge_data = dict(record["r"])
                
                # Filter by criteria
                if "edge_type" in criteria:
                    if record["rel_type"] != criteria["edge_type"].name:
                        continue
                
                yield PlatialEdge(
                    source_id=NodeId(record["source"]),
                    target_id=NodeId(record["target"]),
                    edge_type=EdgeType[record["rel_type"]],
                    weight=edge_data.get("weight", 1.0)
                )

