# Theoretical Foundations

## The Problem with "Place"

Traditional GIS treats space as a container with objects located within it. But **place** is not simply location — it emerges from:

- Repeated **encounters** between agents and spatial extents
- Accumulated **familiarity** that grows and decays
- **Affect** — the emotional character of experience
- **Meaning** — symbolic interpretations attached to locations
- **Practices** — routines and habits that pattern our engagement

## Core Premise

> **Place is not a primitive. Place emerges.**

Chora models place as an *emergent subgraph* from a typed, temporal, heterogeneous graph of encounters, rather than as a predefined spatial category.

## Design Principles

| Principle | Implementation |
|-----------|----------------|
| **Relational Primacy** | Platial qualities on edges, not nodes |
| **Encounter-Centricity** | Encounters as first-class objects |
| **Epistemic Separation** | OBSERVED → DERIVED → INTERPRETED |
| **Probabilistic Representation** | Uncertainty throughout |
| **Temporal Explicitness** | All entities have lifetimes |
| **Theory-Encoded Computation** | Derivations embody platial theory |

## The Platial Graph

```
Agent ──PARTICIPATES_IN──► Encounter ──OCCURS_AT──► SpatialExtent
                              │
                              ├──HAS_CONTEXT──► Context
                              ├──EXPRESSES──► Affect
                              ├──REINFORCES──► Familiarity
                              └──BELONGS_TO──► Practice
```

## Epistemic Levels

All data is explicitly categorised:

- **OBSERVED** — Direct measurements (GPS traces, check-ins)
- **DERIVED** — Computed from observations (familiarity scores)
- **INTERPRETED** — Semantic/symbolic meanings

This separation ensures that uncertainty and provenance are preserved through all transformations.

## Familiarity Dynamics

Familiarity is modelled with:
- **Reinforcement** on each encounter (saturating growth)
- **Decay** over time without encounters (exponential)

```python
# After 5 visits
familiarity = 0.16

# After 14 days without visits
familiarity = 0.08  # Decayed by half
```

## Place Emergence

A "place" in Chora is not a stored entity but a **computed view**:

```python
place = extract_place(graph, extent_id, agent_id)
# Returns: EmergentPlace with familiarity, affect, meanings
```

This allows multiple agents to have different "places" at the same location.
