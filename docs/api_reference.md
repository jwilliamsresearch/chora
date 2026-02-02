# API Reference

Complete reference for the Chora library.

## Core Module (`chora.core`)

### Domain Objects

#### `Agent`
Entities that participate in encounters.
```python
agent = Agent.individual(name="Alice", age=30)
```
- **Attributes**: `id`, `name`, `properties`, `validity`.
- **Methods**: `individual()`, `group()`.

#### `SpatialExtent`
The physical support for an encounter (geometry + basic semantics).
```python
park = SpatialExtent.from_bounds(-0.1, 51.5, -0.09, 51.51, name="Hyde Park")
```
- **Attributes**: `geometry` (Shapely), `properties`.

#### `Encounter`
The atomic unit of place-making.
```python
enc = Encounter(agent_id=..., extent_id=..., start_time=..., end_time=...)
```
- **Attributes**: `duration`, `activity`.

#### `Practice`
Repeated patterns of behavior.
- **Type**: `PracticeType` (ROUTINE, HABIT, RITUAL).

#### `Affect` / `Meaning`
- **Affect**: Valence/Arousal values attached to encounters.
- **Meaning**: Symbolic labels (e.g., "Home", "Danger").

### Graph Infrastructure

#### `PlatialGraph`
The container for all platial knowledge.
```python
graph = PlatialGraph(name="My City")
graph.add_node(agent)
graph.add_edge(PlatialEdge.participates_in(agent.id, enc.id))
```

---

## Derivation Module (`chora.derive`)

Operators that transform data into higher-level platial constructs.

### `update_familiarity(graph, encounter)`
Updates the `Familiarity` node for an agent/extent pair.
- Applies `exponential_decay` to previous value.
- Applies reinforcement from new encounter.

### `extract_place(graph, extent_id, agent_id)`
Computes an `EmergentPlace` view.
- NOT a node in the graph.
- A dynamically computed structure summarizing all history between an agent and an extent.
- **Returns**: `EmergentPlace` object with `character`, `familiarity_score`.

### `detect_practices(graph, agent_id)`
Scans agent history for repeating temporal/spatial motifs.
- **Returns**: List of `Practice` nodes added to the graph.

---

## Query Module (`chora.query`)

Fluent interface for asking questions.

### `PlatialQuery`
```python
results = (
    PlatialQuery(graph)
    .for_agent(alice_id)
    .where(familiarity__gt=0.5)
    .at_time(datetime.now())
    .execute()
)
```

### Convenience Functions
- `find_familiar_places(graph, agent_id)`
- `find_positive_places(graph, agent_id)`
- `find_shared_places([agent_ids...])`

---

## Adapters (`chora.adapters`)

Data persistence layers.

### `InMemoryAdapter`
Default reference implementation. Fast, transient.

### `Neo4jAdapter`
Connects to Neo4j database.
```python
adapter = Neo4jAdapter(uri="bolt://localhost:7687", auth=(user, pass))
adapter.save_graph(graph)
```

### `PostGISAdapter`
Connects to PostgreSQL/PostGIS (Stub).

---

## Server Module (`chora.server`)

### `create_app()`
FastAPI application factory. Configures lifespan events and middleware.

### Endpoints
- **POST** `/agents/`: Create new agent.
- **POST** `/encounters/`: Log space-time interaction.
- **GET** `/places/{agent}/{extent}`: Derive place familiarity.
- **WS** `/ws/stream`: Real-time event stream.
- **POST** `/vectors/embed`: Get text embeddings (Real).

---

## Embeddings Module (`chora.embeddings`)

### `get_embedding_model()`
Returns the singleton `LocalEmbedder` (uses `sentence-transformers`).

### `Embedder` (Protocol)
- `embed_text(text: str) -> List[float]`
