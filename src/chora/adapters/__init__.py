"""
Chora Adapters Module

Backend adapters for persisting and querying platial graphs.
The in-memory adapter is always available; other adapters
(Neo4j, PostGIS, RDF) require optional dependencies.
"""

from chora.adapters.base import GraphAdapter
from chora.adapters.memory import InMemoryAdapter

__all__ = [
    "GraphAdapter",
    "InMemoryAdapter",
]

try:
    from chora.adapters.neo4j import Neo4jAdapter
    __all__.append("Neo4jAdapter")
except ImportError:
    pass

# Lazy loaders for other optional adapters
try:
    from chora.adapters.postgis import PostGISAdapter
    __all__.append("PostGISAdapter")
except ImportError:
    pass

try:
    from chora.adapters.redis import RedisAdapter
    __all__.append("RedisAdapter")
except ImportError:
    pass


def get_rdf_adapter():
    """Get RDF adapter (requires rdflib)."""
    from chora.adapters.rdf import RDFAdapter
    return RDFAdapter
