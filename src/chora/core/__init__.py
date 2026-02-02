"""
Chora Core Module

This module provides the foundational domain objects, graph infrastructure,
and type system for platial modelling.

Core Abstractions
-----------------
The library formalises the following first-class concepts:

- **Agent** — an entity with situated experience
- **SpatialExtent** — weakly semanticised spatial support
- **Encounter** — spatio-temporal relation between agent and extent
- **Context** — situational modifiers (temporal, social, purposive)
- **Practice** — emergent, patterned structures over encounters
- **Affect** — experiential response distributions
- **Familiarity** — evolving state variable
- **Liminality** — conditional, transitional quality
- **Meaning** — structured symbolic interpretation

Graph-Based Model
-----------------
The core representation is a typed, temporal, heterogeneous graph where:

- Nodes represent agents, encounters, abstractions, and symbolic entities
- Edges encode relations, transitions, derivations, and interpretations
- Edges carry weights, uncertainty, provenance, and temporal validity

Platial qualities are primarily encoded on edges and paths, enabling
multiple, even conflicting, experiences of the same spatial extent to coexist.

Epistemic Separation
--------------------
All data is explicitly categorised by epistemic level:

- OBSERVED — direct observation or measurement
- DERIVED — computed from observed data
- INTERPRETED — semantic/symbolic interpretation

This separation is enforced throughout the library and preserved in all
derivation and query operations.
"""

# Types and enumerations
from chora.core.types import (
    NodeType,
    EdgeType,
    EpistemicLevel,
    ContextType,
    AffectDimension,
    PracticeType,
    NodeId,
    EdgeId,
    AgentId,
    ExtentId,
    EncounterId,
)

# Exceptions
from chora.core.exceptions import (
    ChoraError,
    ValidationError,
    TemporalError,
    GraphError,
    ProvenanceError,
    QueryError,
)

# Temporal semantics
from chora.core.temporal import (
    TimeInterval,
    TemporalValidity,
    DecayFunction,
    ReinforcementFunction,
    exponential_decay,
    linear_decay,
    power_law_decay,
    linear_reinforcement,
    saturating_reinforcement,
)

# Uncertainty representation
from chora.core.uncertainty import (
    UncertaintyValue,
    ConfidenceInterval,
    ProbabilityDistribution,
    FuzzyMembership,
    GaussianDistribution,
    CategoricalDistribution,
    TriangularFuzzy,
    TrapezoidalFuzzy,
)

# Provenance tracking
from chora.core.provenance import (
    Provenance,
    ProvenanceRecord,
    ProvenanceChain,
    ProvenanceType,
)

# Graph infrastructure
from chora.core.node import PlatialNode
from chora.core.edge import PlatialEdge
from chora.core.graph import PlatialGraph

# Domain objects
from chora.core.agent import Agent
from chora.core.spatial_extent import SpatialExtent
from chora.core.encounter import Encounter
from chora.core.context import Context
from chora.core.practice import Practice
from chora.core.affect import Affect
from chora.core.familiarity import Familiarity
from chora.core.liminality import Liminality
from chora.core.meaning import Meaning

# Validation
from chora.core.validation import (
    validate_graph,
    validate_node,
    validate_edge,
    GraphValidator,
)

__all__ = [
    # Types
    "NodeType",
    "EdgeType",
    "EpistemicLevel",
    "ContextType",
    "AffectDimension",
    "PracticeType",
    "NodeId",
    "EdgeId",
    "AgentId",
    "ExtentId",
    "EncounterId",
    # Exceptions
    "ChoraError",
    "ValidationError",
    "TemporalError",
    "GraphError",
    "ProvenanceError",
    "QueryError",
    # Temporal
    "TimeInterval",
    "TemporalValidity",
    "DecayFunction",
    "ReinforcementFunction",
    "exponential_decay",
    "linear_decay",
    "power_law_decay",
    "linear_reinforcement",
    "saturating_reinforcement",
    # Uncertainty
    "UncertaintyValue",
    "ConfidenceInterval",
    "ProbabilityDistribution",
    "FuzzyMembership",
    "GaussianDistribution",
    "CategoricalDistribution",
    "TriangularFuzzy",
    "TrapezoidalFuzzy",
    # Provenance
    "Provenance",
    "ProvenanceRecord",
    "ProvenanceChain",
    "ProvenanceType",
    # Graph
    "PlatialNode",
    "PlatialEdge",
    "PlatialGraph",
    # Domain objects
    "Agent",
    "SpatialExtent",
    "Encounter",
    "Context",
    "Practice",
    "Affect",
    "Familiarity",
    "Liminality",
    "Meaning",
    # Validation
    "validate_graph",
    "validate_node",
    "validate_edge",
    "GraphValidator",
]
