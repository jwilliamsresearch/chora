"""
Context Domain Object

Context represents situational modifiers that affect the character
of an encounter — temporal, social, purposive, environmental, etc.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from chora.core.types import NodeType, ContextType
from chora.core.node import PlatialNode


@dataclass
class Context(PlatialNode):
    """
    Situational modifiers for encounters.
    
    Context affects the character and meaning of encounters without
    changing the spatial or temporal facts. Multiple contexts can
    apply to a single encounter.
    
    Parameters
    ----------
    context_type : ContextType
        Classification of this context.
    value : Any
        The context value (type depends on context_type).
    description : str
        Human-readable description.
    intensity : float
        How strongly this context applies [0, 1].
    
    Examples
    --------
    >>> # Temporal context
    >>> morning = Context(
    ...     context_type=ContextType.TEMPORAL,
    ...     value="morning",
    ...     description="Early morning walk"
    ... )
    >>> 
    >>> # Social context
    >>> with_family = Context(
    ...     context_type=ContextType.SOCIAL,
    ...     value={"companions": ["partner", "child"]},
    ...     description="Weekend family outing"
    ... )
    """
    
    context_type: ContextType = ContextType.TEMPORAL
    value: Any = None
    description: str = ""
    intensity: float = 1.0
    metadata: dict[str, Any] = field(default_factory=dict)
    
    node_type: NodeType = field(default=NodeType.CONTEXT, init=False)
    
    def __post_init__(self) -> None:
        if not 0.0 <= self.intensity <= 1.0:
            raise ValueError("intensity must be in [0, 1]")
    
    def __repr__(self) -> str:
        return f"Context(type={self.context_type}, value={self.value!r})"
    
    @property
    def is_temporal(self) -> bool:
        return self.context_type == ContextType.TEMPORAL
    
    @property
    def is_social(self) -> bool:
        return self.context_type == ContextType.SOCIAL
    
    @property
    def is_purposive(self) -> bool:
        return self.context_type == ContextType.PURPOSIVE
    
    # Factory methods for common contexts
    @classmethod
    def temporal(cls, value: str, description: str = "") -> Context:
        """Create a temporal context."""
        return cls(context_type=ContextType.TEMPORAL, value=value, 
                   description=description)
    
    @classmethod
    def social(cls, companions: list[str] | None = None,
               alone: bool = False, description: str = "") -> Context:
        """Create a social context."""
        value = {"alone": alone, "companions": companions or []}
        return cls(context_type=ContextType.SOCIAL, value=value,
                   description=description)
    
    @classmethod
    def purposive(cls, purpose: str, description: str = "") -> Context:
        """Create a purposive context."""
        return cls(context_type=ContextType.PURPOSIVE, value=purpose,
                   description=description)
    
    @classmethod
    def environmental(cls, conditions: dict[str, Any],
                      description: str = "") -> Context:
        """Create an environmental context."""
        return cls(context_type=ContextType.ENVIRONMENTAL, value=conditions,
                   description=description)
