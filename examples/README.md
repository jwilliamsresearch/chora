# Chora Examples

Working examples demonstrating all library functionality.

## Quick Start

```bash
# Activate virtual environment
source .venv/bin/activate

# Run any example
python examples/basic_walk.py
```

## Simulations

| Example | Description |
|---------|-------------|
| `basic_walk.py` | Single agent, 5 visits, place emergence |
| `urban_mobility.py` | Multi-agent commuting, practice detection |
| `affective_mapping.py` | Emotional qualities of places |
| `familiarity_dynamics.py` | Growth, decay, and recovery |

## Real Data Loading

| Example | Description |
|---------|-------------|
| `load_gpx_traces.py` | Parse GPX files, detect stops |
| `load_geojson_pois.py` | Load OSM/Overture GeoJSON POIs |
| `server_demo.py` | **Phase 2**: Run the Chora API Server and simulate client requests. |
| `vector_search.py` | **Phase 2**: Semantic search for places using "vibe" (Embeddings). |
| `place_diary.py` | Experience sampling/diary CSV data |

## Queries & Utilities

| Example | Description |
|---------|-------------|
| `graph_queries.py` | Fluent query builder, traversal |
| `temporal_queries.py` | Snapshots, time ranges |
| `practice_detection.py` | Routine/habit identification |
| `graph_export.py` | Export to GeoJSON, GraphML, D3.js |
