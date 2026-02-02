"""
Unit tests for derivation operators in chora.derive.
"""
import pytest
from datetime import datetime, timedelta
from chora.core import PlatialEdge, EdgeType, Familiarity, ExtentId
from chora.derive import (
    update_familiarity, 
    decay_all_familiarities,
    extract_place
)

def test_update_familiarity_growth(basic_graph, agent_alice, park_extent, encounter_factory):
    """Test familiarity grows with encounters."""
    # Add initial nodes
    basic_graph.add_node(agent_alice)
    basic_graph.add_node(park_extent)
    
    # Create encounter
    enc = encounter_factory()
    basic_graph.add_node(enc)
    
    # Must link encounter to agent/extent for update_familiarity to work?
    # Actually update_familiarity(graph, encounter) usually reads from the encounter object
    # provided the encounter has agent_id and extent_id set.
    
    # Link in graph anyway (good practice)
    basic_graph.add_edge(PlatialEdge.participates_in(agent_alice.id, enc.id))
    basic_graph.add_edge(PlatialEdge.occurs_at(enc.id, park_extent.id))
    
    # 1. First update - creates familiarity
    fam1 = update_familiarity(basic_graph, enc)
    assert isinstance(fam1, Familiarity)
    assert fam1.value > 0.0
    val1 = fam1.value
    
    # 2. Second update - reinforces familiarity
    enc2 = encounter_factory(start_time=datetime.now() + timedelta(days=1))
    basic_graph.add_node(enc2) # Add to graph
    basic_graph.add_edge(PlatialEdge.participates_in(agent_alice.id, enc2.id))
    basic_graph.add_edge(PlatialEdge.occurs_at(enc2.id, park_extent.id))
    
    fam2 = update_familiarity(basic_graph, enc2)
    assert fam2.value > val1
    
    # Check that the familiarity node exists in the graph
    assert basic_graph.has_node(fam2.id)

def test_extract_place_metadata(basic_graph, agent_alice, park_extent, encounter_factory):
    """Test place extraction returns correct metadata."""
    basic_graph.add_node(agent_alice)
    basic_graph.add_node(park_extent)
    
    # Add minimal encounter to establish relation
    # Start 2 hours ago so it finished 1 hour ago
    start_time = datetime.now() - timedelta(hours=2)
    enc = encounter_factory(start_time=start_time)
    basic_graph.add_node(enc)
    basic_graph.add_edge(PlatialEdge.participates_in(agent_alice.id, enc.id))
    basic_graph.add_edge(PlatialEdge.occurs_at(enc.id, park_extent.id))
    
    update_familiarity(basic_graph, enc)
    
    place = extract_place(basic_graph, park_extent.id, agent_alice.id)
    
    assert place.extent.id == park_extent.id
    assert place.extent.id == park_extent.id
    # place.agent is not stored, only extent and stats
    assert place.encounter_count == 1
    assert place.familiarity_score > 0
    assert place.character is not None
