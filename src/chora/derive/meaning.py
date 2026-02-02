"""
Meaning Derivation

Attach and derive symbolic meaning from encounters and practices.
"""

from __future__ import annotations

from typing import Sequence

from chora.core.types import MeaningType, AgentId, ExtentId, EpistemicLevel
from chora.core.encounter import Encounter
from chora.core.practice import Practice
from chora.core.meaning import Meaning
from chora.core.provenance import Provenance


def attach_meaning(
    agent_id: AgentId | None,
    extent_id: ExtentId,
    content: str,
    meaning_type: MeaningType = MeaningType.PERSONAL,
    symbols: Sequence[str] | None = None,
    strength: float = 1.0
) -> Meaning:
    """
    Attach meaning to a place.
    
    Parameters
    ----------
    agent_id : AgentId | None
        Who holds this meaning (None for shared).
    extent_id : ExtentId
        Which place.
    content : str
        The meaning content.
    meaning_type : MeaningType
        Type of meaning.
    symbols : Sequence[str] | None
        Symbolic labels.
    strength : float
        How strongly held [0, 1].
    
    Returns
    -------
    Meaning
        The created meaning node.
    """
    meaning = Meaning(
        meaning_type=meaning_type,
        agent_id=agent_id,
        extent_id=extent_id,
        content=content,
        symbols=tuple(symbols or []),
        strength=strength,
    )
    
    meaning.add_provenance(
        Provenance.derivation(
            source_ids=[],
            operator="attach_meaning",
            parameters={"meaning_type": meaning_type.value}
        )
    )
    
    return meaning


def derive_meaning_from_practices(
    practices: Sequence[Practice],
    agent_id: AgentId,
    extent_id: ExtentId
) -> list[Meaning]:
    """
    Derive meaning from observed practices.
    
    Practices reveal how a place is used and experienced,
    which gives rise to functional and personal meanings.
    
    Parameters
    ----------
    practices : Sequence[Practice]
        Practices involving this place.
    agent_id : AgentId
        Agent whose practices to analyze.
    extent_id : ExtentId
        The place to derive meaning for.
    
    Returns
    -------
    list[Meaning]
        Derived meanings.
    """
    meanings = []
    
    # Analyze practice patterns
    routine_count = sum(1 for p in practices if p.is_routine)
    habit_count = sum(1 for p in practices if p.is_habit)
    total_encounters = sum(p.encounter_count for p in practices)
    
    # Derive functional meaning from routine use
    if routine_count > 0:
        dominant_practice = max(
            [p for p in practices if p.is_routine],
            key=lambda p: p.encounter_count
        )
        
        meaning = Meaning(
            meaning_type=MeaningType.FUNCTIONAL,
            agent_id=agent_id,
            extent_id=extent_id,
            content=f"Regular place for {dominant_practice.name}",
            symbols=("routine", "regular", dominant_practice.practice_type.value),
            strength=min(1.0, dominant_practice.regularity),
            epistemic_level=EpistemicLevel.DERIVED,
        )
        meaning.add_provenance(
            Provenance.derivation(
                source_ids=[str(dominant_practice.id)],
                operator="derive_meaning_from_practices"
            )
        )
        meanings.append(meaning)
    
    # High familiarity suggests personal attachment
    if total_encounters > 20:
        meaning = Meaning(
            meaning_type=MeaningType.PERSONAL,
            agent_id=agent_id,
            extent_id=extent_id,
            content="A significant personal place",
            symbols=("familiar", "personal", "significant"),
            strength=min(1.0, total_encounters / 50),
            epistemic_level=EpistemicLevel.INTERPRETED,
        )
        meaning.add_provenance(
            Provenance.derivation(
                source_ids=[str(p.id) for p in practices],
                operator="derive_meaning_from_practices",
                parameters={"total_encounters": total_encounters}
            )
        )
        meanings.append(meaning)
    
    return meanings
