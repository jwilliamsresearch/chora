# H3 Spatial Indexing

Use hexagonal grids for multi-resolution place analysis.

---

## What is H3?

[H3](https://h3geo.org/) is Uber's hexagonal hierarchical spatial index. Unlike traditional grids, hexagons provide:

- **Equal distance** to all neighbors (no diagonal bias)
- **Hierarchical resolution** (0-15, where 0 is ~1107km, 15 is ~0.5m)
- **Compact representation** of arbitrary shapes

---

## Resolution Guide

| Resolution | Edge Length | Use Case |
|------------|-------------|----------|
| 0 | ~1107 km | Continental |
| 3 | ~59 km | Metropolitan area |
| 6 | ~3 km | Neighborhood |
| 9 | ~174 m | Building cluster |
| 10 | ~65 m | Building |
| 12 | ~9 m | Room |
| 15 | ~0.5 m | Very precise |

---

## Basic Usage

### Create H3 Extent from Point

```python
from chora.core.h3 import H3SpatialExtent

# Create at resolution 9 (~174m)
hex_extent = H3SpatialExtent.from_point_h3(
    lon=-0.1276,
    lat=51.5074,
    resolution=9,
    name="London Center"
)

print(f"H3 Index: {hex_extent.h3_index}")
print(f"Resolution: {hex_extent.resolution}")
print(f"Centroid: {hex_extent.centroid}")
```

### Convert Existing Extent to H3

```python
from chora.core.h3 import extent_to_h3, h3_to_extent
from chora.core import SpatialExtent

# Regular extent
park = SpatialExtent.from_bounds(-0.1, 51.5, -0.09, 51.51, name="Park")

# Get covering H3 cells
cells = extent_to_h3(park, resolution=10)
print(f"Park covers {len(cells)} hexagons")

# Convert back
for cell in cells[:3]:
    hex_ext = h3_to_extent(cell)
    print(f"  {cell[:8]}... ({hex_ext.centroid})")
```

---

## Spatial Queries

### Neighbors

```python
# Get immediate neighbors (ring 1)
neighbors = hex_extent.neighbors
print(f"6 neighbors: {len(neighbors)}")

# Get k-ring (all cells within k hops)
k_ring = hex_extent.k_ring(k=2)
print(f"Cells within 2 rings: {len(k_ring)}")  # 19 cells
```

### Hierarchy

```python
# Go up a resolution level
parent = hex_extent.parent
print(f"Parent (res {hex_extent.resolution - 1}): {parent[:8]}...")

# Go down a resolution level  
children = hex_extent.children
print(f"Children (res {hex_extent.resolution + 1}): {len(children)} cells")
```

### Distance

```python
other = H3SpatialExtent.from_point_h3(-0.1, 51.5, resolution=9)
distance = hex_extent.distance_to_h3(other)
print(f"Grid distance: {distance} cells")
```

---

## Multi-Resolution Analysis

Analyze the same area at different resolutions:

```python
from chora.core.h3 import point_to_h3, H3_RESOLUTION_GUIDE

lon, lat = -0.1276, 51.5074

for res in [6, 9, 12]:
    cell = point_to_h3(lon, lat, res)
    desc = H3_RESOLUTION_GUIDE.get(res, "")
    print(f"Resolution {res}: {cell[:12]}... ({desc})")
```

**Output:**
```
Resolution 6: 861203a4ff... (~3 km edge, neighborhood)
Resolution 9: 891203a4c1... (~174 m edge, building cluster)
Resolution 12: 8c1203a4c1... (~9 m edge, room)
```

---

## Scale-Based Resolution

```python
from chora.core.h3 import resolution_for_scale

# Get appropriate resolution for your scale
city_res = resolution_for_scale("city")         # 4
neighborhood_res = resolution_for_scale("neighborhood")  # 6
building_res = resolution_for_scale("building")      # 10

print(f"City analysis: resolution {city_res}")
print(f"Neighborhood: resolution {neighborhood_res}")
print(f"Building level: resolution {building_res}")
```

---

## Compact Representation

Efficiently represent large areas:

```python
from chora.core.h3 import compact_h3_cells, uncompact_h3_cells

# Lots of small cells
cells = hex_extent.k_ring(k=5)
print(f"Original: {len(cells)} cells")

# Compact to minimal representation
compacted = compact_h3_cells(cells)
print(f"Compacted: {len(compacted)} cells")

# Expand back to original resolution
expanded = uncompact_h3_cells(compacted, hex_extent.resolution)
print(f"Expanded: {len(expanded)} cells")
```

---

## Complete Example

```python
"""H3 spatial indexing for place analysis."""
from chora.core import PlatialGraph, Agent
from chora.core.h3 import (
    H3SpatialExtent, 
    extent_to_h3, 
    resolution_for_scale
)

def analyze_area_at_scales(lon: float, lat: float, name: str = "Location"):
    """Multi-resolution analysis of a location."""
    
    graph = PlatialGraph(name=f"{name}_analysis")
    
    scales = ["neighborhood", "block", "building"]
    
    for scale in scales:
        res = resolution_for_scale(scale)
        hex_ext = H3SpatialExtent.from_point_h3(lon, lat, resolution=res, name=f"{name}_{scale}")
        graph.add_node(hex_ext)
        
        print(f"\n{scale.upper()} (resolution {res}):")
        print(f"  H3: {hex_ext.h3_index}")
        print(f"  Neighbors: {len(hex_ext.neighbors)}")
        print(f"  K-ring(2): {len(hex_ext.k_ring(2))} cells")
    
    return graph

# Analyze central London
graph = analyze_area_at_scales(-0.1276, 51.5074, "Westminster")
```

---

## Installation

H3 requires the `h3` Python package:

```bash
pip install h3
```

---

## Next Steps

- [GPS to Places](gps-to-places.md) — Process GPS into H3 cells
- [Vibe Search](vibe-search.md) — Search H3 cells by semantic content
- [Streaming](streaming.md) — Real-time H3 cell tracking
