<div align="center">

# Chora
### The Platial Modelling Operating System

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Status: Alpha](https://img.shields.io/badge/Status-Alpha-orange)](https://github.com/jameswilliams/chora)
[![Docs](https://img.shields.io/badge/Docs-Book_of_Chora-teal)](https://jameswilliams.github.io/chora)
[![CI](https://github.com/jameswilliams/chora/actions/workflows/ci.yml/badge.svg)](https://github.com/jameswilliams/chora/actions)

**"Place is not a location."**

**Chora** is the first Python library designed to model the **human experience of place**. 
It moves beyond standard GIS (geometry + coordinates) to simulate how places *emerge* from memory, habit, and social interaction.

[Get Started](docs/getting_started.md) • [The Theory](docs/theory.md) • [API Reference](docs/api_reference.md)

</div>

---

## ✨ Why Chora?

Standard tools ask: *"What is at Lat/Lon 51.5, -0.1?"*
**Chora** asks: *"Why does this park feel like 'Home' to Alice, but 'Danger' to Bob?"*

| 🧠 Cognitive | 🕰 Temporal | 🕸 Relational |
|:---:|:---:|:---:|
| Models **Familiarity** & **Memory** decay over time. | Places **emerge** and <br> **dissolve** dynamically. | A "Place" is a graph of <br> **Encounters**, not a polygon. |

## 🛠 Features

- **Experiential Physics**: Built-in decay functions (`linear`, `exponential`) simulate how memories fade without reinforcement.
- **Emergent Places**: "Place" is not stored; it is *computed* on-the-fly from the history of interaction.
- **Practice Detection**: Algorithms to detect *Routines*, *Habits*, and *Rituals* from GPS traces.
- **Graph Native**: Built on a Property Graph model (NetworkX), exportable to **Neo4j** and **D3.js**.
- **Social**: Models multi-agent shared experiences and "intersubjective" places.

---

## ⚡ Quick Start

### Installation
```bash
pip install chora
```

### The "Hello Place" API

```python
from chora.core import PlatialGraph, Agent, SpatialExtent, Encounter, PlatialEdge
from chora.derive import update_familiarity

# 1. Create the world
graph = PlatialGraph("My World")
alice = Agent.individual("Alice")
park = SpatialExtent.from_bounds(-0.1, 51.5, -0.09, 51.51, name="Hyde Park")

# 2. Add to the graph
graph.add_node(alice)
graph.add_node(park)

# 3. Alice visits the park (An Encounter)
visit = Encounter(alice.id, park.id, start_time=..., end_time=...)
graph.add_node(visit)
graph.add_edge(PlatialEdge.participates_in(alice.id, visit.id))

# 4. Derive Familiarity
# Chora calculates Alice's familiarity based on the frequency and recency of her visits.
fam = update_familiarity(graph, visit)
print(f"Alice's familiarity with Park: {fam.value:.2f}")
# -> "Alice's familiarity with Park: 0.15"
```

---

## 📚 The Book of Chora

Our documentation is written as a progressive book:

1. **[Theory](docs/theory.md)**: Why standard GIS fails at "Place".
2. **[Getting Started](docs/getting_started.md)**: Build your first model.
3. **[Core Concepts](docs/core_concepts.md)**: Agents, Extents, and the Graph.
4. **[Derivation](docs/derivation.md)**: From GPS traces to Meaningful Places.
5. **[Querying](docs/queries.md)**: "Where feels like..." queries.

---

## 🔮 The Roadmap

We are building the **OS for Social Physics**.
- **v0.5**: H3 Indexing & Vector Search (Semantic Vibe).
- **v1.0**: React Frontend Explorer & Real-time Streams.
- **v1.5**: LLM Integration ("Genius Loci" Narrative Generation).

See the full [Strategic Roadmap](COMMIT_TO_SEE_ROADMAP).

## 🤝 Contributing

We welcome contributions from Geographers, Developers, and Philosophers.
See [CONTRIBUTING.md](CONTRIBUTING.md) to join the project.

---
<div align="center">
    <i>Built with ❤️ for the Platial Turn.</i>
</div>
