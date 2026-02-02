"""
Practice Domain Object

Practice represents emergent, patterned structures over encounters —
the regularities that constitute routines, habits, and rituals.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Any, Sequence

from chora.core.types import NodeType, PracticeType, EncounterId
from chora.core.node import PlatialNode
from chora.core.temporal import TimeInterval


@dataclass
class Practice(PlatialNode):
    """
    An emergent, patterned structure over encounters.
    
    Practices are detected from patterns in encounter sequences.
    They represent routines, habits, rituals, and other regularities
    that characterise how an agent engages with places.
    
    Parameters
    ----------
    practice_type : PracticeType
        Classification of this practice.
    name : str
        Name for this practice.
    encounter_ids : tuple[EncounterId, ...]
        IDs of encounters that constitute this practice.
    frequency : float
        How often this practice occurs (events per day).
    regularity : float
        How regular/consistent the pattern is [0, 1].
    stability : float
        How stable this practice is over time [0, 1].
    
    Examples
    --------
    >>> # A morning routine
    >>> morning_walk = Practice(
    ...     practice_type=PracticeType.ROUTINE,
    ...     name="Morning park walk",
    ...     encounter_ids=(EncounterId("enc_001"), EncounterId("enc_042")),
    ...     frequency=0.8,  # ~6 times per week
    ...     regularity=0.9,
    ...     stability=0.85
    ... )
    """
    
    practice_type: PracticeType = PracticeType.ROUTINE
    name: str = ""
    encounter_ids: tuple[str, ...] = field(default_factory=tuple)
    frequency: float = 0.0
    regularity: float = 0.0
    stability: float = 0.0
    typical_duration: timedelta | None = None
    typical_time: str = ""  # e.g., "morning", "08:00-09:00"
    metadata: dict[str, Any] = field(default_factory=dict)
    
    node_type: NodeType = field(default=NodeType.PRACTICE, init=False)
    
    def __post_init__(self) -> None:
        for val in (self.regularity, self.stability):
            if not 0.0 <= val <= 1.0:
                raise ValueError("regularity and stability must be in [0, 1]")
    
    def __repr__(self) -> str:
        return f"Practice(type={self.practice_type}, name={self.name!r})"
    
    @property
    def encounter_count(self) -> int:
        """Number of encounters in this practice."""
        return len(self.encounter_ids)
    
    @property
    def is_routine(self) -> bool:
        return self.practice_type == PracticeType.ROUTINE
    
    @property
    def is_habit(self) -> bool:
        return self.practice_type == PracticeType.HABIT
    
    @property
    def is_established(self) -> bool:
        """Check if practice is well-established (high stability & regularity)."""
        return self.stability >= 0.7 and self.regularity >= 0.7
    
    def add_encounter(self, encounter_id: str) -> None:
        """Add an encounter to this practice."""
        self.encounter_ids = (*self.encounter_ids, encounter_id)
    
    @classmethod
    def routine(cls, name: str, frequency: float,
                encounter_ids: Sequence[str] | None = None,
                **kwargs: Any) -> Practice:
        """Create a routine practice."""
        return cls(
            practice_type=PracticeType.ROUTINE,
            name=name,
            frequency=frequency,
            encounter_ids=tuple(encounter_ids or []),
            **kwargs
        )
    
    @classmethod
    def habit(cls, name: str, 
              encounter_ids: Sequence[str] | None = None,
              **kwargs: Any) -> Practice:
        """Create a habit practice."""
        return cls(
            practice_type=PracticeType.HABIT,
            name=name,
            encounter_ids=tuple(encounter_ids or []),
            **kwargs
        )
    
    @classmethod
    def avoidance(cls, name: str, description: str = "",
                  **kwargs: Any) -> Practice:
        """Create an avoidance practice (pattern of avoiding places)."""
        return cls(
            practice_type=PracticeType.AVOIDANCE,
            name=name,
            metadata={"description": description},
            **kwargs
        )
