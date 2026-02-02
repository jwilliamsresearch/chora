"""
Platial Queries

High-level query interface for common platial queries.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Callable, Iterator

from chora.core.types import NodeType, EdgeType, AgentId, ExtentId
from chora.core.graph import PlatialGraph
from chora.core.node import PlatialNode
from chora.core.familiarity import Familiarity
from chora.core.affect import Affect
from chora.core.encounter import Encounter
from chora.derive.place import EmergentPlace, extract_place


@dataclass
class PlatialQuery:
    """
    Fluent query builder for platial queries.
    
    Examples
    --------
    >>> query = (PlatialQuery(graph)
    ...     .for_agent("walker_001")
    ...     .with_familiarity(min_value=0.5)
    ...     .with_positive_affect()
    ...     .valid_at(datetime.now()))
    >>> places = query.execute()
    """
    
    graph: PlatialGraph
    agent_id: AgentId | None = None
    min_familiarity: float | None = None
    max_familiarity: float | None = None
    min_affect_valence: float | None = None
    max_affect_valence: float | None = None
    at_time: datetime | None = None
    extent_ids: set[str] | None = None
    filters: list[Callable[[PlatialNode], bool]] = field(default_factory=list)
    
    def for_agent(self, agent_id: str | AgentId) -> PlatialQuery:
        """Filter to a specific agent."""
        self.agent_id = AgentId(str(agent_id))
        return self
    
    def with_familiarity(self, min_value: float | None = None,
                         max_value: float | None = None) -> PlatialQuery:
        """Filter by familiarity range."""
        self.min_familiarity = min_value
        self.max_familiarity = max_value
        return self
    
    def with_positive_affect(self) -> PlatialQuery:
        """Filter to positive affect."""
        self.min_affect_valence = 0.0
        return self
    
    def with_negative_affect(self) -> PlatialQuery:
        """Filter to negative affect."""
        self.max_affect_valence = 0.0
        return self
    
    def valid_at(self, timestamp: datetime) -> PlatialQuery:
        """Filter to nodes valid at timestamp."""
        self.at_time = timestamp
        return self
    
    def at_extents(self, extent_ids: list[str]) -> PlatialQuery:
        """Filter to specific extents."""
        self.extent_ids = set(extent_ids)
        return self
    
    def add_filter(self, predicate: Callable[[PlatialNode], bool]) -> PlatialQuery:
        """Add custom filter."""
        self.filters.append(predicate)
        return self
    
    def execute(self) -> list[EmergentPlace]:
        """Execute query and return matching places."""
        places = []
        
        for node in self.graph.nodes(NodeType.SPATIAL_EXTENT):
            if self.extent_ids and str(node.id) not in self.extent_ids:
                continue
            
            place = extract_place(
                self.graph,
                ExtentId(str(node.id)),
                self.agent_id
            )
            
            # Apply filters
            if self.min_familiarity is not None:
                if place.familiarity_score < self.min_familiarity:
                    continue
            
            if self.max_familiarity is not None:
                if place.familiarity_score > self.max_familiarity:
                    continue
            
            if self.min_affect_valence is not None:
                if place.affect_valence_mean < self.min_affect_valence:
                    continue
            
            if self.max_affect_valence is not None:
                if place.affect_valence_mean > self.max_affect_valence:
                    continue
            
            places.append(place)
        
        return places


def find_familiar_places(
    graph: PlatialGraph,
    agent_id: AgentId,
    min_familiarity: float = 0.5
) -> list[EmergentPlace]:
    """Find places where agent has high familiarity."""
    return (PlatialQuery(graph)
            .for_agent(agent_id)
            .with_familiarity(min_value=min_familiarity)
            .execute())


def find_positive_places(
    graph: PlatialGraph,
    agent_id: AgentId
) -> list[EmergentPlace]:
    """Find places with positive affect for agent."""
    return (PlatialQuery(graph)
            .for_agent(agent_id)
            .with_positive_affect()
            .execute())


def find_routine_places(
    graph: PlatialGraph,
    agent_id: AgentId,
    min_encounters: int = 5
) -> list[EmergentPlace]:
    """Find places that are part of routines."""
    places = (PlatialQuery(graph)
              .for_agent(agent_id)
              .execute())
    return [p for p in places if p.encounter_count >= min_encounters]


def query_encounters(
    graph: PlatialGraph,
    agent_id: AgentId | None = None,
    extent_id: ExtentId | None = None,
    start_time: datetime | None = None,
    end_time: datetime | None = None
) -> Iterator[Encounter]:
    """Query encounters with filters."""
    for node in graph.nodes(NodeType.ENCOUNTER):
        if not isinstance(node, Encounter):
            continue
        
        if agent_id and node.agent_id != agent_id:
            continue
        
        if extent_id and node.extent_id != extent_id:
            continue
        
        if start_time and node.start_time < start_time:
            continue
        
        if end_time and node.end_time and node.end_time > end_time:
            continue
        
        yield node
