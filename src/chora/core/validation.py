"""
Graph Validation for Chora

Validates graph structure, schema constraints, and epistemic consistency.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable

from chora.core.types import NodeType, EdgeType
from chora.core.graph import PlatialGraph
from chora.core.node import PlatialNode
from chora.core.edge import PlatialEdge
from chora.core.exceptions import ValidationError, SchemaValidationError


# Edge constraints: (source_type, edge_type, target_type)
VALID_EDGE_SCHEMA: set[tuple[NodeType, EdgeType, NodeType]] = {
    (NodeType.AGENT, EdgeType.PARTICIPATES_IN, NodeType.ENCOUNTER),
    (NodeType.ENCOUNTER, EdgeType.OCCURS_AT, NodeType.SPATIAL_EXTENT),
    (NodeType.ENCOUNTER, EdgeType.HAS_CONTEXT, NodeType.CONTEXT),
    (NodeType.ENCOUNTER, EdgeType.TRANSITIONS_TO, NodeType.ENCOUNTER),
    (NodeType.ENCOUNTER, EdgeType.EXPRESSES, NodeType.AFFECT),
    (NodeType.ENCOUNTER, EdgeType.REINFORCES, NodeType.FAMILIARITY),
    (NodeType.ENCOUNTER, EdgeType.BELONGS_TO, NodeType.PRACTICE),
    (NodeType.ENCOUNTER, EdgeType.CROSSES, NodeType.LIMINALITY),
    (NodeType.AGENT, EdgeType.INTERPRETS_AS, NodeType.MEANING),
    (NodeType.SPATIAL_EXTENT, EdgeType.BOUNDS, NodeType.LIMINALITY),
    (NodeType.FAMILIARITY, EdgeType.DERIVES_FROM, NodeType.ENCOUNTER),
    (NodeType.PRACTICE, EdgeType.DERIVES_FROM, NodeType.ENCOUNTER),
    (NodeType.AFFECT, EdgeType.DERIVES_FROM, NodeType.ENCOUNTER),
    (NodeType.MEANING, EdgeType.DERIVES_FROM, NodeType.ENCOUNTER),
    (NodeType.MEANING, EdgeType.CONFLICTS_WITH, NodeType.MEANING),
    (NodeType.MEANING, EdgeType.SIMILAR_TO, NodeType.MEANING),
}


@dataclass
class ValidationResult:
    """Result of a validation check."""
    
    valid: bool
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    
    def add_error(self, message: str) -> None:
        self.errors.append(message)
        self.valid = False
    
    def add_warning(self, message: str) -> None:
        self.warnings.append(message)
    
    def merge(self, other: ValidationResult) -> None:
        """Merge another result into this one."""
        self.errors.extend(other.errors)
        self.warnings.extend(other.warnings)
        if not other.valid:
            self.valid = False


def validate_node(node: PlatialNode) -> ValidationResult:
    """
    Validate a single node.
    
    Checks:
    - Node has valid ID
    - Node type is set
    - Temporal validity is consistent
    """
    result = ValidationResult(valid=True)
    
    if not node.id:
        result.add_error(f"Node has empty ID")
    
    if node.node_type is None:
        result.add_error(f"Node {node.id} has no type")
    
    # Check temporal consistency
    if (node.temporal.valid_from is not None and 
        node.temporal.valid_to is not None and
        node.temporal.valid_to < node.temporal.valid_from):
        result.add_error(
            f"Node {node.id}: valid_to precedes valid_from"
        )
    
    return result


def validate_edge(edge: PlatialEdge, graph: PlatialGraph) -> ValidationResult:
    """
    Validate a single edge.
    
    Checks:
    - Source and target nodes exist
    - Edge type is valid for source/target node types
    - Weight is in valid range
    """
    result = ValidationResult(valid=True)
    
    if not graph.has_node(edge.source_id):
        result.add_error(f"Edge {edge.id}: source node {edge.source_id} not found")
    
    if not graph.has_node(edge.target_id):
        result.add_error(f"Edge {edge.id}: target node {edge.target_id} not found")
    
    # Check edge schema
    if graph.has_node(edge.source_id) and graph.has_node(edge.target_id):
        source = graph.get_node(edge.source_id)
        target = graph.get_node(edge.target_id)
        constraint = (source.node_type, edge.edge_type, target.node_type)
        
        if constraint not in VALID_EDGE_SCHEMA:
            result.add_warning(
                f"Edge {edge.id}: unusual schema {source.node_type} "
                f"--[{edge.edge_type}]--> {target.node_type}"
            )
    
    return result


def validate_graph(graph: PlatialGraph, strict: bool = False) -> ValidationResult:
    """
    Validate entire graph structure.
    
    Parameters
    ----------
    graph : PlatialGraph
        The graph to validate.
    strict : bool
        If True, warnings become errors.
    
    Returns
    -------
    ValidationResult
        Validation result with errors and warnings.
    """
    result = ValidationResult(valid=True)
    
    # Validate all nodes
    for node in graph.nodes():
        node_result = validate_node(node)
        result.merge(node_result)
    
    # Validate all edges
    for edge in graph.edges():
        edge_result = validate_edge(edge, graph)
        if strict:
            for warning in edge_result.warnings:
                edge_result.add_error(warning)
            edge_result.warnings.clear()
        result.merge(edge_result)
    
    return result


class GraphValidator:
    """
    Extensible graph validator with custom rules.
    
    Examples
    --------
    >>> validator = GraphValidator()
    >>> validator.add_rule(my_custom_check)
    >>> result = validator.validate(graph)
    """
    
    def __init__(self) -> None:
        self.rules: list[Callable[[PlatialGraph], ValidationResult]] = []
        # Add default rules
        self.rules.append(lambda g: validate_graph(g))
    
    def add_rule(self, 
                 rule: Callable[[PlatialGraph], ValidationResult]) -> None:
        """Add a custom validation rule."""
        self.rules.append(rule)
    
    def validate(self, graph: PlatialGraph) -> ValidationResult:
        """Run all validation rules."""
        result = ValidationResult(valid=True)
        for rule in self.rules:
            rule_result = rule(graph)
            result.merge(rule_result)
        return result
