"""
Local Embedding Model using Sentence Transformers.

Uses 'all-MiniLM-L6-v2' by default (small, fast, good quality).
"""
from typing import List
from typing import Protocol

class Embedder(Protocol):
    def embed_text(self, text: str) -> List[float]:
        ...

class LocalEmbedder:
    """
    Real local embedding using HuggingFace SentenceTransformers.
    """
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        try:
            from sentence_transformers import SentenceTransformer
            self._model = SentenceTransformer(model_name)
        except ImportError:
            raise ImportError("sentence-transformers not installed. Install with `pip install .[server]`")

    def embed_text(self, text: str) -> List[float]:
        """Convert text to a vector (list of floats)."""
        # encode returns numpy array, convert to list
        vector = self._model.encode(text)
        return vector.tolist()

_global_embedder = None

def get_embedding_model() -> Embedder:
    """Factory to get the configured embedding model (Singleton)."""
    global _global_embedder
    if _global_embedder is None:
        # Lazy load to avoid overhead on import
        try:
            _global_embedder = LocalEmbedder()
        except ImportError:
            # Fallback for dev environment without deps? 
            # User explicitly asked for REAL embedder, so we should error if missing.
            raise ImportError("Real Embedder requested but sentence-transformers missing.")
    return _global_embedder
