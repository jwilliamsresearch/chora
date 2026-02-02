"""
Chora Derive Module

Theory-encoded derivation operators for transforming raw data into
platial structures. These operators embody platial theory, not ad-hoc heuristics.

Operators include:
- Encounter extraction from traces
- Familiarity update functions
- Practice detection via sequence analysis
- Liminality inference from transitions
- Affect and meaning attachment with provenance
- Place emergence as subgraph extraction
"""

from chora.derive.encounters import (
    extract_encounters,
    extract_encounters_from_trace,
    merge_nearby_encounters,
)
from chora.derive.familiarity import (
    update_familiarity,
    compute_familiarity_trajectory,
    decay_all_familiarities,
)
from chora.derive.practices import (
    detect_practices,
    detect_routines,
    find_sequence_patterns,
)
from chora.derive.liminality import (
    infer_liminality,
    detect_boundary_crossings,
)
from chora.derive.affect import (
    attach_affect,
    derive_affect_from_context,
)
from chora.derive.meaning import (
    attach_meaning,
    derive_meaning_from_practices,
)
from chora.derive.place import (
    extract_place,
    find_emergent_places,
)

__all__ = [
    # Encounters
    "extract_encounters",
    "extract_encounters_from_trace",
    "merge_nearby_encounters",
    # Familiarity
    "update_familiarity",
    "compute_familiarity_trajectory",
    "decay_all_familiarities",
    # Practices
    "detect_practices",
    "detect_routines",
    "find_sequence_patterns",
    # Liminality
    "infer_liminality",
    "detect_boundary_crossings",
    # Affect
    "attach_affect",
    "derive_affect_from_context",
    # Meaning
    "attach_meaning",
    "derive_meaning_from_practices",
    # Place
    "extract_place",
    "find_emergent_places",
]
