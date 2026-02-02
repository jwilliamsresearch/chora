"""
Familiarity Derivation

Update and compute familiarity states based on encounter patterns.
"""

from __future__ import annotations

from datetime import datetime
from typing import Sequence

from chora.core.types import AgentId, ExtentId, EpistemicLevel
from chora.core.graph import PlatialGraph
from chora.core.encounter import Encounter
from chora.core.familiarity import Familiarity
from chora.core.provenance import Provenance


def update_familiarity(
    graph: PlatialGraph,
    encounter: Encounter
) -> Familiarity:
    """
    Update familiarity based on a new encounter.
    
    Finds or creates a Familiarity node for the agent-extent pair
    and reinforces it based on the encounter.
    
    Parameters
    ----------
    graph : PlatialGraph
        The platial graph.
    encounter : Encounter
        The encounter to process.
    
    Returns
    -------
    Familiarity
        The updated familiarity node.
    """
    agent_id = encounter.agent_id
    extent_id = encounter.extent_id
    
    # Find existing familiarity or create new
    familiarity = _find_familiarity(graph, agent_id, extent_id)
    
    if familiarity is None:
        familiarity = Familiarity(
            agent_id=agent_id,
            extent_id=extent_id,
            epistemic_level=EpistemicLevel.DERIVED,
        )
        graph.add_node(familiarity)
    
    # Reinforce based on encounter duration
    duration_hours = encounter.duration_hours or 1.0
    familiarity.reinforce(duration_hours, at=encounter.end_time or encounter.start_time)
    
    # Add provenance
    familiarity.add_provenance(
        Provenance.derivation(
            source_ids=[str(encounter.id)],
            operator="update_familiarity",
            parameters={"duration_hours": duration_hours}
        )
    )
    
    return familiarity


def compute_familiarity_trajectory(
    encounters: Sequence[Encounter],
    agent_id: AgentId,
    extent_id: ExtentId,
    decay_half_life_days: float = 14.0
) -> list[tuple[datetime, float]]:
    """
    Compute familiarity trajectory over time.
    
    Returns a time series of (timestamp, familiarity_value) pairs
    showing how familiarity evolved through the encounters.
    
    Parameters
    ----------
    encounters : Sequence[Encounter]
        Encounters for this agent-extent pair.
    agent_id : AgentId
        Agent ID.
    extent_id : ExtentId
        Extent ID.
    decay_half_life_days : float
        Half-life for familiarity decay.
    
    Returns
    -------
    list[tuple[datetime, float]]
        Time series of familiarity values.
    """
    # Filter to relevant encounters
    relevant = [
        e for e in encounters
        if e.agent_id == agent_id and e.extent_id == extent_id
    ]
    
    if not relevant:
        return []
    
    # Sort by time
    relevant = sorted(relevant, key=lambda e: e.start_time)
    
    # Build trajectory
    familiarity = Familiarity(
        agent_id=agent_id,
        extent_id=extent_id,
        decay_half_life_days=decay_half_life_days
    )
    
    trajectory = []
    
    for enc in relevant:
        duration = enc.duration_hours or 1.0
        time = enc.end_time or enc.start_time
        familiarity.reinforce(duration, at=time)
        trajectory.append((time, familiarity.value))
    
    return trajectory


def decay_all_familiarities(
    graph: PlatialGraph,
    to_time: datetime | None = None
) -> int:
    """
    Apply decay to all familiarity nodes in the graph.
    
    Returns the number of familiarities updated.
    """
    from chora.core.types import NodeType
    
    count = 0
    to_time = to_time or datetime.now()
    
    for node in graph.nodes(NodeType.FAMILIARITY):
        if isinstance(node, Familiarity):
            node.apply_decay(to_time)
            count += 1
    
    return count


def _find_familiarity(
    graph: PlatialGraph,
    agent_id: AgentId | None,
    extent_id: ExtentId | None
) -> Familiarity | None:
    """Find familiarity node for agent-extent pair."""
    from chora.core.types import NodeType
    
    for node in graph.nodes(NodeType.FAMILIARITY):
        if isinstance(node, Familiarity):
            if node.agent_id == agent_id and node.extent_id == extent_id:
                return node
    return None
