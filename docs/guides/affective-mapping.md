# Affective Mapping

Map emotional qualities to places and query by "vibe".

---

## What is Affect?

**Affect** in Chora represents the emotional quality of a place experience. It uses the psychological circumplex model with two dimensions:

| Dimension | Range | Low | High |
|-----------|-------|-----|------|
| **Valence** | -1 to +1 | Negative (fear, sadness) | Positive (joy, peace) |
| **Arousal** | -1 to +1 | Calm (rest, meditation) | Excited (thrill, energy) |

```
                High Arousal (+1)
                     ↑
         Tense   │   Excited
                 │
Low Valence ─────┼───── High Valence
(-1)             │            (+1)
         Sad    │   Content
                 ↓
               Low Arousal (-1)
```

---

## Step 1: Create Affect Nodes

```python
from chora.core import PlatialGraph, SpatialExtent, Affect

# Create graph with places
graph = PlatialGraph(name="city_feels")

# A peaceful park (positive, calm)
park = SpatialExtent.from_bounds(-0.1, 51.5, -0.09, 51.51, name="Quiet Park")
graph.add_node(park)

park_affect = Affect(
    extent_id=park.id,
    valence=0.8,   # Very positive
    arousal=-0.3,  # Calm
    labels=["peaceful", "restorative", "nature"]
)
graph.add_node(park_affect)

# A busy market (positive, energetic)
market = SpatialExtent.from_bounds(-0.08, 51.52, -0.07, 51.53, name="Borough Market")
graph.add_node(market)

market_affect = Affect(
    extent_id=market.id,
    valence=0.6,   # Positive
    arousal=0.7,   # Energetic
    labels=["vibrant", "social", "exciting"]
)
graph.add_node(market_affect)

# A dark alley (negative, tense)
alley = SpatialExtent.from_point(-0.085, 51.515, name="Dark Alley")
graph.add_node(alley)

alley_affect = Affect(
    extent_id=alley.id,
    valence=-0.6,  # Negative
    arousal=0.4,   # Tense
    labels=["unsafe", "avoid", "uncomfortable"]
)
graph.add_node(alley_affect)
```

---

## Step 2: Query by Affect

### Find Positive Places

```python
from chora.query import PlatialQuery

# Find all places with positive affect (valence > 0.5)
query = PlatialQuery(graph)
happy_places = query.filter_extent_by_affect(
    min_valence=0.5
).execute()

for place in happy_places:
    print(f"✓ {place.name}")
# ✓ Quiet Park
# ✓ Borough Market
```

### Find Calm Places

```python
# Find relaxing spots (low arousal, positive valence)
calm_places = query.filter_extent_by_affect(
    min_valence=0.3,
    max_arousal=0.0
).execute()

for place in calm_places:
    print(f"😌 {place.name}")
# 😌 Quiet Park
```

### Avoid Negative Places

```python
# Find places to avoid
avoid = query.filter_extent_by_affect(
    max_valence=-0.3
).execute()

for place in avoid:
    print(f"⚠️ {place.name}")
# ⚠️ Dark Alley
```

---

## Step 3: Vibe Search with Embeddings

Go beyond simple filters—search places by semantic description.

```python
from chora.search import vibe_search, build_place_index

# Build the search index (requires sentence-transformers)
index = build_place_index(graph)

# Search by vibe description
results = vibe_search(
    graph,
    query="quiet peaceful place for reading and relaxation",
    top_k=3,
    index=index
)

for extent, similarity in results:
    print(f"{extent.name}: {similarity:.2f}")
# Quiet Park: 0.87
# Borough Market: 0.31
# Dark Alley: 0.12
```

### More Vibe Queries

```python
# Find energetic social spots
lively = vibe_search(graph, "busy exciting place with lots of people")
# Borough Market: 0.82

# Find cozy refuge
cozy = vibe_search(graph, "cozy safe comfortable shelter")
# Quiet Park: 0.71
```

---

## Step 4: Aggregate Affect Over Time

Place affect can change based on experiences over time:

```python
from chora.derive.affect import aggregate_affect
from chora.core.types import NodeType

# Collect all affect annotations for a place
affects = [
    node for node in graph.nodes(NodeType.AFFECT)
    if str(node.extent_id) == str(park.id)
]

# Aggregate with recency weighting
overall = aggregate_affect(affects, decay_rate=0.1)

print(f"Park's current vibe:")
print(f"  Valence: {overall.valence:.2f}")
print(f"  Arousal: {overall.arousal:.2f}")
print(f"  Confidence: {overall.confidence:.2f}")
```

---

## Complete Example

```python
"""Affective mapping workflow."""
from chora.core import PlatialGraph, Agent, SpatialExtent, Encounter, Affect, PlatialEdge
from chora.search import vibe_search

def create_affective_map():
    graph = PlatialGraph(name="emotional_city")
    me = Agent.individual("me")
    graph.add_node(me)
    
    # Define places with affect
    places = [
        {"name": "Home", "lon": -0.1, "lat": 51.5, "valence": 0.9, "arousal": -0.4, "labels": ["safe", "comfort"]},
        {"name": "Office", "lon": -0.08, "lat": 51.52, "valence": 0.2, "arousal": 0.5, "labels": ["stress", "focus"]},
        {"name": "Gym", "lon": -0.09, "lat": 51.51, "valence": 0.7, "arousal": 0.8, "labels": ["energy", "strength"]},
        {"name": "Library", "lon": -0.11, "lat": 51.49, "valence": 0.6, "arousal": -0.5, "labels": ["quiet", "focus"]},
        {"name": "Pub", "lon": -0.085, "lat": 51.515, "valence": 0.8, "arousal": 0.6, "labels": ["social", "fun"]},
    ]
    
    for p in places:
        extent = SpatialExtent.from_point(p["lon"], p["lat"], name=p["name"])
        graph.add_node(extent)
        
        affect = Affect(
            extent_id=extent.id,
            valence=p["valence"],
            arousal=p["arousal"],
            labels=p["labels"]
        )
        graph.add_node(affect)
    
    return graph

# Create and query
graph = create_affective_map()

# Find a place to unwind after work
results = vibe_search(graph, "relaxing place to decompress after stressful day")
print("Best places to unwind:")
for extent, score in results[:3]:
    print(f"  {extent.name}: {score:.2f}")
```

---

## Next Steps

- [GPS to Places](gps-to-places.md) — Process real location data
- [Practice Detection](practice-detection.md) — Find patterns in behavior
- [LLM Narratives](llm-integration.md) — Generate place descriptions
