# GPS to Places

Turn raw GPS traces into meaningful places with familiarity scores.

---

## Overview

Most location data comes as timestamped coordinates—GPS traces from phones, fitness trackers, or vehicle telemetry. Chora transforms these raw points into **meaningful places** by detecting where people dwell, building familiarity over repeated visits, and creating a graph of platial relationships.

```mermaid
graph LR
    A[GPS Points] --> B[Encounters]
    B --> C[Dwell Detection]
    C --> D[Spatial Extents]
    D --> E[Familiarity Scores]
    E --> F[Emergent Places]
```

---

## Step 1: Load GPS Data

### From GPX Files

```python
import gpxpy
from chora.core import PlatialGraph, Agent, SpatialExtent, Encounter, PlatialEdge
from datetime import datetime

# Create graph and agent
graph = PlatialGraph(name="my_walks")
alice = Agent.individual("alice")
graph.add_node(alice)

# Parse GPX
with open("morning_walk.gpx") as f:
    gpx = gpxpy.parse(f)

for track in gpx.tracks:
    for segment in track.segments:
        for point in segment.points:
            # Create spatial extent for this point
            extent = SpatialExtent.from_point(
                lon=point.longitude,
                lat=point.latitude,
                name=f"pt_{point.time.isoformat()}"
            )
            graph.add_node(extent)
            
            # Create encounter
            encounter = Encounter(
                agent_id=alice.id,
                extent_id=extent.id,
                start_time=point.time,
                activity="walking"
            )
            graph.add_node(encounter)
            
            # Link agent → encounter → extent
            graph.add_edge(PlatialEdge.participates_in(alice.id, encounter.id))
            graph.add_edge(PlatialEdge.occurs_at(encounter.id, extent.id))
```

### Using the CLI

```bash
chora load gpx morning_walk.gpx --agent alice --activity walking
```

---

## Step 2: Cluster Into Dwells

Raw GPS points are noisy. We need to cluster nearby points into **dwells**—locations where someone stayed for a meaningful duration.

```python
from chora.streaming import StreamProcessor, StreamConfig, LocationEvent

# Configure dwell detection
config = StreamConfig(
    dwell_radius_m=50.0,     # Points within 50m are same place
    dwell_time_s=60.0,       # 60 seconds to trigger a dwell
    min_dwell_for_encounter=120.0  # 2 min to create encounter
)

processor = StreamProcessor(graph, config)

# Process locations
for point in gps_points:
    event = LocationEvent(
        agent_id="alice",
        longitude=point.lon,
        latitude=point.lat,
        timestamp=point.time
    )
    events = processor.process(event)
    
    for e in events:
        if e.event_type == "encounter":
            print(f"Dwell detected at {e.data['location']}")
```

---

## Step 3: Derive Familiarity

Familiarity grows with repeated visits and decays over time without reinforcement.

```python
from chora.derive import update_familiarity
from chora.core.types import NodeType

# Update familiarity for all encounters
for encounter in graph.nodes(NodeType.ENCOUNTER):
    update_familiarity(graph, encounter)

# Check familiarity scores
from chora.query import find_familiar_places, AgentId

familiar = find_familiar_places(
    graph, 
    AgentId(str(alice.id)), 
    min_familiarity=0.5
)

for place in familiar:
    print(f"{place.extent.name}: {place.familiarity:.2f}")
```

**Output:**
```
home: 0.95
coffee_shop: 0.72
park: 0.58
```

---

## Step 4: Extract Emergent Places

Places emerge from patterns of encounters—they're not predefined, they're discovered.

```python
from chora.derive.place import extract_place

# Extract place for a spatial extent based on alice's encounters
place = extract_place(graph, extent_id=park.id, agent_id=alice.id)

print(f"Place: {place.name}")
print(f"Visit count: {place.encounter_count}")
print(f"Familiarity: {place.familiarity}")
print(f"Character: {place.semantic_hints}")
```

---

## Complete Example

```python
"""Full GPS-to-Places pipeline."""
from chora.core import PlatialGraph, Agent, SpatialExtent, Encounter, PlatialEdge
from chora.derive import update_familiarity
from chora.query import find_familiar_places
from chora.streaming import create_processor
import gpxpy

def process_gpx(gpx_path: str, agent_name: str = "user"):
    # Setup
    graph = PlatialGraph(name="locations")
    agent = Agent.individual(agent_name)
    graph.add_node(agent)
    
    # Create streaming processor for dwell detection
    processor = create_processor(
        graph,
        dwell_radius=50.0,  # meters
        dwell_time=60.0     # seconds
    )
    
    # Load and process GPS
    with open(gpx_path) as f:
        gpx = gpxpy.parse(f)
    
    for track in gpx.tracks:
        for segment in track.segments:
            for point in segment.points:
                from chora.streaming import LocationEvent
                
                event = LocationEvent(
                    agent_id=agent_name,
                    longitude=point.longitude,
                    latitude=point.latitude,
                    timestamp=point.time
                )
                processor.process(event)
    
    # Derive familiarity
    from chora.core.types import NodeType
    for enc in graph.nodes(NodeType.ENCOUNTER):
        update_familiarity(graph, enc)
    
    # Query results
    from chora.core.types import AgentId
    places = find_familiar_places(graph, AgentId(agent_name), min_familiarity=0.3)
    
    return graph, places

# Run
graph, places = process_gpx("my_track.gpx", "alice")
for p in places:
    print(f"{p.extent.name}: {p.familiarity:.2f}")
```

---

## Next Steps

- [Affective Mapping](affective-mapping.md) — Add emotional qualities
- [Practice Detection](practice-detection.md) — Find routines in your data
- [CLI Reference](../api_reference.md) — Full CLI documentation
