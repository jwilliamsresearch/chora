"""
Chora Example: Practice Detection

Demonstrates detecting routines, habits, and patterns from encounter data.
"""

import sys
import os
from datetime import datetime, timedelta
from random import Random

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))

from chora.core import (
    Agent, SpatialExtent, Encounter, PlatialGraph,
    PlatialEdge, PracticeType
)
from chora.derive import detect_practices, detect_routines, update_familiarity


def run_practice_detection():
    print("🔄 Practice Detection Example")
    print("=" * 50)
    
    # Create scenario
    user = Agent.individual("Routine Person")
    
    locations = {
        'home': SpatialExtent.point(-0.130, 51.510, "Home"),
        'gym': SpatialExtent.point(-0.125, 51.508, "Gym"),
        'office': SpatialExtent.point(-0.120, 51.515, "Office"),
        'cafe': SpatialExtent.point(-0.122, 51.513, "Coffee Shop"),
        'supermarket': SpatialExtent.point(-0.128, 51.509, "Supermarket"),
    }
    
    graph = PlatialGraph(name="Practice Detection")
    graph.add_node(user)
    for loc in locations.values():
        graph.add_node(loc)
    
    # Generate 4 weeks of activity with patterns
    base = datetime.now() - timedelta(days=28)
    rng = Random(42)
    encounters = []
    
    for day in range(28):
        date = base + timedelta(days=day)
        weekday = day % 7
        
        # Morning: home (always)
        enc = Encounter(
            agent_id=user.id,
            extent_id=locations['home'].id,
            start_time=date + timedelta(hours=7),
            end_time=date + timedelta(hours=8),
            activity="morning_routine"
        )
        graph.add_node(enc)
        graph.add_edge(PlatialEdge.participates_in(user.id, enc.id))
        graph.add_edge(PlatialEdge.occurs_at(enc.id, locations['home'].id))
        encounters.append(enc)
        
        if weekday < 5:  # Weekdays
            # Morning gym (Mon, Wed, Fri)
            if weekday in [0, 2, 4]:
                enc = Encounter(
                    agent_id=user.id,
                    extent_id=locations['gym'].id,
                    start_time=date + timedelta(hours=6, minutes=30),
                    end_time=date + timedelta(hours=7, minutes=30),
                    activity="workout"
                )
                graph.add_node(enc)
                graph.add_edge(PlatialEdge.participates_in(user.id, enc.id))
                graph.add_edge(PlatialEdge.occurs_at(enc.id, locations['gym'].id))
                encounters.append(enc)
            
            # Morning cafe (daily)
            enc = Encounter(
                agent_id=user.id,
                extent_id=locations['cafe'].id,
                start_time=date + timedelta(hours=8, minutes=15),
                end_time=date + timedelta(hours=8, minutes=45),
                activity="morning_coffee"
            )
            graph.add_node(enc)
            graph.add_edge(PlatialEdge.participates_in(user.id, enc.id))
            graph.add_edge(PlatialEdge.occurs_at(enc.id, locations['cafe'].id))
            encounters.append(enc)
            
            # Office (daily)
            enc = Encounter(
                agent_id=user.id,
                extent_id=locations['office'].id,
                start_time=date + timedelta(hours=9),
                end_time=date + timedelta(hours=17),
                activity="work"
            )
            graph.add_node(enc)
            graph.add_edge(PlatialEdge.participates_in(user.id, enc.id))
            graph.add_edge(PlatialEdge.occurs_at(enc.id, locations['office'].id))
            encounters.append(enc)
        
        # Weekly supermarket run (Saturday)
        if weekday == 5:
            enc = Encounter(
                agent_id=user.id,
                extent_id=locations['supermarket'].id,
                start_time=date + timedelta(hours=11),
                end_time=date + timedelta(hours=12),
                activity="grocery_shopping"
            )
            graph.add_node(enc)
            graph.add_edge(PlatialEdge.participates_in(user.id, enc.id))
            graph.add_edge(PlatialEdge.occurs_at(enc.id, locations['supermarket'].id))
            encounters.append(enc)
        
        # Evening: home (always)
        enc = Encounter(
            agent_id=user.id,
            extent_id=locations['home'].id,
            start_time=date + timedelta(hours=19),
            end_time=date + timedelta(hours=22),
            activity="evening_at_home"
        )
        graph.add_node(enc)
        graph.add_edge(PlatialEdge.participates_in(user.id, enc.id))
        graph.add_edge(PlatialEdge.occurs_at(enc.id, locations['home'].id))
        encounters.append(enc)
    
    print(f"Generated {len(encounters)} encounters over 28 days")
    
    # Detect practices
    print("\n📊 Detected Practices")
    print("-" * 40)
    
    practices = detect_practices(encounters, user.id)
    
    # Group by type
    routines = [p for p in practices if p.practice_type == PracticeType.ROUTINE]
    habits = [p for p in practices if p.practice_type == PracticeType.HABIT]
    rituals = [p for p in practices if p.practice_type == PracticeType.RITUAL]
    
    print(f"\nRoutines ({len(routines)}):")
    for p in routines[:5]:
        print(f"  • {p.name}")
        print(f"    Regularity: {p.regularity:.0%}")
        print(f"    Frequency: {p.frequency:.1f}/week")
    
    if habits:
        print(f"\nHabits ({len(habits)}):")
        for p in habits[:3]:
            print(f"  • {p.name} (regularity: {p.regularity:.0%})")
    
    # Analyse by location
    print("\n📍 Practices by Location")
    print("-" * 40)
    
    loc_practices = {}
    for enc in encounters:
        loc_id = enc.extent_id
        loc_name = next(l.name for l in locations.values() if l.id == loc_id)
        if loc_name not in loc_practices:
            loc_practices[loc_name] = []
        loc_practices[loc_name].append(enc.activity)
    
    for loc_name, activities in loc_practices.items():
        from collections import Counter
        counts = Counter(activities)
        top_activity = counts.most_common(1)[0]
        print(f"  {loc_name}: {top_activity[0]} ({top_activity[1]} times)")
    
    # Key insight
    print("\n💡 Key Patterns Detected:")
    print("  • Daily morning coffee routine (weekdays)")
    print("  • Tri-weekly gym habit (Mon/Wed/Fri)")
    print("  • Weekly grocery shopping (Saturday)")
    print("  • Home-based morning and evening rituals (daily)")


if __name__ == "__main__":
    run_practice_detection()
