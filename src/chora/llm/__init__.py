"""
LLM Integration for Chora

Generate natural language narratives about places using large language models.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable, Protocol
from abc import ABC, abstractmethod

from chora.core import PlatialGraph, SpatialExtent
from chora.core.types import NodeType, NodeId


# =============================================================================
# LLM Provider Protocol
# =============================================================================

class LLMProvider(Protocol):
    """Protocol for LLM providers."""
    
    def generate(self, prompt: str, **kwargs) -> str:
        """Generate text from a prompt."""
        ...


# =============================================================================
# Provider Implementations
# =============================================================================

@dataclass
class OpenAIProvider:
    """OpenAI API provider."""
    
    api_key: str = ""
    model: str = "gpt-4o-mini"
    temperature: float = 0.7
    max_tokens: int = 500
    
    def generate(self, prompt: str, **kwargs) -> str:
        try:
            from openai import OpenAI
        except ImportError:
            raise ImportError("openai not installed. Run: pip install openai")
        
        client = OpenAI(api_key=self.api_key or None)
        
        response = client.chat.completions.create(
            model=kwargs.get("model", self.model),
            messages=[{"role": "user", "content": prompt}],
            temperature=kwargs.get("temperature", self.temperature),
            max_tokens=kwargs.get("max_tokens", self.max_tokens)
        )
        
        return response.choices[0].message.content or ""


@dataclass
class AnthropicProvider:
    """Anthropic Claude API provider."""
    
    api_key: str = ""
    model: str = "claude-3-haiku-20240307"
    temperature: float = 0.7
    max_tokens: int = 500
    
    def generate(self, prompt: str, **kwargs) -> str:
        try:
            import anthropic
        except ImportError:
            raise ImportError("anthropic not installed. Run: pip install anthropic")
        
        client = anthropic.Anthropic(api_key=self.api_key or None)
        
        message = client.messages.create(
            model=kwargs.get("model", self.model),
            max_tokens=kwargs.get("max_tokens", self.max_tokens),
            messages=[{"role": "user", "content": prompt}]
        )
        
        return message.content[0].text if message.content else ""


@dataclass
class OllamaProvider:
    """Local Ollama provider."""
    
    model: str = "llama3.2"
    base_url: str = "http://localhost:11434"
    
    def generate(self, prompt: str, **kwargs) -> str:
        import json
        import urllib.request
        
        data = {
            "model": kwargs.get("model", self.model),
            "prompt": prompt,
            "stream": False
        }
        
        req = urllib.request.Request(
            f"{self.base_url}/api/generate",
            data=json.dumps(data).encode(),
            headers={"Content-Type": "application/json"}
        )
        
        try:
            with urllib.request.urlopen(req, timeout=60) as response:
                result = json.loads(response.read().decode())
                return result.get("response", "")
        except Exception as e:
            return f"Error: {e}"


# =============================================================================
# Narrative Generator
# =============================================================================

@dataclass
class NarrativeGenerator:
    """
    Generate natural language narratives about places.
    
    Uses LLMs to create descriptions, stories, and interpretations
    based on platial data.
    """
    
    provider: LLMProvider = field(default_factory=OllamaProvider)
    
    def describe_place(
        self, 
        graph: PlatialGraph, 
        extent: SpatialExtent,
        style: str = "descriptive"
    ) -> str:
        """
        Generate a narrative description of a place.
        
        Parameters
        ----------
        graph : PlatialGraph
            The graph containing the place
        extent : SpatialExtent
            The spatial extent to describe
        style : str
            Writing style: descriptive, poetic, analytical, personal
        """
        context = self._gather_context(graph, extent)
        prompt = self._build_describe_prompt(context, style)
        return self.provider.generate(prompt)
    
    def compare_places(
        self,
        graph: PlatialGraph,
        extent1: SpatialExtent,
        extent2: SpatialExtent
    ) -> str:
        """Generate a narrative comparing two places."""
        ctx1 = self._gather_context(graph, extent1)
        ctx2 = self._gather_context(graph, extent2)
        
        prompt = f"""Compare these two places:

Place 1: {ctx1['name']}
{self._format_context(ctx1)}

Place 2: {ctx2['name']}
{self._format_context(ctx2)}

Write a brief comparison highlighting how these places differ in terms of 
character, atmosphere, and the experiences they afford. Keep it to 2-3 paragraphs."""
        
        return self.provider.generate(prompt)
    
    def narrate_journey(
        self,
        graph: PlatialGraph,
        extents: list[SpatialExtent],
        agent_name: str = "the traveler"
    ) -> str:
        """Generate a narrative of a journey through multiple places."""
        places_info = []
        for i, ext in enumerate(extents):
            ctx = self._gather_context(graph, ext)
            places_info.append(f"{i+1}. {ctx['name']}: {self._format_context(ctx)}")
        
        prompt = f"""Write a short narrative about {agent_name}'s journey through these places:

{chr(10).join(places_info)}

Create an engaging first-person narrative (2-3 paragraphs) that captures the 
experience of moving through these places, noting the transitions and how 
each place feels different."""
        
        return self.provider.generate(prompt)
    
    def interpret_familiarity(
        self,
        graph: PlatialGraph,
        extent: SpatialExtent,
        familiarity_score: float
    ) -> str:
        """Generate interpretation of familiarity level."""
        ctx = self._gather_context(graph, extent)
        
        level = "very unfamiliar" if familiarity_score < 0.2 else \
                "somewhat familiar" if familiarity_score < 0.5 else \
                "quite familiar" if familiarity_score < 0.8 else \
                "deeply familiar"
        
        prompt = f"""A person has a familiarity score of {familiarity_score:.2f} with this place:

{ctx['name']}
{self._format_context(ctx)}

This means the place is {level} to them. Write 2-3 sentences interpreting 
what this level of familiarity might feel like and mean for their relationship 
with this place."""
        
        return self.provider.generate(prompt)
    
    def suggest_exploration(
        self,
        graph: PlatialGraph,
        familiar_places: list[SpatialExtent],
        unfamiliar_places: list[SpatialExtent]
    ) -> str:
        """Suggest places to explore based on familiarity patterns."""
        familiar_names = [p.name or str(p.id)[:8] for p in familiar_places[:5]]
        unfamiliar_names = [p.name or str(p.id)[:8] for p in unfamiliar_places[:5]]
        
        prompt = f"""Based on someone's place familiarity patterns:

Familiar places: {', '.join(familiar_names)}
Unfamiliar nearby places: {', '.join(unfamiliar_names)}

Suggest which unfamiliar places might be interesting to explore and why, 
based on the pattern of places they already know. Be specific and give 
reasons. Keep it to 2-3 suggestions."""
        
        return self.provider.generate(prompt)
    
    def _gather_context(
        self, 
        graph: PlatialGraph, 
        extent: SpatialExtent
    ) -> dict[str, Any]:
        """Gather contextual information about a place."""
        context = {
            "name": extent.name or "unnamed place",
            "type": extent.extent_type,
            "hints": extent.semantic_hints,
            "encounter_count": 0,
            "activities": set(),
            "affect": None
        }
        
        # Count encounters
        for node in graph.nodes(NodeType.ENCOUNTER):
            if hasattr(node, 'extent_id') and str(node.extent_id) == str(extent.id):
                context["encounter_count"] += 1
                if hasattr(node, 'activity'):
                    context["activities"].add(node.activity)
        
        # Get affect if available
        for node in graph.nodes(NodeType.AFFECT):
            if hasattr(node, 'extent_id') and str(node.extent_id) == str(extent.id):
                context["affect"] = {
                    "valence": getattr(node, 'valence', 0),
                    "arousal": getattr(node, 'arousal', 0)
                }
                break
        
        return context
    
    def _format_context(self, ctx: dict) -> str:
        """Format context dict as text."""
        parts = []
        
        if ctx.get("type"):
            parts.append(f"Type: {ctx['type']}")
        
        if ctx.get("hints"):
            hints = ", ".join(f"{k}={v}" for k, v in ctx["hints"].items())
            parts.append(f"Characteristics: {hints}")
        
        if ctx.get("encounter_count", 0) > 0:
            parts.append(f"Visited {ctx['encounter_count']} times")
        
        if ctx.get("activities"):
            parts.append(f"Activities: {', '.join(ctx['activities'])}")
        
        if ctx.get("affect"):
            v = ctx["affect"]["valence"]
            a = ctx["affect"]["arousal"]
            mood = "positive" if v > 0 else "negative" if v < 0 else "neutral"
            energy = "high energy" if a > 0 else "calm" if a < 0 else "moderate energy"
            parts.append(f"Feels: {mood}, {energy}")
        
        return "\n".join(parts) if parts else "No details available"
    
    def _build_describe_prompt(self, ctx: dict, style: str) -> str:
        """Build the description prompt."""
        style_instructions = {
            "descriptive": "Write a clear, informative description",
            "poetic": "Write a lyrical, evocative description with metaphor",
            "analytical": "Write an analytical description focusing on patterns",
            "personal": "Write as if describing a meaningful personal place"
        }
        
        instruction = style_instructions.get(style, style_instructions["descriptive"])
        
        return f"""{instruction} of this place:

Name: {ctx['name']}
{self._format_context(ctx)}

Keep the description to 2-3 sentences that capture the essence of the place."""


# =============================================================================
# Convenience Functions
# =============================================================================

def describe_place(
    graph: PlatialGraph,
    extent: SpatialExtent,
    provider: LLMProvider | None = None,
    style: str = "descriptive"
) -> str:
    """Generate a description of a place."""
    gen = NarrativeGenerator(provider=provider or OllamaProvider())
    return gen.describe_place(graph, extent, style)


def narrate_journey(
    graph: PlatialGraph,
    extents: list[SpatialExtent],
    provider: LLMProvider | None = None
) -> str:
    """Generate a narrative of a journey through places."""
    gen = NarrativeGenerator(provider=provider or OllamaProvider())
    return gen.narrate_journey(graph, extents)
