"""
Tests for practice and routine detection.
"""
import pytest
from datetime import datetime, timedelta

from chora.core import PlatialGraph, Agent, SpatialExtent, Encounter, PlatialEdge
from chora.derive.practices import (
    detect_practices, detect_routines, find_sequence_patterns,
    PracticeDetectionConfig
)
from chora.core.types import PracticeType


# =============================================================================
# Practice Detection Tests
# =============================================================================

class TestPracticeDetection:
    """Tests for practice detection algorithms."""
    
    @pytest.fixture
    def routine_encounters(self):
        """Create encounters that form a routine pattern."""
        agent_id = "agent_test"
        extent_id = "park_test"
        
        encounters = []
        base_time = datetime(2025, 1, 1, 9, 0)  # 9am
        
        # Create routine: park visit at 9am for 10 days
        for i in range(10):
            enc = Encounter(
                agent_id=agent_id,
                extent_id=extent_id,
                start_time=base_time + timedelta(days=i),
                end_time=base_time + timedelta(days=i, hours=1),
                activity="morning walk"
            )
            encounters.append(enc)
        
        return encounters, agent_id
    
    @pytest.fixture
    def sequence_encounters(self):
        """Create encounters that form a sequential pattern (A → B)."""
        agent_id = "commuter_test"
        home_id = "home"
        office_id = "office"
        
        encounters = []
        base_time = datetime(2025, 1, 1, 8, 0)
        
        # Create sequence: home → office for 10 days
        for i in range(10):
            # Morning at home
            enc_home = Encounter(
                agent_id=agent_id,
                extent_id=home_id,
                start_time=base_time + timedelta(days=i),
                end_time=base_time + timedelta(days=i, hours=1)
            )
            # Arrive at office
            enc_office = Encounter(
                agent_id=agent_id,
                extent_id=office_id,
                start_time=base_time + timedelta(days=i, hours=2),
                end_time=base_time + timedelta(days=i, hours=10)
            )
            encounters.extend([enc_home, enc_office])
        
        return encounters, agent_id
    
    def test_detect_routines_from_regular_visits(self, routine_encounters):
        """Test routine detection from regular visits."""
        encounters, agent_id = routine_encounters
        
        config = PracticeDetectionConfig(
            min_occurrences=3,
            min_regularity=0.5
        )
        
        routines = detect_routines(encounters, config)
        
        assert len(routines) >= 1
        # First routine should be the morning park visit
        routine = routines[0]
        assert routine.practice_type == PracticeType.ROUTINE
        assert routine.regularity >= 0.5
    
    def test_detect_practices_for_agent(self, routine_encounters):
        """Test detect_practices for specific agent."""
        encounters, agent_id = routine_encounters
        
        practices = detect_practices(encounters, agent_id)
        
        assert len(practices) >= 1
    
    def test_detect_practices_insufficient_data(self):
        """Test that too few encounters returns no practices."""
        encounters = [
            Encounter(
                agent_id="test",
                extent_id="place",
                start_time=datetime.now()
            )
        ]
        
        practices = detect_practices(encounters, "test")
        assert len(practices) == 0
    
    def test_find_sequence_patterns(self, sequence_encounters):
        """Test sequential pattern detection."""
        encounters, agent_id = sequence_encounters
        
        config = PracticeDetectionConfig(min_occurrences=3)
        patterns = find_sequence_patterns(encounters, config)
        
        # Should find home → office pattern
        assert len(patterns) >= 1
        pattern_names = [p[0] for p in patterns]
        assert any("home" in name and "office" in name for name in pattern_names)
    
    def test_routine_regularity_calculation(self, routine_encounters):
        """Test that regularity is calculated correctly."""
        encounters, agent_id = routine_encounters
        
        routines = detect_routines(encounters)
        
        if routines:
            routine = routines[0]
            # All at same time should be high regularity
            assert routine.regularity >= 0.7
    
    def test_irregular_visits_low_regularity(self):
        """Test that irregular visits have low regularity."""
        agent_id = "random_walker"
        extent_id = "park"
        
        # Random times throughout the day
        encounters = []
        for i, hour in enumerate([9, 14, 22, 6, 18, 3, 15, 20]):
            enc = Encounter(
                agent_id=agent_id,
                extent_id=extent_id,
                start_time=datetime(2025, 1, i+1, hour, 0)
            )
            encounters.append(enc)
        
        config = PracticeDetectionConfig(min_regularity=0.8)
        routines = detect_routines(encounters, config)
        
        # Should not detect a routine due to low regularity
        assert len(routines) == 0


# =============================================================================
# Practice Detection Config Tests
# =============================================================================

class TestPracticeDetectionConfig:
    """Tests for configuration."""
    
    def test_default_config(self):
        """Test default configuration values."""
        config = PracticeDetectionConfig()
        
        assert config.min_occurrences == 3
        assert config.time_window_days == 30
        assert config.min_regularity == 0.5
    
    def test_custom_config(self):
        """Test custom configuration."""
        config = PracticeDetectionConfig(
            min_occurrences=5,
            min_regularity=0.8
        )
        
        assert config.min_occurrences == 5
        assert config.min_regularity == 0.8


# =============================================================================
# Practice Type Tests
# =============================================================================

class TestPracticeTypes:
    """Tests for practice type classification."""
    
    def test_routine_type(self):
        """Test routine practice type."""
        assert hasattr(PracticeType, 'ROUTINE')
    
    def test_ritual_type(self):
        """Test ritual practice type."""
        assert hasattr(PracticeType, 'RITUAL')
    
    def test_habit_type(self):
        """Test habit practice type."""
        assert hasattr(PracticeType, 'HABIT')


# =============================================================================
# Edge Cases
# =============================================================================

class TestEdgeCases:
    """Tests for edge cases in practice detection."""
    
    def test_empty_encounters(self):
        """Test with empty encounter list."""
        practices = detect_practices([], "agent")
        assert practices == []
    
    def test_single_encounter(self):
        """Test with single encounter."""
        enc = Encounter(
            agent_id="agent",
            extent_id="place",
            start_time=datetime.now()
        )
        
        practices = detect_practices([enc], "agent")
        assert len(practices) == 0
    
    def test_different_agent_filter(self):
        """Test that encounters are filtered by agent."""
        encounters = [
            Encounter(agent_id="alice", extent_id="park", start_time=datetime.now()),
            Encounter(agent_id="bob", extent_id="park", start_time=datetime.now()),
        ]
        
        practices = detect_practices(encounters, "alice")
        # Bob's encounter should be filtered out
        # Since only 1 encounter for alice, no practices
        assert len(practices) == 0
    
    def test_missing_extent_id(self):
        """Test encounters with missing extent_id."""
        encounters = [
            Encounter(
                agent_id="agent",
                extent_id=None,  # type: ignore
                start_time=datetime.now()
            )
            for _ in range(5)
        ]
        
        # Should handle gracefully
        routines = detect_routines(encounters)
        assert routines == []
