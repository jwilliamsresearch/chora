# Query Interface

Chora provides a fluent query interface for finding and analysing places.

## Fluent Query Builder

```python
from chora.query import PlatialQuery

# Find familiar, positive places
places = (PlatialQuery(graph)
    .for_agent(alice.id)
    .with_familiarity(min_value=0.5)
    .with_positive_affect()
    .execute())

for place in places:
    print(f"{place.extent.name}: {place.character}")
```

## Convenience Functions

```python
from chora.query import (
    find_familiar_places,
    find_positive_places,
    find_routine_places,
    query_encounters
)

# Familiar places
familiar = find_familiar_places(graph, alice.id, min_familiarity=0.5)

# Positive places
positive = find_positive_places(graph, alice.id)

# Routine places (high encounter count)
routines = find_routine_places(graph, alice.id, min_encounters=10)

# Query encounters with filters
for enc in query_encounters(graph, agent_id=alice.id, extent_id=park.id):
    print(f"{enc.start_time}: {enc.activity}")
```

## Pattern Matching

```python
from chora.query import find_practices_like, match_pattern

# Find practices similar to a template
similar = find_practices_like(graph, template_practice, min_similarity=0.7)

# Match named patterns
morning_routines = match_pattern(graph, "morning_routine")
avoidances = match_pattern(graph, "avoidance")
explorations = match_pattern(graph, "exploration")
```

## Similarity Measures

```python
from chora.query import place_similarity, practice_similarity

# Compare two places
sim = place_similarity(place_a, place_b)
print(f"Similarity: {sim:.2f}")

# Compare practices
sim = practice_similarity(routine_a, routine_b)
```

## Graph Traversal

```python
from chora.query import traverse_from, find_connected, find_path
from chora.core import EdgeType

# BFS from a node
for node, depth in traverse_from(graph, start_id, max_depth=3):
    print(f"Depth {depth}: {node}")

# Find connected nodes
connected = find_connected(graph, encounter_id, 
                          edge_types=[EdgeType.HAS_CONTEXT])

# Find path between nodes
path = find_path(graph, start_id, end_id)
if path:
    print(" → ".join(str(n) for n in path))
```

## Temporal Queries

```python
from chora.query import snapshot_query, temporal_range_query
from datetime import datetime, timedelta

# Snapshot at a point in time
past = datetime.now() - timedelta(days=30)
snapshot = snapshot_query(graph, at=past)
print(f"Nodes at {past}: {snapshot.node_count}")

# Nodes active during a range
start = datetime(2024, 1, 1)
end = datetime(2024, 6, 30)
for node in temporal_range_query(graph, start, end):
    print(node)
```
