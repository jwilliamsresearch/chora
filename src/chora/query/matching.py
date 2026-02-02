"""
Pattern Matching for Platial Graphs
"""

from __future__ import annotations

from typing import Sequence

from chora.core.graph import PlatialGraph
from chora.core.practice import Practice
from chora.core.types import NodeType


def find_practices_like(
    graph: PlatialGraph,
    template: Practice,
    min_similarity: float = 0.5
) -> list[Practice]:
    """Find practices similar to a template."""
    matches = []
    
    for node in graph.nodes(NodeType.PRACTICE):
        if not isinstance(node, Practice):
            continue
        
        sim = _practice_similarity(template, node)
        if sim >= min_similarity:
            matches.append(node)
    
    return sorted(matches, key=lambda p: _practice_similarity(template, p), reverse=True)


def match_pattern(
    graph: PlatialGraph,
    pattern_type: str,
    **kwargs
) -> list:
    """Match a named pattern against the graph."""
    patterns = {
        "morning_routine": _match_morning_routine,
        "avoidance": _match_avoidance,
        "exploration": _match_exploration,
    }
    
    if pattern_type in patterns:
        return patterns[pattern_type](graph, **kwargs)
    
    return []


def _practice_similarity(p1: Practice, p2: Practice) -> float:
    """Compute similarity between practices."""
    score = 0.0
    
    # Same type
    if p1.practice_type == p2.practice_type:
        score += 0.4
    
    # Similar regularity
    reg_diff = abs(p1.regularity - p2.regularity)
    score += 0.3 * (1 - reg_diff)
    
    # Similar frequency
    if p1.frequency > 0 and p2.frequency > 0:
        freq_ratio = min(p1.frequency, p2.frequency) / max(p1.frequency, p2.frequency)
        score += 0.3 * freq_ratio
    
    return score


def _match_morning_routine(graph: PlatialGraph, **kwargs) -> list[Practice]:
    """Find morning routines."""
    routines = []
    for node in graph.nodes(NodeType.PRACTICE):
        if isinstance(node, Practice):
            if node.is_routine and "morning" in node.typical_time.lower():
                routines.append(node)
    return routines


def _match_avoidance(graph: PlatialGraph, **kwargs) -> list[Practice]:
    """Find avoidance patterns."""
    from chora.core.types import PracticeType
    return [
        node for node in graph.nodes(NodeType.PRACTICE)
        if isinstance(node, Practice) and node.practice_type == PracticeType.AVOIDANCE
    ]


def _match_exploration(graph: PlatialGraph, **kwargs) -> list[Practice]:
    """Find exploration patterns."""
    from chora.core.types import PracticeType
    return [
        node for node in graph.nodes(NodeType.PRACTICE)
        if isinstance(node, Practice) and node.practice_type == PracticeType.EXPLORATION
    ]
