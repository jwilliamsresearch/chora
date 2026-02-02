"""
Chora Example: Urban Mobility

Multi-agent simulation of urban mobility patterns,
demonstrating practice detection and comparative place analysis.
"""

import sys
import os
from datetime import datetime, timedelta
from random import Random

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))

from chora.core import (
    Agent, SpatialExtent, Encounter, PlatialGraph,
    PlatialEdge, EdgeType, Context
)
from chora.derive import (
    update_familiarity, extract_place, detect_practices,
    attach_affect
)
from chora.query import find_familiar_places, place_similarity


def create_city():
    """Create a simple urban environment."""
    extents = {
        "home_alice": SpatialExtent.from_bounds(-0.130, 51.510, -0.129, 51.511, "Alice's Home"),
        "home_bob": SpatialExtent.from_bounds(-0.125, 51.505, -0.124, 51.506, "Bob's Home"),
        "office": SpatialExtent.from_bounds(-0.120, 51.515, -0.118, 51.517, "Tech Hub Office"),
        "park": SpatialExtent.from_bounds(-0.127, 51.512, -0.125, 51.514, "Central Park"),
        "cafe": SpatialExtent.point(-0.122, 51.513, "Morning Cafe"),
        "gym": SpatialExtent.from_bounds(-0.119, 51.508, -0.118, 51.509, "Fitness Center"),
    }
    for ext in extents.values():
        ext.set_hint("type", "urban")
    extents["park"].set_hint("type", "recreation")
    extents["cafe"].set_hint("type", "commercial")
    return extents


def simulate_commuter(graph, agent, home, office, park, days=14, rng=None):
    """Simulate a daily commuter with occasional park visits."""
    rng = rng or Random(42)
    base_time = datetime.now() - timedelta(days=days)
    encounters = []
    
    for day in range(days):
        if day % 7 >= 5:  # Weekend
            continue
            
        day_start = base_time + timedelta(days=day)
        
        # Morning at home
        enc_home = Encounter(
            agent_id=agent.id,
            extent_id=home.id,
            start_time=day_start + timedelta(hours=7),
            end_time=day_start + timedelta(hours=8),
            activity="morning_routine"
        )
        graph.add_node(enc_home)
        graph.add_edge(PlatialEdge.participates_in(agent.id, enc_home.id))
        graph.add_edge(PlatialEdge.occurs_at(enc_home.id, home.id))
        update_familiarity(graph, enc_home)
        encounters.append(enc_home)
        
        # Work
        enc_work = Encounter(
            agent_id=agent.id,
            extent_id=office.id,
            start_time=day_start + timedelta(hours=9),
            end_time=day_start + timedelta(hours=17),
            activity="work"
        )
        graph.add_node(enc_work)
        graph.add_edge(PlatialEdge.participates_in(agent.id, enc_work.id))
        graph.add_edge(PlatialEdge.occurs_at(enc_work.id, office.id))
        update_familiarity(graph, enc_work)
        encounters.append(enc_work)
        
        # Sometimes lunch in park
        if rng.random() < 0.4:
            enc_park = Encounter(
                agent_id=agent.id,
                extent_id=park.id,
                start_time=day_start + timedelta(hours=12, minutes=30),
                end_time=day_start + timedelta(hours=13),
                activity="lunch_walk"
            )
            graph.add_node(enc_park)
            graph.add_edge(PlatialEdge.participates_in(agent.id, enc_park.id))
            graph.add_edge(PlatialEdge.occurs_at(enc_park.id, park.id))
            
            affect = attach_affect(enc_park, valence=0.6, arousal=0.3)
            graph.add_node(affect)
            graph.add_edge(PlatialEdge(
                source_id=enc_park.id, target_id=affect.id,
                edge_type=EdgeType.EXPRESSES
            ))
            
            update_familiarity(graph, enc_park)
            encounters.append(enc_park)
    
    return encounters


def run_simulation():
    print("🏙️  Urban Mobility Simulation")
    print("=" * 50)
    
    # Create environment
    extents = create_city()
    print(f"Created {len(extents)} urban locations")
    
    # Create agents
    alice = Agent.individual("Alice", occupation="engineer")
    bob = Agent.individual("Bob", occupation="designer")
    print(f"Created agents: {alice.name}, {bob.name}")
    
    # Build graph
    graph = PlatialGraph(name="Urban Mobility Study")
    graph.add_node(alice)
    graph.add_node(bob)
    for ext in extents.values():
        graph.add_node(ext)
    
    # Simulate
    print("\n📅 Simulating 14 days of activity...")
    
    alice_encounters = simulate_commuter(
        graph, alice,
        extents["home_alice"], extents["office"], extents["park"],
        days=14, rng=Random(123)
    )
    
    bob_encounters = simulate_commuter(
        graph, bob,
        extents["home_bob"], extents["office"], extents["park"],
        days=14, rng=Random(456)
    )
    
    print(f"  Alice: {len(alice_encounters)} encounters")
    print(f"  Bob: {len(bob_encounters)} encounters")
    
    # Detect practices
    print("\n🔄 Detecting Practices...")
    alice_practices = detect_practices(alice_encounters, alice.id)
    bob_practices = detect_practices(bob_encounters, bob.id)
    
    for p in alice_practices[:3]:
        print(f"  Alice: {p.name} (regularity={p.regularity:.2f})")
    for p in bob_practices[:3]:
        print(f"  Bob: {p.name} (regularity={p.regularity:.2f})")
    
    # Extract places
    print("\n📍 Emergent Places...")
    
    alice_office = extract_place(graph, extents["office"].id, alice.id)
    bob_office = extract_place(graph, extents["office"].id, bob.id)
    alice_park = extract_place(graph, extents["park"].id, alice.id)
    
    print(f"\n  Office (Alice): {alice_office.character}")
    print(f"    Familiarity: {alice_office.familiarity_score:.2f}")
    print(f"    Encounters: {alice_office.encounter_count}")
    
    print(f"\n  Office (Bob): {bob_office.character}")
    print(f"    Familiarity: {bob_office.familiarity_score:.2f}")
    
    print(f"\n  Park (Alice): {alice_park.character}")
    print(f"    Familiarity: {alice_park.familiarity_score:.2f}")
    print(f"    Avg Affect: {alice_park.affect_valence_mean:.2f}")
    
    # Compare places
    print("\n📊 Place Comparison...")
    sim = place_similarity(alice_office, bob_office)
    print(f"  Alice's Office vs Bob's Office: {sim:.2f} similarity")
    
    # Find familiar places
    print("\n🏠 Alice's Familiar Places:")
    familiar = find_familiar_places(graph, alice.id, min_familiarity=0.05)
    for p in familiar:
        print(f"  - {p.extent.name}: familiarity={p.familiarity_score:.2f}")


if __name__ == "__main__":
    run_simulation()
