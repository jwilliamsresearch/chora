"""
Chora Example: Graph Export

Demonstrates exporting platial graphs to various formats
for visualization and interoperability.
"""

import sys
import os
import json
from datetime import datetime, timedelta

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))

from chora.core import (
    Agent, SpatialExtent, Encounter, PlatialGraph,
    PlatialEdge, EdgeType, NodeType
)
from chora.derive import update_familiarity, extract_place, attach_affect


def graph_to_geojson(graph: PlatialGraph) -> dict:
    """
    Export spatial extents from graph to GeoJSON.
    
    Useful for visualizing places in GIS tools like QGIS, Kepler.gl, etc.
    """
    features = []
    
    for node in graph.nodes(NodeType.SPATIAL_EXTENT):
        # Extract geometry
        if hasattr(node, 'geometry') and node.geometry is not None:
            from shapely.geometry import mapping
            geom = mapping(node.geometry)
        else:
            # Fallback to point
            geom = {"type": "Point", "coordinates": [0, 0]}
        
        # Collect properties
        props = {
            "id": str(node.id),
            "name": node.name,
            "node_type": "spatial_extent"
        }
        
        # Add hints
        if hasattr(node, '_hints'):
            props.update(node._hints)
        
        features.append({
            "type": "Feature",
            "properties": props,
            "geometry": geom
        })
    
    return {
        "type": "FeatureCollection",
        "features": features
    }


def graph_to_graphml(graph: PlatialGraph) -> str:
    """
    Export graph to GraphML format.
    
    Useful for visualization in tools like Gephi, yEd, Cytoscape.
    """
    lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<graphml xmlns="http://graphml.graphdrawing.org/xmlns">',
        '  <key id="label" for="node" attr.name="label" attr.type="string"/>',
        '  <key id="type" for="node" attr.name="type" attr.type="string"/>',
        '  <key id="edge_type" for="edge" attr.name="edge_type" attr.type="string"/>',
        '  <key id="weight" for="edge" attr.name="weight" attr.type="double"/>',
        f'  <graph id="{graph.name}" edgedefault="directed">',
    ]
    
    # Add nodes
    for node in graph.nodes():
        label = getattr(node, 'name', str(node.id)[:8])
        node_type = node.node_type.value if hasattr(node.node_type, 'value') else str(node.node_type)
        lines.append(f'    <node id="{node.id}">')
        lines.append(f'      <data key="label">{label}</data>')
        lines.append(f'      <data key="type">{node_type}</data>')
        lines.append(f'    </node>')
    
    # Add edges
    for edge in graph.edges():
        edge_type = edge.edge_type.value if hasattr(edge.edge_type, 'value') else str(edge.edge_type)
        lines.append(f'    <edge id="{edge.id}" source="{edge.source_id}" target="{edge.target_id}">')
        lines.append(f'      <data key="edge_type">{edge_type}</data>')
        lines.append(f'      <data key="weight">{edge.weight}</data>')
        lines.append(f'    </edge>')
    
    lines.append('  </graph>')
    lines.append('</graphml>')
    
    return '\n'.join(lines)


def graph_to_d3_json(graph: PlatialGraph) -> dict:
    """
    Export graph to D3.js-compatible JSON format.
    
    Useful for web-based force-directed graph visualizations.
    """
    nodes = []
    links = []
    
    node_index = {}
    
    for i, node in enumerate(graph.nodes()):
        node_index[node.id] = i
        node_type = node.node_type.value if hasattr(node.node_type, 'value') else str(node.node_type)
        nodes.append({
            "id": str(node.id),
            "label": getattr(node, 'name', str(node.id)[:8]),
            "type": node_type,
            "group": hash(node_type) % 10
        })
    
    for edge in graph.edges():
        if edge.source_id in node_index and edge.target_id in node_index:
            edge_type = edge.edge_type.value if hasattr(edge.edge_type, 'value') else str(edge.edge_type)
            links.append({
                "source": node_index[edge.source_id],
                "target": node_index[edge.target_id],
                "type": edge_type,
                "weight": edge.weight
            })
    
    return {"nodes": nodes, "links": links}


def run_export_example():
    print("📤 Graph Export Example")
    print("=" * 50)
    
    # Build a sample graph
    graph = PlatialGraph(name="Export Demo")
    
    user = Agent.individual("Demo User")
    park = SpatialExtent.from_bounds(-0.127, 51.507, -0.126, 51.508, "Central Park")
    cafe = SpatialExtent.point(-0.125, 51.509, "Corner Cafe")
    
    graph.add_node(user)
    graph.add_node(park)
    graph.add_node(cafe)
    
    # Add some encounters
    base = datetime.now() - timedelta(days=7)
    for i in range(3):
        enc = Encounter(
            agent_id=user.id,
            extent_id=park.id,
            start_time=base + timedelta(days=i),
            end_time=base + timedelta(days=i, hours=1)
        )
        graph.add_node(enc)
        graph.add_edge(PlatialEdge.participates_in(user.id, enc.id))
        graph.add_edge(PlatialEdge.occurs_at(enc.id, park.id))
        
        affect = attach_affect(enc, valence=0.7, arousal=0.3)
        graph.add_node(affect)
        graph.add_edge(PlatialEdge(enc.id, affect.id, EdgeType.EXPRESSES))
    
    print(f"Graph: {graph.node_count} nodes, {graph.edge_count} edges")
    
    # Export to GeoJSON
    print("\n📍 GeoJSON Export (spatial extents only)")
    print("-" * 40)
    geojson = graph_to_geojson(graph)
    print(json.dumps(geojson, indent=2)[:500] + "...")
    
    # Export to GraphML
    print("\n📊 GraphML Export (first 20 lines)")
    print("-" * 40)
    graphml = graph_to_graphml(graph)
    for line in graphml.split('\n')[:20]:
        print(line)
    print("...")
    
    # Export to D3 JSON
    print("\n🌐 D3.js JSON Export")
    print("-" * 40)
    d3_data = graph_to_d3_json(graph)
    print(f"Nodes: {len(d3_data['nodes'])}")
    print(f"Links: {len(d3_data['links'])}")
    print(json.dumps(d3_data, indent=2)[:400] + "...")
    
    # Save examples
    output_dir = os.path.dirname(__file__)
    
    print(f"\n💾 To save exports:")
    print(f"   with open('places.geojson', 'w') as f:")
    print(f"       json.dump(graph_to_geojson(graph), f)")
    print(f"   ")
    print(f"   with open('graph.graphml', 'w') as f:")
    print(f"       f.write(graph_to_graphml(graph))")


if __name__ == "__main__":
    run_export_example()
