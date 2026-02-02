"""
Liminality Inference

Infer liminal qualities from spatial transitions and boundary crossings.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

from chora.core.types import LiminalityType, EpistemicLevel
from chora.core.encounter import Encounter
from chora.core.spatial_extent import SpatialExtent
from chora.core.liminality import Liminality
from chora.core.provenance import Provenance


@dataclass
class LiminalityInferenceConfig:
    """Configuration for liminality inference."""
    
    # Minimum transition count to identify as liminal
    min_transitions: int = 3
    # Intensity threshold for strong liminality
    strong_threshold: float = 0.7


def infer_liminality(
    encounters: Sequence[Encounter],
    extents: dict[str, SpatialExtent],
    config: LiminalityInferenceConfig | None = None
) -> list[Liminality]:
    """
    Infer liminal zones from transition patterns.
    
    Identifies spatial extents that frequently serve as transition
    points between other places.
    
    Parameters
    ----------
    encounters : Sequence[Encounter]
        Ordered encounters.
    extents : dict[str, SpatialExtent]
        Mapping of extent IDs to SpatialExtent objects.
    config : LiminalityInferenceConfig | None
        Inference configuration.
    
    Returns
    -------
    list[Liminality]
        Inferred liminal zones.
    """
    if config is None:
        config = LiminalityInferenceConfig()
    
    crossings = detect_boundary_crossings(encounters, extents)
    liminal_zones = []
    
    # Aggregate crossings by extent
    extent_crossings: dict[str, list[tuple[str, str]]] = {}
    
    for extent_id, from_type, to_type in crossings:
        if extent_id not in extent_crossings:
            extent_crossings[extent_id] = []
        extent_crossings[extent_id].append((from_type, to_type))
    
    for extent_id, transitions in extent_crossings.items():
        if len(transitions) < config.min_transitions:
            continue
        
        # Calculate intensity based on transition frequency
        intensity = min(1.0, len(transitions) / (config.min_transitions * 2))
        
        # Find most common transition pattern
        from_types = [t[0] for t in transitions]
        to_types = [t[1] for t in transitions]
        common_from = max(set(from_types), key=from_types.count)
        common_to = max(set(to_types), key=to_types.count)
        
        liminal = Liminality(
            liminality_type=LiminalityType.SPATIAL,
            extent_ids=(extent_id,),
            intensity=intensity,
            transitional_from=common_from,
            transitional_to=common_to,
            epistemic_level=EpistemicLevel.DERIVED,
        )
        liminal.add_provenance(
            Provenance.derivation(
                source_ids=[],
                operator="infer_liminality",
                parameters={"transition_count": len(transitions)}
            )
        )
        liminal_zones.append(liminal)
    
    return liminal_zones


def detect_boundary_crossings(
    encounters: Sequence[Encounter],
    extents: dict[str, SpatialExtent]
) -> list[tuple[str, str, str]]:
    """
    Detect boundary crossings between adjacent encounters.
    
    Returns list of (boundary_extent_id, from_type, to_type) tuples.
    """
    if len(encounters) < 2:
        return []
    
    # Sort by time
    sorted_encs = sorted(encounters, key=lambda e: e.start_time)
    crossings = []
    
    for i in range(1, len(sorted_encs)):
        prev_enc = sorted_encs[i - 1]
        curr_enc = sorted_encs[i]
        
        prev_id = str(prev_enc.extent_id) if prev_enc.extent_id else None
        curr_id = str(curr_enc.extent_id) if curr_enc.extent_id else None
        
        if prev_id and curr_id and prev_id != curr_id:
            # Get extent types from semantic hints
            prev_type = _get_extent_type(prev_id, extents)
            curr_type = _get_extent_type(curr_id, extents)
            
            # Short encounters at transition point may be liminal
            if curr_enc.duration_seconds is not None and curr_enc.duration_seconds < 300:
                crossings.append((curr_id, prev_type, curr_type))
    
    return crossings


def _get_extent_type(extent_id: str, extents: dict[str, SpatialExtent]) -> str:
    """Get extent type from semantic hints or default."""
    if extent_id in extents:
        extent = extents[extent_id]
        return extent.get_hint("type", extent.extent_type)
    return "unknown"
