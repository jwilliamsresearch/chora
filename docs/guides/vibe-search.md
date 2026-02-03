# Semantic "Vibe" Search

Find places by their qualitative "vibe" rather than keywords or coordinates.

---

## What is Vibe Search?

Traditional search finds "coffee" or "gym". **Vibe search** uses vector embeddings to understand the semantic meaning of places.

It finds places that *feel* like your query, even if they don't contain the exact words.

- "Quiet place to read" -> matches **Parks, Libraries, Cozy Cafes**
- "Late night bonding" -> matches **Pubs, 24/7 Diners, Rooftops**

---

## How It Works

1. **Embed**: Convert text (place names, hints, descriptions) into a vector.
2. **Index**: Store place vectors.
3. **Query**: Convert user query into a vector.
4. **Compare**: Find nearest neighbors using cosine similarity.

---

## Step 1: Build the Index

You need `sentence-transformers` installed.

```python
from chora.core import PlatialGraph
from chora.search import build_place_index, PlaceIndex

# Load your populated graph
graph = PlatialGraph.load("my_city.json")

# Build index (computes embeddings for all places)
# Uses 'all-MiniLM-L6-v2' by default (small & fast)
index = build_place_index(graph)

# Save for later
index.save("place_index.json")
```

---

## Step 2: Search by Vibe

```python
from chora.search import vibe_search

# Load index if needed
# index = PlaceIndex.load("place_index.json")

# 1. Productive vibe
results = vibe_search(
    graph, 
    "place to get deep work done with coffee",
    index=index
)

for extent, score in results[:3]:
    print(f"{score:.2f} | {extent.name} ({extent.extent_type})")
# 0.82 | Third Space Library (public)
# 0.79 | Ozone Roasters (cafe)
# 0.65 | WeWork Lobby (coworking)

# 2. Romantic vibe
results = vibe_search(
    graph,
    "romantic evening spot with a view",
    index=index
)
# 0.85 | Sky Garden (viewpoint)
# 0.78 | Southbank Walk (path)
```

---

## Step 3: Find Similar Places (Recommendation)

"If you like *The Book Club*, you might like..."

```python
from chora.search import find_similar_places

# Get reference place
book_club = graph.get_node_by_name("The Book Club")

# Find lookalikes
recommendations = find_similar_places(
    graph,
    reference_extent=book_club,
    top_k=3
)
```

---

## Advanced: Custom Embeddings

You can enrich the embeddings by including more context:

```python
from chora.search import embed_extent

# Custom embedding that prioritizes "activities"
embedding = embed_extent(
    place, 
    graph, 
    include_encounters=True,  # Include "visited 50 times"
    model_name="all-mpnet-base-v2"  # Larger, more accurate model
)
```

---

## CLI Usage

Currently available as a library function. CLI integration coming in v0.9.5.

```python
# Quick script
from chora.cli import get_graph
from chora.search import vibe_search

graph = get_graph()
print(vibe_search(graph, "cozy spot"))
```

---

## Next Steps

- [H3 Indexing](h3-indexing.md) — Combine semantic search with spatial search
- [LLM Integration](llm-integration.md) — Generate descriptions for results
