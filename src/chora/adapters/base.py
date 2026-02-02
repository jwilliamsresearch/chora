"""
Base Adapter Interface

Abstract interface for graph storage backends.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import datetime
from typing import Iterator

from chora.core.types import NodeId, EdgeId, NodeType, EdgeType
from chora.core.graph import PlatialGraph
from chora.core.node import PlatialNode
from chora.core.edge import PlatialEdge


class GraphAdapter(ABC):
    """
    Abstract base class for graph storage adapters.
    
    Adapters provide persistence and querying for platial graphs,
    abstracting over different backend technologies.
    """
    
    @abstractmethod
    def connect(self, **kwargs) -> None:
        """Establish connection to the backend."""
        pass
    
    @abstractmethod
    def disconnect(self) -> None:
        """Close connection to the backend."""
        pass
    
    @abstractmethod
    def save_graph(self, graph: PlatialGraph) -> None:
        """Save entire graph to the backend."""
        pass
    
    @abstractmethod
    def load_graph(self, name: str) -> PlatialGraph:
        """Load a graph by name from the backend."""
        pass
    
    @abstractmethod
    def add_node(self, node: PlatialNode) -> None:
        """Add or update a single node."""
        pass
    
    @abstractmethod
    def get_node(self, node_id: NodeId) -> PlatialNode | None:
        """Retrieve a node by ID."""
        pass
    
    @abstractmethod
    def delete_node(self, node_id: NodeId) -> bool:
        """Delete a node. Returns True if deleted."""
        pass
    
    @abstractmethod
    def add_edge(self, edge: PlatialEdge) -> None:
        """Add or update a single edge."""
        pass
    
    @abstractmethod
    def get_edge(self, edge_id: EdgeId) -> PlatialEdge | None:
        """Retrieve an edge by ID."""
        pass
    
    @abstractmethod
    def delete_edge(self, edge_id: EdgeId) -> bool:
        """Delete an edge. Returns True if deleted."""
        pass
    
    @abstractmethod
    def query_nodes(
        self,
        node_type: NodeType | None = None,
        **filters
    ) -> Iterator[PlatialNode]:
        """Query nodes with optional filters."""
        pass
    
    @abstractmethod
    def query_edges(
        self,
        edge_type: EdgeType | None = None,
        source_id: NodeId | None = None,
        target_id: NodeId | None = None,
        **filters
    ) -> Iterator[PlatialEdge]:
        """Query edges with optional filters."""
        pass
    
    def snapshot(self, at: datetime) -> PlatialGraph:
        """Get temporal snapshot (default: load and filter)."""
        raise NotImplementedError("Snapshot not implemented for this adapter")
    
    def __enter__(self):
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.disconnect()
        return False
