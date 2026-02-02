"""
Chora Example: Loading Real GPX Traces

Demonstrates loading actual GPS traces from GPX files and extracting
encounters with real-world locations.

Requires: gpxpy (pip install gpxpy)
"""

import sys
import os
from datetime import datetime, timedelta
from pathlib import Path

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))

from chora.core import (
    Agent, SpatialExtent, Encounter, PlatialGraph,
    PlatialEdge, EdgeType
)
from chora.derive import update_familiarity, extract_place

# Sample GPX data (embedded for portability)
SAMPLE_GPX = """<?xml version="1.0" encoding="UTF-8"?>
<gpx version="1.1">
  <trk>
    <name>Morning Walk</name>
    <trkseg>
      <trkpt lat="51.5074" lon="-0.1278"><time>2024-06-15T08:00:00Z</time></trkpt>
      <trkpt lat="51.5076" lon="-0.1275"><time>2024-06-15T08:05:00Z</time></trkpt>
      <trkpt lat="51.5078" lon="-0.1270"><time>2024-06-15T08:10:00Z</time></trkpt>
      <trkpt lat="51.5080" lon="-0.1265"><time>2024-06-15T08:15:00Z</time></trkpt>
      <trkpt lat="51.5082" lon="-0.1260"><time>2024-06-15T08:20:00Z</time></trkpt>
      <trkpt lat="51.5085" lon="-0.1255"><time>2024-06-15T08:30:00Z</time></trkpt>
      <trkpt lat="51.5085" lon="-0.1255"><time>2024-06-15T08:45:00Z</time></trkpt>
      <trkpt lat="51.5085" lon="-0.1254"><time>2024-06-15T09:00:00Z</time></trkpt>
      <trkpt lat="51.5080" lon="-0.1265"><time>2024-06-15T09:15:00Z</time></trkpt>
      <trkpt lat="51.5074" lon="-0.1278"><time>2024-06-15T09:30:00Z</time></trkpt>
    </trkseg>
  </trk>
</gpx>
"""


def parse_gpx_string(gpx_string: str) -> list[tuple[datetime, float, float]]:
    """Parse GPX string into list of (timestamp, lat, lon) tuples."""
    import xml.etree.ElementTree as ET
    
    root = ET.fromstring(gpx_string)
    ns = {'gpx': 'http://www.topografix.com/GPX/1/1'}
    
    points = []
    # Handle both namespaced and non-namespaced GPX
    for trkpt in root.iter():
        if 'trkpt' in trkpt.tag:
            lat = float(trkpt.get('lat'))
            lon = float(trkpt.get('lon'))
            
            time_elem = None
            for child in trkpt:
                if 'time' in child.tag:
                    time_elem = child
                    break
            
            if time_elem is not None:
                # Parse ISO timestamp
                ts = time_elem.text.replace('Z', '+00:00')
                dt = datetime.fromisoformat(ts.replace('+00:00', ''))
                points.append((dt, lat, lon))
    
    return points


def load_gpx_file(filepath: str) -> list[tuple[datetime, float, float]]:
    """Load GPX file and return points."""
    with open(filepath, 'r') as f:
        return parse_gpx_string(f.read())


def detect_stops(points: list, min_duration_minutes: float = 10, 
                 radius_meters: float = 50) -> list[dict]:
    """
    Detect stops (dwell locations) from GPS trace.
    
    A stop is where the agent remained within `radius_meters` 
    for at least `min_duration_minutes`.
    """
    from math import radians, sin, cos, sqrt, atan2
    
    def haversine(lat1, lon1, lat2, lon2):
        R = 6371000  # Earth radius in meters
        phi1, phi2 = radians(lat1), radians(lat2)
        dphi = radians(lat2 - lat1)
        dlam = radians(lon2 - lon1)
        a = sin(dphi/2)**2 + cos(phi1)*cos(phi2)*sin(dlam/2)**2
        return 2 * R * atan2(sqrt(a), sqrt(1-a))
    
    stops = []
    i = 0
    
    while i < len(points):
        start_time, start_lat, start_lon = points[i]
        
        j = i + 1
        while j < len(points):
            dt, lat, lon = points[j]
            dist = haversine(start_lat, start_lon, lat, lon)
            
            if dist > radius_meters:
                break
            j += 1
        
        # Check if we stayed long enough
        if j > i + 1:
            end_time = points[j-1][0]
            duration = (end_time - start_time).total_seconds() / 60
            
            if duration >= min_duration_minutes:
                # Calculate centroid
                lats = [points[k][1] for k in range(i, j)]
                lons = [points[k][2] for k in range(i, j)]
                
                stops.append({
                    'start_time': start_time,
                    'end_time': end_time,
                    'lat': sum(lats) / len(lats),
                    'lon': sum(lons) / len(lons),
                    'duration_minutes': duration,
                    'point_count': j - i
                })
        
        i = max(i + 1, j)
    
    return stops


def run_gpx_example():
    print("🗺️  Real GPX Trace Analysis")
    print("=" * 50)
    
    # Parse the sample GPX
    points = parse_gpx_string(SAMPLE_GPX)
    print(f"Loaded {len(points)} GPS points")
    print(f"Time range: {points[0][0]} to {points[-1][0]}")
    
    # Detect stops (potential encounters)
    stops = detect_stops(points, min_duration_minutes=10)
    print(f"\nDetected {len(stops)} stops:")
    
    for i, stop in enumerate(stops):
        print(f"  Stop {i+1}: {stop['duration_minutes']:.0f} min at "
              f"({stop['lat']:.4f}, {stop['lon']:.4f})")
    
    # Build platial graph
    graph = PlatialGraph(name="GPX Trace Analysis")
    user = Agent.individual("GPX User")
    graph.add_node(user)
    
    # Create extents for each stop
    for i, stop in enumerate(stops):
        extent = SpatialExtent.point(
            stop['lon'], stop['lat'],
            name=f"Stop {i+1}"
        )
        graph.add_node(extent)
        
        # Create encounter
        encounter = Encounter(
            agent_id=user.id,
            extent_id=extent.id,
            start_time=stop['start_time'],
            end_time=stop['end_time'],
            activity="detected_stop"
        )
        graph.add_node(encounter)
        graph.add_edge(PlatialEdge.participates_in(user.id, encounter.id))
        graph.add_edge(PlatialEdge.occurs_at(encounter.id, extent.id))
        
        update_familiarity(graph, encounter)
    
    print(f"\nGraph: {graph.node_count} nodes, {graph.edge_count} edges")
    
    # To use with a real GPX file:
    print("\n📁 To analyse your own GPX file:")
    print("   points = load_gpx_file('/path/to/your/trace.gpx')")
    print("   stops = detect_stops(points)")


if __name__ == "__main__":
    run_gpx_example()
