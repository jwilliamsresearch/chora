"""
Tests for query module: PlatialQuery, traversal, similarity.
"""
import pytest
from datetime import datetime, timedelta

from chora.core import PlatialGraph, Agent, SpatialExtent, Encounter, PlatialEdge
from chora.core.types import NodeType
from chora.query.queries import PlatialQuery, find_familiar_places
from chora.query.traversal import traverse_from, find_path
from chora.query.similarity import place_similarity


# =============================================================================
# PlatialQuery Tests
# =============================================================================

class TestPlatialQuery:
    """Tests for fluent query builder."""
    
    def test_query_creation(self, basic_graph):
        """Test query builder creation."""
        query = PlatialQuery(basic_graph)
        assert query.graph == basic_graph
    
    def test_for_agent(self, basic_graph, agent_alice):
        """Test filtering by agent."""
        basic_graph.add_node(agent_alice)
        query = PlatialQuery(basic_graph).for_agent(agent_alice.id)
        assert query.agent_id == agent_alice.id
    
    def test_with_familiarity_min(self, basic_graph):
        """Test setting minimum familiarity."""
        query = PlatialQuery(basic_graph).with_familiarity(min_value=0.5)
        assert query.min_familiarity == 0.5
    
    def test_with_familiarity_range(self, basic_graph):
        """Test setting familiarity range."""
        query = PlatialQuery(basic_graph).with_familiarity(min_value=0.3, max_value=0.7)
        assert query.min_familiarity == 0.3
        assert query.max_familiarity == 0.7
    
    def test_with_positive_affect(self, basic_graph):
        """Test filtering for positive affect."""
        query = PlatialQuery(basic_graph).with_positive_affect()
        assert query.min_affect_valence == 0.0
    
    def test_with_negative_affect(self, basic_graph):
        """Test filtering for negative affect."""
        query = PlatialQuery(basic_graph).with_negative_affect()
        assert query.max_affect_valence == 0.0
    
    def test_valid_at_timestamp(self, basic_graph):
        """Test filtering by timestamp."""
        ts = datetime(2025, 6, 1)
        query = PlatialQuery(basic_graph).valid_at(ts)
        assert query.at_time == ts
    
    def test_at_extents_filter(self, basic_graph):
        """Test filtering by extent IDs."""
        query = PlatialQuery(basic_graph).at_extents(["ext_1", "ext_2"])
        assert "ext_1" in query.extent_ids
        assert "ext_2" in query.extent_ids
    
    def test_custom_filter(self, basic_graph):
        """Test adding custom predicate filter."""
        query = PlatialQuery(basic_graph).add_filter(lambda n: True)
        assert len(query.filters) == 1
    
    def test_fluent_chaining(self, basic_graph, agent_alice):
        """Test method chaining returns self."""
        basic_graph.add_node(agent_alice)
        
        query = (PlatialQuery(basic_graph)
                 .for_agent(agent_alice.id)
                 .with_familiarity(min_value=0.1)
                 .with_positive_affect())
        
        assert isinstance(query, PlatialQuery)


# =============================================================================
# Traversal Tests
# =============================================================================

class TestTraversal:
    """Tests for graph traversal."""
    
    def test_traverse_from_yields_nodes(self, basic_graph, agent_alice, park_extent, encounter_factory):
        """Test traverse_from yields nodes with depths."""
        basic_graph.add_node(agent_alice)
        basic_graph.add_node(park_extent)
        enc = encounter_factory()
        basic_graph.add_node(enc)
        basic_graph.add_edge(PlatialEdge.participates_in(agent_alice.id, enc.id))
        
        results = list(traverse_from(basic_graph, agent_alice.id))
        
        # Should yield tuples of (node, depth)
        assert len(results) >= 1
        # First result is start node at depth 0
        node, depth = results[0]
        assert depth == 0
    
    def test_find_path_same_node(self, basic_graph, agent_alice):
        """Test path to self is single node."""
        basic_graph.add_node(agent_alice)
        path = find_path(basic_graph, agent_alice.id, agent_alice.id)
        assert path == [agent_alice.id]
    
    def test_find_path_connected(self, basic_graph, agent_alice, park_extent, encounter_factory):
        """Test path finding between connected nodes."""
        basic_graph.add_node(agent_alice)
        basic_graph.add_node(park_extent)
        enc = encounter_factory()
        basic_graph.add_node(enc)
        basic_graph.add_edge(PlatialEdge.participates_in(agent_alice.id, enc.id))
        basic_graph.add_edge(PlatialEdge.occurs_at(enc.id, park_extent.id))
        
        path = find_path(basic_graph, agent_alice.id, park_extent.id)
        
        # Path should exist through the encounter
        assert path is not None
        assert len(path) == 3  # alice -> encounter -> park
    
    def test_find_path_disconnected(self, basic_graph, agent_alice, park_extent):
        """Test path returns None for disconnected nodes."""
        basic_graph.add_node(agent_alice)
        basic_graph.add_node(park_extent)
        
        path = find_path(basic_graph, agent_alice.id, park_extent.id)
        assert path is None


# =============================================================================
# Similarity Tests  
# =============================================================================

class TestSimilarity:
    """Tests for place similarity measures."""
    
    def test_place_similarity_import(self):
        """Test place_similarity function exists."""
        from chora.query.similarity import place_similarity
        assert callable(place_similarity)
