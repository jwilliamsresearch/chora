"""
Chora Example: Affective Mapping

Demonstrating how to attach and analyse emotional/experiential
qualities of places through affect derivation.
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
    update_familiarity, extract_place, attach_affect,
    derive_affect_from_context
)
from chora.query import find_positive_places


def run_affective_mapping():
    print("💭 Affective Mapping Example")
    print("=" * 50)
    
    # Create agent
    user = Agent.individual("Survey Participant", age=35)
    
    # Create locations with different affective qualities
    locations = {
        "beach": SpatialExtent.from_bounds(-0.05, 50.82, -0.04, 50.83, "Brighton Beach"),
        "office": SpatialExtent.from_bounds(-0.10, 51.52, -0.09, 51.53, "Office Block"),
        "hospital": SpatialExtent.point(-0.12, 51.49, "Memorial Hospital"),
        "childhood_park": SpatialExtent.from_bounds(-0.15, 51.45, -0.14, 51.46, "Childhood Park"),
        "gym": SpatialExtent.point(-0.08, 51.50, "Local Gym"),
    }
    
    # Affective data (from survey or experience sampling)
    affect_data = {
        "beach": {"valence": 0.9, "arousal": 0.4, "source": "survey"},  # Very positive, relaxed
        "office": {"valence": 0.1, "arousal": 0.6, "source": "survey"},  # Slightly negative, activated
        "hospital": {"valence": -0.4, "arousal": 0.7, "source": "survey"},  # Negative, anxious
        "childhood_park": {"valence": 0.8, "arousal": 0.2, "source": "memory"},  # Positive, calm (nostalgic)
        "gym": {"valence": 0.5, "arousal": 0.8, "source": "survey"},  # Positive, energetic
    }
    
    # Build graph
    graph = PlatialGraph(name="Affective Mapping Study")
    graph.add_node(user)
    for ext in locations.values():
        graph.add_node(ext)
    
    print(f"\nCreated {len(locations)} locations with affect data")
    
    # Simulate encounters with affect
    base_time = datetime.now() - timedelta(days=30)
    
    for loc_name, extent in locations.items():
        # Create encounter
        encounter = Encounter(
            agent_id=user.id,
            extent_id=extent.id,
            start_time=base_time,
            end_time=base_time + timedelta(hours=1)
        )
        graph.add_node(encounter)
        graph.add_edge(PlatialEdge.participates_in(user.id, encounter.id))
        graph.add_edge(PlatialEdge.occurs_at(encounter.id, extent.id))
        
        # Attach affect
        aff_data = affect_data[loc_name]
        affect = attach_affect(
            encounter,
            valence=aff_data["valence"],
            arousal=aff_data["arousal"],
            source=aff_data["source"]
        )
        graph.add_node(affect)
        graph.add_edge(PlatialEdge(
            source_id=encounter.id,
            target_id=affect.id,
            edge_type=EdgeType.EXPRESSES
        ))
        
        update_familiarity(graph, encounter)
        base_time += timedelta(days=1)
    
    # Analyse affective places
    print("\n📊 Affective Analysis")
    print("-" * 40)
    
    for loc_name, extent in locations.items():
        place = extract_place(graph, extent.id, user.id)
        
        # Determine affective quadrant
        valence = place.affect_valence_mean
        arousal = affect_data[loc_name]["arousal"]  # We know this from input
        
        if valence > 0.3:
            if arousal > 0.5:
                quadrant = "excited/energetic"
            else:
                quadrant = "calm/content"
        elif valence < -0.2:
            if arousal > 0.5:
                quadrant = "anxious/stressed"
            else:
                quadrant = "sad/depressed"
        else:
            quadrant = "neutral"
        
        print(f"\n{extent.name}:")
        print(f"  Character: {place.character}")
        print(f"  Valence: {valence:+.2f}")
        print(f"  Quadrant: {quadrant}")
    
    # Find positive places
    print("\n✨ Positive Places (valence > 0.3):")
    positive = find_positive_places(graph, user.id)
    for p in positive:
        print(f"  - {p.extent.name}: valence={p.affect_valence_mean:.2f}")
    
    # Affective summary
    print("\n📈 Affective Summary")
    all_places = [extract_place(graph, ext.id, user.id) for ext in locations.values()]
    avg_valence = sum(p.affect_valence_mean for p in all_places) / len(all_places)
    print(f"  Average valence across places: {avg_valence:+.2f}")
    
    positive_count = sum(1 for p in all_places if p.affect_valence_mean > 0.3)
    negative_count = sum(1 for p in all_places if p.affect_valence_mean < -0.2)
    print(f"  Positive places: {positive_count}")
    print(f"  Negative places: {negative_count}")


if __name__ == "__main__":
    run_affective_mapping()
