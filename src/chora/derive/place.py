"""
Place Emergence

Extract emergent place as a coherent subgraph from the platial graph.
Place is not a primitive — it emerges from patterns of encounters,
familiarity, affect, and meaning.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

from chora.core.types import NodeType, EdgeType, AgentId, ExtentId
from chora.core.graph import PlatialGraph
from chora.core.spatial_extent import SpatialExtent
from chora.core.familiarity import Familiarity


@dataclass
class EmergentPlace:
    """
    An emergent place as a coherent subgraph.
    
    Place is not stored as a node but computed as a view over
    the platial graph, centered on a spatial extent and including
    related encounters, affects, meanings, and familiarities.
    """
    
    extent_id: ExtentId
    extent: SpatialExtent | None
    subgraph: PlatialGraph
    familiarity_score: float
    meaning_count: int
    affect_valence_mean: float
    encounter_count: int
    
    @property
    def is_significant(self) -> bool:
        """Check if this is a significant place."""
        return (self.familiarity_score >= 0.5 or 
                self.meaning_count > 0 or
                self.encounter_count >= 5)
    
    @property
    def character(self) -> str:
        """Describe the character of this place."""
        if self.affect_valence_mean > 0.3:
            affect_char = "positive"
        elif self.affect_valence_mean < -0.3:
            affect_char = "negative"
        else:
            affect_char = "neutral"
        
        if self.familiarity_score > 0.7:
            fam_char = "very familiar"
        elif self.familiarity_score > 0.3:
            fam_char = "familiar"
        else:
            fam_char = "novel"
        
        return f"{affect_char}, {fam_char}"


def extract_place(
    graph: PlatialGraph,
    extent_id: ExtentId,
    agent_id: AgentId | None = None
) -> EmergentPlace:
    """
    Extract an emergent place centered on a spatial extent.
    
    Gathers all encounters, affects, meanings, and familiarities
    related to the specified extent, optionally filtered by agent.
    
    Parameters
    ----------
    graph : PlatialGraph
        The platial graph.
    extent_id : ExtentId
        ID of the central spatial extent.
    agent_id : AgentId | None
        Optional agent filter.
    
    Returns
    -------
    EmergentPlace
        The emergent place structure.
    """
    # Get the extent node
    from chora.core.types import NodeId
    extent = None
    try:
        node = graph.get_node(NodeId(str(extent_id)))
        if isinstance(node, SpatialExtent):
            extent = node
    except Exception:
        pass
    
    # Find related nodes
    subgraph = PlatialGraph(name=f"Place: {extent_id}")
    encounter_ids = []
    familiarities = []
    affect_values = []
    meaning_count = 0
    
    # Add extent to subgraph
    if extent:
        subgraph.add_node(extent)
    
    # Find encounters at this extent
    for edge in graph.edges(EdgeType.OCCURS_AT):
        if str(edge.target_id) == str(extent_id):
            encounter_id = edge.source_id
            try:
                encounter = graph.get_node(encounter_id)
                # Filter by agent if specified
                if agent_id is not None:
                    from chora.core.encounter import Encounter
                    if isinstance(encounter, Encounter):
                        if encounter.agent_id != agent_id:
                            continue
                
                subgraph.add_node(encounter)
                encounter_ids.append(encounter_id)
            except Exception:
                pass
    
    # Find familiarities
    for node in graph.nodes(NodeType.FAMILIARITY):
        if isinstance(node, Familiarity):
            if str(node.extent_id) == str(extent_id):
                if agent_id is None or node.agent_id == agent_id:
                    familiarities.append(node.current_value)
                    subgraph.add_node(node)
    
    # Find affects linked to encounters
    for edge in graph.edges(EdgeType.EXPRESSES):
        if edge.source_id in encounter_ids:
            try:
                affect = graph.get_node(edge.target_id)
                from chora.core.affect import Affect
                if isinstance(affect, Affect):
                    affect_values.append(affect.valence)
                    subgraph.add_node(affect)
            except Exception:
                pass
    
    # Find meanings
    for node in graph.nodes(NodeType.MEANING):
        from chora.core.meaning import Meaning
        if isinstance(node, Meaning):
            if str(node.extent_id) == str(extent_id):
                if agent_id is None or node.agent_id == agent_id or node.is_shared:
                    meaning_count += 1
                    subgraph.add_node(node)
    
    # Compute aggregates
    familiarity_score = sum(familiarities) / len(familiarities) if familiarities else 0.0
    affect_mean = sum(affect_values) / len(affect_values) if affect_values else 0.0
    
    return EmergentPlace(
        extent_id=extent_id,
        extent=extent,
        subgraph=subgraph,
        familiarity_score=familiarity_score,
        meaning_count=meaning_count,
        affect_valence_mean=affect_mean,
        encounter_count=len(encounter_ids)
    )


def find_emergent_places(
    graph: PlatialGraph,
    agent_id: AgentId | None = None,
    min_encounters: int = 3
) -> list[EmergentPlace]:
    """
    Find all emergent places in the graph.
    
    Returns places that have sufficient activity to be meaningful.
    """
    # Get all spatial extents
    extent_ids: set[str] = set()
    
    for node in graph.nodes(NodeType.SPATIAL_EXTENT):
        extent_ids.add(str(node.id))
    
    # Extract places
    places = []
    for extent_id in extent_ids:
        place = extract_place(graph, ExtentId(extent_id), agent_id)
        if place.encounter_count >= min_encounters:
            places.append(place)
    
    # Sort by significance
    places.sort(key=lambda p: (p.familiarity_score + p.encounter_count / 10), 
                reverse=True)
    
    return places
