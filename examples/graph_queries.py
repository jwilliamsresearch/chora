"""
Chora Example: Graph Traversal & Queries

Demonstrates the query interface for finding and analysing
platial structures within the graph.
"""

import sys
import os
from datetime import datetime, timedelta

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))

from chora.core import (
    Agent, SpatialExtent, Encounter, PlatialGraph,
    PlatialEdge, EdgeType, Context
)
from chora.query import (
    PlatialQuery, find_familiar_places, find_positive_places,
    traverse_from, find_path, find_connected
)
from chora.derive import update_familiarity, attach_affect, extract_place


def run_query_examples():
    print("🔍 Graph Query Examples")
    print("=" * 50)
    
    # Build a rich graph
    graph = PlatialGraph(name="Query Demo")
    
    # Agents
    alice = Agent.individual("Alice")
    bob = Agent.individual("Bob")
    graph.add_node(alice)
    graph.add_node(bob)
    
    # Locations
    locations = {
        'park': SpatialExtent.from_bounds(-0.127, 51.507, -0.126, 51.508, "Green Park"),
        'cafe': SpatialExtent.point(-0.125, 51.509, "Morning Cafe"),
        'office': SpatialExtent.from_bounds(-0.120, 51.515, -0.118, 51.517, "Tech Office"),
        'gym': SpatialExtent.point(-0.122, 51.510, "City Gym"),
    }
    for loc in locations.values():
        graph.add_node(loc)
    
    # Create encounters
    base = datetime.now() - timedelta(days=14)
    
    # Alice: frequent park visitor (positive), occasional cafe, regular office
    for day in range(14):
        # Park (daily, positive)
        enc = Encounter(
            agent_id=alice.id,
            extent_id=locations['park'].id,
            start_time=base + timedelta(days=day, hours=7),
            end_time=base + timedelta(days=day, hours=8)
        )
        graph.add_node(enc)
        graph.add_edge(PlatialEdge.participates_in(alice.id, enc.id))
        graph.add_edge(PlatialEdge.occurs_at(enc.id, locations['park'].id))
        affect = attach_affect(enc, valence=0.8, arousal=0.3)
        graph.add_node(affect)
        graph.add_edge(PlatialEdge(enc.id, affect.id, EdgeType.EXPRESSES))
        update_familiarity(graph, enc)
        
        if day % 7 < 5:  # Weekdays
            # Office
            enc_office = Encounter(
                agent_id=alice.id,
                extent_id=locations['office'].id,
                start_time=base + timedelta(days=day, hours=9),
                end_time=base + timedelta(days=day, hours=17)
            )
            graph.add_node(enc_office)
            graph.add_edge(PlatialEdge.participates_in(alice.id, enc_office.id))
            graph.add_edge(PlatialEdge.occurs_at(enc_office.id, locations['office'].id))
            affect = attach_affect(enc_office, valence=0.2, arousal=0.5)
            graph.add_node(affect)
            graph.add_edge(PlatialEdge(enc_office.id, affect.id, EdgeType.EXPRESSES))
            update_familiarity(graph, enc_office)
    
    # Bob: mainly office and gym
    for day in range(14):
        if day % 7 < 5:
            # Office
            enc_bob_office = Encounter(
                agent_id=bob.id,
                extent_id=locations['office'].id,
                start_time=base + timedelta(days=day, hours=9),
                end_time=base + timedelta(days=day, hours=17)
            )
            graph.add_node(enc_bob_office)
            graph.add_edge(PlatialEdge.participates_in(bob.id, enc_bob_office.id))
            graph.add_edge(PlatialEdge.occurs_at(enc_bob_office.id, locations['office'].id))
            update_familiarity(graph, enc_bob_office)
        
        if day % 2 == 0:  # Every other day
            enc_gym = Encounter(
                agent_id=bob.id,
                extent_id=locations['gym'].id,
                start_time=base + timedelta(days=day, hours=18),
                end_time=base + timedelta(days=day, hours=19)
            )
            graph.add_node(enc_gym)
            graph.add_edge(PlatialEdge.participates_in(bob.id, enc_gym.id))
            graph.add_edge(PlatialEdge.occurs_at(enc_gym.id, locations['gym'].id))
            affect = attach_affect(enc_gym, valence=0.6, arousal=0.8)
            graph.add_node(affect)
            graph.add_edge(PlatialEdge(enc_gym.id, affect.id, EdgeType.EXPRESSES))
            update_familiarity(graph, enc_gym)
    
    print(f"Graph: {graph.node_count} nodes, {graph.edge_count} edges")
    
    # Query 1: Fluent query builder
    print("\n🔎 Fluent Query: Alice's familiar, positive places")
    print("-" * 40)
    
    results = (PlatialQuery(graph)
        .for_agent(alice.id)
        .with_familiarity(min_value=0.1)
        .with_positive_affect()
        .execute())
    
    for place in results:
        print(f"  • {place.extent.name}")
        print(f"    Familiarity: {place.familiarity_score:.2f}")
        print(f"    Avg Valence: {place.affect_valence_mean:.2f}")
    
    # Query 2: Convenience functions
    print("\n🔎 Convenience Functions")
    print("-" * 40)
    
    alice_familiar = find_familiar_places(graph, alice.id, min_familiarity=0.05)
    bob_familiar = find_familiar_places(graph, bob.id, min_familiarity=0.05)
    
    print(f"Alice's familiar places: {[p.extent.name for p in alice_familiar]}")
    print(f"Bob's familiar places: {[p.extent.name for p in bob_familiar]}")
    
    alice_positive = find_positive_places(graph, alice.id)
    print(f"Alice's positive places: {[p.extent.name for p in alice_positive]}")
    
    # Query 3: Graph traversal
    print("\n🔎 Graph Traversal from Alice")
    print("-" * 40)
    
    print("Nodes reachable from Alice (depth 2):")
    for node, depth in traverse_from(graph, alice.id, max_depth=2):
        if hasattr(node, 'name'):
            print(f"  Depth {depth}: {node.name}")
    
    # Query 4: Shared places
    print("\n🔎 Shared Places (Alice & Bob)")
    print("-" * 40)
    
    alice_extents = {p.extent.id for p in alice_familiar}
    bob_extents = {p.extent.id for p in bob_familiar}
    shared = alice_extents & bob_extents
    
    for ext_id in shared:
        ext = graph.get_node(ext_id)
        alice_place = extract_place(graph, ext_id, alice.id)
        bob_place = extract_place(graph, ext_id, bob.id)
        
        print(f"  {ext.name}:")
        print(f"    Alice: familiarity={alice_place.familiarity_score:.2f}, "
              f"valence={alice_place.affect_valence_mean:.2f}")
        print(f"    Bob: familiarity={bob_place.familiarity_score:.2f}, "
              f"valence={bob_place.affect_valence_mean:.2f}")


if __name__ == "__main__":
    run_query_examples()
