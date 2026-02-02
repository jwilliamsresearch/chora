"""
Unit tests for Adapters.
"""
import pytest
from unittest.mock import MagicMock, patch
from chora.core import PlatialNode, Agent, PlatialGraph, PlatialEdge
from chora.adapters import InMemoryAdapter

# -----------------------------------------------------------------------------
# In-Memory Adapter Tests
# -----------------------------------------------------------------------------

def test_in_memory_adapter_crud(agent_alice):
    """Test basic CRUD in memory adapter."""
    adapter = InMemoryAdapter()
    adapter.connect()
    
    # Add node
    adapter.add_node(agent_alice)
    fetched = adapter.get_node(agent_alice.id)
    assert fetched.id == agent_alice.id
    
    # Connectivity check
    assert adapter.is_connected
    
    adapter.disconnect()
    assert not adapter.is_connected

def test_in_memory_save_load(basic_graph, agent_alice, park_extent, encounter_factory):
    """Test saving and loading a full graph."""
    # Populate graph
    basic_graph.add_node(agent_alice)
    basic_graph.add_node(park_extent)
    enc = encounter_factory()
    basic_graph.add_node(enc)
    basic_graph.add_edge(PlatialEdge.participates_in(agent_alice.id, enc.id))
    
    adapter = InMemoryAdapter()
    adapter.connect()
    
    # Save
    adapter.save_graph(basic_graph)
    
    # Load (into new graph)
    loaded_graph = adapter.load_graph("Test Graph")
    
    assert loaded_graph.node_count == 3
    assert loaded_graph.edge_count == 1
    assert loaded_graph.has_node(agent_alice.id)


# -----------------------------------------------------------------------------
# Neo4j Adapter Tests (Mocked)
# -----------------------------------------------------------------------------

import sys
from unittest.mock import MagicMock, patch

def test_neo4j_missing_dependency():
    """Test that AdapterError is raised if neo4j is missing."""
    # Ensure neo4j is NOT in sys.modules
    with patch.dict(sys.modules, {'neo4j': None}):
        # Force reload or just rely on the class checking imports at runtime
        # Our class checks 'from neo4j import ...' inside __init__
        # But since we already imported Neo4jAdapter at top level? 
        # Actually Neo4jAdapter does the check in __init__.
        
        # We need to ensure the import FAILS inside __init__
        # 'import neo4j' will fail if sys.modules['neo4j'] is None
        
        # However, we need to import the class first.
        from chora.adapters.neo4j import Neo4jAdapter
        
        with pytest.raises(Exception, match="neo4j package not installed"):
             Neo4jAdapter("bolt://localhost")

def test_neo4j_save_graph():
    """Test save_graph calls driver correctly (with mocked neo4j)."""
    # Mock the neo4j module
    mock_neo4j = MagicMock()
    mock_driver = MagicMock()
    mock_session = MagicMock()
    mock_driver.session.return_value.__enter__.return_value = mock_session
    mock_neo4j.GraphDatabase.driver.return_value = mock_driver
    
    with patch.dict(sys.modules, {'neo4j': mock_neo4j}):
        # Now we can instantiate without error
        from chora.adapters.neo4j import Neo4jAdapter
        adapter = Neo4jAdapter("bolt://localhost")
        adapter.connect() # uses the mocked driver
        
        # Create a small graph
        g = PlatialGraph("Mock Graph")
        a = Agent.individual("Mock Agent")
        g.add_node(a)
        
        adapter.save_graph(g)
        
        # Verify session executed write
        assert mock_session.execute_write.called
