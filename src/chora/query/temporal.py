"""
Temporal Queries
"""

from __future__ import annotations

from datetime import datetime
from typing import Iterator, Callable

from chora.core.graph import PlatialGraph
from chora.core.node import PlatialNode
from chora.core.temporal import TimeInterval


def snapshot_query(
    graph: PlatialGraph,
    at: datetime
) -> PlatialGraph:
    """
    Get a snapshot of the graph at a specific time.
    
    Returns a new graph containing only nodes and edges
    valid at the given timestamp.
    """
    return graph.snapshot(at)


def temporal_range_query(
    graph: PlatialGraph,
    start: datetime,
    end: datetime
) -> Iterator[PlatialNode]:
    """
    Query nodes active during a time range.
    
    Yields nodes whose validity overlaps with [start, end].
    """
    query_interval = TimeInterval(start=start, end=end)
    
    for node in graph.nodes():
        if node.temporal.interval.overlaps(query_interval):
            yield node
