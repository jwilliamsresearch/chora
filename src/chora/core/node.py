"""
Base Node for Platial Graph

Nodes represent entities in the platial graph: agents, encounters,
spatial extents, and derived abstractions.
"""

from __future__ import annotations

from abc import ABC
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any
from uuid import uuid4

from chora.core.types import NodeType, EpistemicLevel, NodeId
from chora.core.temporal import TemporalValidity
from chora.core.uncertainty import UncertaintyValue
from chora.core.provenance import ProvenanceChain, Provenance


@dataclass
class PlatialNode(ABC):
    """
    Abstract base class for all nodes in the platial graph.
    
    Every node has:
    - Unique identifier
    - Node type classification
    - Temporal validity (when is this node valid)
    - Epistemic level (observed, derived, or interpreted)
    - Provenance chain (how was this node created)
    - Optional uncertainty on existence
    
    Parameters
    ----------
    id : NodeId
        Unique identifier for this node.
    node_type : NodeType
        Classification of this node.
    epistemic_level : EpistemicLevel
        How this node was produced.
    temporal : TemporalValidity
        When this node is/was valid.
    provenance : ProvenanceChain
        Complete derivation history.
    existence_uncertainty : UncertaintyValue | None
        Uncertainty about whether this node exists.
    properties : dict[str, Any]
        Additional flexible properties.
    
    Examples
    --------
    >>> from chora.core import Agent
    >>> agent = Agent(id=NodeId("agent_001"), name="Alice")
    >>> agent.node_type
    <NodeType.AGENT: 'agent'>
    >>> agent.is_observed
    True
    """
    
    id: NodeId = field(default_factory=lambda: NodeId(str(uuid4())))
    node_type: NodeType = field(init=False)
    epistemic_level: EpistemicLevel = EpistemicLevel.OBSERVED
    temporal: TemporalValidity = field(default_factory=TemporalValidity)
    provenance: ProvenanceChain = field(default_factory=ProvenanceChain)
    existence_uncertainty: UncertaintyValue | None = None
    properties: dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self) -> None:
        # Subclasses must set node_type
        if not hasattr(self, 'node_type') or self.node_type is None:
            raise NotImplementedError("Subclasses must set node_type")
    
    def __hash__(self) -> int:
        return hash(self.id)
    
    def __eq__(self, other: object) -> bool:
        if not isinstance(other, PlatialNode):
            return NotImplemented
        return self.id == other.id
    
    @property
    def is_observed(self) -> bool:
        """Check if this node is from direct observation."""
        return self.epistemic_level == EpistemicLevel.OBSERVED
    
    @property
    def is_derived(self) -> bool:
        """Check if this node is derived from other data."""
        return self.epistemic_level == EpistemicLevel.DERIVED
    
    @property
    def is_interpreted(self) -> bool:
        """Check if this node is an interpretation."""
        return self.epistemic_level == EpistemicLevel.INTERPRETED
    
    @property
    def is_valid_now(self) -> bool:
        """Check if this node is currently valid."""
        return self.temporal.is_current
    
    def is_valid_at(self, timestamp: datetime) -> bool:
        """Check if this node was valid at a given time."""
        return self.temporal.is_valid_at(timestamp)
    
    def add_provenance(self, prov: Provenance) -> None:
        """Add a provenance record to this node's chain."""
        self.provenance.add(prov)
    
    def set_property(self, key: str, value: Any) -> None:
        """Set a flexible property."""
        self.properties[key] = value
    
    def get_property(self, key: str, default: Any = None) -> Any:
        """Get a flexible property."""
        return self.properties.get(key, default)
    
    def invalidate(self, at: datetime | None = None) -> None:
        """Mark this node as no longer valid."""
        self.temporal.invalidate(at)
    
    def to_dict(self) -> dict[str, Any]:
        """Serialize node to dictionary."""
        return {
            "id": str(self.id),
            "node_type": self.node_type.value,
            "epistemic_level": self.epistemic_level.value,
            "valid_from": self.temporal.valid_from.isoformat() if self.temporal.valid_from else None,
            "valid_to": self.temporal.valid_to.isoformat() if self.temporal.valid_to else None,
            "properties": self.properties,
        }
