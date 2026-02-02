"""
Affect Domain Object

Affect represents experiential response distributions attached to
encounters and places — the emotional/felt qualities of experience.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from chora.core.types import NodeType, AffectDimension
from chora.core.node import PlatialNode
from chora.core.uncertainty import GaussianDistribution, UncertaintyValue


@dataclass
class AffectState:
    """
    Multi-dimensional affect state.
    
    Based on dimensional models of affect (Russell's circumplex,
    Mehrabian's PAD model). Each dimension is represented with
    a value and uncertainty.
    """
    
    valence: UncertaintyValue = field(
        default_factory=lambda: UncertaintyValue(0.0, 0.1)
    )
    arousal: UncertaintyValue = field(
        default_factory=lambda: UncertaintyValue(0.0, 0.1)
    )
    dominance: UncertaintyValue | None = None
    safety: UncertaintyValue | None = None
    belonging: UncertaintyValue | None = None
    
    @property
    def is_positive(self) -> bool:
        """Check if valence is positive."""
        return self.valence.value > 0
    
    @property
    def is_high_arousal(self) -> bool:
        """Check if arousal is high."""
        return self.arousal.value > 0.5
    
    def to_dict(self) -> dict[str, float]:
        """Convert to dictionary of values."""
        result = {
            "valence": self.valence.value,
            "arousal": self.arousal.value,
        }
        if self.dominance:
            result["dominance"] = self.dominance.value
        if self.safety:
            result["safety"] = self.safety.value
        if self.belonging:
            result["belonging"] = self.belonging.value
        return result


@dataclass
class Affect(PlatialNode):
    """
    Experiential response distribution.
    
    Affect captures the felt, emotional character of encounters
    and places. It is modelled as a distribution to preserve
    uncertainty and variability.
    
    Parameters
    ----------
    affect_state : AffectState
        Multi-dimensional affect representation.
    source_type : str
        How this affect was determined ("self_report", "derived", etc.).
    intensity : float
        Overall intensity of the affect [0, 1].
    
    Examples
    --------
    >>> # Positive, calm experience
    >>> peaceful = Affect(
    ...     affect_state=AffectState(
    ...         valence=UncertaintyValue(0.8, 0.1),
    ...         arousal=UncertaintyValue(0.2, 0.1)
    ...     ),
    ...     source_type="self_report"
    ... )
    >>> peaceful.affect_state.is_positive
    True
    """
    
    affect_state: AffectState = field(default_factory=AffectState)
    source_type: str = "derived"
    intensity: float = 1.0
    description: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)
    
    node_type: NodeType = field(default=NodeType.AFFECT, init=False)
    
    def __repr__(self) -> str:
        v = self.affect_state.valence.value
        a = self.affect_state.arousal.value
        return f"Affect(valence={v:.2f}, arousal={a:.2f})"
    
    @property
    def valence(self) -> float:
        """Get valence value."""
        return self.affect_state.valence.value
    
    @property
    def arousal(self) -> float:
        """Get arousal value."""
        return self.affect_state.arousal.value
    
    @property
    def quadrant(self) -> str:
        """Get affect quadrant (Russell's circumplex)."""
        v_pos = self.valence >= 0
        a_high = self.arousal >= 0.5
        if v_pos and a_high:
            return "excited"  # Happy, energetic
        elif v_pos and not a_high:
            return "calm"  # Relaxed, peaceful
        elif not v_pos and a_high:
            return "distressed"  # Anxious, angry
        else:
            return "depressed"  # Sad, tired
    
    @classmethod
    def positive(cls, intensity: float = 0.7,
                 arousal: float = 0.5) -> Affect:
        """Create a positive affect."""
        return cls(
            affect_state=AffectState(
                valence=UncertaintyValue(intensity, 0.1),
                arousal=UncertaintyValue(arousal, 0.1)
            )
        )
    
    @classmethod
    def negative(cls, intensity: float = 0.7,
                 arousal: float = 0.5) -> Affect:
        """Create a negative affect."""
        return cls(
            affect_state=AffectState(
                valence=UncertaintyValue(-intensity, 0.1),
                arousal=UncertaintyValue(arousal, 0.1)
            )
        )
    
    @classmethod
    def neutral(cls) -> Affect:
        """Create a neutral affect."""
        return cls(
            affect_state=AffectState(
                valence=UncertaintyValue(0.0, 0.05),
                arousal=UncertaintyValue(0.5, 0.05)
            )
        )
