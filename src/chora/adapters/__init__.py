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

# Optional adapters loaded on demand
def get_neo4j_adapter():
    """Get Neo4j adapter (requires neo4j package)."""
    from chora.adapters.neo4j import Neo4jAdapter
    return Neo4jAdapter


def get_postgis_adapter():
    """Get PostGIS adapter (requires psycopg/geoalchemy2)."""
    from chora.adapters.postgis import PostGISAdapter
    return PostGISAdapter


def get_rdf_adapter():
    """Get RDF adapter (requires rdflib)."""
    from chora.adapters.rdf import RDFAdapter
    return RDFAdapter
