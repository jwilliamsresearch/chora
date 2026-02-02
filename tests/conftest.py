import pytest
from datetime import datetime, timedelta
from chora.core import (
    Agent, SpatialExtent, Encounter, PlatialGraph,
    PlatialEdge, EdgeType
)

@pytest.fixture
def basic_graph():
    """Return a fresh empty graph."""
    return PlatialGraph(name="Test Graph")

@pytest.fixture
def agent_alice():
    """Return a standard test agent."""
    return Agent.individual("Alice", age=30)

@pytest.fixture
def park_extent():
    """Return a standard test spatial extent."""
    return SpatialExtent.from_bounds(
        -0.127, 51.507, -0.126, 51.508, 
        name="Test Park"
    )

@pytest.fixture
def encounter_factory(agent_alice, park_extent):
    """
    Return a function that creates encounters easily.
    
    Usage:
        enc = encounter_factory(start_time=dt)
    """
    def _create_encounter(
        agent=agent_alice,
        extent=park_extent,
        start_time=None,
        duration_minutes=60,
        activity="testing"
    ):
        start = start_time or datetime.now()
        end = start + timedelta(minutes=duration_minutes)
        return Encounter(
            agent_id=agent.id,
            extent_id=extent.id,
            start_time=start,
            end_time=end,
            activity=activity
        )
    return _create_encounter
