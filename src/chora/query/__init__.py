"""
Chora Query Module

High-level platial queries and graph traversal operations.
Queries compile down to graph traversals with temporal filtering.
"""

from chora.query.queries import (
    PlatialQuery,
    find_familiar_places,
    find_positive_places,
    find_routine_places,
    query_encounters,
)
from chora.query.matching import (
    find_practices_like,
    match_pattern,
)
from chora.query.similarity import (
    place_similarity,
    practice_similarity,
)
from chora.query.traversal import (
    traverse_from,
    find_connected,
    find_path,
)
from chora.query.temporal import (
    snapshot_query,
    temporal_range_query,
)

__all__ = [
    # Queries
    "PlatialQuery",
    "find_familiar_places",
    "find_positive_places",
    "find_routine_places",
    "query_encounters",
    # Matching
    "find_practices_like",
    "match_pattern",
    # Similarity
    "place_similarity",
    "practice_similarity",
    # Traversal
    "traverse_from",
    "find_connected",
    "find_path",
    # Temporal
    "snapshot_query",
    "temporal_range_query",
]
