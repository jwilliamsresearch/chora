"""
Example: Semantic Place Search using Vector Embeddings.

Demonstrates how to use the 'chora.embeddings' module to find places by "vibe".

Note: In a real app, you would store these vectors in a Vector DB (like Qdrant or PGVector).
Here we just do a linear scan for demonstration.
"""
import numpy as np
from chora.embeddings import get_embedding_model
from chora.core import SpatialExtent

def cosine_similarity(v1, v2):
    return np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2))

def main():
    try:
        model = get_embedding_model()
    except ImportError:
        print("Error: sentence-transformers not installed.")
        return

    # 1. our "Database" of places with descriptions
    places = [
        {"name": "Library", "desc": "A quiet place for reading books and studying in silence."},
        {"name": "Coffee Shop", "desc": "A busy cafe with espresso machines noise and people chatting."},
        {"name": "Nightclub", "desc": "Loud music, dancing, dark lighting, energetic atmosphere."},
        {"name": "Meditation Garden", "desc": "Peaceful nature, running water, zen atmosphere."},
    ]
    
    print("🧠 Embedding Database...")
    db_vectors = []
    for p in places:
        vec = model.embed_text(p["desc"])
        db_vectors.append(vec)
        print(f"Encoded '{p['name']}'")

    # 2. Search Query
    query = "Where can I find some peace and quiet?"
    print(f"\n🔎 Searching for: '{query}'")
    
    query_vec = model.embed_text(query)
    
    # 3. Semantic Search
    results = []
    for i, p_vec in enumerate(db_vectors):
        score = cosine_similarity(query_vec, p_vec)
        results.append((score, places[i]["name"]))
    
    # Sort
    results.sort(key=lambda x: x[0], reverse=True)
    
    print("\n🏆 Top Matches:")
    for score, name in results:
        print(f"  {score:.4f} | {name}")

if __name__ == "__main__":
    main()
