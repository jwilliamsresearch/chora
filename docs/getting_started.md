# Getting Started

## Installation

```bash
# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install from source
pip install -e .

# With development dependencies
pip install -e ".[dev]"
```

## Your First Platial Model

```python
from datetime import datetime, timedelta
from chora.core import (
    Agent, SpatialExtent, Encounter, PlatialGraph,
    PlatialEdge, EdgeType
)
from chora.derive import update_familiarity, extract_place

# 1. Create the world
park = SpatialExtent.from_bounds(
    -0.127, 51.507, -0.126, 51.508,
    name="Local Park"
)

# 2. Create an agent
alice = Agent.individual("Alice")

# 3. Build the graph
graph = PlatialGraph(name="My First Graph")
graph.add_node(park)
graph.add_node(alice)

# 4. Record encounters
for day in range(5):
    visit_time = datetime.now() - timedelta(days=7-day)
    
    encounter = Encounter(
        agent_id=alice.id,
        extent_id=park.id,
        start_time=visit_time,
        end_time=visit_time + timedelta(hours=1)
    )
    graph.add_node(encounter)
    
    # Add edges
    graph.add_edge(PlatialEdge.participates_in(alice.id, encounter.id))
    graph.add_edge(PlatialEdge.occurs_at(encounter.id, park.id))
    
    # Update derived state
    update_familiarity(graph, encounter)

# 5. Extract the emergent place
place = extract_place(graph, park.id, alice.id)
print(f"Place: {place.extent.name}")
print(f"Familiarity: {place.familiarity_score:.2f}")
print(f"Encounters: {place.encounter_count}")
```

## Next Steps

- [Core Concepts](core_concepts.md) — Understanding domain objects
- [Derivation Operators](derivation.md) — Transforming data
- [Examples](../examples/) — Full working examples
