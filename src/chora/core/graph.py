"""
Platial Graph Container

The core representation is a typed, temporal, heterogeneous graph
that enables multiple, even conflicting experiences to coexist.
"""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime
from typing import Iterator, Sequence

from chora.core.types import NodeType, EdgeType, NodeId, EdgeId
from chora.core.node import PlatialNode
from chora.core.edge import PlatialEdge
from chora.core.exceptions import (
    NodeNotFoundError,
    DuplicateNodeError,
    InvalidEdgeError,
    EdgeNotFoundError,
)


@dataclass
class PlatialGraph:
    """
    A typed, temporal, heterogeneous graph for platial modelling.
    
    The graph stores nodes (entities) and edges (relations) with
    full temporal validity, uncertainty, and provenance tracking.
    
    Attributes
    ----------
    name : str
        Optional name for the graph.
    description : str
        Optional description.
    
    Examples
    --------
    >>> from chora.core import PlatialGraph, Agent, SpatialExtent
    >>> graph = PlatialGraph(name="Urban Mobility Study")
    >>> agent = Agent(name="Alice")
    >>> graph.add_node(agent)
    >>> graph.node_count
    1
    """
    
    name: str = ""
    description: str = ""
    
    # Internal storage
    _nodes: dict[NodeId, PlatialNode] = field(default_factory=dict, repr=False)
    _edges: dict[EdgeId, PlatialEdge] = field(default_factory=dict, repr=False)
    
    # Indices for efficient querying
    _nodes_by_type: dict[NodeType, set[NodeId]] = field(
        default_factory=lambda: defaultdict(set), repr=False
    )
    _outgoing_edges: dict[NodeId, set[EdgeId]] = field(
        default_factory=lambda: defaultdict(set), repr=False
    )
    _incoming_edges: dict[NodeId, set[EdgeId]] = field(
        default_factory=lambda: defaultdict(set), repr=False
    )
    _edges_by_type: dict[EdgeType, set[EdgeId]] = field(
        default_factory=lambda: defaultdict(set), repr=False
    )
    
    # =========================================================================
    # Node Operations
    # =========================================================================
    
    def add_node(self, node: PlatialNode) -> NodeId:
        """
        Add a node to the graph.
        
        Parameters
        ----------
        node : PlatialNode
            The node to add.
        
        Returns
        -------
        NodeId
            The ID of the added node.
        
        Raises
        ------
        DuplicateNodeError
            If a node with this ID already exists.
        """
        if node.id in self._nodes:
            raise DuplicateNodeError(
                "Node already exists", node_id=str(node.id)
            )
        
        self._nodes[node.id] = node
        self._nodes_by_type[node.node_type].add(node.id)
        return node.id
    
    def get_node(self, node_id: NodeId) -> PlatialNode:
        """
        Get a node by ID.
        
        Raises
        ------
        NodeNotFoundError
            If the node does not exist.
        """
        if node_id not in self._nodes:
            raise NodeNotFoundError(
                "Node not found", node_id=str(node_id)
            )
        return self._nodes[node_id]
    
    def has_node(self, node_id: NodeId) -> bool:
        """Check if a node exists."""
        return node_id in self._nodes
    
    def remove_node(self, node_id: NodeId) -> PlatialNode:
        """
        Remove a node and all its edges.
        
        Returns
        -------
        PlatialNode
            The removed node.
        """
        node = self.get_node(node_id)
        
        # Remove incident edges
        for edge_id in list(self._outgoing_edges[node_id]):
            self.remove_edge(edge_id)
        for edge_id in list(self._incoming_edges[node_id]):
            self.remove_edge(edge_id)
        
        # Remove from indices
        self._nodes_by_type[node.node_type].discard(node_id)
        del self._nodes[node_id]
        del self._outgoing_edges[node_id]
        del self._incoming_edges[node_id]
        
        return node
    
    def nodes(self, node_type: NodeType | None = None) -> Iterator[PlatialNode]:
        """
        Iterate over nodes, optionally filtered by type.
        
        Parameters
        ----------
        node_type : NodeType | None
            If provided, only yield nodes of this type.
        """
        if node_type is None:
            yield from self._nodes.values()
        else:
            for node_id in self._nodes_by_type[node_type]:
                yield self._nodes[node_id]
    
    def nodes_valid_at(self, timestamp: datetime,
                       node_type: NodeType | None = None) -> Iterator[PlatialNode]:
        """Iterate over nodes valid at a given timestamp."""
        for node in self.nodes(node_type):
            if node.is_valid_at(timestamp):
                yield node
    
    # =========================================================================
    # Edge Operations
    # =========================================================================
    
    def add_edge(self, edge: PlatialEdge) -> EdgeId:
        """
        Add an edge to the graph.
        
        Both source and target nodes must exist.
        
        Raises
        ------
        NodeNotFoundError
            If source or target node doesn't exist.
        """
        if not self.has_node(edge.source_id):
            raise NodeNotFoundError(
                "Source node not found", node_id=str(edge.source_id)
            )
        if not self.has_node(edge.target_id):
            raise NodeNotFoundError(
                "Target node not found", node_id=str(edge.target_id)
            )
        
        self._edges[edge.id] = edge
        self._outgoing_edges[edge.source_id].add(edge.id)
        self._incoming_edges[edge.target_id].add(edge.id)
        self._edges_by_type[edge.edge_type].add(edge.id)
        
        return edge.id
    
    def get_edge(self, edge_id: EdgeId) -> PlatialEdge:
        """Get an edge by ID."""
        if edge_id not in self._edges:
            raise EdgeNotFoundError(
                "Edge not found", edge_id=str(edge_id)
            )
        return self._edges[edge_id]
    
    def has_edge(self, edge_id: EdgeId) -> bool:
        """Check if an edge exists."""
        return edge_id in self._edges
    
    def remove_edge(self, edge_id: EdgeId) -> PlatialEdge:
        """Remove an edge from the graph."""
        edge = self.get_edge(edge_id)
        
        self._outgoing_edges[edge.source_id].discard(edge_id)
        self._incoming_edges[edge.target_id].discard(edge_id)
        self._edges_by_type[edge.edge_type].discard(edge_id)
        del self._edges[edge_id]
        
        return edge
    
    def edges(self, edge_type: EdgeType | None = None) -> Iterator[PlatialEdge]:
        """Iterate over edges, optionally filtered by type."""
        if edge_type is None:
            yield from self._edges.values()
        else:
            for edge_id in self._edges_by_type[edge_type]:
                yield self._edges[edge_id]
    
    def outgoing_edges(self, node_id: NodeId,
                       edge_type: EdgeType | None = None) -> Iterator[PlatialEdge]:
        """Get edges originating from a node."""
        for edge_id in self._outgoing_edges[node_id]:
            edge = self._edges[edge_id]
            if edge_type is None or edge.edge_type == edge_type:
                yield edge
    
    def incoming_edges(self, node_id: NodeId,
                       edge_type: EdgeType | None = None) -> Iterator[PlatialEdge]:
        """Get edges pointing to a node."""
        for edge_id in self._incoming_edges[node_id]:
            edge = self._edges[edge_id]
            if edge_type is None or edge.edge_type == edge_type:
                yield edge
    
    def neighbors(self, node_id: NodeId,
                  edge_type: EdgeType | None = None) -> Iterator[PlatialNode]:
        """Get neighboring nodes (via outgoing edges)."""
        for edge in self.outgoing_edges(node_id, edge_type):
            yield self._nodes[edge.target_id]
    
    def predecessors(self, node_id: NodeId,
                     edge_type: EdgeType | None = None) -> Iterator[PlatialNode]:
        """Get predecessor nodes (via incoming edges)."""
        for edge in self.incoming_edges(node_id, edge_type):
            yield self._nodes[edge.source_id]
    
    # =========================================================================
    # Graph Properties
    # =========================================================================
    
    @property
    def node_count(self) -> int:
        """Total number of nodes."""
        return len(self._nodes)
    
    @property
    def edge_count(self) -> int:
        """Total number of edges."""
        return len(self._edges)
    
    def node_count_by_type(self, node_type: NodeType) -> int:
        """Count nodes of a specific type."""
        return len(self._nodes_by_type[node_type])
    
    def edge_count_by_type(self, edge_type: EdgeType) -> int:
        """Count edges of a specific type."""
        return len(self._edges_by_type[edge_type])
    
    @property
    def all_node_ids(self) -> set[NodeId]:
        """Get all node IDs."""
        return set(self._nodes.keys())
    
    # =========================================================================
    # Subgraph Operations
    # =========================================================================
    
    def subgraph(self, node_ids: Sequence[NodeId]) -> PlatialGraph:
        """
        Extract a subgraph containing only the specified nodes.
        
        Includes all edges where both endpoints are in the subgraph.
        """
        sub = PlatialGraph(
            name=f"Subgraph of {self.name}",
            description=f"Extracted from {self.name}"
        )
        
        node_set = set(node_ids)
        
        for node_id in node_ids:
            if self.has_node(node_id):
                sub.add_node(self.get_node(node_id))
        
        for edge in self.edges():
            if edge.source_id in node_set and edge.target_id in node_set:
                sub.add_edge(edge)
        
        return sub
    
    def snapshot(self, timestamp: datetime) -> PlatialGraph:
        """
        Create a snapshot of the graph at a specific time.
        
        Only includes nodes and edges valid at that timestamp.
        """
        snap = PlatialGraph(
            name=f"{self.name} @ {timestamp.isoformat()}",
            description=f"Snapshot of {self.name}"
        )
        
        valid_nodes: set[NodeId] = set()
        
        for node in self.nodes():
            if node.is_valid_at(timestamp):
                snap.add_node(node)
                valid_nodes.add(node.id)
        
        for edge in self.edges():
            if (edge.is_valid_at(timestamp) and
                edge.source_id in valid_nodes and
                edge.target_id in valid_nodes):
                snap.add_edge(edge)
        
        return snap
    
    def clear(self) -> None:
        """Remove all nodes and edges."""
        self._nodes.clear()
        self._edges.clear()
        self._nodes_by_type.clear()
        self._outgoing_edges.clear()
        self._incoming_edges.clear()
        self._edges_by_type.clear()
