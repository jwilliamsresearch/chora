# Derivation Operators

Derivation operators transform raw data into platial structures. They embody platial theory, not ad-hoc heuristics.

## Encounter Extraction

Extract encounters from GPS traces:

```python
from chora.derive import extract_encounters, TracePoint, EncounterExtractionConfig
from datetime import datetime

# GPS trace data
trace = [
    TracePoint(datetime(2024, 1, 1, 10, 0), -0.127, 51.507),
    TracePoint(datetime(2024, 1, 1, 10, 15), -0.127, 51.507),
    TracePoint(datetime(2024, 1, 1, 10, 30), -0.127, 51.507),
    TracePoint(datetime(2024, 1, 1, 11, 0), -0.130, 51.510),
]

# Extract encounters at predefined extents
encounters = extract_encounters(trace, agent_id, extents)

# Or cluster without predefined extents
from chora.derive import extract_encounters_from_trace
encounters = extract_encounters_from_trace(trace, agent_id)
```

## Familiarity Updates

Update familiarity based on encounters:

```python
from chora.derive import update_familiarity, compute_familiarity_trajectory

# Update from single encounter
familiarity = update_familiarity(graph, encounter)
print(f"New familiarity: {familiarity.value:.2f}")

# Compute trajectory over time
trajectory = compute_familiarity_trajectory(
    encounters, agent_id, extent_id,
    decay_half_life_days=14.0
)
for timestamp, value in trajectory:
    print(f"{timestamp}: {value:.2f}")

# Apply decay to all familiarities
from chora.derive import decay_all_familiarities
count = decay_all_familiarities(graph)
```

## Practice Detection

Detect routines and patterns:

```python
from chora.derive import detect_practices, detect_routines, PracticeDetectionConfig

config = PracticeDetectionConfig(
    min_occurrences=3,
    time_window_days=30,
    min_regularity=0.5
)

practices = detect_practices(encounters, agent_id, config)

for practice in practices:
    print(f"{practice.name}: regularity={practice.regularity:.2f}")
```

## Liminality Inference

Detect liminal zones from transitions:

```python
from chora.derive import infer_liminality, detect_boundary_crossings

liminal_zones = infer_liminality(encounters, extents)

for zone in liminal_zones:
    print(f"{zone.transitional_from} → {zone.transitional_to}")
    print(f"  Intensity: {zone.intensity:.2f}")
```

## Affect Derivation

Attach affect from context:

```python
from chora.derive import attach_affect, derive_affect_from_context

# Explicit attachment
affect = attach_affect(encounter, valence=0.7, arousal=0.3, source="survey")

# Derive from context
affect = derive_affect_from_context(encounter, contexts)
print(f"Derived valence: {affect.valence:.2f}")
```

## Meaning Derivation

Derive meanings from practices:

```python
from chora.derive import attach_meaning, derive_meaning_from_practices

# Explicit attachment
meaning = attach_meaning(
    agent_id, extent_id,
    content="My daily exercise spot",
    symbols=["health", "routine"]
)

# Derive from practice patterns
meanings = derive_meaning_from_practices(practices, agent_id, extent_id)
```

## Place Emergence

Extract emergent place as subgraph:

```python
from chora.derive import extract_place, find_emergent_places

# Single place for agent-extent pair
place = extract_place(graph, extent_id, agent_id)
print(f"Familiarity: {place.familiarity_score:.2f}")
print(f"Character: {place.character}")
print(f"Encounter count: {place.encounter_count}")

# Find all significant places
places = find_emergent_places(graph, agent_id, min_encounters=3)
for p in places:
    print(f"{p.extent.name}: {p.character}")
```
