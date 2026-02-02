"""
Familiarity Domain Object

Familiarity is an evolving state variable that represents accumulated
experience with a place — it grows with encounters and decays with time.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from chora.core.types import NodeType, AgentId, ExtentId
from chora.core.node import PlatialNode
from chora.core.temporal import (
    exponential_decay, 
    saturating_reinforcement,
    compute_decay
)
from chora.core.uncertainty import UncertaintyValue


@dataclass
class Familiarity(PlatialNode):
    """
    Evolving state variable representing accumulated place experience.
    
    Familiarity captures how well an agent knows a place through
    repeated encounters. It increases with each encounter and decays
    over time without new encounters.
    
    Parameters
    ----------
    agent_id : AgentId
        ID of the agent this familiarity belongs to.
    extent_id : ExtentId
        ID of the spatial extent.
    value : float
        Current familiarity level [0, 1].
    encounter_count : int
        Total number of encounters contributing to this familiarity.
    last_encounter : datetime | None
        When the most recent encounter occurred.
    total_duration_hours : float
        Cumulative time spent at this extent.
    
    Examples
    --------
    >>> fam = Familiarity(
    ...     agent_id=AgentId("walker_001"),
    ...     extent_id=ExtentId("park_central"),
    ...     value=0.75,
    ...     encounter_count=15,
    ...     total_duration_hours=22.5
    ... )
    >>> fam.is_familiar
    True
    """
    
    agent_id: AgentId | None = None
    extent_id: ExtentId | None = None
    value: float = 0.0
    uncertainty: UncertaintyValue | None = None
    encounter_count: int = 0
    last_encounter: datetime | None = None
    first_encounter: datetime | None = None
    total_duration_hours: float = 0.0
    decay_half_life_days: float = 14.0
    metadata: dict[str, Any] = field(default_factory=dict)
    
    node_type: NodeType = field(default=NodeType.FAMILIARITY, init=False)
    
    def __post_init__(self) -> None:
        if not 0.0 <= self.value <= 1.0:
            raise ValueError("Familiarity value must be in [0, 1]")
    
    def __repr__(self) -> str:
        return f"Familiarity(value={self.value:.2f}, encounters={self.encounter_count})"
    
    @property
    def is_familiar(self) -> bool:
        """Check if this represents familiar territory."""
        return self.value >= 0.5
    
    @property
    def is_very_familiar(self) -> bool:
        """Check if this represents very familiar territory."""
        return self.value >= 0.8
    
    @property
    def is_novel(self) -> bool:
        """Check if this represents novel territory."""
        return self.value < 0.2
    
    @property
    def days_since_last_encounter(self) -> float | None:
        """Calculate days since last encounter."""
        if self.last_encounter is None:
            return None
        delta = datetime.now() - self.last_encounter
        return delta.total_seconds() / 86400
    
    @property
    def current_value(self) -> float:
        """Get current value after applying decay."""
        if self.last_encounter is None:
            return self.value
        return compute_decay(
            self.value,
            self.last_encounter,
            datetime.now(),
            lambda v, t: exponential_decay(v, t, self.decay_half_life_days)
        )
    
    def reinforce(self, encounter_duration_hours: float = 1.0,
                  at: datetime | None = None) -> float:
        """
        Reinforce familiarity from a new encounter.
        
        Parameters
        ----------
        encounter_duration_hours : float
            Duration of the encounter in hours.
        at : datetime | None
            When the encounter occurred.
        
        Returns
        -------
        float
            New familiarity value.
        """
        now = at or datetime.now()
        
        # First, apply decay since last encounter
        if self.last_encounter is not None:
            self.value = compute_decay(
                self.value,
                self.last_encounter,
                now,
                lambda v, t: exponential_decay(v, t, self.decay_half_life_days)
            )
        
        # Then reinforce based on duration
        increment = min(0.1, 0.05 * encounter_duration_hours)
        self.value = saturating_reinforcement(self.value, increment)
        
        # Update tracking
        self.encounter_count += 1
        self.last_encounter = now
        self.total_duration_hours += encounter_duration_hours
        
        if self.first_encounter is None:
            self.first_encounter = now
        
        return self.value
    
    def apply_decay(self, to: datetime | None = None) -> float:
        """Apply decay up to the specified time."""
        if self.last_encounter is None:
            return self.value
        
        end = to or datetime.now()
        self.value = compute_decay(
            self.value,
            self.last_encounter,
            end,
            lambda v, t: exponential_decay(v, t, self.decay_half_life_days)
        )
        return self.value
    
    @classmethod
    def initial(cls, agent_id: AgentId, extent_id: ExtentId) -> Familiarity:
        """Create initial (zero) familiarity."""
        return cls(agent_id=agent_id, extent_id=extent_id, value=0.0)
    
    @classmethod
    def established(cls, agent_id: AgentId, extent_id: ExtentId,
                    value: float = 0.8) -> Familiarity:
        """Create established familiarity."""
        return cls(
            agent_id=agent_id,
            extent_id=extent_id,
            value=value,
            encounter_count=20,
            last_encounter=datetime.now()
        )
