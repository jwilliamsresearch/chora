"""
Graph Traversal Primitives
"""

from __future__ import annotations

from collections import deque
from typing import Iterator, Callable

from chora.core.types import NodeId, EdgeType
from chora.core.graph import PlatialGraph
from chora.core.node import PlatialNode
from chora.core.edge import PlatialEdge


def traverse_from(
    graph: PlatialGraph,
    start_id: NodeId,
    edge_types: list[EdgeType] | None = None,
    max_depth: int = 3
) -> Iterator[tuple[PlatialNode, int]]:
    """
    Breadth-first traversal from a starting node.
    
    Yields (node, depth) tuples.
    """
    visited: set[NodeId] = {start_id}
    queue: deque[tuple[NodeId, int]] = deque([(start_id, 0)])
    
    while queue:
        current_id, depth = queue.popleft()
        
        try:
            node = graph.get_node(current_id)
            yield node, depth
        except Exception:
            continue
        
        if depth >= max_depth:
            continue
        
        for edge in graph.outgoing_edges(current_id, None):
            if edge_types and edge.edge_type not in edge_types:
                continue
            
            if edge.target_id not in visited:
                visited.add(edge.target_id)
                queue.append((edge.target_id, depth + 1))


def find_connected(
    graph: PlatialGraph,
    node_id: NodeId,
    edge_types: list[EdgeType] | None = None
) -> set[NodeId]:
    """Find all nodes connected to the given node."""
    connected: set[NodeId] = set()
    
    for node, _ in traverse_from(graph, node_id, edge_types, max_depth=10):
        connected.add(node.id)
    
    return connected


def find_path(
    graph: PlatialGraph,
    start_id: NodeId,
    end_id: NodeId,
    edge_types: list[EdgeType] | None = None
) -> list[NodeId] | None:
    """
    Find shortest path between two nodes.
    
    Returns list of node IDs or None if no path exists.
    """
    if start_id == end_id:
        return [start_id]
    
    visited: set[NodeId] = {start_id}
    queue: deque[tuple[NodeId, list[NodeId]]] = deque([(start_id, [start_id])])
    
    while queue:
        current_id, path = queue.popleft()
        
        for edge in graph.outgoing_edges(current_id, None):
            if edge_types and edge.edge_type not in edge_types:
                continue
            
            if edge.target_id == end_id:
                return path + [end_id]
            
            if edge.target_id not in visited:
                visited.add(edge.target_id)
                queue.append((edge.target_id, path + [edge.target_id]))
    
    return None
