"""
Chora CLI — Command-line interface for the platial modelling library.

Usage:
    chora load gpx <file> --agent <id>
    chora load geojson <file>
    chora derive familiarity --agent <id>
    chora derive practices --agent <id>
    chora query familiar --agent <id> --min <value>
    chora viz export --format d3 --output <file>
"""
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Optional

import click

from chora.core import PlatialGraph, Agent, SpatialExtent, Encounter
from chora.adapters.memory import InMemoryAdapter


# Global graph instance for CLI session
_adapter = InMemoryAdapter()
_graph: PlatialGraph | None = None


def get_graph() -> PlatialGraph:
    """Get or create the active graph."""
    global _graph
    if _graph is None:
        _graph = PlatialGraph(name="cli_session")
    return _graph


# =============================================================================
# Main CLI Group
# =============================================================================

@click.group()
@click.version_option(version="0.1.0", prog_name="chora")
def cli():
    """Chora — A platial modelling library for Python.
    
    Model human experience of place with encounters, familiarity, affect, and practices.
    """
    pass


# =============================================================================
# Load Commands
# =============================================================================

@cli.group()
def load():
    """Load data into Chora graph."""
    pass


@load.command("gpx")
@click.argument("file", type=click.Path(exists=True))
@click.option("--agent", "-a", required=True, help="Agent ID for the trace")
@click.option("--activity", default="walking", help="Activity type")
def load_gpx(file: str, agent: str, activity: str):
    """Load GPX trace as encounters.
    
    Each trackpoint becomes an encounter at the corresponding location.
    """
    try:
        import gpxpy
    except ImportError:
        click.echo("Error: gpxpy not installed. Run: pip install gpxpy", err=True)
        sys.exit(1)
    
    graph = get_graph()
    path = Path(file)
    
    # Create or get agent
    agent_node = Agent.individual(agent)
    try:
        graph.add_node(agent_node)
    except Exception:
        pass  # Agent may already exist
    
    with open(path) as f:
        gpx = gpxpy.parse(f)
    
    encounter_count = 0
    for track in gpx.tracks:
        for segment in track.segments:
            for point in segment.points:
                # Create spatial extent for this point
                extent = SpatialExtent.from_point(
                    lon=point.longitude,
                    lat=point.latitude,
                    name=f"point_{encounter_count}"
                )
                try:
                    graph.add_node(extent)
                except Exception:
                    pass
                
                # Create encounter
                enc = Encounter(
                    agent_id=agent_node.id,
                    extent_id=extent.id,
                    start_time=point.time,
                    activity=activity
                )
                graph.add_node(enc)
                encounter_count += 1
    
    click.echo(f"✓ Loaded {encounter_count} encounters from {path.name}")


@load.command("geojson")
@click.argument("file", type=click.Path(exists=True))
@click.option("--name-field", default="name", help="Property to use as name")
def load_geojson(file: str, name_field: str):
    """Load GeoJSON as spatial extents."""
    graph = get_graph()
    path = Path(file)
    
    with open(path) as f:
        data = json.load(f)
    
    features = data.get("features", [])
    extent_count = 0
    
    for feature in features:
        props = feature.get("properties", {})
        geom = feature.get("geometry", {})
        
        name = props.get(name_field, f"feature_{extent_count}")
        
        if geom.get("type") == "Point":
            coords = geom.get("coordinates", [0, 0])
            extent = SpatialExtent.from_point(
                lon=coords[0], lat=coords[1], name=name
            )
        elif geom.get("type") == "Polygon":
            from shapely.geometry import shape
            extent = SpatialExtent(
                geometry=shape(geom),
                name=name
            )
        else:
            continue
        
        try:
            graph.add_node(extent)
            extent_count += 1
        except Exception:
            pass
    
    click.echo(f"✓ Loaded {extent_count} extents from {path.name}")


@load.command("csv")
@click.argument("file", type=click.Path(exists=True))
@click.option("--lon-col", default="longitude", help="Longitude column")
@click.option("--lat-col", default="latitude", help="Latitude column")
@click.option("--name-col", default="name", help="Name column")
def load_csv(file: str, lon_col: str, lat_col: str, name_col: str):
    """Load CSV as spatial extents."""
    import csv
    
    graph = get_graph()
    path = Path(file)
    
    extent_count = 0
    with open(path) as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                lon = float(row.get(lon_col, 0))
                lat = float(row.get(lat_col, 0))
                name = row.get(name_col, f"point_{extent_count}")
                
                extent = SpatialExtent.from_point(lon=lon, lat=lat, name=name)
                graph.add_node(extent)
                extent_count += 1
            except (ValueError, KeyError):
                continue
    
    click.echo(f"✓ Loaded {extent_count} extents from {path.name}")


# =============================================================================
# Derive Commands
# =============================================================================

@cli.group()
def derive():
    """Derive platial qualities from data."""
    pass


@derive.command("familiarity")
@click.option("--agent", "-a", required=True, help="Agent ID")
def derive_familiarity(agent: str):
    """Update familiarity scores for an agent."""
    from chora.derive import update_familiarity
    from chora.core.types import NodeType
    
    graph = get_graph()
    
    count = 0
    for node in graph.nodes(NodeType.ENCOUNTER):
        if hasattr(node, 'agent_id') and str(node.agent_id) == agent:
            update_familiarity(graph, node)
            count += 1
    
    click.echo(f"✓ Updated familiarity for {count} encounters")


@derive.command("practices")
@click.option("--agent", "-a", required=True, help="Agent ID")
@click.option("--min-occurrences", default=3, help="Minimum occurrences for routine")
def derive_practices(agent: str, min_occurrences: int):
    """Detect practices and routines for an agent."""
    from chora.derive.practices import detect_practices, PracticeDetectionConfig
    from chora.core.types import NodeType
    
    graph = get_graph()
    
    # Collect encounters
    encounters = [
        node for node in graph.nodes(NodeType.ENCOUNTER)
        if hasattr(node, 'agent_id') and str(node.agent_id) == agent
    ]
    
    config = PracticeDetectionConfig(min_occurrences=min_occurrences)
    practices = detect_practices(encounters, agent, config)
    
    click.echo(f"✓ Detected {len(practices)} practices for agent '{agent}':")
    for p in practices:
        click.echo(f"  - {p.name} ({p.practice_type.name}, regularity={p.regularity:.2f})")


# =============================================================================
# Query Commands
# =============================================================================

@cli.group()
def query():
    """Query the platial graph."""
    pass


@query.command("familiar")
@click.option("--agent", "-a", required=True, help="Agent ID")
@click.option("--min", "min_val", default=0.5, help="Minimum familiarity")
def query_familiar(agent: str, min_val: float):
    """Find places where agent has high familiarity."""
    from chora.query import find_familiar_places
    from chora.core.types import AgentId
    
    graph = get_graph()
    places = find_familiar_places(graph, AgentId(agent), min_familiarity=min_val)
    
    click.echo(f"Found {len(places)} familiar places (familiarity ≥ {min_val}):")
    for p in places:
        click.echo(f"  - {p.extent.name}: {p.familiarity_score:.2f}")


@query.command("stats")
def query_stats():
    """Show graph statistics."""
    from chora.core.types import NodeType
    
    graph = get_graph()
    
    click.echo("Graph Statistics:")
    click.echo(f"  Name: {graph.name}")
    click.echo(f"  Total nodes: {graph.node_count}")
    click.echo(f"  Total edges: {graph.edge_count}")
    
    for node_type in NodeType:
        count = len(list(graph.nodes(node_type)))
        if count > 0:
            click.echo(f"  {node_type.name}: {count}")


# =============================================================================
# Viz Commands
# =============================================================================

@cli.group()
def viz():
    """Visualization and export commands."""
    pass


@viz.command("export")
@click.option("--format", "-f", "fmt", type=click.Choice(["d3", "json", "dot"]), default="d3")
@click.option("--output", "-o", type=click.Path(), help="Output file")
def viz_export(fmt: str, output: Optional[str]):
    """Export graph for visualization."""
    graph = get_graph()
    
    if fmt == "d3" or fmt == "json":
        data = export_d3(graph)
        result = json.dumps(data, indent=2, default=str)
    elif fmt == "dot":
        result = export_dot(graph)
    else:
        result = "{}"
    
    if output:
        Path(output).write_text(result)
        click.echo(f"✓ Exported to {output}")
    else:
        click.echo(result)


def export_d3(graph: PlatialGraph) -> dict:
    """Export graph to D3.js-compatible JSON."""
    nodes = []
    links = []
    
    node_ids = []
    for node in graph.nodes():
        nodes.append({
            "id": str(node.id),
            "type": node.node_type.name,
            "name": getattr(node, "name", str(node.id)[:20])
        })
        node_ids.append(str(node.id))
    
    for edge in graph.edges():
        if str(edge.source_id) in node_ids and str(edge.target_id) in node_ids:
            links.append({
                "source": str(edge.source_id),
                "target": str(edge.target_id),
                "type": edge.edge_type.name,
                "weight": edge.weight
            })
    
    return {"nodes": nodes, "links": links}


def export_dot(graph: PlatialGraph) -> str:
    """Export graph to GraphViz DOT format."""
    lines = ["digraph chora {"]
    lines.append("  rankdir=LR;")
    lines.append("  node [shape=box];")
    
    for node in graph.nodes():
        name = getattr(node, "name", str(node.id)[:20])
        lines.append(f'  "{node.id}" [label="{name}"];')
    
    for edge in graph.edges():
        lines.append(f'  "{edge.source_id}" -> "{edge.target_id}" [label="{edge.edge_type.name}"];')
    
    lines.append("}")
    return "\n".join(lines)


@viz.command("timeline")
@click.option("--agent", "-a", required=True, help="Agent ID")
@click.option("--output", "-o", type=click.Path(), help="Output HTML file")
def viz_timeline(agent: str, output: Optional[str]):
    """Generate timeline visualization for an agent."""
    from chora.core.types import NodeType
    
    graph = get_graph()
    
    # Collect encounters
    encounters = []
    for node in graph.nodes(NodeType.ENCOUNTER):
        if hasattr(node, 'agent_id') and str(node.agent_id) == agent:
            encounters.append({
                "time": str(getattr(node, 'start_time', '')),
                "extent": str(getattr(node, 'extent_id', '')),
                "activity": getattr(node, 'activity', 'unknown')
            })
    
    html = generate_timeline_html(encounters, agent)
    
    if output:
        Path(output).write_text(html)
        click.echo(f"✓ Timeline exported to {output}")
    else:
        click.echo(f"Generated timeline with {len(encounters)} events")


def generate_timeline_html(encounters: list, agent: str) -> str:
    """Generate simple HTML timeline."""
    events_json = json.dumps(encounters, default=str)
    return f"""<!DOCTYPE html>
<html>
<head>
    <title>Chora Timeline - {agent}</title>
    <style>
        body {{ font-family: system-ui; max-width: 800px; margin: 0 auto; padding: 2rem; }}
        .event {{ padding: 1rem; margin: 0.5rem 0; background: #f0f0f0; border-radius: 4px; }}
        .time {{ font-size: 0.9rem; color: #666; }}
    </style>
</head>
<body>
    <h1>Timeline: {agent}</h1>
    <div id="timeline"></div>
    <script>
        const events = {events_json};
        const container = document.getElementById('timeline');
        events.forEach(e => {{
            container.innerHTML += `<div class="event">
                <div class="time">${{e.time}}</div>
                <strong>${{e.extent}}</strong> - ${{e.activity}}
            </div>`;
        }});
    </script>
</body>
</html>"""


# =============================================================================
# Entry Point
# =============================================================================

def main():
    """CLI entry point."""
    cli()


if __name__ == "__main__":
    main()
