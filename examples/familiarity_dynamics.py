"""
Chora Example: Familiarity Dynamics

Demonstrating how familiarity grows with encounters and decays over time.
"""

import sys
import os
from datetime import datetime, timedelta

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))

from chora.core import (
    Agent, SpatialExtent, Encounter, PlatialGraph,
    PlatialEdge, EdgeType
)
from chora.core.temporal import exponential_decay
from chora.derive import update_familiarity, extract_place


def run_familiarity_demo():
    print("📈 Familiarity Dynamics Demo")
    print("=" * 50)
    
    # Create scenario
    user = Agent.individual("Regular Visitor")
    cafe = SpatialExtent.point(-0.127, 51.507, "Neighbourhood Cafe")
    
    graph = PlatialGraph(name="Familiarity Demo")
    graph.add_node(user)
    graph.add_node(cafe)
    
    # Phase 1: Building familiarity (daily visits for 2 weeks)
    print("\n📅 Phase 1: Daily visits for 14 days")
    print("-" * 40)
    
    base_time = datetime.now() - timedelta(days=60)  # Start 60 days ago
    familiarity_history = []
    
    for day in range(14):
        visit_time = base_time + timedelta(days=day, hours=8)
        
        encounter = Encounter(
            agent_id=user.id,
            extent_id=cafe.id,
            start_time=visit_time,
            end_time=visit_time + timedelta(minutes=30),
            activity="morning_coffee"
        )
        graph.add_node(encounter)
        graph.add_edge(PlatialEdge.participates_in(user.id, encounter.id))
        graph.add_edge(PlatialEdge.occurs_at(encounter.id, cafe.id))
        
        fam = update_familiarity(graph, encounter)
        familiarity_history.append((day, fam.value))
        
        if day % 3 == 0:
            print(f"  Day {day+1:2d}: familiarity = {fam.value:.3f}")
    
    print(f"\n  Final familiarity after 14 daily visits: {familiarity_history[-1][1]:.3f}")
    
    # Phase 2: No visits for 3 weeks (decay)
    print("\n📅 Phase 2: 21 days without visits (decay)")
    print("-" * 40)
    
    # Get the familiarity node
    place = extract_place(graph, cafe.id, user.id)
    initial_fam = place.familiarity_score
    
    # Simulate decay at different time points
    half_life = 14.0  # days
    
    for days_elapsed in [7, 14, 21]:
        decayed = initial_fam * (0.5 ** (days_elapsed / half_life))
        print(f"  After {days_elapsed:2d} days: familiarity = {decayed:.3f} "
              f"({(1 - decayed/initial_fam)*100:.0f}% decay)")
    
    # Phase 3: Return with weekly visits
    print("\n📅 Phase 3: Weekly visits for 4 weeks (recovery)")
    print("-" * 40)
    
    # Continue from day 35 (14 daily + 21 gap)
    recovery_start = base_time + timedelta(days=35)
    
    for week in range(4):
        visit_time = recovery_start + timedelta(weeks=week, hours=10)
        
        encounter = Encounter(
            agent_id=user.id,
            extent_id=cafe.id,
            start_time=visit_time,
            end_time=visit_time + timedelta(hours=1),
            activity="weekend_coffee"
        )
        graph.add_node(encounter)
        graph.add_edge(PlatialEdge.participates_in(user.id, encounter.id))
        graph.add_edge(PlatialEdge.occurs_at(encounter.id, cafe.id))
        
        fam = update_familiarity(graph, encounter)
        print(f"  Week {week+1}: familiarity = {fam.value:.3f}")
    
    # Final analysis
    print("\n📊 Familiarity Trajectory Summary")
    print("-" * 40)
    
    final_place = extract_place(graph, cafe.id, user.id)
    print(f"  Total encounters: {final_place.encounter_count}")
    print(f"  Current familiarity: {final_place.familiarity_score:.3f}")
    print(f"  Character: {final_place.character}")
    
    # Explain the dynamics
    print("\n💡 Key Insights:")
    print("  • Familiarity grows ~0.03 per encounter (saturating)")
    print("  • Decay half-life: 14 days")
    print("  • More frequent visits → faster familiarity growth")
    print("  • Long gaps → significant familiarity loss")


if __name__ == "__main__":
    run_familiarity_demo()
