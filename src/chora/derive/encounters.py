"""
Encounter Extraction

Derive encounters from GPS traces, check-ins, activity logs, or other
spatio-temporal data sources.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Sequence

from chora.core.types import AgentId, ExtentId, EpistemicLevel
from chora.core.encounter import Encounter
from chora.core.spatial_extent import SpatialExtent
from chora.core.provenance import Provenance, ProvenanceType


@dataclass
class TracePoint:
    """A single point in a GPS or location trace."""
    
    timestamp: datetime
    longitude: float
    latitude: float
    accuracy_m: float = 10.0
    metadata: dict | None = None


@dataclass
class EncounterExtractionConfig:
    """Configuration for encounter extraction."""
    
    # Minimum duration for a valid encounter
    min_duration: timedelta = timedelta(minutes=1)
    # Maximum gap between points to consider continuous
    max_gap: timedelta = timedelta(minutes=30)
    # Spatial clustering radius in meters
    cluster_radius_m: float = 50.0
    # Minimum points required in cluster
    min_points: int = 2


def extract_encounters(
    trace: Sequence[TracePoint],
    agent_id: AgentId,
    extents: Sequence[SpatialExtent],
    config: EncounterExtractionConfig | None = None
) -> list[Encounter]:
    """
    Extract encounters from a location trace.
    
    An encounter is detected when the agent dwells within a spatial
    extent for a minimum duration.
    
    Parameters
    ----------
    trace : Sequence[TracePoint]
        Ordered sequence of location points.
    agent_id : AgentId
        ID of the agent being tracked.
    extents : Sequence[SpatialExtent]
        Spatial extents to match against.
    config : EncounterExtractionConfig | None
        Extraction configuration.
    
    Returns
    -------
    list[Encounter]
        Extracted encounters.
    
    Examples
    --------
    >>> trace = [
    ...     TracePoint(datetime(2024, 1, 1, 10, 0), -0.127, 51.507),
    ...     TracePoint(datetime(2024, 1, 1, 10, 30), -0.127, 51.507),
    ...     TracePoint(datetime(2024, 1, 1, 11, 0), -0.128, 51.508),
    ... ]
    >>> park = SpatialExtent.from_bounds(-0.13, 51.50, -0.12, 51.51, "Park")
    >>> encounters = extract_encounters(trace, AgentId("a1"), [park])
    """
    if config is None:
        config = EncounterExtractionConfig()
    
    encounters = []
    
    for extent in extents:
        if extent.geometry is None:
            continue
        
        # Find points within this extent
        points_in_extent: list[TracePoint] = []
        
        for point in trace:
            if extent.contains_point(point.longitude, point.latitude):
                points_in_extent.append(point)
        
        if len(points_in_extent) < config.min_points:
            continue
        
        # Segment into continuous dwell periods
        segments = _segment_by_gap(points_in_extent, config.max_gap)
        
        for segment in segments:
            duration = segment[-1].timestamp - segment[0].timestamp
            
            if duration >= config.min_duration:
                encounter = Encounter(
                    agent_id=agent_id,
                    extent_id=extent.id,
                    start_time=segment[0].timestamp,
                    end_time=segment[-1].timestamp,
                    epistemic_level=EpistemicLevel.DERIVED,
                )
                encounter.add_provenance(
                    Provenance.derivation(
                        source_ids=[],
                        operator="extract_encounters",
                        parameters={
                            "point_count": len(segment),
                            "min_duration": str(config.min_duration)
                        }
                    )
                )
                encounters.append(encounter)
    
    return encounters


def extract_encounters_from_trace(
    trace: Sequence[TracePoint],
    agent_id: AgentId,
    config: EncounterExtractionConfig | None = None
) -> list[Encounter]:
    """
    Extract encounters by clustering a trace without predefined extents.
    
    Detects dwell locations by finding spatial clusters of points
    that exceed the minimum duration threshold.
    """
    if config is None:
        config = EncounterExtractionConfig()
    
    if len(trace) < config.min_points:
        return []
    
    encounters = []
    clusters = _cluster_points(list(trace), config.cluster_radius_m)
    
    for cluster in clusters:
        if len(cluster) < config.min_points:
            continue
        
        # Sort by time
        cluster_sorted = sorted(cluster, key=lambda p: p.timestamp)
        segments = _segment_by_gap(cluster_sorted, config.max_gap)
        
        for segment in segments:
            duration = segment[-1].timestamp - segment[0].timestamp
            
            if duration >= config.min_duration:
                # Create extent from cluster centroid
                avg_lon = sum(p.longitude for p in segment) / len(segment)
                avg_lat = sum(p.latitude for p in segment) / len(segment)
                extent = SpatialExtent.point(avg_lon, avg_lat, "derived_location")
                
                encounter = Encounter(
                    agent_id=agent_id,
                    extent_id=extent.id,
                    start_time=segment[0].timestamp,
                    end_time=segment[-1].timestamp,
                    epistemic_level=EpistemicLevel.DERIVED,
                )
                encounter.set_metadata("derived_extent", extent)
                encounters.append(encounter)
    
    return encounters


def merge_nearby_encounters(
    encounters: Sequence[Encounter],
    max_time_gap: timedelta = timedelta(minutes=5)
) -> list[Encounter]:
    """
    Merge temporally adjacent encounters at the same extent.
    """
    if not encounters:
        return []
    
    # Sort by extent and time
    sorted_encs = sorted(encounters, key=lambda e: (str(e.extent_id), e.start_time))
    merged = []
    current = sorted_encs[0]
    
    for enc in sorted_encs[1:]:
        if (enc.extent_id == current.extent_id and 
            current.end_time is not None and
            enc.start_time - current.end_time <= max_time_gap):
            # Extend current encounter
            current = Encounter(
                agent_id=current.agent_id,
                extent_id=current.extent_id,
                start_time=current.start_time,
                end_time=enc.end_time,
                epistemic_level=current.epistemic_level,
            )
        else:
            merged.append(current)
            current = enc
    
    merged.append(current)
    return merged


def _segment_by_gap(
    points: list[TracePoint],
    max_gap: timedelta
) -> list[list[TracePoint]]:
    """Segment points into continuous sequences based on time gaps."""
    if not points:
        return []
    
    segments = []
    current_segment = [points[0]]
    
    for i in range(1, len(points)):
        gap = points[i].timestamp - points[i-1].timestamp
        if gap <= max_gap:
            current_segment.append(points[i])
        else:
            segments.append(current_segment)
            current_segment = [points[i]]
    
    segments.append(current_segment)
    return segments


def _cluster_points(
    points: list[TracePoint],
    radius_m: float
) -> list[list[TracePoint]]:
    """Simple spatial clustering using greedy approach."""
    if not points:
        return []
    
    # Convert radius to approximate degrees (rough approximation)
    radius_deg = radius_m / 111000.0
    
    clusters = []
    used = set()
    
    for i, point in enumerate(points):
        if i in used:
            continue
        
        cluster = [point]
        used.add(i)
        
        for j, other in enumerate(points):
            if j in used:
                continue
            
            dist = ((point.longitude - other.longitude) ** 2 + 
                    (point.latitude - other.latitude) ** 2) ** 0.5
            
            if dist <= radius_deg:
                cluster.append(other)
                used.add(j)
        
        clusters.append(cluster)
    
    return clusters
