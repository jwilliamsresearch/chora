"""
Temporal Semantics for Chora

This module implements temporal representation and functions for platial modelling.
All nodes and edges have explicit lifetimes; decay and reinforcement functions
govern familiarity, affect, and practice stability.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Callable, Protocol, TypeAlias

from chora.core.exceptions import InvalidTimeIntervalError, TemporalError


# Type aliases
Timestamp: TypeAlias = datetime
Duration: TypeAlias = timedelta
DecayFunction: TypeAlias = Callable[[float, float], float]
ReinforcementFunction: TypeAlias = Callable[[float, float], float]


class Temporal(Protocol):
    """Protocol for objects with temporal validity."""
    
    @property
    def valid_from(self) -> Timestamp | None: ...
    
    @property
    def valid_to(self) -> Timestamp | None: ...
    
    def is_valid_at(self, timestamp: Timestamp) -> bool: ...


@dataclass(frozen=True, slots=True)
class TimeInterval:
    """
    Represents a time interval with optional open bounds.
    
    A time interval [start, end] where either bound may be None
    (open-ended). Supports containment, overlap, and duration queries.
    
    Parameters
    ----------
    start : Timestamp | None
        Start of interval (inclusive). None means unbounded past.
    end : Timestamp | None
        End of interval (inclusive). None means unbounded future.
    
    Examples
    --------
    >>> from datetime import datetime
    >>> interval = TimeInterval(
    ...     start=datetime(2024, 1, 1),
    ...     end=datetime(2024, 12, 31)
    ... )
    >>> interval.contains(datetime(2024, 6, 15))
    True
    >>> interval.duration
    datetime.timedelta(days=365)
    """
    
    start: Timestamp | None = None
    end: Timestamp | None = None
    
    def __post_init__(self) -> None:
        if self.start is not None and self.end is not None:
            if self.end < self.start:
                raise InvalidTimeIntervalError(
                    "End time cannot precede start time",
                    start=self.start.isoformat(),
                    end=self.end.isoformat()
                )
    
    def contains(self, timestamp: Timestamp) -> bool:
        """Check if timestamp falls within this interval."""
        if self.start is not None and timestamp < self.start:
            return False
        if self.end is not None and timestamp > self.end:
            return False
        return True
    
    def overlaps(self, other: TimeInterval) -> bool:
        """Check if this interval overlaps with another."""
        if self.end is not None and other.start is not None:
            if self.end < other.start:
                return False
        if self.start is not None and other.end is not None:
            if self.start > other.end:
                return False
        return True
    
    @property
    def duration(self) -> Duration | None:
        """Return the duration of this interval, or None if unbounded."""
        if self.start is None or self.end is None:
            return None
        return self.end - self.start
    
    @property
    def is_bounded(self) -> bool:
        """Check if both bounds are defined."""
        return self.start is not None and self.end is not None
    
    @property
    def is_instant(self) -> bool:
        """Check if this represents a single point in time."""
        return self.start is not None and self.start == self.end
    
    @classmethod
    def instant(cls, timestamp: Timestamp) -> TimeInterval:
        """Create an interval representing a single instant."""
        return cls(start=timestamp, end=timestamp)
    
    @classmethod
    def unbounded(cls) -> TimeInterval:
        """Create an unbounded interval (all time)."""
        return cls(start=None, end=None)
    
    @classmethod
    def from_now(cls, duration: Duration) -> TimeInterval:
        """Create an interval from now for the given duration."""
        now = datetime.now()
        return cls(start=now, end=now + duration)


@dataclass(slots=True)
class TemporalValidity:
    """
    Tracks temporal validity with creation and modification timestamps.
    
    Attributes
    ----------
    created_at : Timestamp
        When this entity was created.
    valid_from : Timestamp | None
        Start of validity period.
    valid_to : Timestamp | None
        End of validity period (None = still valid).
    modified_at : Timestamp | None
        When this entity was last modified.
    """
    
    created_at: Timestamp = field(default_factory=datetime.now)
    valid_from: Timestamp | None = None
    valid_to: Timestamp | None = None
    modified_at: Timestamp | None = None
    
    def __post_init__(self) -> None:
        if self.valid_from is None:
            self.valid_from = self.created_at
    
    def is_valid_at(self, timestamp: Timestamp) -> bool:
        """Check if valid at the given timestamp."""
        if self.valid_from is not None and timestamp < self.valid_from:
            return False
        if self.valid_to is not None and timestamp > self.valid_to:
            return False
        return True
    
    @property
    def is_current(self) -> bool:
        """Check if currently valid (valid_to is None or in future)."""
        if self.valid_to is None:
            return True
        return self.valid_to > datetime.now()
    
    def invalidate(self, at: Timestamp | None = None) -> None:
        """Mark as no longer valid."""
        self.valid_to = at or datetime.now()
        self.modified_at = datetime.now()
    
    @property
    def interval(self) -> TimeInterval:
        """Return the validity as a TimeInterval."""
        return TimeInterval(start=self.valid_from, end=self.valid_to)


# =============================================================================
# Decay Functions
# =============================================================================

def exponential_decay(initial_value: float, time_delta: float, 
                      half_life: float = 7.0) -> float:
    """
    Exponential decay function for familiarity and affect.
    
    Parameters
    ----------
    initial_value : float
        Starting value (typically in [0, 1]).
    time_delta : float
        Time elapsed (in days).
    half_life : float
        Time for value to decay to half (in days). Default 7 days.
    
    Returns
    -------
    float
        Decayed value.
    
    Examples
    --------
    >>> exponential_decay(1.0, 7.0, half_life=7.0)  # After one half-life
    0.5
    >>> exponential_decay(1.0, 14.0, half_life=7.0)  # After two half-lives
    0.25
    """
    if time_delta < 0:
        raise TemporalError("Negative time delta", time_delta=time_delta)
    if half_life <= 0:
        raise TemporalError("Half-life must be positive", half_life=half_life)
    
    decay_constant = math.log(2) / half_life
    return initial_value * math.exp(-decay_constant * time_delta)


def linear_decay(initial_value: float, time_delta: float,
                 rate: float = 0.1) -> float:
    """
    Linear decay function.
    
    Parameters
    ----------
    initial_value : float
        Starting value.
    time_delta : float
        Time elapsed (in days).
    rate : float
        Decay rate per day. Default 0.1.
    
    Returns
    -------
    float
        Decayed value, clamped to [0, initial_value].
    """
    if time_delta < 0:
        raise TemporalError("Negative time delta", time_delta=time_delta)
    return max(0.0, initial_value - rate * time_delta)


def power_law_decay(initial_value: float, time_delta: float,
                    exponent: float = 0.5, offset: float = 1.0) -> float:
    """
    Power law decay: value = initial / (offset + time)^exponent
    
    Models slower decay over time, often observed in memory research.
    
    Parameters
    ----------
    initial_value : float
        Starting value.
    time_delta : float
        Time elapsed (in days).
    exponent : float
        Power law exponent. Default 0.5.
    offset : float
        Time offset to avoid division by zero. Default 1.0.
    
    Returns
    -------
    float
        Decayed value.
    """
    if time_delta < 0:
        raise TemporalError("Negative time delta", time_delta=time_delta)
    return initial_value / ((offset + time_delta) ** exponent)


# =============================================================================
# Reinforcement Functions
# =============================================================================

def linear_reinforcement(current_value: float, increment: float = 0.1,
                         maximum: float = 1.0) -> float:
    """
    Linear reinforcement with saturation.
    
    Parameters
    ----------
    current_value : float
        Current value before reinforcement.
    increment : float
        Amount to add. Default 0.1.
    maximum : float
        Maximum allowed value. Default 1.0.
    
    Returns
    -------
    float
        Reinforced value, clamped to maximum.
    """
    return min(maximum, current_value + increment)


def saturating_reinforcement(current_value: float, increment: float = 0.1,
                             maximum: float = 1.0) -> float:
    """
    Saturating reinforcement: diminishing returns near maximum.
    
    Uses formula: new = current + increment * (1 - current/maximum)
    
    Parameters
    ----------
    current_value : float
        Current value before reinforcement.
    increment : float
        Base increment amount. Default 0.1.
    maximum : float
        Asymptotic maximum. Default 1.0.
    
    Returns
    -------
    float
        Reinforced value approaching but never exceeding maximum.
    """
    remaining = 1.0 - (current_value / maximum)
    return min(maximum, current_value + increment * remaining)


def compute_decay(initial_value: float, start: Timestamp, end: Timestamp,
                  decay_fn: DecayFunction = exponential_decay) -> float:
    """
    Compute decayed value between two timestamps.
    
    Parameters
    ----------
    initial_value : float
        Value at start time.
    start : Timestamp
        Starting timestamp.
    end : Timestamp
        Ending timestamp.
    decay_fn : DecayFunction
        Decay function to apply.
    
    Returns
    -------
    float
        Decayed value at end time.
    """
    delta = (end - start).total_seconds() / 86400  # Convert to days
    return decay_fn(initial_value, delta)
