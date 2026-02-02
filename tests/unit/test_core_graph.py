import pytest
from chora.core import (
    PlatialGraph, PlatialEdge, EdgeType
)
from chora.core.exceptions import (
    NodeNotFoundError, DuplicateNodeError
)

def test_add_node(basic_graph, agent_alice):
    """Test adding a node to the graph."""
    node_id = basic_graph.add_node(agent_alice)
    assert node_id == agent_alice.id
    assert basic_graph.has_node(agent_alice.id)
    assert basic_graph.node_count == 1

def test_add_duplicate_node(basic_graph, agent_alice):
    """Test that adding a duplicate node raises error."""
    basic_graph.add_node(agent_alice)
    with pytest.raises(DuplicateNodeError):
        basic_graph.add_node(agent_alice)

def test_add_edge(basic_graph, agent_alice, park_extent, encounter_factory):
    """Test adding an edge between nodes."""
    encounter = encounter_factory()
    
    # Must add nodes first
    basic_graph.add_node(agent_alice)
    basic_graph.add_node(encounter)
    
    edge = PlatialEdge.participates_in(agent_alice.id, encounter.id)
    edge_id = basic_graph.add_edge(edge)
    
    assert basic_graph.has_edge(edge_id)
    assert basic_graph.edge_count == 1
    
    # Verify connectivity
    outgoing = list(basic_graph.outgoing_edges(agent_alice.id))
    assert any(e.id == edge_id for e in outgoing)

def test_add_edge_missing_node(basic_graph, agent_alice, encounter_factory):
    """Test adding edge with missing nodes raises error."""
    encounter = encounter_factory()
    basic_graph.add_node(agent_alice)
    # encounter NOT added
    
    edge = PlatialEdge.participates_in(agent_alice.id, encounter.id)
    
    with pytest.raises(NodeNotFoundError):
        basic_graph.add_edge(edge)
