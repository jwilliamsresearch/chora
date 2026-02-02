"""
Uncertainty Representation for Chora

This module provides probabilistic and fuzzy representation of uncertainty.
Vagueness is modelled, not suppressed. This is a core design principle.
"""

from __future__ import annotations

import math
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Sequence

from chora.core.exceptions import (
    DistributionError,
    InvalidProbabilityError,
    UncertaintyError,
)


def _validate_probability(value: float, name: str = "Probability") -> None:
    """Validate that a value is a valid probability in [0, 1]."""
    if not 0.0 <= value <= 1.0:
        raise InvalidProbabilityError(
            f"{name} must be in [0, 1]", value=value
        )


@dataclass(frozen=True, slots=True)
class ConfidenceInterval:
    """
    Represents a confidence interval.
    
    Parameters
    ----------
    lower : float
        Lower bound of the interval.
    upper : float
        Upper bound of the interval.
    confidence : float
        Confidence level (e.g., 0.95 for 95%).
    """
    
    lower: float
    upper: float
    confidence: float = 0.95
    
    def __post_init__(self) -> None:
        if self.lower > self.upper:
            raise UncertaintyError(
                "Lower bound exceeds upper bound",
                lower=self.lower, upper=self.upper
            )
        _validate_probability(self.confidence, "Confidence level")
    
    def contains(self, value: float) -> bool:
        """Check if a value falls within the interval."""
        return self.lower <= value <= self.upper
    
    @property
    def width(self) -> float:
        """Return the width of the interval."""
        return self.upper - self.lower
    
    @property
    def midpoint(self) -> float:
        """Return the midpoint of the interval."""
        return (self.lower + self.upper) / 2


@dataclass(frozen=True, slots=True)
class UncertaintyValue:
    """
    A value with associated uncertainty.
    
    Parameters
    ----------
    value : float
        Central/expected value.
    uncertainty : float
        Uncertainty measure (interpretation depends on context).
    confidence : float | None
        Optional confidence level.
    
    Examples
    --------
    >>> uv = UncertaintyValue(value=0.75, uncertainty=0.1)
    >>> uv.as_interval(confidence=0.95)
    ConfidenceInterval(lower=0.55, upper=0.95, confidence=0.95)
    """
    
    value: float
    uncertainty: float = 0.0
    confidence: float | None = None
    
    def __post_init__(self) -> None:
        if self.uncertainty < 0:
            raise UncertaintyError(
                "Uncertainty cannot be negative", uncertainty=self.uncertainty
            )
        if self.confidence is not None:
            _validate_probability(self.confidence, "Confidence")
    
    def as_interval(self, confidence: float = 0.95) -> ConfidenceInterval:
        """Convert to confidence interval (assuming ±uncertainty)."""
        return ConfidenceInterval(
            lower=self.value - self.uncertainty,
            upper=self.value + self.uncertainty,
            confidence=confidence
        )


# =============================================================================
# Probability Distributions
# =============================================================================

class ProbabilityDistribution(ABC):
    """Abstract base class for probability distributions."""
    
    @abstractmethod
    def pdf(self, x: float) -> float:
        """Probability density function."""
        ...
    
    @abstractmethod
    def sample(self) -> float:
        """Draw a random sample from the distribution."""
        ...
    
    @property
    @abstractmethod
    def mean(self) -> float:
        """Expected value."""
        ...
    
    @property
    @abstractmethod
    def variance(self) -> float:
        """Variance."""
        ...


@dataclass(frozen=True, slots=True)
class GaussianDistribution(ProbabilityDistribution):
    """
    Gaussian (normal) distribution.
    
    Parameters
    ----------
    mu : float
        Mean of the distribution.
    sigma : float
        Standard deviation (must be positive).
    """
    
    mu: float = 0.0
    sigma: float = 1.0
    
    def __post_init__(self) -> None:
        if self.sigma <= 0:
            raise DistributionError(
                "Standard deviation must be positive", sigma=self.sigma
            )
    
    def pdf(self, x: float) -> float:
        """Probability density at x."""
        coefficient = 1 / (self.sigma * math.sqrt(2 * math.pi))
        exponent = -0.5 * ((x - self.mu) / self.sigma) ** 2
        return coefficient * math.exp(exponent)
    
    def sample(self) -> float:
        """Draw a random sample using Box-Muller transform."""
        import random
        u1, u2 = random.random(), random.random()
        z = math.sqrt(-2 * math.log(u1)) * math.cos(2 * math.pi * u2)
        return self.mu + self.sigma * z
    
    @property
    def mean(self) -> float:
        return self.mu
    
    @property
    def variance(self) -> float:
        return self.sigma ** 2
    
    def confidence_interval(self, confidence: float = 0.95) -> ConfidenceInterval:
        """Return confidence interval for given level."""
        # Z-scores for common confidence levels
        z_scores = {0.90: 1.645, 0.95: 1.96, 0.99: 2.576}
        z = z_scores.get(confidence, 1.96)
        margin = z * self.sigma
        return ConfidenceInterval(
            lower=self.mu - margin,
            upper=self.mu + margin,
            confidence=confidence
        )


@dataclass(slots=True)
class CategoricalDistribution(ProbabilityDistribution):
    """
    Categorical distribution over discrete outcomes.
    
    Parameters
    ----------
    categories : Sequence[str]
        Category labels.
    probabilities : Sequence[float]
        Probability for each category (must sum to 1).
    """
    
    categories: Sequence[str]
    probabilities: Sequence[float]
    _prob_dict: dict[str, float] = field(init=False, repr=False)
    
    def __post_init__(self) -> None:
        if len(self.categories) != len(self.probabilities):
            raise DistributionError(
                "Categories and probabilities must have same length",
                n_categories=len(self.categories),
                n_probabilities=len(self.probabilities)
            )
        
        for p in self.probabilities:
            _validate_probability(p, "Category probability")
        
        total = sum(self.probabilities)
        if not math.isclose(total, 1.0, rel_tol=1e-6):
            raise DistributionError(
                "Probabilities must sum to 1", total=total
            )
        
        self._prob_dict = dict(zip(self.categories, self.probabilities))
    
    def probability(self, category: str) -> float:
        """Get probability of a specific category."""
        return self._prob_dict.get(category, 0.0)
    
    def pdf(self, x: float) -> float:
        """Not applicable for categorical; raises error."""
        raise NotImplementedError("Use probability() for categorical distributions")
    
    def sample(self) -> str:
        """Draw a random category."""
        import random
        return random.choices(
            list(self.categories),
            weights=list(self.probabilities)
        )[0]
    
    @property
    def mean(self) -> float:
        raise NotImplementedError("Mean not defined for categorical")
    
    @property
    def variance(self) -> float:
        raise NotImplementedError("Variance not defined for categorical")
    
    @property
    def mode(self) -> str:
        """Return the most likely category."""
        return max(self._prob_dict, key=lambda k: self._prob_dict[k])
    
    @property
    def entropy(self) -> float:
        """Shannon entropy of the distribution."""
        return -sum(
            p * math.log2(p) if p > 0 else 0
            for p in self.probabilities
        )


# =============================================================================
# Fuzzy Membership
# =============================================================================

class FuzzyMembership(ABC):
    """Abstract base class for fuzzy membership functions."""
    
    @abstractmethod
    def membership(self, x: float) -> float:
        """Return membership degree in [0, 1] for value x."""
        ...
    
    def __call__(self, x: float) -> float:
        return self.membership(x)


@dataclass(frozen=True, slots=True)
class TriangularFuzzy(FuzzyMembership):
    """
    Triangular fuzzy membership function.
    
    Parameters
    ----------
    left : float
        Left foot (membership = 0).
    peak : float
        Peak (membership = 1).
    right : float
        Right foot (membership = 0).
    """
    
    left: float
    peak: float
    right: float
    
    def __post_init__(self) -> None:
        if not self.left <= self.peak <= self.right:
            raise UncertaintyError(
                "Must have left <= peak <= right",
                left=self.left, peak=self.peak, right=self.right
            )
    
    def membership(self, x: float) -> float:
        if x <= self.left or x >= self.right:
            return 0.0
        if x == self.peak:
            return 1.0
        if x < self.peak:
            return (x - self.left) / (self.peak - self.left)
        return (self.right - x) / (self.right - self.peak)


@dataclass(frozen=True, slots=True)
class TrapezoidalFuzzy(FuzzyMembership):
    """
    Trapezoidal fuzzy membership function.
    
    Parameters
    ----------
    left_foot : float
        Left foot (membership = 0).
    left_shoulder : float
        Start of flat top (membership = 1).
    right_shoulder : float
        End of flat top (membership = 1).
    right_foot : float
        Right foot (membership = 0).
    """
    
    left_foot: float
    left_shoulder: float
    right_shoulder: float
    right_foot: float
    
    def __post_init__(self) -> None:
        if not (self.left_foot <= self.left_shoulder <= 
                self.right_shoulder <= self.right_foot):
            raise UncertaintyError(
                "Parameters must be in ascending order",
                left_foot=self.left_foot,
                left_shoulder=self.left_shoulder,
                right_shoulder=self.right_shoulder,
                right_foot=self.right_foot
            )
    
    def membership(self, x: float) -> float:
        if x <= self.left_foot or x >= self.right_foot:
            return 0.0
        if self.left_shoulder <= x <= self.right_shoulder:
            return 1.0
        if x < self.left_shoulder:
            return (x - self.left_foot) / (self.left_shoulder - self.left_foot)
        return (self.right_foot - x) / (self.right_foot - self.right_shoulder)
