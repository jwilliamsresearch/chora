"""
Redis Adapter for Chora.

High-performance caching for Chora nodes/edges.
Best used for 'Hot State' (e.g., current location of agents).
"""
import json
from typing import Iterator

from chora.adapters.base import GraphAdapter
from chora.core import (
    PlatialGraph, PlatialNode, PlatialEdge,
    NodeId, EdgeId
)
from chora.core.exceptions import AdapterError, ConnectionError

class RedisAdapter(GraphAdapter):
    """
    Adapter for Redis Key-Value store.
    
    Schema:
    - node:{id} -> JSON
    - edge:{id} -> JSON
    - nodes:set -> Set of IDs
    """
    def __init__(self, host: str = "localhost", port: int = 6379, db: int = 0):
        try:
            import redis
            self._redis_cls = redis.Redis
        except ImportError:
            raise AdapterError("redis package not installed")
            
        self._host = host
        self._port = port
        self._db = db
        self._client = None

    def connect(self) -> None:
        try:
            self._client = self._redis_cls(
                host=self._host, port=self._port, db=self._db, decode_responses=True
            )
            self._client.ping()
        except Exception as e:
            raise ConnectionError(f"Failed to connect to Redis: {e}")

    def disconnect(self) -> None:
        if self._client:
            self._client.close()
            self._client = None
            
    def add_node(self, node: PlatialNode) -> NodeId:
        if not self._client: raise ConnectionError("Not connected")
        
        # Serialize
        data = {
            "id": str(node.id),
            "type": node.node_type.name,
            # Basic JSON dump of slots/dict
            # This requires a proper serializer for complex objects
            "name": getattr(node, "name", "")
        }
        
        pipe = self._client.pipeline()
        pipe.set(f"node:{node.id}", json.dumps(data))
        pipe.sadd("nodes:all", str(node.id))
        pipe.execute()
        return node.id

    def get_node(self, node_id: NodeId) -> PlatialNode:
        # Stub deserialization
        raise NotImplementedError("Deserialization not fully implemented")

    def add_edge(self, edge: PlatialEdge) -> EdgeId:
        if not self._client: raise ConnectionError("Not connected")
        data = {
            "id": str(edge.id),
            "source": str(edge.source_id),
            "target": str(edge.target_id),
            "type": edge.edge_type.name
        }
        self._client.set(f"edge:{edge.id}", json.dumps(data))
        return edge.id

    # Required stubs
    def delete_node(self, node_id: NodeId) -> None: pass
    def get_edge(self, edge_id: EdgeId) -> PlatialEdge: raise NotImplementedError
    def delete_edge(self, edge_id: EdgeId) -> None: pass
    def save_graph(self, graph: PlatialGraph) -> None: pass
    def load_graph(self, name: str) -> PlatialGraph: return PlatialGraph(name)
    def query_nodes(self, **criteria) -> Iterator[PlatialNode]: yield from []
    def query_edges(self, **criteria) -> Iterator[PlatialEdge]: yield from []
