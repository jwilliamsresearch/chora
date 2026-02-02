"""
Unit tests for temporal logic in chora.core.temporal.
"""
from datetime import datetime, timedelta
import pytest
from chora.core.temporal import (
    exponential_decay,
    linear_decay,
    TimeInterval,
    InvalidTimeIntervalError
)

def test_exponential_decay_calculations():
    """Verify exponential decay math."""
    initial_value = 1.0
    half_life = 10.0  # days
    
    # At t=0, value should be 1.0
    val_0 = exponential_decay(initial_value, 0, half_life)
    assert val_0 == 1.0
    
    # At t=half_life, value should be 0.5
    val_half = exponential_decay(initial_value, half_life, half_life)
    # Floating point comparison
    assert abs(val_half - 0.5) < 1e-9
    
    # At t=2*half_life, value should be 0.25
    val_quarter = exponential_decay(initial_value, half_life * 2, half_life)
    assert abs(val_quarter - 0.25) < 1e-9

def test_linear_decay_calculations():
    """Verify linear decay math."""
    initial = 1.0
    lifetime = 10.0 # days
    rate = initial / lifetime
    
    # t=0 -> 1.0
    assert linear_decay(initial, 0, rate=rate) == 1.0
    
    # t=5 -> 0.5
    assert linear_decay(initial, 5.0, rate=rate) == 0.5
    
    # t=10 -> 0.0
    assert linear_decay(initial, 10.0, rate=rate) == 0.0
    
    # t=11 -> 0.0 (clamped)
    assert linear_decay(initial, 11.0, rate=rate) == 0.0

def test_time_interval_validation():
    """Verify time range validation in TimeInterval."""
    now = datetime.now()
    later = now + timedelta(hours=1)
    
    # Valid range
    valid = TimeInterval(start=now, end=later)
    assert valid.duration == timedelta(hours=1)
    
    # Zero duration (allowed)
    instant = TimeInterval(start=now, end=now)
    assert instant.is_instant
    
    # Invalid range (end before start)
    with pytest.raises(InvalidTimeIntervalError):
        TimeInterval(start=later, end=now)
