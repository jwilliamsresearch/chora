"""
In-Memory Adapter

Default adapter that stores graphs in memory.
Suitable for development, testing, and small datasets.
"""

from __future__ import annotations

from datetime import datetime
from typing import Iterator
import copy

from chora.adapters.base import GraphAdapter
from chora.core.types import NodeId, EdgeId, NodeType, EdgeType
from chora.core.graph import PlatialGraph
from chora.core.node import PlatialNode
from chora.core.edge import PlatialEdge


class InMemoryAdapter(GraphAdapter):
    """
    In-memory graph storage adapter.
    
    Stores graphs in dictionaries. Supports multiple named graphs.
    Data is lost when the adapter is garbage collected.
    
    Examples
    --------
    >>> adapter = InMemoryAdapter()
    >>> adapter.connect()
    >>> adapter.save_graph(my_graph)
    >>> loaded = adapter.load_graph("my_graph")
    """
    
    def __init__(self):
        self._graphs: dict[str, PlatialGraph] = {}
        self._active_graph: PlatialGraph | None = None
        self._connected = False
    
    def connect(self, **kwargs) -> None:
        """Connect (no-op for in-memory)."""
        self._connected = True
    
    def disconnect(self) -> None:
        """Disconnect (no-op for in-memory)."""
        self._connected = False
    
    @property
    def is_connected(self) -> bool:
        return self._connected
    
    def save_graph(self, graph: PlatialGraph) -> None:
        """Save graph to memory."""
        name = graph.name or "default"
        self._graphs[name] = copy.deepcopy(graph)
    
    def load_graph(self, name: str) -> PlatialGraph:
        """Load graph from memory."""
        if name not in self._graphs:
            raise KeyError(f"Graph '{name}' not found")
        self._active_graph = self._graphs[name]
        return self._active_graph
    
    def list_graphs(self) -> list[str]:
        """List all stored graph names."""
        return list(self._graphs.keys())
    
    def delete_graph(self, name: str) -> bool:
        """Delete a graph. Returns True if deleted."""
        if name in self._graphs:
            del self._graphs[name]
            return True
        return False
    
    def set_active_graph(self, graph: PlatialGraph) -> None:
        """Set the active graph for node/edge operations."""
        self._active_graph = graph
    
    def add_node(self, node: PlatialNode) -> None:
        """Add node to active graph."""
        if self._active_graph is None:
            self._active_graph = PlatialGraph()
        self._active_graph.add_node(node)
    
    def get_node(self, node_id: NodeId) -> PlatialNode | None:
        """Get node from active graph."""
        if self._active_graph is None:
            return None
        try:
            return self._active_graph.get_node(node_id)
        except KeyError:
            return None
    
    def delete_node(self, node_id: NodeId) -> bool:
        """Delete node from active graph."""
        if self._active_graph is None:
            return False
        return self._active_graph.remove_node(node_id)
    
    def add_edge(self, edge: PlatialEdge) -> None:
        """Add edge to active graph."""
        if self._active_graph is None:
            self._active_graph = PlatialGraph()
        self._active_graph.add_edge(edge)
    
    def get_edge(self, edge_id: EdgeId) -> PlatialEdge | None:
        """Get edge from active graph."""
        if self._active_graph is None:
            return None
        try:
            return self._active_graph.get_edge(edge_id)
        except KeyError:
            return None
    
    def delete_edge(self, edge_id: EdgeId) -> bool:
        """Delete edge from active graph."""
        if self._active_graph is None:
            return False
        return self._active_graph.remove_edge(edge_id)
    
    def query_nodes(
        self,
        node_type: NodeType | None = None,
        **filters
    ) -> Iterator[PlatialNode]:
        """Query nodes in active graph."""
        if self._active_graph is None:
            return
        
        for node in self._active_graph.nodes(node_type):
            match = True
            for key, value in filters.items():
                if hasattr(node, key):
                    if getattr(node, key) != value:
                        match = False
                        break
            if match:
                yield node
    
    def query_edges(
        self,
        edge_type: EdgeType | None = None,
        source_id: NodeId | None = None,
        target_id: NodeId | None = None,
        **filters
    ) -> Iterator[PlatialEdge]:
        """Query edges in active graph."""
        if self._active_graph is None:
            return
        
        for edge in self._active_graph.edges(edge_type):
            if source_id and edge.source_id != source_id:
                continue
            if target_id and edge.target_id != target_id:
                continue
            
            match = True
            for key, value in filters.items():
                if hasattr(edge, key):
                    if getattr(edge, key) != value:
                        match = False
                        break
            if match:
                yield edge
    
    def snapshot(self, at: datetime) -> PlatialGraph:
        """Get temporal snapshot of active graph."""
        if self._active_graph is None:
            return PlatialGraph()
        return self._active_graph.snapshot(at)
    
    def clear(self) -> None:
        """Clear all stored graphs."""
        self._graphs.clear()
        self._active_graph = None
