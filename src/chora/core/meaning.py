"""
Meaning Domain Object

Meaning represents structured symbolic interpretation attached to
places — the semantic and symbolic significance of place experience.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Sequence

from chora.core.types import NodeType, MeaningType, AgentId, ExtentId, EpistemicLevel
from chora.core.node import PlatialNode
from chora.core.uncertainty import UncertaintyValue


@dataclass
class Meaning(PlatialNode):
    """
    Structured symbolic interpretation attached to place.
    
    Meaning captures the semantic/symbolic significance that agents
    attach to places. Multiple, even conflicting, meanings can coexist
    for the same spatial extent.
    
    Parameters
    ----------
    meaning_type : MeaningType
        Classification of this meaning.
    agent_id : AgentId | None
        Who holds this meaning (None for shared meanings).
    extent_id : ExtentId | None
        Which spatial extent this meaning is attached to.
    content : str
        The meaning content (description).
    symbols : tuple[str, ...]
        Associated symbolic labels.
    strength : float
        How strongly held this meaning is [0, 1].
    
    Examples
    --------
    >>> # Personal biographical meaning
    >>> childhood_home = Meaning(
    ...     meaning_type=MeaningType.PERSONAL,
    ...     agent_id=AgentId("alice"),
    ...     extent_id=ExtentId("house_123"),
    ...     content="Where I grew up and learned to ride a bike",
    ...     symbols=("childhood", "home", "safety"),
    ...     strength=0.95
    ... )
    >>> 
    >>> # Cultural meaning (shared)
    >>> memorial = Meaning(
    ...     meaning_type=MeaningType.CULTURAL,
    ...     extent_id=ExtentId("war_memorial"),
    ...     content="Site of remembrance for fallen soldiers",
    ...     symbols=("remembrance", "sacrifice", "nation"),
    ...     strength=0.9
    ... )
    """
    
    meaning_type: MeaningType = MeaningType.PERSONAL
    agent_id: AgentId | None = None
    extent_id: ExtentId | None = None
    content: str = ""
    symbols: tuple[str, ...] = field(default_factory=tuple)
    strength: float = 1.0
    certainty: UncertaintyValue | None = None
    related_meanings: tuple[str, ...] = field(default_factory=tuple)
    conflicting_meanings: tuple[str, ...] = field(default_factory=tuple)
    metadata: dict[str, Any] = field(default_factory=dict)
    
    node_type: NodeType = field(default=NodeType.MEANING, init=False)
    # Meanings are always interpreted
    epistemic_level: EpistemicLevel = field(
        default=EpistemicLevel.INTERPRETED, init=False
    )
    
    def __post_init__(self) -> None:
        if not 0.0 <= self.strength <= 1.0:
            raise ValueError("strength must be in [0, 1]")
    
    def __repr__(self) -> str:
        return f"Meaning(type={self.meaning_type}, content={self.content[:30]!r}...)"
    
    @property
    def is_personal(self) -> bool:
        return self.meaning_type == MeaningType.PERSONAL
    
    @property
    def is_shared(self) -> bool:
        """Check if this is a shared (non-personal) meaning."""
        return self.agent_id is None
    
    @property
    def is_cultural(self) -> bool:
        return self.meaning_type == MeaningType.CULTURAL
    
    @property
    def has_conflicts(self) -> bool:
        """Check if there are conflicting meanings."""
        return len(self.conflicting_meanings) > 0
    
    def add_symbol(self, symbol: str) -> None:
        """Add a symbolic label."""
        if symbol not in self.symbols:
            self.symbols = (*self.symbols, symbol)
    
    def relates_to(self, meaning_id: str) -> None:
        """Mark a relationship to another meaning."""
        if meaning_id not in self.related_meanings:
            self.related_meanings = (*self.related_meanings, meaning_id)
    
    def conflicts_with(self, meaning_id: str) -> None:
        """Mark a conflict with another meaning."""
        if meaning_id not in self.conflicting_meanings:
            self.conflicting_meanings = (*self.conflicting_meanings, meaning_id)
    
    @classmethod
    def personal(cls, agent_id: AgentId, extent_id: ExtentId,
                 content: str, symbols: Sequence[str] | None = None,
                 **kwargs: Any) -> Meaning:
        """Create a personal biographical meaning."""
        return cls(
            meaning_type=MeaningType.PERSONAL,
            agent_id=agent_id,
            extent_id=extent_id,
            content=content,
            symbols=tuple(symbols or []),
            **kwargs
        )
    
    @classmethod
    def cultural(cls, extent_id: ExtentId, content: str,
                 symbols: Sequence[str] | None = None,
                 **kwargs: Any) -> Meaning:
        """Create a shared cultural meaning."""
        return cls(
            meaning_type=MeaningType.CULTURAL,
            agent_id=None,
            extent_id=extent_id,
            content=content,
            symbols=tuple(symbols or []),
            **kwargs
        )
    
    @classmethod
    def functional(cls, extent_id: ExtentId, function: str,
                   **kwargs: Any) -> Meaning:
        """Create a functional meaning from use."""
        return cls(
            meaning_type=MeaningType.FUNCTIONAL,
            extent_id=extent_id,
            content=function,
            **kwargs
        )
