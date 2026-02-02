"""
Encounter Domain Object

An Encounter is the atomic unit of platial experience — a spatio-temporal
relation between an agent and a spatial extent.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Any

from chora.core.types import NodeType, EpistemicLevel, EncounterId, AgentId, ExtentId
from chora.core.node import PlatialNode
from chora.core.temporal import TimeInterval


@dataclass
class Encounter(PlatialNode):
    """
    A spatio-temporal relation between an agent and a spatial extent.
    
    Encounters are the foundational units of platial modelling. They
    capture the fact that an agent was present at a spatial extent
    during a specific time interval. Place emerges from patterns of
    repeated encounters.
    
    Parameters
    ----------
    agent_id : AgentId
        ID of the agent participating in this encounter.
    extent_id : ExtentId
        ID of the spatial extent where the encounter occurred.
    start_time : datetime
        When the encounter began.
    end_time : datetime | None
        When the encounter ended (None for ongoing).
    duration : timedelta | None
        Computed duration (for convenience).
    activity : str
        Optional activity classification.
    intensity : float
        Engagement intensity in [0, 1].
    
    Examples
    --------
    >>> from datetime import datetime, timedelta
    >>> 
    >>> encounter = Encounter(
    ...     agent_id=AgentId("walker_001"),
    ...     extent_id=ExtentId("park_central"),
    ...     start_time=datetime(2024, 6, 15, 10, 0),
    ...     end_time=datetime(2024, 6, 15, 11, 30),
    ...     activity="walking",
    ...     intensity=0.8
    ... )
    >>> encounter.duration
    datetime.timedelta(seconds=5400)
    """
    
    agent_id: AgentId | None = None
    extent_id: ExtentId | None = None
    start_time: datetime = field(default_factory=datetime.now)
    end_time: datetime | None = None
    activity: str = ""
    intensity: float = 1.0
    encounter_id: EncounterId | None = None
    metadata: dict[str, Any] = field(default_factory=dict)
    
    # Set node_type
    node_type: NodeType = field(default=NodeType.ENCOUNTER, init=False)
    
    def __post_init__(self) -> None:
        if self.end_time is not None and self.end_time < self.start_time:
            raise ValueError("end_time cannot precede start_time")
        if not 0.0 <= self.intensity <= 1.0:
            raise ValueError("intensity must be in [0, 1]")
    
    def __repr__(self) -> str:
        return (f"Encounter(agent={self.agent_id!r}, "
                f"extent={self.extent_id!r}, time={self.start_time})")
    
    @property
    def duration(self) -> timedelta | None:
        """Calculate encounter duration."""
        if self.end_time is None:
            return None
        return self.end_time - self.start_time
    
    @property
    def duration_seconds(self) -> float | None:
        """Get duration in seconds."""
        d = self.duration
        return d.total_seconds() if d else None
    
    @property
    def duration_hours(self) -> float | None:
        """Get duration in hours."""
        d = self.duration
        return d.total_seconds() / 3600 if d else None
    
    @property
    def is_ongoing(self) -> bool:
        """Check if encounter is still ongoing."""
        return self.end_time is None
    
    @property
    def time_interval(self) -> TimeInterval:
        """Get the encounter as a TimeInterval."""
        return TimeInterval(start=self.start_time, end=self.end_time)
    
    @property
    def midpoint_time(self) -> datetime:
        """Get the temporal midpoint of the encounter."""
        if self.end_time is None:
            return self.start_time
        duration = self.end_time - self.start_time
        return self.start_time + duration / 2
    
    def overlaps(self, other: Encounter) -> bool:
        """Check if this encounter overlaps temporally with another."""
        return self.time_interval.overlaps(other.time_interval)
    
    def end_now(self) -> None:
        """End an ongoing encounter."""
        if self.end_time is None:
            self.end_time = datetime.now()
    
    def set_metadata(self, key: str, value: Any) -> None:
        """Set encounter metadata."""
        self.metadata[key] = value
    
    def get_metadata(self, key: str, default: Any = None) -> Any:
        """Get encounter metadata."""
        return self.metadata.get(key, default)
    
    @classmethod
    def instant(cls, agent_id: AgentId, extent_id: ExtentId,
                at: datetime | None = None, **kwargs: Any) -> Encounter:
        """Create an instantaneous encounter (start == end)."""
        now = at or datetime.now()
        return cls(
            agent_id=agent_id,
            extent_id=extent_id,
            start_time=now,
            end_time=now,
            **kwargs
        )
    
    @classmethod
    def ongoing(cls, agent_id: AgentId, extent_id: ExtentId,
                started_at: datetime | None = None, **kwargs: Any) -> Encounter:
        """Create an ongoing encounter (no end time)."""
        return cls(
            agent_id=agent_id,
            extent_id=extent_id,
            start_time=started_at or datetime.now(),
            end_time=None,
            **kwargs
        )
