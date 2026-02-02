# Chora

**A Python library for place-based modelling in geospatial systems**

Chora represents place as an emergent, relational, and temporal structure derived from human encounters with spatial extents, preserving uncertainty and provenance throughout.

## Installation

```bash
pip install chora
```

For development:
```bash
pip install chora[dev]
```

## Core Concepts

- **Agent** — an entity with situated experience
- **SpatialExtent** — weakly semanticised spatial support  
- **Encounter** — spatio-temporal relation between agent and extent
- **Context** — situational modifiers (temporal, social, purposive)
- **Practice** — emergent, patterned structures over encounters
- **Affect** — experiential response distributions
- **Familiarity** — evolving state variable
- **Liminality** — conditional, transitional quality
- **Meaning** — structured symbolic interpretation

**Place is not a primitive** — it emerges as a subgraph from the intersection of these concepts.

## Quick Start

```python
from chora.core import Agent, SpatialExtent, Encounter, PlatialGraph
from chora.derive import extract_place
from datetime import datetime

# Create entities
walker = Agent.individual("Alice")
park = SpatialExtent.from_bounds(-0.13, 51.50, -0.12, 51.51, "Hyde Park")

# Record an encounter
encounter = Encounter(
    agent_id=walker.id,
    extent_id=park.id,
    start_time=datetime(2024, 6, 15, 10, 0),
    end_time=datetime(2024, 6, 15, 11, 30),
    activity="walking"
)

# Build graph and extract emergent place
graph = PlatialGraph("London Walks")
graph.add_node(walker)
graph.add_node(park)
graph.add_node(encounter)

place = extract_place(graph, park.id, walker.id)
print(f"Character: {place.character}")
```

## License

MIT
