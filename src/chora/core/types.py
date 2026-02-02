"""
Core Type Definitions for Chora

This module defines the foundational types, enumerations, and type aliases
used throughout the Chora library. These types encode the ontological
structure of platial modelling.

Type Categories
---------------
1. **Node Types** — classify entities in the platial graph
2. **Edge Types** — classify relations between entities
3. **Epistemic Levels** — distinguish data provenance and certainty
4. **Context Types** — categorise situational modifiers
5. **Affect Dimensions** — model experiential response
6. **Practice Types** — classify emergent patterns

Design Rationale
----------------
Types are defined as string-backed enums to ensure:
- Serialization compatibility across backends
- Human-readable graph inspection
- Extension without breaking existing data

Examples
--------
>>> from chora.core.types import NodeType, EpistemicLevel
>>> NodeType.ENCOUNTER
<NodeType.ENCOUNTER: 'encounter'>
>>> EpistemicLevel.OBSERVED.value
'observed'
"""

from __future__ import annotations

from enum import Enum
from typing import NewType, TypeAlias


# =============================================================================
# Type Aliases for Identifiers
# =============================================================================

#: Unique identifier for any node in the platial graph
NodeId = NewType("NodeId", str)

#: Unique identifier for any edge in the platial graph
EdgeId = NewType("EdgeId", str)

#: Unique identifier for an Agent
AgentId = NewType("AgentId", str)

#: Unique identifier for a SpatialExtent
ExtentId = NewType("ExtentId", str)

#: Unique identifier for an Encounter
EncounterId = NewType("EncounterId", str)

#: Weight value for edges (typically in [0, 1] but not enforced)
Weight: TypeAlias = float

#: Probability value in [0, 1]
Probability: TypeAlias = float

#: Membership degree for fuzzy sets in [0, 1]
MembershipDegree: TypeAlias = float


# =============================================================================
# Node Types
# =============================================================================

class NodeType(str, Enum):
    """
    Classification of node types in the platial graph.

    Each type represents a distinct ontological category in platial modelling.
    Place is notably absent because it emerges as a subgraph, not a primitive.

    Attributes
    ----------
    AGENT : str
        An entity with situated experience (human, group, or proxy).
    SPATIAL_EXTENT : str
        A weakly semanticised spatial support (geometry with minimal semantics).
    ENCOUNTER : str
        A spatio-temporal relation between an agent and a spatial extent.
    CONTEXT : str
        Situational modifiers that affect the character of an encounter.
    PRACTICE : str
        An emergent, patterned structure over repeated encounters.
    AFFECT : str
        An experiential response distribution attached to an encounter or place.
    FAMILIARITY : str
        An evolving state variable representing accumulated experience.
    LIMINALITY : str
        A conditional, transitional quality at spatial or experiential boundaries.
    MEANING : str
        A structured symbolic interpretation attached to place.

    Examples
    --------
    >>> NodeType.ENCOUNTER
    <NodeType.ENCOUNTER: 'encounter'>
    >>> NodeType.ENCOUNTER.value
    'encounter'
    >>> NodeType('encounter')
    <NodeType.ENCOUNTER: 'encounter'>
    """

    AGENT = "agent"
    SPATIAL_EXTENT = "spatial_extent"
    ENCOUNTER = "encounter"
    CONTEXT = "context"
    PRACTICE = "practice"
    AFFECT = "affect"
    FAMILIARITY = "familiarity"
    LIMINALITY = "liminality"
    MEANING = "meaning"

    def __str__(self) -> str:
        return self.value


# =============================================================================
# Edge Types
# =============================================================================

class EdgeType(str, Enum):
    """
    Classification of edge types in the platial graph.

    Edges encode relations, transitions, derivations, and interpretations.
    Platial qualities are primarily encoded on edges, not nodes.

    Attributes
    ----------
    PARTICIPATES_IN : str
        Agent ─participates_in─▶ Encounter
    OCCURS_AT : str
        Encounter ─occurs_at─▶ SpatialExtent
    HAS_CONTEXT : str
        Encounter ─has_context─▶ Context
    DERIVES_FROM : str
        Derived entity ─derives_from─▶ Source entity (provenance)
    TRANSITIONS_TO : str
        Encounter ─transitions_to─▶ Encounter (temporal sequence)
    REINFORCES : str
        Encounter ─reinforces─▶ Familiarity (strengthening relation)
    DECAYS : str
        Time ─decays─▶ Familiarity (weakening relation)
    EXPRESSES : str
        Encounter ─expresses─▶ Affect
    INTERPRETS_AS : str
        Agent ─interprets_as─▶ Meaning (subjective interpretation)
    BELONGS_TO : str
        Encounter ─belongs_to─▶ Practice (pattern membership)
    BOUNDS : str
        SpatialExtent ─bounds─▶ Liminality (boundary relation)
    CROSSES : str
        Encounter ─crosses─▶ Liminality (threshold crossing)
    SIMILAR_TO : str
        Entity ─similar_to─▶ Entity (similarity relation)
    CONFLICTS_WITH : str
        Meaning ─conflicts_with─▶ Meaning (interpretive conflict)

    Examples
    --------
    >>> EdgeType.PARTICIPATES_IN
    <EdgeType.PARTICIPATES_IN: 'participates_in'>
    """

    PARTICIPATES_IN = "participates_in"
    OCCURS_AT = "occurs_at"
    HAS_CONTEXT = "has_context"
    DERIVES_FROM = "derives_from"
    TRANSITIONS_TO = "transitions_to"
    REINFORCES = "reinforces"
    DECAYS = "decays"
    EXPRESSES = "expresses"
    INTERPRETS_AS = "interprets_as"
    BELONGS_TO = "belongs_to"
    BOUNDS = "bounds"
    CROSSES = "crosses"
    SIMILAR_TO = "similar_to"
    CONFLICTS_WITH = "conflicts_with"

    def __str__(self) -> str:
        return self.value


# =============================================================================
# Epistemic Levels
# =============================================================================

class EpistemicLevel(str, Enum):
    """
    Classification of data by epistemic status.

    This is a core design principle: observed, derived, and interpreted
    data are explicitly distinguished throughout the library.

    Attributes
    ----------
    OBSERVED : str
        Direct observation or measurement from sensors, surveys, or traces.
        Highest confidence, lowest interpretation.
    DERIVED : str
        Computed from observed data using deterministic or probabilistic
        methods. Provenance to source data is preserved.
    INTERPRETED : str
        Semantic or symbolic interpretation involving subjective judgement.
        Lowest confidence, highest interpretation.

    Examples
    --------
    >>> from chora.core.types import EpistemicLevel
    >>> level = EpistemicLevel.OBSERVED
    >>> level.is_more_certain_than(EpistemicLevel.DERIVED)
    True

    Notes
    -----
    The ordering OBSERVED > DERIVED > INTERPRETED represents decreasing
    epistemic certainty and increasing interpretive content.
    """

    OBSERVED = "observed"
    DERIVED = "derived"
    INTERPRETED = "interpreted"

    def __str__(self) -> str:
        return self.value

    @property
    def certainty_order(self) -> int:
        """Return numeric ordering for certainty comparisons."""
        return {"observed": 3, "derived": 2, "interpreted": 1}[self.value]

    def is_more_certain_than(self, other: EpistemicLevel) -> bool:
        """
        Compare epistemic certainty levels.

        Parameters
        ----------
        other : EpistemicLevel
            The level to compare against.

        Returns
        -------
        bool
            True if this level is epistemically more certain.

        Examples
        --------
        >>> EpistemicLevel.OBSERVED.is_more_certain_than(EpistemicLevel.DERIVED)
        True
        >>> EpistemicLevel.INTERPRETED.is_more_certain_than(EpistemicLevel.OBSERVED)
        False
        """
        return self.certainty_order > other.certainty_order


# =============================================================================
# Context Types
# =============================================================================

class ContextType(str, Enum):
    """
    Classification of contextual modifiers for encounters.

    Context affects the character and meaning of encounters without
    changing the spatial or temporal facts.

    Attributes
    ----------
    TEMPORAL : str
        Time-related context (time of day, season, duration).
    SOCIAL : str
        Social context (alone, with family, with strangers).
    PURPOSIVE : str
        Purpose or intention (commuting, leisure, exploration).
    ENVIRONMENTAL : str
        Environmental conditions (weather, lighting, noise).
    EMOTIONAL : str
        Pre-existing emotional state of the agent.
    PHYSICAL : str
        Physical state or constraints (mobility, fatigue).
    CULTURAL : str
        Cultural or normative context affecting interpretation.

    Examples
    --------
    >>> ContextType.SOCIAL
    <ContextType.SOCIAL: 'social'>
    """

    TEMPORAL = "temporal"
    SOCIAL = "social"
    PURPOSIVE = "purposive"
    ENVIRONMENTAL = "environmental"
    EMOTIONAL = "emotional"
    PHYSICAL = "physical"
    CULTURAL = "cultural"

    def __str__(self) -> str:
        return self.value


# =============================================================================
# Affect Dimensions
# =============================================================================

class AffectDimension(str, Enum):
    """
    Dimensions for representing experiential affect.

    Based on established psychological models of affect, particularly
    the circumplex model (Russell, 1980) and PAD model (Mehrabian, 1996).

    Attributes
    ----------
    VALENCE : str
        Positive to negative feeling (pleasure-displeasure).
    AROUSAL : str
        Activation level (calm-excited).
    DOMINANCE : str
        Sense of control or agency (submissive-dominant).
    SAFETY : str
        Perceived safety or threat level.
    BELONGING : str
        Sense of inclusion or exclusion.
    ATTACHMENT : str
        Emotional connection strength to place.

    Examples
    --------
    >>> AffectDimension.VALENCE
    <AffectDimension.VALENCE: 'valence'>

    References
    ----------
    Russell, J.A. (1980). A circumplex model of affect.
    Mehrabian, A. (1996). Pleasure-arousal-dominance: A general framework.
    """

    VALENCE = "valence"
    AROUSAL = "arousal"
    DOMINANCE = "dominance"
    SAFETY = "safety"
    BELONGING = "belonging"
    ATTACHMENT = "attachment"

    def __str__(self) -> str:
        return self.value


# =============================================================================
# Practice Types
# =============================================================================

class PracticeType(str, Enum):
    """
    Classification of emergent practices over encounters.

    Practices are patterned structures that emerge from repeated
    encounters and form the basis of routines and habits.

    Attributes
    ----------
    ROUTINE : str
        Regularly repeated pattern with consistent timing.
    HABIT : str
        Automatic, often unconscious repeated behaviour.
    RITUAL : str
        Symbolically meaningful repeated practice.
    EXPLORATION : str
        Pattern of novelty-seeking and discovery.
    AVOIDANCE : str
        Consistent pattern of avoiding certain places.
    DWELLING : str
        Extended presence in a place.
    TRAVERSAL : str
        Movement through places without dwelling.

    Examples
    --------
    >>> PracticeType.ROUTINE
    <PracticeType.ROUTINE: 'routine'>
    """

    ROUTINE = "routine"
    HABIT = "habit"
    RITUAL = "ritual"
    EXPLORATION = "exploration"
    AVOIDANCE = "avoidance"
    DWELLING = "dwelling"
    TRAVERSAL = "traversal"

    def __str__(self) -> str:
        return self.value


# =============================================================================
# Liminality Types
# =============================================================================

class LiminalityType(str, Enum):
    """
    Classification of liminal (threshold/transitional) qualities.

    Liminality represents the in-between, transitional character of
    certain places or experiences.

    Attributes
    ----------
    SPATIAL : str
        Physical boundary or threshold between spaces.
    TEMPORAL : str
        Transitional time period (dawn, dusk, season change).
    SOCIAL : str
        Transition between social roles or statuses.
    EXPERIENTIAL : str
        Psychological transition in experience of place.
    FUNCTIONAL : str
        Transition between functional zones.

    Examples
    --------
    >>> LiminalityType.SPATIAL
    <LiminalityType.SPATIAL: 'spatial'>
    """

    SPATIAL = "spatial"
    TEMPORAL = "temporal"
    SOCIAL = "social"
    EXPERIENTIAL = "experiential"
    FUNCTIONAL = "functional"

    def __str__(self) -> str:
        return self.value


# =============================================================================
# Meaning Types
# =============================================================================

class MeaningType(str, Enum):
    """
    Classification of symbolic meanings attached to places.

    Meanings are interpretations that go beyond physical or
    functional description.

    Attributes
    ----------
    PERSONAL : str
        Individual biographical significance.
    SOCIAL : str
        Shared social or community meaning.
    CULTURAL : str
        Broader cultural or historical significance.
    SYMBOLIC : str
        Abstract symbolic or metaphorical meaning.
    FUNCTIONAL : str
        Meaning derived from use and activity.
    AESTHETIC : str
        Meaning derived from sensory experience.
    SPIRITUAL : str
        Religious or spiritual significance.

    Examples
    --------
    >>> MeaningType.PERSONAL
    <MeaningType.PERSONAL: 'personal'>
    """

    PERSONAL = "personal"
    SOCIAL = "social"
    CULTURAL = "cultural"
    SYMBOLIC = "symbolic"
    FUNCTIONAL = "functional"
    AESTHETIC = "aesthetic"
    SPIRITUAL = "spiritual"

    def __str__(self) -> str:
        return self.value
