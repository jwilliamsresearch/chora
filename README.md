# Chora: Platial Modelling Library

> **"Place is not a location."**

**Chora** is a Python library for modelling the human experience of place. It moves beyond standard GIS (which handles geometry and location) to handle *platial* concepts: familiarity, affect, routine, meaning, and emergence.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Status: Alpha](https://img.shields.io/badge/Status-Alpha-orange)](https://github.com/jameswilliams/chora)

---

## 📚 The Book of Chora

Documentation is organised as a progressive guide to platial modelling.

| Chapter | Description |
|---------|-------------|
| **1. [Theory](docs/theory.md)** | Why standard GIS fails at "Place". The theory of emergent place. |
| **2. [Getting Started](docs/getting_started.md)** | Installation and your first "Hello World" model. |
| **3. [Core Concepts](docs/core_concepts.md)** | Agents, Encounters, Meaning, and the Platial Graph. |
| **4. [Derivation](docs/derivation.md)** | How place emerges from raw data (GPS -> Encounter -> Place). |
| **5. [Querying](docs/queries.md)** | Asking questions: "Where does Alice feel at home?" |
| **6. [API Reference](docs/api_reference.md)** | Technical manual for all classes and functions. |

---

## 🚀 Quick Start

```bash
# Install
pip install chora

# or for development
git clone https://github.com/jameswilliams/chora.git
cd chora
pip install -e ".[dev]"
```

### The "Hello Place" Example

```python
from chora.core import PlatialGraph, Agent, SpatialExtent, Encounter, PlatialEdge
from chora.derive import update_familiarity

# 1. Create the world
graph = PlatialGraph("My World")
alice = Agent.individual("Alice")
park = SpatialExtent.from_bounds(-0.1, 51.5, -0.09, 51.51, name="Hyde Park")

graph.add_node(alice)
graph.add_node(park)

# 2. Alice visits the park (An Encounter)
visit = Encounter(alice.id, park.id, start_time=..., end_time=...)
graph.add_node(visit)
graph.add_edge(PlatialEdge.participates_in(alice.id, visit.id))

# 3. Derive Familiarity (Theory in Action)
# Familiarity is not set manually; it is derived from history!
fam = update_familiarity(graph, visit)
print(f"Alice's familiarity with Park: {fam.value:.2f}")
```

## 🧩 Examples

See the [`examples/`](examples/README.md) directory for full scripts:
- **[Real Data]** `load_gpx_traces.py` — Turn GPS logs into meaningful places.
- **[Simulation]** `urban_mobility.py` — Simulating city-wide habits.
- **[Analysis]** `practice_detection.py` — Finding "Commutes" and "Rituals".

## 🤝 Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for details on our code of conduct and development process.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
