"""
Practice Detection

Detect emergent practices via sequence and motif analysis.
"""

from __future__ import annotations

from collections import Counter, defaultdict
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Sequence

from chora.core.types import AgentId, ExtentId, PracticeType, EpistemicLevel
from chora.core.encounter import Encounter
from chora.core.practice import Practice
from chora.core.provenance import Provenance


@dataclass
class PracticeDetectionConfig:
    """Configuration for practice detection."""
    
    # Minimum occurrences for a routine
    min_occurrences: int = 3
    # Time window for considering patterns
    time_window_days: int = 30
    # Time tolerance for matching (e.g., ±1 hour)
    time_tolerance: timedelta = timedelta(hours=1)
    # Minimum regularity score
    min_regularity: float = 0.5


def detect_practices(
    encounters: Sequence[Encounter],
    agent_id: AgentId,
    config: PracticeDetectionConfig | None = None
) -> list[Practice]:
    """
    Detect practices from encounter sequences.
    
    Identifies routines, habits, and other patterns based on
    spatial, temporal, and sequential regularities.
    
    Parameters
    ----------
    encounters : Sequence[Encounter]
        Encounters to analyze.
    agent_id : AgentId
        Agent to detect practices for.
    config : PracticeDetectionConfig | None
        Detection configuration.
    
    Returns
    -------
    list[Practice]
        Detected practices.
    """
    if config is None:
        config = PracticeDetectionConfig()
    
    # Filter to agent
    agent_encounters = [e for e in encounters if e.agent_id == agent_id]
    
    if len(agent_encounters) < config.min_occurrences:
        return []
    
    practices = []
    
    # Detect location-based routines
    routines = detect_routines(agent_encounters, config)
    practices.extend(routines)
    
    # Detect sequence patterns
    sequences = find_sequence_patterns(agent_encounters, config)
    for pattern_name, enc_ids, regularity in sequences:
        practice = Practice(
            practice_type=PracticeType.ROUTINE,
            name=pattern_name,
            encounter_ids=tuple(enc_ids),
            regularity=regularity,
            epistemic_level=EpistemicLevel.DERIVED,
        )
        practice.add_provenance(
            Provenance.derivation(
                source_ids=list(enc_ids),
                operator="find_sequence_patterns"
            )
        )
        practices.append(practice)
    
    return practices


def detect_routines(
    encounters: Sequence[Encounter],
    config: PracticeDetectionConfig | None = None
) -> list[Practice]:
    """
    Detect location-time routines.
    
    A routine is a repeated pattern of visiting the same location
    at similar times.
    """
    if config is None:
        config = PracticeDetectionConfig()
    
    # Group by extent and time-of-day bucket
    patterns: dict[tuple[str, int], list[Encounter]] = defaultdict(list)
    
    for enc in encounters:
        if enc.extent_id is None:
            continue
        
        hour_bucket = enc.start_time.hour // 4  # 4-hour buckets
        key = (str(enc.extent_id), hour_bucket)
        patterns[key].append(enc)
    
    routines = []
    
    for (extent_id, hour_bucket), pattern_encounters in patterns.items():
        if len(pattern_encounters) < config.min_occurrences:
            continue
        
        # Calculate regularity
        regularity = _calculate_regularity(pattern_encounters)
        
        if regularity >= config.min_regularity:
            time_label = _hour_bucket_to_label(hour_bucket)
            
            practice = Practice(
                practice_type=PracticeType.ROUTINE,
                name=f"{time_label} visit to {extent_id}",
                encounter_ids=tuple(str(e.id) for e in pattern_encounters),
                frequency=len(pattern_encounters) / config.time_window_days,
                regularity=regularity,
                typical_time=time_label,
                epistemic_level=EpistemicLevel.DERIVED,
            )
            practice.add_provenance(
                Provenance.derivation(
                    source_ids=[str(e.id) for e in pattern_encounters],
                    operator="detect_routines"
                )
            )
            routines.append(practice)
    
    return routines


def find_sequence_patterns(
    encounters: Sequence[Encounter],
    config: PracticeDetectionConfig | None = None
) -> list[tuple[str, list[str], float]]:
    """
    Find sequential patterns (A → B → C).
    
    Returns list of (pattern_name, encounter_ids, regularity).
    """
    if config is None:
        config = PracticeDetectionConfig()
    
    # Sort encounters by time
    sorted_encs = sorted(encounters, key=lambda e: e.start_time)
    
    # Find bigram patterns
    bigrams: dict[tuple[str, str], list[tuple[str, str]]] = defaultdict(list)
    
    for i in range(len(sorted_encs) - 1):
        enc1, enc2 = sorted_encs[i], sorted_encs[i + 1]
        
        if enc1.extent_id is None or enc2.extent_id is None:
            continue
        
        # Check if they're on the same day
        if enc1.start_time.date() == enc2.start_time.date():
            key = (str(enc1.extent_id), str(enc2.extent_id))
            bigrams[key].append((str(enc1.id), str(enc2.id)))
    
    patterns = []
    
    for (loc1, loc2), instances in bigrams.items():
        if len(instances) >= config.min_occurrences:
            regularity = len(instances) / len(sorted_encs)
            enc_ids = [eid for pair in instances for eid in pair]
            patterns.append(
                (f"{loc1} → {loc2}", enc_ids, regularity)
            )
    
    return patterns


def _calculate_regularity(encounters: Sequence[Encounter]) -> float:
    """Calculate regularity score based on timing consistency."""
    if len(encounters) < 2:
        return 0.0
    
    # Calculate std of start times (hour + minute/60)
    times = [e.start_time.hour + e.start_time.minute / 60 for e in encounters]
    mean_time = sum(times) / len(times)
    variance = sum((t - mean_time) ** 2 for t in times) / len(times)
    std = variance ** 0.5
    
    # Convert to regularity score (lower std = higher regularity)
    # Max std is about 12 hours (half day)
    regularity = max(0, 1 - std / 6)
    return regularity


def _hour_bucket_to_label(bucket: int) -> str:
    """Convert 4-hour bucket to label."""
    labels = {
        0: "night (0-4)",
        1: "early morning (4-8)",
        2: "morning (8-12)",
        3: "afternoon (12-16)",
        4: "evening (16-20)",
        5: "night (20-24)",
    }
    return labels.get(bucket, f"time bucket {bucket}")
