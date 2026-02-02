"""
Chora Example: Temporal Queries

Demonstrates querying graphs across time — snapshots, time ranges,
and temporal decay analysis.
"""

import sys
import os
from datetime import datetime, timedelta

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))

from chora.core import (
    Agent, SpatialExtent, Encounter, PlatialGraph,
    PlatialEdge, NodeType
)
from chora.query import snapshot_query, temporal_range_query
from chora.derive import update_familiarity, extract_place


def run_temporal_queries():
    print("⏰ Temporal Query Examples")
    print("=" * 50)
    
    # Build a graph with temporal data
    graph = PlatialGraph(name="Temporal Demo")
    
    user = Agent.individual("Temporal User")
    cafe = SpatialExtent.point(-0.127, 51.507, "Morning Cafe")
    park = SpatialExtent.point(-0.125, 51.509, "Lunch Park")
    
    graph.add_node(user)
    graph.add_node(cafe)
    graph.add_node(park)
    
    # Create encounters across different times
    base = datetime.now() - timedelta(days=60)
    
    encounters = []
    
    # Week 1-2: Regular cafe visits
    for day in range(14):
        enc = Encounter(
            agent_id=user.id,
            extent_id=cafe.id,
            start_time=base + timedelta(days=day, hours=8),
            end_time=base + timedelta(days=day, hours=8, minutes=30),
            activity="morning_coffee"
        )
        graph.add_node(enc)
        graph.add_edge(PlatialEdge.participates_in(user.id, enc.id))
        graph.add_edge(PlatialEdge.occurs_at(enc.id, cafe.id))
        update_familiarity(graph, enc)
        encounters.append(enc)
    
    # Week 4-5: Park visits start
    for day in range(21, 35):
        enc = Encounter(
            agent_id=user.id,
            extent_id=park.id,
            start_time=base + timedelta(days=day, hours=12),
            end_time=base + timedelta(days=day, hours=13),
            activity="lunch_walk"
        )
        graph.add_node(enc)
        graph.add_edge(PlatialEdge.participates_in(user.id, enc.id))
        graph.add_edge(PlatialEdge.occurs_at(enc.id, park.id))
        update_familiarity(graph, enc)
        encounters.append(enc)
    
    print(f"Created {len(encounters)} encounters")
    print(f"Cafe visits: days 0-13")
    print(f"Park visits: days 21-34")
    
    # Snapshot queries at different times
    print("\n📸 Snapshot Queries")
    print("-" * 40)
    
    # Day 7: Only cafe encounters exist
    day7 = base + timedelta(days=7)
    snap7 = snapshot_query(graph, at=day7)
    enc_count = snap7.node_count_by_type(NodeType.ENCOUNTER)
    print(f"Day 7 snapshot: {enc_count} encounters (cafe only)")
    
    # Day 28: Both locations have encounters
    day28 = base + timedelta(days=28)
    snap28 = snapshot_query(graph, at=day28)
    enc_count = snap28.node_count_by_type(NodeType.ENCOUNTER)
    print(f"Day 28 snapshot: {enc_count} encounters (cafe + park)")
    
    # Today: All encounters visible
    today = datetime.now()
    snap_now = snapshot_query(graph, at=today)
    enc_count = snap_now.node_count_by_type(NodeType.ENCOUNTER)
    print(f"Today snapshot: {enc_count} encounters (all)")
    
    # Range queries
    print("\n📅 Range Queries")
    print("-" * 40)
    
    # First two weeks
    week1_start = base
    week2_end = base + timedelta(days=14)
    early_nodes = list(temporal_range_query(graph, week1_start, week2_end))
    early_enc = [n for n in early_nodes if n.node_type == NodeType.ENCOUNTER]
    print(f"Weeks 1-2: {len(early_enc)} encounters")
    
    # Weeks 4-5
    week4_start = base + timedelta(days=21)
    week5_end = base + timedelta(days=35)
    late_nodes = list(temporal_range_query(graph, week4_start, week5_end))
    late_enc = [n for n in late_nodes if n.node_type == NodeType.ENCOUNTER]
    print(f"Weeks 4-5: {len(late_enc)} encounters")
    
    # Familiarity over time
    print("\n📈 Familiarity Timeline")
    print("-" * 40)
    
    # Cafe familiarity decays after week 2
    cafe_place = extract_place(graph, cafe.id, user.id)
    park_place = extract_place(graph, park.id, user.id)
    
    print(f"Cafe (no visits since day 14):")
    print(f"  Current familiarity: {cafe_place.familiarity_score:.3f}")
    print(f"  Note: Decayed over ~{(datetime.now() - (base + timedelta(days=14))).days} days")
    
    print(f"\nPark (visited until day 34):")
    print(f"  Current familiarity: {park_place.familiarity_score:.3f}")
    print(f"  Note: More recent, less decay")


if __name__ == "__main__":
    run_temporal_queries()
