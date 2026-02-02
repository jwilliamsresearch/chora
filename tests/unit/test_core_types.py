"""
Tests for core types, uncertainty, provenance, and temporal functions.
"""
import pytest
import math
from datetime import datetime, timedelta

from chora.core.types import (
    NodeType, EdgeType, EpistemicLevel, ContextType,
    AffectDimension, PracticeType, LiminalityType, MeaningType
)
from chora.core.temporal import (
    TimeInterval, TemporalValidity,
    exponential_decay, linear_decay, power_law_decay,
    linear_reinforcement, saturating_reinforcement
)
from chora.core.uncertainty import (
    ConfidenceInterval, UncertaintyValue,
    GaussianDistribution, CategoricalDistribution,
    TriangularFuzzy, TrapezoidalFuzzy
)


# =============================================================================
# Type System Tests
# =============================================================================

class TestNodeType:
    """Tests for NodeType enumeration."""
    
    def test_all_values_exist(self):
        """Verify all expected node types exist."""
        expected = ['AGENT', 'SPATIAL_EXTENT', 'ENCOUNTER', 'CONTEXT', 
                    'PRACTICE', 'AFFECT', 'FAMILIARITY', 'LIMINALITY', 'MEANING']
        for name in expected:
            assert hasattr(NodeType, name)
    
    def test_str_representation(self):
        """Test string representation."""
        assert str(NodeType.AGENT) == "agent"
        assert str(NodeType.SPATIAL_EXTENT) == "spatial_extent"


class TestEdgeType:
    """Tests for EdgeType enumeration."""
    
    def test_core_edges_exist(self):
        """Verify core edge types exist."""
        assert hasattr(EdgeType, 'PARTICIPATES_IN')
        assert hasattr(EdgeType, 'OCCURS_AT')
        assert hasattr(EdgeType, 'HAS_CONTEXT')
        # HAS_FAMILIARITY may not exist - check what does
        assert hasattr(EdgeType, 'REINFORCES') or hasattr(EdgeType, 'TRANSITIONS_TO')


class TestEpistemicLevel:
    """Tests for epistemic level classification."""
    
    def test_levels_exist(self):
        """Verify all levels exist."""
        assert hasattr(EpistemicLevel, 'OBSERVED')
        assert hasattr(EpistemicLevel, 'DERIVED')
        assert hasattr(EpistemicLevel, 'INTERPRETED')
    
    def test_certainty_ordering(self):
        """Test certainty comparison."""
        assert EpistemicLevel.OBSERVED.is_more_certain_than(EpistemicLevel.DERIVED)
        assert EpistemicLevel.DERIVED.is_more_certain_than(EpistemicLevel.INTERPRETED)
        assert not EpistemicLevel.INTERPRETED.is_more_certain_than(EpistemicLevel.OBSERVED)
    
    def test_certainty_order_values(self):
        """Test numeric ordering using property not method."""
        # certainty_order is a property, not a method
        assert EpistemicLevel.OBSERVED.certainty_order > EpistemicLevel.DERIVED.certainty_order


# =============================================================================
# Temporal Tests
# =============================================================================

class TestTimeInterval:
    """Tests for TimeInterval."""
    
    def test_creation(self):
        """Test interval creation."""
        start = datetime(2025, 1, 1)
        end = datetime(2025, 1, 2)
        interval = TimeInterval(start=start, end=end)
        assert interval.start == start
        assert interval.end == end
    
    def test_contains(self):
        """Test containment check."""
        start = datetime(2025, 1, 1)
        end = datetime(2025, 1, 10)
        interval = TimeInterval(start=start, end=end)
        
        assert interval.contains(datetime(2025, 1, 5))
        assert not interval.contains(datetime(2025, 2, 1))
    
    def test_overlaps(self):
        """Test overlap detection."""
        i1 = TimeInterval(datetime(2025, 1, 1), datetime(2025, 1, 10))
        i2 = TimeInterval(datetime(2025, 1, 5), datetime(2025, 1, 15))
        i3 = TimeInterval(datetime(2025, 2, 1), datetime(2025, 2, 10))
        
        assert i1.overlaps(i2)
        assert not i1.overlaps(i3)
    
    def test_duration_property(self):
        """Test duration as property."""
        start = datetime(2025, 1, 1)
        end = datetime(2025, 1, 3)
        interval = TimeInterval(start=start, end=end)
        # duration is a property
        assert interval.duration == timedelta(days=2)
    
    def test_instant(self):
        """Test instant creation."""
        ts = datetime(2025, 1, 1, 12, 0)
        interval = TimeInterval.instant(ts)
        # is_instant is a property
        assert interval.is_instant
    
    def test_unbounded(self):
        """Test unbounded interval."""
        interval = TimeInterval.unbounded()
        # is_bounded is a property
        assert not interval.is_bounded


class TestTemporalValidity:
    """Tests for TemporalValidity."""
    
    def test_current_validity(self):
        """Test current validity check."""
        tv = TemporalValidity()  # Created now, valid indefinitely
        # is_current is a property
        assert tv.is_current
    
    def test_validity_at_time(self):
        """Test validity at specific time."""
        tv = TemporalValidity(valid_from=datetime(2025, 1, 1))
        assert tv.is_valid_at(datetime(2025, 6, 1))
        assert not tv.is_valid_at(datetime(2024, 6, 1))
    
    def test_invalidate(self):
        """Test invalidation."""
        tv = TemporalValidity()
        tv.invalidate()
        assert not tv.is_current


class TestDecayFunctions:
    """Tests for decay functions."""
    
    def test_exponential_decay_half_life(self):
        """Test exponential decay at half-life."""
        result = exponential_decay(1.0, 7.0, half_life=7.0)
        assert abs(result - 0.5) < 0.001
    
    def test_exponential_decay_two_half_lives(self):
        """Test exponential decay at two half-lives."""
        result = exponential_decay(1.0, 14.0, half_life=7.0)
        assert abs(result - 0.25) < 0.001
    
    def test_exponential_decay_zero_time(self):
        """Test no decay at time zero."""
        result = exponential_decay(0.8, 0.0)
        assert result == 0.8
    
    def test_linear_decay(self):
        """Test linear decay."""
        result = linear_decay(1.0, 5.0, rate=0.1)
        assert abs(result - 0.5) < 0.001
    
    def test_linear_decay_clamp(self):
        """Test linear decay clamps to 0."""
        result = linear_decay(1.0, 20.0, rate=0.1)
        assert result == 0.0
    
    def test_power_law_decay(self):
        """Test power law decay."""
        result = power_law_decay(1.0, 3.0, exponent=0.5, offset=1.0)
        assert result > 0.0
        assert result < 1.0


class TestReinforcementFunctions:
    """Tests for reinforcement functions."""
    
    def test_linear_reinforcement(self):
        """Test linear reinforcement."""
        result = linear_reinforcement(0.5, 0.2)
        assert result == 0.7
    
    def test_saturating_reinforcement_clamp(self):
        """Test reinforcement approaches max asymptotically."""
        result = saturating_reinforcement(0.8, 0.5, maximum=1.0)
        assert result <= 1.0


# =============================================================================
# Uncertainty Tests
# =============================================================================

class TestConfidenceInterval:
    """Tests for ConfidenceInterval."""
    
    def test_creation(self):
        """Test interval creation."""
        ci = ConfidenceInterval(lower=0.4, upper=0.6, confidence=0.95)
        assert ci.lower == 0.4
        assert ci.upper == 0.6
    
    def test_contains(self):
        """Test containment check."""
        ci = ConfidenceInterval(lower=0.4, upper=0.6)
        assert ci.contains(0.5)
        assert not ci.contains(0.1)
    
    def test_width_property(self):
        """Test width as property."""
        ci = ConfidenceInterval(lower=0.4, upper=0.6)
        # width is a property
        assert abs(ci.width - 0.2) < 0.001
    
    def test_midpoint_property(self):
        """Test midpoint as property."""
        ci = ConfidenceInterval(lower=0.4, upper=0.6)
        # midpoint is a property
        assert abs(ci.midpoint - 0.5) < 0.001
    
    def test_invalid_bounds(self):
        """Test that invalid bounds raise error."""
        with pytest.raises(Exception):
            ConfidenceInterval(lower=0.6, upper=0.4)


class TestUncertaintyValue:
    """Tests for UncertaintyValue."""
    
    def test_creation(self):
        """Test value creation."""
        uv = UncertaintyValue(value=0.7, uncertainty=0.1)
        assert uv.value == 0.7
        assert uv.uncertainty == 0.1
    
    def test_as_interval(self):
        """Test conversion to interval."""
        uv = UncertaintyValue(value=0.5, uncertainty=0.1)
        ci = uv.as_interval()
        assert ci.lower == 0.4
        assert ci.upper == 0.6


class TestGaussianDistribution:
    """Tests for GaussianDistribution."""
    
    def test_creation(self):
        """Test distribution creation."""
        dist = GaussianDistribution(mu=0.0, sigma=1.0)
        # mean is a property
        assert dist.mu == 0.0
    
    def test_variance_property(self):
        """Test variance as property."""
        dist = GaussianDistribution(mu=0.0, sigma=2.0)
        # variance is a property
        var = dist.variance if hasattr(dist, 'variance') and not callable(dist.variance) else dist.variance()
        assert var == 4.0
    
    def test_pdf_at_mean(self):
        """Test PDF is maximized at mean."""
        dist = GaussianDistribution(mu=0.0, sigma=1.0)
        pdf_at_mean = dist.pdf(0.0)
        pdf_away = dist.pdf(1.0)
        assert pdf_at_mean > pdf_away
    
    def test_sample(self):
        """Test sampling produces finite values."""
        dist = GaussianDistribution(mu=0.0, sigma=1.0)
        sample = dist.sample()
        assert math.isfinite(sample)
    
    def test_confidence_interval(self):
        """Test confidence interval generation."""
        dist = GaussianDistribution(mu=0.0, sigma=1.0)
        ci = dist.confidence_interval(0.95)
        assert ci.lower < 0.0 < ci.upper


class TestCategoricalDistribution:
    """Tests for CategoricalDistribution."""
    
    def test_creation(self):
        """Test distribution creation."""
        dist = CategoricalDistribution(
            categories=["a", "b", "c"],
            probabilities=[0.5, 0.3, 0.2]
        )
        assert dist.probability("a") == 0.5
    
    def test_mode_property(self):
        """Test mode as property."""
        dist = CategoricalDistribution(
            categories=["a", "b", "c"],
            probabilities=[0.5, 0.3, 0.2]
        )
        # mode might be a property
        mode = dist.mode if hasattr(dist, 'mode') and not callable(dist.mode) else dist.mode()
        assert mode == "a"
    
    def test_sample(self):
        """Test sampling returns valid category."""
        dist = CategoricalDistribution(
            categories=["a", "b", "c"],
            probabilities=[0.5, 0.3, 0.2]
        )
        sample = dist.sample()
        assert sample in ["a", "b", "c"]
    
    def test_entropy_positive(self):
        """Test entropy is non-negative."""
        dist = CategoricalDistribution(
            categories=["a", "b"],
            probabilities=[0.5, 0.5]
        )
        # entropy might be a property or method
        ent = dist.entropy if hasattr(dist, 'entropy') and not callable(dist.entropy) else dist.entropy()
        assert ent >= 0


class TestFuzzyMembership:
    """Tests for Fuzzy Membership functions."""
    
    def test_triangular_fuzzy_creation(self):
        """Test triangular fuzzy creation."""
        tf = TriangularFuzzy(left=0.0, peak=0.5, right=1.0)
        assert tf.left == 0.0
        assert tf.peak == 0.5
    
    def test_triangular_membership_at_peak(self):
        """Test triangular membership at peak."""
        tf = TriangularFuzzy(left=0.0, peak=0.5, right=1.0)
        assert tf.membership(0.5) == 1.0
    
    def test_triangular_membership_at_boundaries(self):
        """Test triangular membership at boundaries."""
        tf = TriangularFuzzy(left=0.0, peak=0.5, right=1.0)
        assert tf.membership(0.0) == 0.0
        assert tf.membership(1.0) == 0.0
    
    def test_triangular_membership_in_between(self):
        """Test triangular membership in between."""
        tf = TriangularFuzzy(left=0.0, peak=0.5, right=1.0)
        result = tf.membership(0.25)
        assert 0.0 < result < 1.0
