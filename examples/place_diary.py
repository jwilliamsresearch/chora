"""
Chora Example: Experience Sampling / Place Diary

Demonstrates loading and analysing data from experience sampling
methodology (ESM) or place diary studies — a common format in
human geography and environmental psychology research.
"""

import sys
import os
import csv
from datetime import datetime
from io import StringIO

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))

from chora.core import (
    Agent, SpatialExtent, Encounter, PlatialGraph,
    PlatialEdge, EdgeType, Context
)
from chora.derive import update_familiarity, attach_affect, extract_place
from chora.query import find_positive_places

# Sample diary data (typical ESM/diary study format)
SAMPLE_DIARY_CSV = """timestamp,participant_id,location_name,latitude,longitude,activity,companions,mood_valence,mood_arousal,notes
2024-06-10T08:30:00,P001,Home,-0.1280,51.5070,breakfast,family,0.7,0.3,Relaxed morning
2024-06-10T09:15:00,P001,Tube Station,-0.1260,51.5090,commuting,alone,-0.2,0.6,Crowded train
2024-06-10T09:45:00,P001,Office,-0.1200,51.5150,working,colleagues,0.3,0.5,Busy day ahead
2024-06-10T12:30:00,P001,Park,-0.1180,51.5160,lunch,colleague,0.8,0.3,Nice weather today
2024-06-10T17:30:00,P001,Gym,-0.1150,51.5080,exercise,alone,0.6,0.8,Good workout
2024-06-10T19:00:00,P001,Home,-0.1280,51.5070,dinner,family,0.8,0.2,Tired but content
2024-06-11T08:00:00,P001,Home,-0.1280,51.5070,breakfast,alone,0.5,0.3,Quiet morning
2024-06-11T09:00:00,P001,Cafe,-0.1240,51.5100,coffee,friend,0.9,0.4,Catching up
2024-06-11T11:00:00,P001,Library,-0.1220,51.5120,reading,alone,0.6,0.2,Peaceful
2024-06-11T14:00:00,P001,Park,-0.1180,51.5160,walking,alone,0.7,0.4,Afternoon stroll
2024-06-11T18:00:00,P001,Restaurant,-0.1190,51.5090,dinner,partner,0.9,0.5,Date night
"""


def parse_diary_csv(csv_string: str) -> list[dict]:
    """Parse diary/ESM data from CSV."""
    reader = csv.DictReader(StringIO(csv_string))
    entries = []
    
    for row in reader:
        entry = {
            'timestamp': datetime.fromisoformat(row['timestamp']),
            'participant_id': row['participant_id'],
            'location_name': row['location_name'],
            'lat': float(row['latitude']),
            'lon': float(row['longitude']),
            'activity': row['activity'],
            'companions': row.get('companions', 'alone'),
            'valence': float(row.get('mood_valence', 0)),
            'arousal': float(row.get('mood_arousal', 0.5)),
            'notes': row.get('notes', '')
        }
        entries.append(entry)
    
    return entries


def load_diary_file(filepath: str) -> list[dict]:
    """Load diary data from CSV file."""
    with open(filepath, 'r') as f:
        return parse_diary_csv(f.read())


def run_diary_example():
    print("📓 Experience Sampling / Place Diary Analysis")
    print("=" * 50)
    
    # Parse diary entries
    entries = parse_diary_csv(SAMPLE_DIARY_CSV)
    print(f"Loaded {len(entries)} diary entries")
    
    # Group by participant
    participants = {}
    for entry in entries:
        pid = entry['participant_id']
        if pid not in participants:
            participants[pid] = []
        participants[pid].append(entry)
    
    print(f"Participants: {', '.join(participants.keys())}")
    
    # Build graph for each participant
    for participant_id, diary_entries in participants.items():
        print(f"\n👤 Participant: {participant_id}")
        print("-" * 40)
        
        graph = PlatialGraph(name=f"Diary Study - {participant_id}")
        agent = Agent.individual(participant_id)
        graph.add_node(agent)
        
        # Track unique locations
        locations = {}
        
        for entry in diary_entries:
            loc_name = entry['location_name']
            
            # Create or reuse extent
            if loc_name not in locations:
                extent = SpatialExtent.point(entry['lon'], entry['lat'], loc_name)
                locations[loc_name] = extent
                graph.add_node(extent)
            else:
                extent = locations[loc_name]
            
            # Create encounter
            encounter = Encounter(
                agent_id=agent.id,
                extent_id=extent.id,
                start_time=entry['timestamp'],
                activity=entry['activity']
            )
            graph.add_node(encounter)
            graph.add_edge(PlatialEdge.participates_in(agent.id, encounter.id))
            graph.add_edge(PlatialEdge.occurs_at(encounter.id, extent.id))
            
            # Add social context
            if entry['companions'] != 'alone':
                ctx = Context.social(companions=entry['companions'].split(','))
                graph.add_node(ctx)
                graph.add_edge(PlatialEdge(
                    source_id=encounter.id, target_id=ctx.id,
                    edge_type=EdgeType.HAS_CONTEXT
                ))
            
            # Add affect from mood ratings
            affect = attach_affect(
                encounter,
                valence=entry['valence'],
                arousal=entry['arousal'],
                source="self_report"
            )
            graph.add_node(affect)
            graph.add_edge(PlatialEdge(
                source_id=encounter.id, target_id=affect.id,
                edge_type=EdgeType.EXPRESSES
            ))
            
            # Update familiarity
            update_familiarity(graph, encounter)
        
        # Analyse places
        print(f"\n  Locations visited: {len(locations)}")
        
        print("\n  Place Analysis:")
        for loc_name, extent in locations.items():
            place = extract_place(graph, extent.id, agent.id)
            visit_count = place.encounter_count
            avg_valence = place.affect_valence_mean
            
            # Emoji based on valence
            if avg_valence > 0.6:
                emoji = "😊"
            elif avg_valence > 0.3:
                emoji = "🙂"
            elif avg_valence > -0.2:
                emoji = "😐"
            else:
                emoji = "😔"
            
            print(f"    {emoji} {loc_name:15} | visits: {visit_count} | "
                  f"valence: {avg_valence:+.2f} | {place.character}")
        
        # Find positive places
        positive = find_positive_places(graph, agent.id)
        if positive:
            print(f"\n  ✨ Positive places: {', '.join(p.extent.name for p in positive)}")
        
        # Activity analysis
        print("\n  Activity by Location:")
        activity_by_loc = {}
        for entry in diary_entries:
            loc = entry['location_name']
            act = entry['activity']
            if loc not in activity_by_loc:
                activity_by_loc[loc] = set()
            activity_by_loc[loc].add(act)
        
        for loc, activities in activity_by_loc.items():
            print(f"    {loc}: {', '.join(activities)}")
    
    # Show how to load real data
    print("\n📁 To load your own diary data:")
    print("   entries = load_diary_file('/path/to/diary.csv')")
    print("   ")
    print("   Required columns: timestamp, participant_id, location_name,")
    print("                     latitude, longitude, activity")
    print("   Optional columns: companions, mood_valence, mood_arousal, notes")


if __name__ == "__main__":
    run_diary_example()
