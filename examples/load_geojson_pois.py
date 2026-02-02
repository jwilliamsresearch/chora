"""
Chora Example: Loading GeoJSON POIs

Demonstrates loading real-world Points of Interest from GeoJSON
(e.g., OpenStreetMap exports, Overture Maps data) into Chora spatial extents.
"""

import sys
import os
import json
from datetime import datetime

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))

from chora.core import SpatialExtent, PlatialGraph
from chora.core.types import EpistemicLevel

# Sample GeoJSON (could be from OSM, Overture, or any GeoJSON source)
SAMPLE_GEOJSON = {
    "type": "FeatureCollection",
    "features": [
        {
            "type": "Feature",
            "properties": {
                "name": "British Museum",
                "amenity": "museum",
                "opening_hours": "10:00-17:00"
            },
            "geometry": {
                "type": "Point",
                "coordinates": [-0.1269, 51.5194]
            }
        },
        {
            "type": "Feature",
            "properties": {
                "name": "Russell Square",
                "leisure": "park"
            },
            "geometry": {
                "type": "Polygon",
                "coordinates": [[
                    [-0.1270, 51.5220],
                    [-0.1250, 51.5220],
                    [-0.1250, 51.5210],
                    [-0.1270, 51.5210],
                    [-0.1270, 51.5220]
                ]]
            }
        },
        {
            "type": "Feature",
            "properties": {
                "name": "King's Cross Station",
                "railway": "station",
                "public_transport": "station"
            },
            "geometry": {
                "type": "Point",
                "coordinates": [-0.1233, 51.5309]
            }
        },
        {
            "type": "Feature",
            "properties": {
                "name": "Regent's Park",
                "leisure": "park",
                "access": "public"
            },
            "geometry": {
                "type": "Polygon",
                "coordinates": [[
                    [-0.1600, 51.5350],
                    [-0.1400, 51.5350],
                    [-0.1400, 51.5250],
                    [-0.1600, 51.5250],
                    [-0.1600, 51.5350]
                ]]
            }
        }
    ]
}


def load_geojson_string(geojson_str: str) -> list[dict]:
    """Parse GeoJSON string and return features."""
    data = json.loads(geojson_str) if isinstance(geojson_str, str) else geojson_str
    
    if data.get("type") == "FeatureCollection":
        return data["features"]
    elif data.get("type") == "Feature":
        return [data]
    else:
        raise ValueError("Invalid GeoJSON: expected Feature or FeatureCollection")


def load_geojson_file(filepath: str) -> list[dict]:
    """Load GeoJSON file."""
    with open(filepath, 'r') as f:
        return load_geojson_string(json.load(f))


def geojson_to_extent(feature: dict) -> SpatialExtent:
    """
    Convert a GeoJSON feature to a Chora SpatialExtent.
    
    Supports Point and Polygon geometries.
    """
    props = feature.get("properties", {})
    geom = feature["geometry"]
    
    name = props.get("name", "Unnamed")
    
    if geom["type"] == "Point":
        lon, lat = geom["coordinates"]
        extent = SpatialExtent.point(lon, lat, name)
        
    elif geom["type"] == "Polygon":
        coords = geom["coordinates"][0]  # Outer ring
        lons = [c[0] for c in coords]
        lats = [c[1] for c in coords]
        extent = SpatialExtent.from_bounds(
            min(lons), min(lats), max(lons), max(lats), name
        )
        
    else:
        # For complex geometries, create from bounding box
        coords = _flatten_coords(geom["coordinates"])
        lons = [c[0] for c in coords]
        lats = [c[1] for c in coords]
        extent = SpatialExtent.from_bounds(
            min(lons), min(lats), max(lons), max(lats), name
        )
    
    # Transfer properties as hints
    for key, value in props.items():
        if key != "name" and isinstance(value, (str, int, float, bool)):
            extent.set_hint(key, value)
    
    # Mark as observed data (from external source)
    extent.epistemic_level = EpistemicLevel.OBSERVED
    
    return extent


def _flatten_coords(coords):
    """Recursively flatten coordinate arrays."""
    if isinstance(coords[0], (int, float)):
        return [coords]
    result = []
    for c in coords:
        result.extend(_flatten_coords(c))
    return result


def categorise_poi(extent: SpatialExtent) -> str:
    """Categorise a POI based on OSM-style tags."""
    hints = {k: extent.get_hint(k) for k in ['amenity', 'leisure', 'railway', 
                                               'shop', 'tourism', 'public_transport']}
    
    if hints.get('leisure') == 'park':
        return 'recreation'
    elif hints.get('amenity') == 'museum':
        return 'culture'
    elif hints.get('railway') or hints.get('public_transport'):
        return 'transport'
    elif hints.get('shop'):
        return 'commercial'
    elif hints.get('tourism'):
        return 'tourism'
    else:
        return 'other'


def run_geojson_example():
    print("📍 Real GeoJSON POI Loading")
    print("=" * 50)
    
    # Load features
    features = load_geojson_string(SAMPLE_GEOJSON)
    print(f"Loaded {len(features)} features from GeoJSON")
    
    # Convert to extents
    graph = PlatialGraph(name="London POIs")
    
    print("\nConverted features:")
    for feature in features:
        extent = geojson_to_extent(feature)
        category = categorise_poi(extent)
        extent.set_hint("category", category)
        
        graph.add_node(extent)
        
        geom_type = feature["geometry"]["type"]
        print(f"  • {extent.name} [{geom_type}] → {category}")
    
    print(f"\nGraph: {graph.node_count} spatial extents")
    
    # Query by category
    print("\n📊 By Category:")
    from chora.core import NodeType
    extents = list(graph.nodes(NodeType.SPATIAL_EXTENT))
    
    categories = {}
    for ext in extents:
        cat = ext.get_hint("category") or "other"
        categories[cat] = categories.get(cat, 0) + 1
    
    for cat, count in sorted(categories.items()):
        print(f"  {cat}: {count}")
    
    # Show how to load real data
    print("\n📁 To load real GeoJSON data:")
    print("   # From file")
    print("   features = load_geojson_file('/path/to/pois.geojson')")
    print("   ")
    print("   # From Overture Maps")
    print("   # overturemaps download --bbox=-0.2,51.4,-0.1,51.6 -f geojson places")
    print("   ")
    print("   # From OpenStreetMap via Overpass")
    print("   # Use overpass-turbo.eu to query and export GeoJSON")


if __name__ == "__main__":
    run_geojson_example()
