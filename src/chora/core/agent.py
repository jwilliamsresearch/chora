"""
Agent Domain Object

An Agent is an entity with situated experience — a human, group,
or proxy that can participate in encounters with spatial extents.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from chora.core.types import NodeType, EpistemicLevel, AgentId, NodeId
from chora.core.node import PlatialNode
from chora.core.temporal import TemporalValidity
from chora.core.provenance import ProvenanceChain


@dataclass
class Agent(PlatialNode):
    """
    An entity with situated experience.
    
    Agents are the experiential subjects in platial modelling. They
    participate in encounters, develop familiarity, express affect,
    and interpret meaning.
    
    Parameters
    ----------
    name : str
        Human-readable name for this agent.
    agent_id : AgentId | None
        Optional domain-specific identifier.
    agent_type : str
        Type of agent (e.g., "individual", "group", "proxy").
    attributes : dict[str, Any]
        Agent attributes (demographics, preferences, etc.).
    
    Examples
    --------
    >>> alice = Agent(name="Alice", agent_type="individual")
    >>> alice.node_type
    <NodeType.AGENT: 'agent'>
    
    >>> # With custom attributes
    >>> walker = Agent(
    ...     name="Walker 001",
    ...     agent_type="individual",
    ...     attributes={"mobility": "walking", "age_group": "adult"}
    ... )
    """
    
    name: str = ""
    agent_id: AgentId | None = None
    agent_type: str = "individual"
    attributes: dict[str, Any] = field(default_factory=dict)
    
    # Set node_type for this subclass
    node_type: NodeType = field(default=NodeType.AGENT, init=False)
    
    def __post_init__(self) -> None:
        # Don't call super().__post_init__ as it checks for node_type
        pass
    
    def __repr__(self) -> str:
        return f"Agent(id={self.id!r}, name={self.name!r})"
    
    @property
    def display_name(self) -> str:
        """Return display name, falling back to ID if no name."""
        return self.name or str(self.id)
    
    def set_attribute(self, key: str, value: Any) -> None:
        """Set an agent attribute."""
        self.attributes[key] = value
    
    def get_attribute(self, key: str, default: Any = None) -> Any:
        """Get an agent attribute."""
        return self.attributes.get(key, default)
    
    @classmethod
    def individual(cls, name: str, **attributes: Any) -> Agent:
        """Create an individual agent."""
        return cls(name=name, agent_type="individual", attributes=attributes)
    
    @classmethod
    def group(cls, name: str, members: list[str] | None = None,
              **attributes: Any) -> Agent:
        """Create a group agent."""
        attrs = {"members": members or [], **attributes}
        return cls(name=name, agent_type="group", attributes=attrs)
    
    @classmethod
    def proxy(cls, name: str, represented_by: str,
              **attributes: Any) -> Agent:
        """Create a proxy agent (representing another entity)."""
        attrs = {"represented_by": represented_by, **attributes}
        return cls(name=name, agent_type="proxy", attributes=attrs)
