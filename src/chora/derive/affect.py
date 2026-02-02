"""
Affect Derivation

Attach and derive experiential affect from encounters.
"""

from __future__ import annotations

from typing import Any

from chora.core.types import EpistemicLevel, ContextType
from chora.core.encounter import Encounter
from chora.core.context import Context
from chora.core.affect import Affect, AffectState
from chora.core.uncertainty import UncertaintyValue
from chora.core.provenance import Provenance


def attach_affect(
    encounter: Encounter,
    valence: float,
    arousal: float,
    source: str = "external",
    uncertainty: float = 0.1
) -> Affect:
    """
    Attach affect to an encounter with explicit values.
    
    Parameters
    ----------
    encounter : Encounter
        The encounter to attach affect to.
    valence : float
        Valence value [-1, 1].
    arousal : float
        Arousal value [0, 1].
    source : str
        Source of affect data ("self_report", "derived", "external").
    uncertainty : float
        Uncertainty in the affect values.
    
    Returns
    -------
    Affect
        The created affect node.
    """
    affect = Affect(
        affect_state=AffectState(
            valence=UncertaintyValue(valence, uncertainty),
            arousal=UncertaintyValue(arousal, uncertainty)
        ),
        source_type=source,
        epistemic_level=EpistemicLevel.OBSERVED if source == "self_report" 
                        else EpistemicLevel.DERIVED,
    )
    
    affect.add_provenance(
        Provenance.derivation(
            source_ids=[str(encounter.id)],
            operator="attach_affect",
            parameters={"source": source}
        )
    )
    
    return affect


def derive_affect_from_context(
    encounter: Encounter,
    contexts: list[Context]
) -> Affect | None:
    """
    Derive affect from encounter context.
    
    Uses contextual information to infer likely affect.
    This is a theory-encoded heuristic based on environmental psychology.
    
    Parameters
    ----------
    encounter : Encounter
        The encounter.
    contexts : list[Context]
        Associated contexts.
    
    Returns
    -------
    Affect | None
        Derived affect, or None if insufficient context.
    """
    if not contexts:
        return None
    
    # Start with neutral baseline
    valence = 0.0
    arousal = 0.5
    uncertainty = 0.2
    
    for ctx in contexts:
        # Purposive context affects valence
        if ctx.context_type == ContextType.PURPOSIVE:
            purpose = str(ctx.value).lower() if ctx.value else ""
            if "leisure" in purpose or "recreation" in purpose:
                valence += 0.3
            elif "work" in purpose or "commute" in purpose:
                valence -= 0.1
                arousal += 0.1
            elif "explore" in purpose:
                valence += 0.2
                arousal += 0.2
        
        # Social context
        elif ctx.context_type == ContextType.SOCIAL:
            value = ctx.value if isinstance(ctx.value, dict) else {}
            if value.get("alone"):
                arousal -= 0.1
            elif value.get("companions"):
                valence += 0.1 * min(len(value["companions"]), 3)
        
        # Environmental context
        elif ctx.context_type == ContextType.ENVIRONMENTAL:
            conditions = ctx.value if isinstance(ctx.value, dict) else {}
            if conditions.get("weather") == "sunny":
                valence += 0.2
            elif conditions.get("weather") == "rainy":
                valence -= 0.1
            if conditions.get("crowded"):
                arousal += 0.2
                valence -= 0.1
        
        # Temporal context
        elif ctx.context_type == ContextType.TEMPORAL:
            time_val = str(ctx.value).lower() if ctx.value else ""
            if "morning" in time_val:
                arousal += 0.1
            elif "evening" in time_val:
                arousal -= 0.1
                valence += 0.05
    
    # Clamp values
    valence = max(-1.0, min(1.0, valence))
    arousal = max(0.0, min(1.0, arousal))
    
    affect = Affect(
        affect_state=AffectState(
            valence=UncertaintyValue(valence, uncertainty),
            arousal=UncertaintyValue(arousal, uncertainty)
        ),
        source_type="context_derived",
        epistemic_level=EpistemicLevel.DERIVED,
    )
    
    affect.add_provenance(
        Provenance.derivation(
            source_ids=[str(encounter.id)] + [str(c.id) for c in contexts],
            operator="derive_affect_from_context",
            parameters={"context_count": len(contexts)}
        )
    )
    
    return affect
