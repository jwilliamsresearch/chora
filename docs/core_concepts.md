# Core Concepts

## Domain Objects

Chora formalises nine first-class concepts:

### Agent
An entity with situated experience — human, group, or proxy.

```python
from chora.core import Agent

alice = Agent.individual("Alice", age=30)
family = Agent.group("The Smiths", members=["Alice", "Bob"])
```

### SpatialExtent
Weakly semanticised spatial support with geometry.

```python
from chora.core import SpatialExtent

# From bounds
park = SpatialExtent.from_bounds(-0.13, 51.50, -0.12, 51.51, "Hyde Park")

# Point location
cafe = SpatialExtent.point(-0.127, 51.507, "Corner Cafe")

# With semantic hints (not strong categories)
park.set_hint("land_use", "recreation")
```

### Encounter
Spatio-temporal relation between agent and extent.

```python
from chora.core import Encounter
from datetime import datetime, timedelta

encounter = Encounter(
    agent_id=alice.id,
    extent_id=park.id,
    start_time=datetime(2024, 6, 15, 10, 0),
    end_time=datetime(2024, 6, 15, 11, 30),
    activity="walking",
    intensity=0.8
)

print(f"Duration: {encounter.duration_hours:.1f} hours")
```

### Context
Situational modifiers — temporal, social, purposive, environmental.

```python
from chora.core import Context

morning = Context.temporal("morning")
with_dog = Context.social(companions=["Max the dog"])
leisure = Context.purposive("leisure walk")
sunny = Context.environmental({"weather": "sunny", "temperature": 22})
```

### Practice
Emergent patterns over encounters — routines, habits, rituals.

```python
from chora.core import Practice, PracticeType

morning_walk = Practice(
    practice_type=PracticeType.ROUTINE,
    name="Morning park walk",
    frequency=0.8,  # ~6 times per week
    regularity=0.9,
    typical_time="morning (8-12)"
)
```

### Affect
Experiential response with valence and arousal.

```python
from chora.core import Affect
from chora.core.affect import AffectState
from chora.core.uncertainty import UncertaintyValue

peaceful = Affect(
    affect_state=AffectState(
        valence=UncertaintyValue(0.7, 0.1),  # Positive
        arousal=UncertaintyValue(0.2, 0.1)   # Calm
    )
)
print(f"Quadrant: {peaceful.quadrant}")  # "calm"
```

### Familiarity
Evolving state that grows with encounters and decays with time.

```python
from chora.core import Familiarity

fam = Familiarity(
    agent_id=alice.id,
    extent_id=park.id,
    value=0.75,
    encounter_count=20
)

# Reinforce with new encounter
fam.reinforce(duration_hours=1.5)

# Check current value (with decay applied)
print(f"Current: {fam.current_value:.2f}")
```

### Liminality
Transitional quality at boundaries.

```python
from chora.core import Liminality, LiminalityType

park_entrance = Liminality.spatial_boundary(
    from_space="street",
    to_space="park",
    intensity=0.9
)
```

### Meaning
Symbolic interpretation attached to places.

```python
from chora.core import Meaning, MeaningType

childhood_home = Meaning.personal(
    agent_id=alice.id,
    extent_id=house_id,
    content="Where I learned to ride a bike",
    symbols=("childhood", "safety", "family")
)

memorial = Meaning.cultural(
    extent_id=monument_id,
    content="Site of remembrance",
    symbols=("sacrifice", "nation")
)
```

## The Platial Graph

All objects exist within a `PlatialGraph`:

```python
from chora.core import PlatialGraph, PlatialEdge, EdgeType

graph = PlatialGraph(name="Urban Mobility Study")

# Add nodes
graph.add_node(alice)
graph.add_node(park)
graph.add_node(encounter)

# Add edges
graph.add_edge(PlatialEdge.participates_in(alice.id, encounter.id))
graph.add_edge(PlatialEdge.occurs_at(encounter.id, park.id))

# Query
for node in graph.nodes(NodeType.ENCOUNTER):
    print(node)
```
