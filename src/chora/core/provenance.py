"""
Provenance Tracking for Chora

This module implements provenance tracking to maintain epistemic transparency.
All derived and interpreted data preserves a chain back to source observations.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Sequence
from uuid import uuid4

from chora.core.exceptions import InvalidProvenanceError, BrokenProvenanceChainError


class ProvenanceType(str, Enum):
    """
    Classification of provenance operations.
    
    Attributes
    ----------
    OBSERVATION : str
        Direct observation or measurement.
    DERIVATION : str
        Computed from source data.
    AGGREGATION : str
        Combined from multiple sources.
    TRANSFORMATION : str
        Transformed representation of source.
    INTERPRETATION : str
        Subjective interpretation.
    ANNOTATION : str
        Additional metadata attachment.
    CORRECTION : str
        Correction of previous data.
    """
    
    OBSERVATION = "observation"
    DERIVATION = "derivation"
    AGGREGATION = "aggregation"
    TRANSFORMATION = "transformation"
    INTERPRETATION = "interpretation"
    ANNOTATION = "annotation"
    CORRECTION = "correction"


@dataclass(frozen=True, slots=True)
class Provenance:
    """
    Single provenance record describing how data was produced.
    
    Parameters
    ----------
    source_ids : tuple[str, ...]
        IDs of source entities this was derived from.
    operation : ProvenanceType
        Type of operation that produced this data.
    operator : str
        Name of the function/method that performed the operation.
    timestamp : datetime
        When the operation was performed.
    parameters : dict[str, Any] | None
        Parameters used in the operation.
    agent : str | None
        ID of agent (human or system) that performed operation.
    notes : str | None
        Free-text notes about the provenance.
    
    Examples
    --------
    >>> prov = Provenance(
    ...     source_ids=("enc_001", "enc_002"),
    ...     operation=ProvenanceType.DERIVATION,
    ...     operator="derive_familiarity",
    ...     timestamp=datetime.now()
    ... )
    """
    
    source_ids: tuple[str, ...]
    operation: ProvenanceType
    operator: str
    timestamp: datetime = field(default_factory=datetime.now)
    parameters: dict[str, Any] | None = None
    agent: str | None = None
    notes: str | None = None
    id: str = field(default_factory=lambda: str(uuid4()))
    
    def __post_init__(self) -> None:
        if self.timestamp > datetime.now():
            raise InvalidProvenanceError(
                "Provenance timestamp cannot be in future",
                timestamp=self.timestamp.isoformat()
            )
    
    @classmethod
    def observation(cls, observer: str, notes: str | None = None) -> Provenance:
        """Create provenance for direct observation."""
        return cls(
            source_ids=(),
            operation=ProvenanceType.OBSERVATION,
            operator="direct_observation",
            agent=observer,
            notes=notes
        )
    
    @classmethod
    def derivation(cls, source_ids: Sequence[str], operator: str,
                   parameters: dict[str, Any] | None = None) -> Provenance:
        """Create provenance for derived data."""
        return cls(
            source_ids=tuple(source_ids),
            operation=ProvenanceType.DERIVATION,
            operator=operator,
            parameters=parameters
        )


@dataclass(slots=True)
class ProvenanceChain:
    """
    Chain of provenance records for complete lineage tracking.
    
    A provenance chain maintains the complete history of how data
    was produced, enabling full reproducibility and explainability.
    
    Parameters
    ----------
    records : list[Provenance]
        Ordered list of provenance records (oldest first).
    
    Examples
    --------
    >>> chain = ProvenanceChain()
    >>> chain.add(Provenance.observation("sensor_001"))
    >>> chain.add(Provenance.derivation(["raw_001"], "clean_data"))
    >>> len(chain)
    2
    """
    
    records: list[Provenance] = field(default_factory=list)
    
    def add(self, provenance: Provenance) -> None:
        """Add a provenance record to the chain."""
        self.records.append(provenance)
    
    def __len__(self) -> int:
        return len(self.records)
    
    def __iter__(self):
        return iter(self.records)
    
    @property
    def origin(self) -> Provenance | None:
        """Return the original provenance record (if any)."""
        return self.records[0] if self.records else None
    
    @property
    def latest(self) -> Provenance | None:
        """Return the most recent provenance record."""
        return self.records[-1] if self.records else None
    
    @property
    def all_source_ids(self) -> set[str]:
        """Return all source IDs referenced in the chain."""
        sources: set[str] = set()
        for record in self.records:
            sources.update(record.source_ids)
        return sources
    
    @property
    def is_observed(self) -> bool:
        """Check if origin is direct observation."""
        return (self.origin is not None and 
                self.origin.operation == ProvenanceType.OBSERVATION)
    
    @property
    def derivation_depth(self) -> int:
        """Count derivation steps from origin."""
        return sum(
            1 for r in self.records 
            if r.operation == ProvenanceType.DERIVATION
        )
    
    def validate(self, existing_ids: set[str]) -> list[str]:
        """
        Validate that all source references exist.
        
        Parameters
        ----------
        existing_ids : set[str]
            Set of all valid entity IDs.
        
        Returns
        -------
        list[str]
            List of missing source IDs.
        """
        missing = []
        for source_id in self.all_source_ids:
            if source_id not in existing_ids:
                missing.append(source_id)
        return missing


@dataclass(slots=True)
class ProvenanceRecord:
    """
    Mixin-style provenance tracking for entities.
    
    This can be composed into any entity that needs provenance.
    """
    
    provenance: ProvenanceChain = field(default_factory=ProvenanceChain)
    
    def add_provenance(self, prov: Provenance) -> None:
        """Add provenance record."""
        self.provenance.add(prov)
    
    def get_lineage(self) -> list[Provenance]:
        """Get complete provenance lineage."""
        return list(self.provenance.records)
