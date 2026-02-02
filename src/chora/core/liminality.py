"""
Liminality Domain Object

Liminality represents conditional, transitional quality at spatial
or experiential boundaries — the in-between character of thresholds.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Sequence

from chora.core.types import NodeType, LiminalityType, ExtentId
from chora.core.node import PlatialNode
from chora.core.uncertainty import UncertaintyValue, FuzzyMembership, TriangularFuzzy


@dataclass
class Liminality(PlatialNode):
    """
    Conditional, transitional quality at boundaries.
    
    Liminality captures the in-between, threshold character of certain
    places or experiences. A liminal space is neither fully one thing
    nor another — it marks a transition.
    
    Parameters
    ----------
    liminality_type : LiminalityType
        Type of liminality (spatial, temporal, social, etc.).
    extent_ids : tuple[ExtentId, ...]
        Spatial extents involved in this liminal zone.
    intensity : float
        Strength of liminal character [0, 1].
    transitional_from : str
        What the transition is from.
    transitional_to : str
        What the transition is to.
    
    Examples
    --------
    >>> # Spatial threshold at park entrance
    >>> entrance = Liminality(
    ...     liminality_type=LiminalityType.SPATIAL,
    ...     extent_ids=(ExtentId("park_entrance"),),
    ...     intensity=0.9,
    ...     transitional_from="street",
    ...     transitional_to="park"
    ... )
    >>> entrance.is_threshold
    True
    """
    
    liminality_type: LiminalityType = LiminalityType.SPATIAL
    extent_ids: tuple[str, ...] = field(default_factory=tuple)
    intensity: float = 0.5
    transitional_from: str = ""
    transitional_to: str = ""
    boundary_fuzziness: FuzzyMembership | None = None
    description: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)
    
    node_type: NodeType = field(default=NodeType.LIMINALITY, init=False)
    
    def __post_init__(self) -> None:
        if not 0.0 <= self.intensity <= 1.0:
            raise ValueError("intensity must be in [0, 1]")
    
    def __repr__(self) -> str:
        return (f"Liminality(type={self.liminality_type}, "
                f"from={self.transitional_from!r}, to={self.transitional_to!r})")
    
    @property
    def is_spatial(self) -> bool:
        return self.liminality_type == LiminalityType.SPATIAL
    
    @property
    def is_temporal(self) -> bool:
        return self.liminality_type == LiminalityType.TEMPORAL
    
    @property
    def is_threshold(self) -> bool:
        """Check if this represents a strong threshold."""
        return self.intensity >= 0.7
    
    @property
    def is_weak(self) -> bool:
        """Check if this is a weak liminal zone."""
        return self.intensity < 0.3
    
    @property
    def transition_description(self) -> str:
        """Get human-readable transition description."""
        if self.transitional_from and self.transitional_to:
            return f"{self.transitional_from} → {self.transitional_to}"
        return self.description
    
    def membership_at(self, position: float) -> float:
        """
        Get liminal membership at a position in the transition.
        
        Parameters
        ----------
        position : float
            Position in [0, 1] where 0 = fully 'from', 1 = fully 'to'.
        
        Returns
        -------
        float
            Liminal membership degree.
        """
        if self.boundary_fuzziness is not None:
            return self.boundary_fuzziness.membership(position)
        # Default triangular with peak at 0.5 (middle of transition)
        default_fuzzy = TriangularFuzzy(left=0.0, peak=0.5, right=1.0)
        return default_fuzzy.membership(position) * self.intensity
    
    @classmethod
    def spatial_boundary(cls, from_space: str, to_space: str,
                         extent_ids: Sequence[str] | None = None,
                         intensity: float = 0.8) -> Liminality:
        """Create a spatial boundary liminality."""
        return cls(
            liminality_type=LiminalityType.SPATIAL,
            extent_ids=tuple(extent_ids or []),
            intensity=intensity,
            transitional_from=from_space,
            transitional_to=to_space
        )
    
    @classmethod
    def temporal_transition(cls, from_time: str, to_time: str,
                            intensity: float = 0.7) -> Liminality:
        """Create a temporal transition liminality (e.g., dawn, dusk)."""
        return cls(
            liminality_type=LiminalityType.TEMPORAL,
            intensity=intensity,
            transitional_from=from_time,
            transitional_to=to_time
        )
    
    @classmethod
    def functional_edge(cls, from_function: str, to_function: str,
                        extent_ids: Sequence[str] | None = None) -> Liminality:
        """Create functional zone edge."""
        return cls(
            liminality_type=LiminalityType.FUNCTIONAL,
            extent_ids=tuple(extent_ids or []),
            transitional_from=from_function,
            transitional_to=to_function
        )
