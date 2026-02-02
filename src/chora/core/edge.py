"""
Base Edge for Platial Graph

Edges encode relations, transitions, derivations, and interpretations.
Platial qualities are primarily encoded on edges, not nodes.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any
from uuid import uuid4

from chora.core.types import EdgeType, EpistemicLevel, EdgeId, NodeId, Weight
from chora.core.temporal import TemporalValidity
from chora.core.uncertainty import UncertaintyValue
from chora.core.provenance import ProvenanceChain, Provenance


@dataclass
class PlatialEdge:
    """
    An edge in the platial graph.
    
    Edges connect nodes and carry platial qualities including
    weights, uncertainty, provenance, and temporal validity.
    
    Parameters
    ----------
    source_id : NodeId
        ID of the source node.
    target_id : NodeId
        ID of the target node.
    edge_type : EdgeType
        Classification of this edge.
    weight : Weight
        Edge weight, typically in [0, 1].
    epistemic_level : EpistemicLevel
        How this edge was established.
    temporal : TemporalValidity
        When this edge is/was valid.
    uncertainty : UncertaintyValue | None
        Uncertainty on edge weight.
    provenance : ProvenanceChain
        How this edge was derived.
    properties : dict[str, Any]
        Additional flexible properties.
    
    Examples
    --------
    >>> edge = PlatialEdge(
    ...     source_id=NodeId("agent_001"),
    ...     target_id=NodeId("encounter_001"),
    ...     edge_type=EdgeType.PARTICIPATES_IN,
    ...     weight=1.0
    ... )
    """
    
    source_id: NodeId
    target_id: NodeId
    edge_type: EdgeType
    weight: Weight = 1.0
    id: EdgeId = field(default_factory=lambda: EdgeId(str(uuid4())))
    epistemic_level: EpistemicLevel = EpistemicLevel.OBSERVED
    temporal: TemporalValidity = field(default_factory=TemporalValidity)
    uncertainty: UncertaintyValue | None = None
    provenance: ProvenanceChain = field(default_factory=ProvenanceChain)
    properties: dict[str, Any] = field(default_factory=dict)
    
    def __hash__(self) -> int:
        return hash(self.id)
    
    def __eq__(self, other: object) -> bool:
        if not isinstance(other, PlatialEdge):
            return NotImplemented
        return self.id == other.id
    
    @property
    def is_valid_now(self) -> bool:
        """Check if this edge is currently valid."""
        return self.temporal.is_current
    
    def is_valid_at(self, timestamp: datetime) -> bool:
        """Check if this edge was valid at a given time."""
        return self.temporal.is_valid_at(timestamp)
    
    @property
    def weighted_value(self) -> float:
        """Get weight, accounting for uncertainty if present."""
        if self.uncertainty is not None:
            return self.weight * (1.0 - self.uncertainty.uncertainty)
        return self.weight
    
    def add_provenance(self, prov: Provenance) -> None:
        """Add a provenance record."""
        self.provenance.add(prov)
    
    def update_weight(self, new_weight: Weight, 
                      uncertainty: UncertaintyValue | None = None) -> None:
        """Update the edge weight."""
        self.weight = new_weight
        if uncertainty is not None:
            self.uncertainty = uncertainty
        self.temporal.modified_at = datetime.now()
    
    def invalidate(self, at: datetime | None = None) -> None:
        """Mark this edge as no longer valid."""
        self.temporal.invalidate(at)
    
    def to_dict(self) -> dict[str, Any]:
        """Serialize edge to dictionary."""
        return {
            "id": str(self.id),
            "source_id": str(self.source_id),
            "target_id": str(self.target_id),
            "edge_type": self.edge_type.value,
            "weight": self.weight,
            "epistemic_level": self.epistemic_level.value,
            "valid_from": self.temporal.valid_from.isoformat() if self.temporal.valid_from else None,
            "valid_to": self.temporal.valid_to.isoformat() if self.temporal.valid_to else None,
            "properties": self.properties,
        }
    
    @classmethod
    def participates_in(cls, agent_id: NodeId, encounter_id: NodeId,
                        weight: Weight = 1.0) -> PlatialEdge:
        """Create a PARTICIPATES_IN edge."""
        return cls(
            source_id=agent_id,
            target_id=encounter_id,
            edge_type=EdgeType.PARTICIPATES_IN,
            weight=weight
        )
    
    @classmethod
    def occurs_at(cls, encounter_id: NodeId, extent_id: NodeId,
                  weight: Weight = 1.0) -> PlatialEdge:
        """Create an OCCURS_AT edge."""
        return cls(
            source_id=encounter_id,
            target_id=extent_id,
            edge_type=EdgeType.OCCURS_AT,
            weight=weight
        )
    
    @classmethod
    def transitions_to(cls, from_encounter: NodeId, to_encounter: NodeId,
                       weight: Weight = 1.0) -> PlatialEdge:
        """Create a TRANSITIONS_TO edge."""
        return cls(
            source_id=from_encounter,
            target_id=to_encounter,
            edge_type=EdgeType.TRANSITIONS_TO,
            weight=weight
        )
