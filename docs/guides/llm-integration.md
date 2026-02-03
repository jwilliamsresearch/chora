# LLM Integration

Generate natural language narratives about places using Large Language Models.

---

## Why Narratives?

Maps give you coordinates. **Narratives give you meaning.**

Chora integrates with LLMs (OpenAI, Anthropic, Ollama) to translate platial graphs into human stories:
- *Describe* a place's character
- *Narrate* a journey through the city
- *Interpret* why a place feels familiar

---

## Setup

```python
from chora.llm import NarrativeGenerator, OllamaProvider, OpenAIProvider

# Option 1: Local LLM (Free, Private)
# Requires Ollama running (ollama serve)
provider = OllamaProvider(model="llama3.2")

# Option 2: OpenAI (High Quality)
# provider = OpenAIProvider(api_key="sk-...", model="gpt-4")

gen = NarrativeGenerator(provider=provider)
```

---

## 1. Describe a Place

Generates a description based on the place's hints, affect, and history.

```python
from chora.llm import describe_place

description = describe_place(
    graph, 
    park, 
    style="poetic"  # or "descriptive", "analytical"
)

print(description)
```

> *The park breathes with a quiet calm, anchored by the rustling oak trees. It is a place of deep familiarity, visited often in the morning hours, carrying an air of restoration and peace.*

---

## 2. Narrate a Journey

Turn a sequence of visits into a travelogue.

```python
from chora.llm import narrate_journey

# List of places visited
route = [home, station, coffee_shop, office]

story = narrate_journey(graph, route, agent_name="Alice")
print(story)
```

> *Alice began her day at the sanctuary of Home, before stepping into the chaotic rhythm of the Station. The sensory transition was sharp—from quiet comfort to the mechanical hum of transit. A brief respite followed at the Coffee Shop, a ritual pause, before the final transition into the focused energy of the Office.*

---

## 3. Interpret Familiarity

Explain *why* a place is familiar.

```python
explanation = gen.interpret_familiarity(graph, work, score=0.95)
print(explanation)
```

> *With a score of 0.95, this place is deeply familiar—an anchor in your daily life. It is not just a location but a habit, reinforced by daily presence. Such high familiarity suggests it shape your identity as much as you inhabit it.*

---

## Supported Models

| Provider | Models | Best For |
|----------|--------|----------|
| **Ollama** | `llama3`, `mistral` | Local dev, privacy, cost |
| **OpenAI** | `gpt-4o`, `gpt-3.5` | High quality narratives |
| **Anthropic** | `claude-3-opus` | Nuanced, poetic descriptions |

---

## Next Steps

- [H3 Indexing](h3-indexing.md) — Analyze places at scale before narrating
- [Vibe Search](vibe-search.md) — Find places to write about
