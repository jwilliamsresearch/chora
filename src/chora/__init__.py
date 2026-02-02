"""
Chora: A Platial Modelling Library

Chora enables geospatial systems to represent, reason with, and operate on
human experience of place — including affect, routine, familiarity, liminality,
and meaning — in a computationally rigorous, epistemically transparent way.

Core Premise
------------
Place is not a primitive. Place emerges from repeated, situated encounters
between agents, spatial extents, and context, and is modelled as a relational,
evolving structure rather than a static container or label.

Design Principles
-----------------
1. Relational primacy — experiential qualities are relations, not attributes
2. Encounter-centric modelling — encounters are the atomic unit of experience
3. Epistemic separation — observed, derived, and interpreted data are distinct
4. Probabilistic representation — vagueness is modelled, not suppressed
5. Temporal explicitness — platial constructs evolve, decay, and reconfigure
6. Theory-encoded computation — derivation operators embody theory

Modules
-------
chora.core
    Domain objects, graph infrastructure, and type system
chora.derive
    Theory-encoded derivation operators
chora.query
    Platial queries and graph traversal
chora.adapters
    Backend-agnostic storage adapters

Example
-------
>>> from chora.core import Agent, SpatialExtent, Encounter, PlatialGraph
>>> from chora.core.types import EpistemicLevel
>>> from chora.derive import extract_encounters, update_familiarity
>>>
>>> # Create a platial graph
>>> graph = PlatialGraph()
>>>
>>> # Add an agent and spatial extent
>>> agent = Agent(id="walker_001", name="Alice")
>>> park = SpatialExtent(id="park_central", name="Central Park")
>>> graph.add_node(agent)
>>> graph.add_node(park)
>>>
>>> # Record an encounter
>>> encounter = Encounter(
...     agent=agent,
...     extent=park,
...     timestamp=datetime.now(),
...     epistemic_level=EpistemicLevel.OBSERVED
... )
>>> graph.add_encounter(encounter)

See Also
--------
- Theory documentation: docs/theory.md
- API reference: https://chora.readthedocs.io
"""

from chora.core import (
    # Domain objects
    Agent,
    SpatialExtent,
    Encounter,
    Context,
    Practice,
    Affect,
    Familiarity,
    Liminality,
    Meaning,
    # Graph infrastructure
    PlatialGraph,
    PlatialNode,
    PlatialEdge,
    # Types
    NodeType,
    EdgeType,
    EpistemicLevel,
    # Temporal
    TimeInterval,
    # Uncertainty
    UncertaintyValue,
    ProbabilityDistribution,
    FuzzyMembership,
    # Provenance
    Provenance,
    ProvenanceChain,
)

__version__ = "0.1.0"
__author__ = "James Williams"

__all__ = [
    # Version
    "__version__",
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
    # Graph infrastructure
    "PlatialGraph",
    "PlatialNode",
    "PlatialEdge",
    # Types
    "NodeType",
    "EdgeType",
    "EpistemicLevel",
    # Temporal
    "TimeInterval",
    # Uncertainty
    "UncertaintyValue",
    "ProbabilityDistribution",
    "FuzzyMembership",
    # Provenance
    "Provenance",
    "ProvenanceChain",
]
