# Contributing to Chora

First off, thank you for considering contributing to Chora! This library aims to bring **platial modelling**—reasoning about human experience of place—to the core of geospatial computing.

## 🌟 The Vision

We are building a library that treats **Place** as an emergent, evolving structure, not a static point on a map.

- **Place ≠ Location**: It is a graph of encounters, meanings, and affects.
- **Theory-First**: Our operators (decay, familiarity) come from social theory, not just math.
- **Relational**: Everything is connected.

## 🛠 Getting Started

1. **Fork and Clone**
   ```bash
   git clone https://github.com/your-username/chora.git
   cd chora
   ```

2. **Environment Setup**
   We recommend `venv`.
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -e ".[dev]"
   ```

3. **Running Tests**
   We use `pytest` for unit tests and `hypothesis` for property-based testing.
   ```bash
   pytest tests/unit
   ```

## 📐 Coding Standards

- **Type Hints**: All code must function signatures must be typed.
- **Docstrings**: We use NumPy style docstrings. Every class and public method needs one.
- **Epistemic Clarity**: Always use `EpistemicLevel` (OBSERVED/DERIVED/INTERPRETED) when creating new nodes.

### Adding a New Adapter

If you are adding a new backend (e.g., RDF, ArangoDB):
1. Inherit from `chora.adapters.base.GraphAdapter`.
2. Implement all abstract methods.
3. Add a lazy loader in `chora.adapters.__init__.py`.
4. Add passing tests in `tests/`.

## 📚 Documentation

Documentation is written in Markdown and lives in `docs/`.
- `theory.md`: Extensions to the specific platial theory.
- `core_concepts.md`: Changes to the domain model.

## 🤝 Community

Join the discussion!
- **Issues**: Use GitHub Issues for bug reports and feature requests.
- **Discussions**: Share your platial modelling use cases.

Thank you for helping us make GIS more human! 🌍
