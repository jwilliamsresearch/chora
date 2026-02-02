"""
Platial Similarity Measures
"""

from __future__ import annotations

from chora.derive.place import EmergentPlace
from chora.core.practice import Practice


def place_similarity(p1: EmergentPlace, p2: EmergentPlace) -> float:
    """
    Compute similarity between two emergent places.
    
    Considers familiarity, affect, and encounter patterns.
    """
    score = 0.0
    
    # Familiarity similarity
    fam_diff = abs(p1.familiarity_score - p2.familiarity_score)
    score += 0.3 * (1 - fam_diff)
    
    # Affect similarity
    affect_diff = abs(p1.affect_valence_mean - p2.affect_valence_mean) / 2
    score += 0.3 * (1 - affect_diff)
    
    # Encounter count similarity (log scale)
    import math
    if p1.encounter_count > 0 and p2.encounter_count > 0:
        log_ratio = abs(math.log(p1.encounter_count) - math.log(p2.encounter_count))
        score += 0.2 * max(0, 1 - log_ratio / 3)
    
    # Meaning count similarity
    max_meaning = max(p1.meaning_count, p2.meaning_count, 1)
    meaning_diff = abs(p1.meaning_count - p2.meaning_count) / max_meaning
    score += 0.2 * (1 - meaning_diff)
    
    return score


def practice_similarity(p1: Practice, p2: Practice) -> float:
    """
    Compute similarity between two practices.
    """
    score = 0.0
    
    # Type match
    if p1.practice_type == p2.practice_type:
        score += 0.4
    
    # Regularity similarity
    reg_diff = abs(p1.regularity - p2.regularity)
    score += 0.3 * (1 - reg_diff)
    
    # Frequency similarity
    if p1.frequency > 0 and p2.frequency > 0:
        freq_ratio = min(p1.frequency, p2.frequency) / max(p1.frequency, p2.frequency)
        score += 0.3 * freq_ratio
    
    return score
