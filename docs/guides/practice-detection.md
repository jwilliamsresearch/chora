# Detecting Routines & Practices

Identify habits, routines, and rituals from mobility patterns.

---

## What Are Practices?

**Practices** in Chora are recurring patterns of behavior that emerge from temporal regularities in encounters:

| Type | Definition | Example |
|------|------------|---------|
| **Routine** | High-frequency, predictable patterns | Daily commute |
| **Habit** | Consistent behavior at certain times | Morning coffee run |
| **Ritual** | Less frequent but meaningful patterns | Sunday park visit |
| **Sequence** | Linked place transitions | Home → Gym → Work |

---

## Step 1: Prepare Encounter Data

```python
from chora.core import PlatialGraph, Agent, SpatialExtent, Encounter, PlatialEdge
from datetime import datetime, timedelta

graph = PlatialGraph(name="my_patterns")
alice = Agent.individual("alice")
graph.add_node(alice)

# Create places
home = SpatialExtent.from_point(-0.1, 51.5, name="Home")
work = SpatialExtent.from_point(-0.08, 51.52, name="Office")
coffee = SpatialExtent.from_point(-0.079, 51.518, name="Coffee Shop")
gym = SpatialExtent.from_point(-0.09, 51.51, name="Gym")

for place in [home, work, coffee, gym]:
    graph.add_node(place)

# Simulate 2 weeks of encounters
base_date = datetime(2024, 1, 1)

for day in range(14):
    date = base_date + timedelta(days=day)
    weekday = date.weekday()
    
    # Daily: Home morning
    enc = Encounter(agent_id=alice.id, extent_id=home.id, 
                    start_time=date.replace(hour=7), activity="morning")
    graph.add_node(enc)
    
    # Weekdays: Coffee → Work
    if weekday < 5:
        enc = Encounter(agent_id=alice.id, extent_id=coffee.id,
                        start_time=date.replace(hour=8), activity="coffee")
        graph.add_node(enc)
        
        enc = Encounter(agent_id=alice.id, extent_id=work.id,
                        start_time=date.replace(hour=9), activity="work")
        graph.add_node(enc)
    
    # MWF: Gym after work
    if weekday in [0, 2, 4]:
        enc = Encounter(agent_id=alice.id, extent_id=gym.id,
                        start_time=date.replace(hour=18), activity="exercise")
        graph.add_node(enc)
```

---

## Step 2: Detect Practices

```python
from chora.derive.practices import detect_practices, PracticeDetectionConfig
from chora.core.types import NodeType

# Gather all encounters for the agent
encounters = [
    node for node in graph.nodes(NodeType.ENCOUNTER)
    if hasattr(node, 'agent_id') and str(node.agent_id) == str(alice.id)
]

# Configure detection
config = PracticeDetectionConfig(
    min_occurrences=3,          # At least 3 times
    time_tolerance_hours=2,     # Within 2 hours counts as same time
    min_regularity=0.5          # 50% of opportunities
)

# Detect
practices = detect_practices(encounters, alice.id, config)

for practice in practices:
    print(f"📅 {practice.name}")
    print(f"   Type: {practice.practice_type}")
    print(f"   Regularity: {practice.regularity:.0%}")
    print(f"   Occurrences: {practice.occurrence_count}")
    print()
```

**Output:**
```
📅 morning_routine
   Type: ROUTINE
   Regularity: 100%
   Occurrences: 14

📅 weekday_coffee
   Type: HABIT  
   Regularity: 100%
   Occurrences: 10

📅 gym_session
   Type: HABIT
   Regularity: 43%
   Occurrences: 6
```

---

## Step 3: Detect Sequences

Find common place-to-place transitions:

```python
from chora.derive.practices import detect_sequences

sequences = detect_sequences(encounters, min_support=3)

for seq in sequences:
    places = " → ".join(seq.place_names)
    print(f"🔗 {places}")
    print(f"   Support: {seq.support}")
    print()
```

**Output:**
```
🔗 Home → Coffee Shop → Office
   Support: 10

🔗 Office → Gym → Home
   Support: 6
```

---

## Step 4: Analyze Temporal Patterns

```python
from chora.derive.practices import analyze_temporal_distribution

# When does alice visit the gym?
gym_encounters = [e for e in encounters if str(e.extent_id) == str(gym.id)]
distribution = analyze_temporal_distribution(gym_encounters)

print("Gym visit patterns:")
print(f"  Typical day: {distribution.most_common_day}")
print(f"  Typical hour: {distribution.most_common_hour}")
print(f"  Day distribution: {distribution.day_counts}")
```

**Output:**
```
Gym visit patterns:
  Typical day: Monday
  Typical hour: 18
  Day distribution: {0: 2, 2: 2, 4: 2}  # Mon, Wed, Fri
```

---

## CLI Usage

```bash
# Detect practices for an agent
chora derive practices --agent alice --min-occurrences 3

# Output
# Found 3 practices:
#   morning_routine (ROUTINE): 100% regularity
#   weekday_coffee (HABIT): 100% regularity  
#   gym_session (HABIT): 43% regularity
```

---

## Complete Example

```python
"""Practice detection from GPS data."""
from chora.core import PlatialGraph, Agent
from chora.derive.practices import detect_practices, PracticeDetectionConfig
from chora.core.types import NodeType

def analyze_routines(graph: PlatialGraph, agent_name: str):
    """Analyze all routines for an agent."""
    
    # Get agent
    agents = [n for n in graph.nodes(NodeType.AGENT) if n.name == agent_name]
    if not agents:
        return []
    agent = agents[0]
    
    # Get encounters
    encounters = [
        n for n in graph.nodes(NodeType.ENCOUNTER)
        if hasattr(n, 'agent_id') and str(n.agent_id) == str(agent.id)
    ]
    
    if len(encounters) < 3:
        print(f"Not enough encounters ({len(encounters)}) to detect patterns")
        return []
    
    # Detect practices
    config = PracticeDetectionConfig(min_occurrences=3)
    practices = detect_practices(encounters, agent.id, config)
    
    # Categorize
    routines = [p for p in practices if p.practice_type.name == "ROUTINE"]
    habits = [p for p in practices if p.practice_type.name == "HABIT"]
    rituals = [p for p in practices if p.practice_type.name == "RITUAL"]
    
    print(f"\n📊 Analysis for {agent_name}")
    print(f"   Total encounters: {len(encounters)}")
    print(f"   Routines: {len(routines)}")
    print(f"   Habits: {len(habits)}")
    print(f"   Rituals: {len(rituals)}")
    
    return practices

# Usage
practices = analyze_routines(graph, "alice")
```

---

## Next Steps

- [GPS to Places](gps-to-places.md) — Process location data first
- [Affective Mapping](affective-mapping.md) — Add emotional context to routines
- [Visualization](visualization.md) — Visualize temporal patterns
