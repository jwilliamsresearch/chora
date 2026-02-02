"""
Chora Example: Basic Walk

A simple simulation of an agent walking between two locations,
generating encounters, and establishing a new place.
"""

import sys
import os
from datetime import datetime, timedelta

# Ensure chora is in path (if running from source)
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))

from chora.core import (
    Agent, SpatialExtent, Encounter, PlatialGraph, 
    Context, ContextType
)
from chora.derive import (
    update_familiarity, 
    extract_place,
    attach_affect
)

def run_simulation():
    print("📍 Initialising Simulation...")
    
    # 1. Create the World
    # -------------------
    # Two parks separated by a street
    park_a = SpatialExtent.from_bounds(
        -0.1275, 51.5072, -0.1270, 51.5076, 
        name="Green Square"
    )
    park_a.set_hint("type", "park")
    
    park_b = SpatialExtent.from_bounds(
        -0.1260, 51.5072, -0.1255, 51.5076, 
        name="Quiet Gardens"
    )
    park_b.set_hint("type", "park")
    
    print(f"Created extents: {park_a.name}, {park_b.name}")
    
    # 2. Create the Agent
    # -------------------
    alice = Agent.individual("Alice", interest="reading")
    print(f"Created agent: {alice.name}")
    
    # 3. Initialise Graph
    # -------------------
    graph = PlatialGraph(name="Simulation Graph")
    graph.add_node(park_a)
    graph.add_node(park_b)
    graph.add_node(alice)
    
    # 4. Simulate Encounters
    # ----------------------
    print("\n🚶 Simulating encounters...")
    # Start simulation 7 days ago so encounters are in the past relative to "now"
    start_time = datetime.now() - timedelta(days=7)
    
    # Alice visits Green Square 5 times over a week
    for i in range(5):
        visit_time = start_time + timedelta(days=i, hours=10)
        
        # Create encounter
        encounter = Encounter(
            agent_id=alice.id,
            extent_id=park_a.id,
            start_time=visit_time,
            end_time=visit_time + timedelta(minutes=45),
            activity="reading"
        )
        graph.add_node(encounter)
        
        # Link agent and extent to encounter
        from chora.core import PlatialEdge
        graph.add_edge(PlatialEdge.participates_in(alice.id, encounter.id))
        graph.add_edge(PlatialEdge.occurs_at(encounter.id, park_a.id))
        
        # Add context (sunny weather)
        ctx = Context.environmental({"weather": "sunny"})
        graph.add_node(ctx)
        
        # Link encounter to context
        from chora.core import PlatialEdge, EdgeType
        edge = PlatialEdge(
            source_id=encounter.id,
            target_id=ctx.id,
            edge_type=EdgeType.HAS_CONTEXT
        )
        graph.add_edge(edge)
        
        # Derive updates derived state
        fam = update_familiarity(graph, encounter)
        
        # Attach positive affect (Alice likes reading in the park)
        affect = attach_affect(encounter, valence=0.7, arousal=0.2, source="simulation")
        graph.add_node(affect)
        graph.add_edge(PlatialEdge(
            source_id=encounter.id,
            target_id=affect.id,
            edge_type=EdgeType.EXPRESSES
        ))
        
        print(f"  - Visit {i+1}: Familiarity now {fam.value:.2f}")
        
    # Alice visits Quiet Gardens only once
    visit_time = start_time + timedelta(days=2, hours=14)
    enc_b = Encounter(
        agent_id=alice.id,
        extent_id=park_b.id,
        start_time=visit_time,
        end_time=visit_time + timedelta(minutes=10),
        activity="passing_through"
    )
    graph.add_node(enc_b)
    update_familiarity(graph, enc_b)
    print(f"  - Visit to {park_b.name}: Familiarity low")

    # 5. Extract Emergent Places
    # --------------------------
    print("\n✨ Extracting Emergent Places...")
    
    place_a = extract_place(graph, park_a.id, alice.id)
    place_b = extract_place(graph, park_b.id, alice.id)
    
    print(f"\nPlace: {place_a.extent.name}")
    print(f"  Type: {place_a.extent.get_hint('type')}")
    print(f"  Character: {place_a.character}")
    print(f"  Familiarity: {place_a.familiarity_score:.2f}")
    print(f"  Encounters: {place_a.encounter_count}")
    print(f"  Avg Affect: {place_a.affect_valence_mean:.2f}")
    
    print(f"\nPlace: {place_b.extent.name}")
    print(f"  Character: {place_b.character}")
    print(f"  Familiarity: {place_b.familiarity_score:.2f}")

if __name__ == "__main__":
    run_simulation()
