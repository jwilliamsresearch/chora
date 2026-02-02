# Visualization

Create interactive graphs, timelines, and HTML reports.

---

## D3.js Force Graph

Export your platial graph as an interactive force-directed visualization.

### Quick Export

```python
from chora.viz import export_force_graph

export_force_graph(
    graph,
    output_path="my_graph.html",
    title="My Place Network"
)
```

Opens in browser with:
- Draggable nodes
- Color-coded by type (Agent, Place, Encounter, etc.)
- Click nodes for details
- Legend and sidebar

### JSON Export for Custom D3

```python
from chora.viz import export_d3_json
import json

data = export_d3_json(graph)
# Returns: {"nodes": [...], "links": [...]}

with open("graph_data.json", "w") as f:
    json.dump(data, f, indent=2, default=str)
```

Node structure:
```json
{
  "id": "abc-123",
  "type": "SPATIAL_EXTENT",
  "name": "Coffee Shop",
  "group": 1
}
```

---

## Timeline Visualization

Create interactive timelines of encounters over time.

```python
from chora.viz import export_timeline_html

export_timeline_html(
    graph,
    agent_id=alice.id,
    output_path="alice_timeline.html",
    title="Alice's Journey"
)
```

Features:
- Chronological event display
- Place labels and durations
- Interactive filtering
- Summary statistics

---

## HTML Reports

Generate comprehensive summary reports.

```python
from chora.viz import generate_report

generate_report(
    graph,
    output_path="report.html",
    title="Platial Analysis Report"
)
```

Report includes:
- Graph statistics (nodes, edges by type)
- Agent overview
- Place inventory
- Encounter summary
- Interactive data tables

---

## CLI Usage

```bash
# Export D3 graph
chora viz export --format d3 --output graph.html

# Export as JSON
chora viz export --format json --output data.json

# Export as DOT (Graphviz)
chora viz export --format dot --output graph.dot

# Generate timeline
chora viz timeline --agent alice --output timeline.html
```

---

## Customization

### Custom Node Colors

```python
from chora.viz.d3_export import export_force_graph

# Custom color scheme
colors = {
    "AGENT": "#e74c3c",
    "SPATIAL_EXTENT": "#2ecc71", 
    "ENCOUNTER": "#f39c12",
    "FAMILIARITY": "#9b59b6",
    "AFFECT": "#1abc9c"
}

export_force_graph(
    graph, 
    "styled_graph.html",
    node_colors=colors
)
```

### Embed in Existing HTML

```python
data = export_d3_json(graph)

# Use in your own D3 code
html = f"""
<script src="https://d3js.org/d3.v7.min.js"></script>
<script>
const data = {json.dumps(data)};
// Your custom D3 visualization
</script>
"""
```

---

## Complete Example

```python
"""Full visualization workflow."""
from chora.core import PlatialGraph, Agent, SpatialExtent, Encounter, PlatialEdge
from chora.viz import export_force_graph, export_timeline_html, generate_report
from datetime import datetime, timedelta

# Create sample graph
graph = PlatialGraph(name="demo")
alice = Agent.individual("alice")
graph.add_node(alice)

places = [
    SpatialExtent.from_point(-0.1, 51.5, name="Home"),
    SpatialExtent.from_point(-0.08, 51.52, name="Work"),
    SpatialExtent.from_point(-0.09, 51.51, name="Park"),
]

for place in places:
    graph.add_node(place)

# Add encounters
base = datetime.now() - timedelta(days=7)
for i, place in enumerate(places):
    enc = Encounter(
        agent_id=alice.id,
        extent_id=place.id,
        start_time=base + timedelta(days=i),
        activity="visit"
    )
    graph.add_node(enc)
    graph.add_edge(PlatialEdge.participates_in(alice.id, enc.id))
    graph.add_edge(PlatialEdge.occurs_at(enc.id, place.id))

# Generate all visualizations
export_force_graph(graph, "output/graph.html", "Place Network")
export_timeline_html(graph, alice.id, "output/timeline.html", "Alice's Week")
generate_report(graph, "output/report.html", "Analysis Summary")

print("✓ Generated: graph.html, timeline.html, report.html")
```

---

## Next Steps

- [GPS to Places](gps-to-places.md) — Get data to visualize
- [H3 Indexing](h3-indexing.md) — Hexagonal visualizations
- [API Reference](../api_reference.md) — Full viz module docs
