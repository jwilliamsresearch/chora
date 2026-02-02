"""
Vector Embeddings for Platial Search

Enables "vibe search" - finding places by semantic similarity to descriptions,
other places, or abstract qualities.
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Iterator, Any, Callable
from pathlib import Path

import numpy as np

from chora.core import PlatialGraph, SpatialExtent
from chora.core.types import NodeType, NodeId


@dataclass
class PlaceEmbedding:
    """
    Vector embedding for a place.
    
    Combines multiple signals into a unified embedding:
    - Name/description text
    - Familiarity patterns
    - Affect qualities
    - Encounter characteristics
    """
    
    extent_id: NodeId
    embedding: np.ndarray
    source: str = "combined"  # text, affect, encounters, combined
    model: str = "all-MiniLM-L6-v2"
    metadata: dict[str, Any] = field(default_factory=dict)
    
    @property
    def dimension(self) -> int:
        return len(self.embedding)
    
    def similarity(self, other: PlaceEmbedding) -> float:
        """Compute cosine similarity with another embedding."""
        return cosine_similarity(self.embedding, other.embedding)
    
    def to_dict(self) -> dict:
        return {
            "extent_id": str(self.extent_id),
            "embedding": self.embedding.tolist(),
            "source": self.source,
            "model": self.model,
            "metadata": self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> PlaceEmbedding:
        return cls(
            extent_id=NodeId(data["extent_id"]),
            embedding=np.array(data["embedding"]),
            source=data.get("source", "combined"),
            model=data.get("model", "unknown"),
            metadata=data.get("metadata", {})
        )


@dataclass
class PlaceIndex:
    """
    Vector index for semantic place search.
    
    Stores embeddings and enables similarity search across all places.
    """
    
    embeddings: dict[str, PlaceEmbedding] = field(default_factory=dict)
    model_name: str = "all-MiniLM-L6-v2"
    _embedder: Any = None
    
    def add(self, embedding: PlaceEmbedding) -> None:
        """Add an embedding to the index."""
        self.embeddings[str(embedding.extent_id)] = embedding
    
    def remove(self, extent_id: NodeId) -> None:
        """Remove an embedding from the index."""
        self.embeddings.pop(str(extent_id), None)
    
    def get(self, extent_id: NodeId) -> PlaceEmbedding | None:
        """Get embedding for a specific extent."""
        return self.embeddings.get(str(extent_id))
    
    def search(
        self, 
        query_embedding: np.ndarray, 
        top_k: int = 10,
        min_similarity: float = 0.0
    ) -> list[tuple[str, float]]:
        """
        Search for most similar places.
        
        Returns list of (extent_id, similarity) tuples.
        """
        results = []
        
        for extent_id, emb in self.embeddings.items():
            sim = cosine_similarity(query_embedding, emb.embedding)
            if sim >= min_similarity:
                results.append((extent_id, sim))
        
        results.sort(key=lambda x: x[1], reverse=True)
        return results[:top_k]
    
    def search_by_text(
        self, 
        query: str, 
        top_k: int = 10
    ) -> list[tuple[str, float]]:
        """Search places by text description."""
        if self._embedder is None:
            self._embedder = get_embedder(self.model_name)
        
        query_embedding = self._embedder.encode(query)
        return self.search(query_embedding, top_k)
    
    def search_by_place(
        self, 
        extent_id: NodeId, 
        top_k: int = 10,
        exclude_self: bool = True
    ) -> list[tuple[str, float]]:
        """Find places similar to a given place."""
        emb = self.get(extent_id)
        if emb is None:
            return []
        
        results = self.search(emb.embedding, top_k + 1)
        
        if exclude_self:
            results = [(eid, sim) for eid, sim in results if eid != str(extent_id)]
        
        return results[:top_k]
    
    def save(self, path: str | Path) -> None:
        """Save index to file."""
        data = {
            "model_name": self.model_name,
            "embeddings": {
                k: v.to_dict() for k, v in self.embeddings.items()
            }
        }
        Path(path).write_text(json.dumps(data))
    
    @classmethod
    def load(cls, path: str | Path) -> PlaceIndex:
        """Load index from file."""
        data = json.loads(Path(path).read_text())
        index = cls(model_name=data.get("model_name", "unknown"))
        for k, v in data.get("embeddings", {}).items():
            index.embeddings[k] = PlaceEmbedding.from_dict(v)
        return index


# =============================================================================
# Embedding Functions
# =============================================================================

def get_embedder(model_name: str = "all-MiniLM-L6-v2"):
    """Get or create a sentence transformer model."""
    try:
        from sentence_transformers import SentenceTransformer
        return SentenceTransformer(model_name)
    except ImportError:
        raise ImportError(
            "sentence-transformers not installed. "
            "Run: pip install sentence-transformers"
        )


def embed_text(text: str, model_name: str = "all-MiniLM-L6-v2") -> np.ndarray:
    """Embed a text string."""
    embedder = get_embedder(model_name)
    return embedder.encode(text)


def embed_extent(
    extent: SpatialExtent,
    graph: PlatialGraph | None = None,
    include_encounters: bool = True,
    model_name: str = "all-MiniLM-L6-v2"
) -> PlaceEmbedding:
    """
    Create an embedding for a spatial extent.
    
    Combines multiple signals:
    - Name and semantic hints as text
    - Encounter descriptions (if graph provided)
    - Affect qualities (if available)
    """
    # Build text description
    parts = []
    
    if extent.name:
        parts.append(extent.name)
    
    if extent.semantic_hints:
        for key, value in extent.semantic_hints.items():
            parts.append(f"{key}: {value}")
    
    if extent.extent_type:
        parts.append(f"type: {extent.extent_type}")
    
    # If we have a graph, add encounter info
    if graph and include_encounters:
        encounter_count = 0
        activities = set()
        
        for node in graph.nodes(NodeType.ENCOUNTER):
            if hasattr(node, 'extent_id') and str(node.extent_id) == str(extent.id):
                encounter_count += 1
                if hasattr(node, 'activity'):
                    activities.add(node.activity)
        
        if encounter_count > 0:
            parts.append(f"visited {encounter_count} times")
        
        if activities:
            parts.append(f"activities: {', '.join(activities)}")
    
    text = ". ".join(parts) if parts else "unknown place"
    
    embedder = get_embedder(model_name)
    embedding = embedder.encode(text)
    
    return PlaceEmbedding(
        extent_id=extent.id,
        embedding=embedding,
        source="combined",
        model=model_name,
        metadata={"text": text}
    )


def build_place_index(
    graph: PlatialGraph,
    model_name: str = "all-MiniLM-L6-v2"
) -> PlaceIndex:
    """Build a complete place index from a graph."""
    index = PlaceIndex(model_name=model_name)
    
    for extent in graph.nodes(NodeType.SPATIAL_EXTENT):
        emb = embed_extent(extent, graph, model_name=model_name)
        index.add(emb)
    
    return index


# =============================================================================
# Vibe Search Functions
# =============================================================================

def vibe_search(
    graph: PlatialGraph,
    query: str,
    top_k: int = 5,
    index: PlaceIndex | None = None
) -> list[tuple[SpatialExtent, float]]:
    """
    Find places matching a vibe/description.
    
    Examples:
        vibe_search(graph, "quiet peaceful park for reading")
        vibe_search(graph, "busy exciting nightlife")
        vibe_search(graph, "cozy coffee shop")
    
    Returns list of (extent, similarity) tuples.
    """
    if index is None:
        index = build_place_index(graph)
    
    results = index.search_by_text(query, top_k)
    
    output = []
    for extent_id, similarity in results:
        try:
            extent = graph.get_node(NodeId(extent_id))
            output.append((extent, similarity))
        except Exception:
            continue
    
    return output


def find_similar_places(
    graph: PlatialGraph,
    reference_extent: SpatialExtent,
    top_k: int = 5,
    index: PlaceIndex | None = None
) -> list[tuple[SpatialExtent, float]]:
    """
    Find places similar to a reference place.
    
    Useful for "places like this one" recommendations.
    """
    if index is None:
        index = build_place_index(graph)
    
    results = index.search_by_place(reference_extent.id, top_k, exclude_self=True)
    
    output = []
    for extent_id, similarity in results:
        try:
            extent = graph.get_node(NodeId(extent_id))
            output.append((extent, similarity))
        except Exception:
            continue
    
    return output


# =============================================================================
# Utility Functions
# =============================================================================

def cosine_similarity(a: np.ndarray, b: np.ndarray) -> float:
    """Compute cosine similarity between two vectors."""
    dot = np.dot(a, b)
    norm_a = np.linalg.norm(a)
    norm_b = np.linalg.norm(b)
    
    if norm_a == 0 or norm_b == 0:
        return 0.0
    
    return float(dot / (norm_a * norm_b))


def batch_embed(
    texts: list[str], 
    model_name: str = "all-MiniLM-L6-v2"
) -> np.ndarray:
    """Embed multiple texts efficiently."""
    embedder = get_embedder(model_name)
    return embedder.encode(texts)
