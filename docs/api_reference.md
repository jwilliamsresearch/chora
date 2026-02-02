# API Reference

Complete reference for the Chora library, auto-generated using mkdocstrings.

## Core Module

### Graph Structure
::: chora.core.graph
    options:
      members:
        - PlatialGraph
      show_source: false

### Types & Enumerations
::: chora.core.types
    options:
      members:
        - NodeType
        - EdgeType
        - EpistemicLevel
        - PracticeType
      show_source: false

### Temporal Functions
::: chora.core.temporal
    options:
      members:
        - TimeInterval
        - TemporalValidity
        - exponential_decay
        - linear_decay

### Uncertainty & Probability
::: chora.core.uncertainty
    options:
      members:
        - ConfidenceInterval
        - UncertaintyValue
        - GaussianDistribution
        - CategoricalDistribution

### Provenance Tracking
::: chora.core.provenance
    options:
      members:
        - Provenance
        - ProvenanceChain

---

## Entities

### Agent
::: chora.core.agent.Agent

### SpatialExtent
::: chora.core.extent.SpatialExtent

### Encounter
::: chora.core.encounter.Encounter

### Familiarity
::: chora.core.familiarity.Familiarity

### Affect
::: chora.core.affect.Affect

### Practice
::: chora.core.practice.Practice

---

## Derivation Module

### Familiarity
::: chora.derive.familiarity
    options:
      members:
        - update_familiarity
        - compute_decay

### Place Extraction
::: chora.derive.place
    options:
      members:
        - extract_place
        - EmergentPlace

### Practice Detection
::: chora.derive.practices
    options:
      members:
        - detect_practices
        - detect_routines
        - PracticeDetectionConfig

---

## Query Module

### Query Builder
::: chora.query.queries
    options:
      members:
        - PlatialQuery
        - find_familiar_places
        - find_positive_places
        - query_encounters

### Graph Traversal
::: chora.query.traversal
    options:
      members:
        - traverse_from
        - find_path
        - find_connected

### Similarity Measures
::: chora.query.similarity
    options:
      members:
        - place_similarity
        - practice_similarity

---

## Adapters

### Base Adapter
::: chora.adapters.base.GraphAdapter

### In-Memory Adapter
::: chora.adapters.memory.InMemoryAdapter

### Neo4j Adapter
::: chora.adapters.neo4j.Neo4jAdapter
    options:
      show_source: false

### PostGIS Adapter
::: chora.adapters.postgis.PostGISAdapter
    options:
      show_source: false

---

## Server Module

### FastAPI Application
::: chora.server.app
    options:
      show_source: false

### API Endpoints
::: chora.server.api
    options:
      show_source: false

---

## Embeddings Module

### Local Embedder
::: chora.embeddings.local
    options:
      members:
        - LocalEmbedder
        - get_embedding_model
