"""
HTML Report Generation for Chora

Generate comprehensive HTML reports summarizing a platial graph.
"""
from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any

from chora.core import PlatialGraph
from chora.core.types import NodeType, NodeId


def generate_report(
    graph: PlatialGraph,
    output_path: str | Path,
    title: str = "Chora Report"
) -> None:
    """
    Generate a comprehensive HTML report for a platial graph.
    
    Includes summaries of agents, places, encounters, familiarity, and practices.
    """
    # Collect statistics
    stats = _collect_stats(graph)
    stats_json = json.dumps(stats, indent=2, default=str)
    
    html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>{title}</title>
    <style>
        * {{ box-sizing: border-box; }}
        body {{
            font-family: system-ui, -apple-system, sans-serif;
            margin: 0;
            padding: 0;
            background: #f5f5f5;
            color: #333;
        }}
        .header {{
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
            color: white;
            padding: 2rem;
            text-align: center;
        }}
        .header h1 {{
            margin: 0;
            font-size: 2rem;
        }}
        .header p {{
            margin: 0.5rem 0 0;
            opacity: 0.8;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            padding: 2rem;
        }}
        .grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
            gap: 1.5rem;
            margin-bottom: 2rem;
        }}
        .card {{
            background: white;
            border-radius: 12px;
            padding: 1.5rem;
            box-shadow: 0 2px 8px rgba(0,0,0,0.08);
        }}
        .card h2 {{
            margin: 0 0 1rem;
            font-size: 1.1rem;
            color: #1a1a2e;
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }}
        .stat-grid {{
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 1rem;
        }}
        .stat {{
            text-align: center;
            padding: 1rem;
            background: #f8f8f8;
            border-radius: 8px;
        }}
        .stat-value {{
            font-size: 1.8rem;
            font-weight: bold;
            color: #00d9ff;
        }}
        .stat-label {{
            font-size: 0.8rem;
            color: #666;
            margin-top: 0.25rem;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
        }}
        th, td {{
            padding: 0.75rem;
            text-align: left;
            border-bottom: 1px solid #eee;
        }}
        th {{
            background: #f8f8f8;
            font-weight: 600;
            font-size: 0.85rem;
            color: #666;
        }}
        .tag {{
            display: inline-block;
            padding: 0.25rem 0.5rem;
            background: #e0f7fa;
            color: #0097a7;
            border-radius: 4px;
            font-size: 0.8rem;
        }}
        .footer {{
            text-align: center;
            padding: 2rem;
            color: #888;
            font-size: 0.85rem;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>🗺️ {title}</h1>
        <p>Generated {datetime.now().strftime('%Y-%m-%d %H:%M')}</p>
    </div>
    
    <div class="container">
        <div class="grid">
            <div class="card">
                <h2>📊 Overview</h2>
                <div class="stat-grid">
                    <div class="stat">
                        <div class="stat-value" id="node-count">-</div>
                        <div class="stat-label">Total Nodes</div>
                    </div>
                    <div class="stat">
                        <div class="stat-value" id="edge-count">-</div>
                        <div class="stat-label">Total Edges</div>
                    </div>
                    <div class="stat">
                        <div class="stat-value" id="agent-count">-</div>
                        <div class="stat-label">Agents</div>
                    </div>
                    <div class="stat">
                        <div class="stat-value" id="place-count">-</div>
                        <div class="stat-label">Places</div>
                    </div>
                </div>
            </div>
            
            <div class="card">
                <h2>👤 Agents</h2>
                <table id="agents-table">
                    <thead>
                        <tr><th>Name</th><th>Encounters</th></tr>
                    </thead>
                    <tbody></tbody>
                </table>
            </div>
            
            <div class="card">
                <h2>📍 Top Places</h2>
                <table id="places-table">
                    <thead>
                        <tr><th>Name</th><th>Visits</th></tr>
                    </thead>
                    <tbody></tbody>
                </table>
            </div>
            
            <div class="card">
                <h2>🔄 Node Types</h2>
                <table id="types-table">
                    <thead>
                        <tr><th>Type</th><th>Count</th></tr>
                    </thead>
                    <tbody></tbody>
                </table>
            </div>
        </div>
    </div>
    
    <div class="footer">
        Generated by Chora — A Platial Modelling Library
    </div>
    
    <script>
        const stats = {stats_json};
        
        document.getElementById('node-count').textContent = stats.node_count;
        document.getElementById('edge-count').textContent = stats.edge_count;
        document.getElementById('agent-count').textContent = stats.agent_count;
        document.getElementById('place-count').textContent = stats.place_count;
        
        // Agents
        const agentsBody = document.querySelector('#agents-table tbody');
        stats.agents.forEach(a => {{
            agentsBody.innerHTML += `<tr><td>${{a.name}}</td><td>${{a.encounter_count}}</td></tr>`;
        }});
        
        // Places
        const placesBody = document.querySelector('#places-table tbody');
        stats.top_places.forEach(p => {{
            placesBody.innerHTML += `<tr><td>${{p.name}}</td><td>${{p.visit_count}}</td></tr>`;
        }});
        
        // Types
        const typesBody = document.querySelector('#types-table tbody');
        Object.entries(stats.node_types).forEach(([type, count]) => {{
            typesBody.innerHTML += `<tr><td><span class="tag">${{type}}</span></td><td>${{count}}</td></tr>`;
        }});
    </script>
</body>
</html>"""
    
    Path(output_path).write_text(html)


def _collect_stats(graph: PlatialGraph) -> dict:
    """Collect statistics from the graph."""
    stats = {
        "node_count": graph.node_count,
        "edge_count": graph.edge_count,
        "agent_count": 0,
        "place_count": 0,
        "node_types": {},
        "agents": [],
        "top_places": []
    }
    
    # Count by type
    for node_type in NodeType:
        count = len(list(graph.nodes(node_type)))
        if count > 0:
            stats["node_types"][node_type.name] = count
    
    stats["agent_count"] = stats["node_types"].get("AGENT", 0)
    stats["place_count"] = stats["node_types"].get("SPATIAL_EXTENT", 0)
    
    # Collect agents
    for node in graph.nodes(NodeType.AGENT):
        agent_data = {
            "name": getattr(node, 'name', str(node.id)[:20]),
            "id": str(node.id),
            "encounter_count": 0
        }
        
        # Count encounters for this agent
        for enc in graph.nodes(NodeType.ENCOUNTER):
            if hasattr(enc, 'agent_id') and str(enc.agent_id) == str(node.id):
                agent_data["encounter_count"] += 1
        
        stats["agents"].append(agent_data)
    
    # Collect top places
    place_visits: dict[str, dict] = {}
    for node in graph.nodes(NodeType.SPATIAL_EXTENT):
        place_visits[str(node.id)] = {
            "name": getattr(node, 'name', str(node.id)[:20]),
            "visit_count": 0
        }
    
    for enc in graph.nodes(NodeType.ENCOUNTER):
        extent_id = str(getattr(enc, 'extent_id', ''))
        if extent_id in place_visits:
            place_visits[extent_id]["visit_count"] += 1
    
    stats["top_places"] = sorted(
        place_visits.values(), 
        key=lambda x: x["visit_count"], 
        reverse=True
    )[:10]
    
    return stats
