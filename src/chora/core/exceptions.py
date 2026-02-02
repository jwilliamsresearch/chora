"""
Exception Hierarchy for Chora

Custom exceptions organised by domain for precise error handling.
"""

from __future__ import annotations
from typing import Any


class ChoraError(Exception):
    """Base exception for all Chora library errors."""

    def __init__(self, message: str, **context: Any) -> None:
        self.message = message
        self.context = context
        super().__init__(self._format_message())

    def _format_message(self) -> str:
        if not self.context:
            return self.message
        context_str = ", ".join(f"{k}={v!r}" for k, v in self.context.items())
        return f"{self.message} ({context_str})"


# Validation Errors
class ValidationError(ChoraError):
    """Raised when data fails schema or constraint validation."""
    pass


class SchemaValidationError(ValidationError):
    """Raised when data violates the graph schema."""
    pass


class ConstraintViolationError(ValidationError):
    """Raised when a domain constraint is violated."""
    pass


# Temporal Errors
class TemporalError(ChoraError):
    """Raised when temporal semantics are violated."""
    pass


class InvalidTimeIntervalError(TemporalError):
    """Raised when a time interval is invalid."""
    pass


class TemporalOrderingError(TemporalError):
    """Raised when temporal ordering constraints are violated."""
    pass


class DecayComputationError(TemporalError):
    """Raised when decay function computation fails."""
    pass


# Graph Errors
class GraphError(ChoraError):
    """Raised for graph structure and operation errors."""
    pass


class NodeNotFoundError(GraphError):
    """Raised when a referenced node does not exist."""
    pass


class EdgeNotFoundError(GraphError):
    """Raised when a referenced edge does not exist."""
    pass


class DuplicateNodeError(GraphError):
    """Raised when attempting to add a node with an existing ID."""
    pass


class InvalidEdgeError(GraphError):
    """Raised when an edge violates graph constraints."""
    pass


class CycleDetectedError(GraphError):
    """Raised when an operation would create a forbidden cycle."""
    pass


# Provenance Errors
class ProvenanceError(ChoraError):
    """Raised for provenance tracking errors."""
    pass


class BrokenProvenanceChainError(ProvenanceError):
    """Raised when the provenance chain is incomplete or broken."""
    pass


class InvalidProvenanceError(ProvenanceError):
    """Raised when provenance metadata is invalid."""
    pass


# Query Errors
class QueryError(ChoraError):
    """Raised for query execution errors."""
    pass


class InvalidQueryError(QueryError):
    """Raised when a query is syntactically or semantically invalid."""
    pass


class QueryTimeoutError(QueryError):
    """Raised when a query exceeds the time limit."""
    pass


class EmptyResultError(QueryError):
    """Raised when a query returns no results but results were expected."""
    pass


# Adapter Errors
class AdapterError(ChoraError):
    """Raised for backend adapter errors."""
    pass


class ConnectionError(AdapterError):
    """Raised when connection to a backend fails."""
    pass


class SerializationError(AdapterError):
    """Raised when serialization or deserialization fails."""
    pass


class BackendOperationError(AdapterError):
    """Raised when a backend-specific operation fails."""
    pass


# Uncertainty Errors
class UncertaintyError(ChoraError):
    """Raised for uncertainty representation errors."""
    pass


class InvalidProbabilityError(UncertaintyError):
    """Raised when a probability value is out of bounds."""
    pass


class DistributionError(UncertaintyError):
    """Raised when probability distribution parameters are invalid."""
    pass
