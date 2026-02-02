"""
D3.js Export for Chora Graphs

Export platial graphs to D3.js-compatible JSON format.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from chora.core import PlatialGraph
from chora.core.types import NodeType


def export_d3_json(graph: PlatialGraph) -> dict:
    """
    Export graph to D3.js force-directed graph format.
    
    Returns a dict with 'nodes' and 'links' arrays.
    """
    nodes = []
    links = []
    node_ids = set()
    
    # Collect all nodes
    for node in graph.nodes():
        node_data = {
            "id": str(node.id),
            "type": node.node_type.name,
            "name": getattr(node, "name", str(node.id)[:20]),
            "group": _node_type_group(node.node_type)
        }
        
        # Add optional properties
        if hasattr(node, 'familiarity_score'):
            node_data["familiarity"] = node.familiarity_score
        if hasattr(node, 'valence'):
            node_data["valence"] = node.valence
        
        nodes.append(node_data)
        node_ids.add(str(node.id))
    
    # Collect all edges
    for edge in graph.edges():
        source = str(edge.source_id)
        target = str(edge.target_id)
        
        if source in node_ids and target in node_ids:
            links.append({
                "source": source,
                "target": target,
                "type": edge.edge_type.name,
                "value": edge.weight
            })
    
    return {"nodes": nodes, "links": links}


def export_force_graph(
    graph: PlatialGraph, 
    output_path: str | Path,
    title: str = "Chora Graph"
) -> None:
    """
    Export graph as a standalone HTML file with D3.js force-directed visualization.
    """
    data = export_d3_json(graph)
    data_json = json.dumps(data, indent=2, default=str)
    
    html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>{title}</title>
    <script src="https://d3js.org/d3.v7.min.js"></script>
    <style>
        body {{
            font-family: system-ui, -apple-system, sans-serif;
            margin: 0;
            padding: 0;
            background: #1a1a2e;
            color: #eee;
        }}
        #container {{
            display: flex;
            height: 100vh;
        }}
        #graph {{
            flex: 1;
        }}
        #sidebar {{
            width: 280px;
            padding: 20px;
            background: #16213e;
            overflow-y: auto;
        }}
        h1 {{
            font-size: 1.2rem;
            margin: 0 0 1rem 0;
            color: #00d9ff;
        }}
        .legend {{
            margin-bottom: 1rem;
        }}
        .legend-item {{
            display: flex;
            align-items: center;
            margin: 4px 0;
            font-size: 0.85rem;
        }}
        .legend-color {{
            width: 14px;
            height: 14px;
            border-radius: 50%;
            margin-right: 8px;
        }}
        .node {{
            cursor: pointer;
        }}
        .node text {{
            font-size: 10px;
            fill: #fff;
        }}
        .link {{
            stroke-opacity: 0.6;
        }}
        #info {{
            background: #0f0f23;
            padding: 12px;
            border-radius: 6px;
            font-size: 0.85rem;
        }}
        #info h3 {{
            margin: 0 0 8px 0;
            color: #00d9ff;
        }}
    </style>
</head>
<body>
    <div id="container">
        <svg id="graph"></svg>
        <div id="sidebar">
            <h1>🗺️ {title}</h1>
            <div class="legend">
                <div class="legend-item"><span class="legend-color" style="background:#ff6b6b"></span>Agent</div>
                <div class="legend-item"><span class="legend-color" style="background:#4ecdc4"></span>Spatial Extent</div>
                <div class="legend-item"><span class="legend-color" style="background:#ffe66d"></span>Encounter</div>
                <div class="legend-item"><span class="legend-color" style="background:#95e1d3"></span>Familiarity</div>
                <div class="legend-item"><span class="legend-color" style="background:#f38181"></span>Affect</div>
                <div class="legend-item"><span class="legend-color" style="background:#aa96da"></span>Practice</div>
            </div>
            <div id="info">
                <h3>Selected Node</h3>
                <p>Click a node to see details</p>
            </div>
        </div>
    </div>
    <script>
        const data = {data_json};
        
        const colors = {{
            AGENT: "#ff6b6b",
            SPATIAL_EXTENT: "#4ecdc4",
            ENCOUNTER: "#ffe66d",
            FAMILIARITY: "#95e1d3",
            AFFECT: "#f38181",
            PRACTICE: "#aa96da"
        }};
        
        const svg = d3.select("#graph");
        const width = svg.node().parentElement.offsetWidth - 280;
        const height = window.innerHeight;
        
        svg.attr("width", width).attr("height", height);
        
        const simulation = d3.forceSimulation(data.nodes)
            .force("link", d3.forceLink(data.links).id(d => d.id).distance(80))
            .force("charge", d3.forceManyBody().strength(-300))
            .force("center", d3.forceCenter(width / 2, height / 2));
        
        const link = svg.append("g")
            .selectAll("line")
            .data(data.links)
            .join("line")
            .attr("class", "link")
            .attr("stroke", "#4a4a6a")
            .attr("stroke-width", d => Math.sqrt(d.value) * 1.5);
        
        const node = svg.append("g")
            .selectAll("g")
            .data(data.nodes)
            .join("g")
            .attr("class", "node")
            .call(d3.drag()
                .on("start", dragstarted)
                .on("drag", dragged)
                .on("end", dragended))
            .on("click", (event, d) => {{
                document.getElementById("info").innerHTML = `
                    <h3>${{d.name}}</h3>
                    <p><strong>Type:</strong> ${{d.type}}</p>
                    <p><strong>ID:</strong> ${{d.id}}</p>
                    ${{d.familiarity !== undefined ? `<p><strong>Familiarity:</strong> ${{d.familiarity.toFixed(2)}}</p>` : ''}}
                    ${{d.valence !== undefined ? `<p><strong>Valence:</strong> ${{d.valence.toFixed(2)}}</p>` : ''}}
                `;
            }});
        
        node.append("circle")
            .attr("r", d => d.type === "AGENT" ? 12 : 8)
            .attr("fill", d => colors[d.type] || "#888");
        
        node.append("text")
            .attr("dx", 12)
            .attr("dy", 4)
            .text(d => d.name);
        
        simulation.on("tick", () => {{
            link
                .attr("x1", d => d.source.x)
                .attr("y1", d => d.source.y)
                .attr("x2", d => d.target.x)
                .attr("y2", d => d.target.y);
            
            node.attr("transform", d => `translate(${{d.x}},${{d.y}})`);
        }});
        
        function dragstarted(event) {{
            if (!event.active) simulation.alphaTarget(0.3).restart();
            event.subject.fx = event.subject.x;
            event.subject.fy = event.subject.y;
        }}
        
        function dragged(event) {{
            event.subject.fx = event.x;
            event.subject.fy = event.y;
        }}
        
        function dragended(event) {{
            if (!event.active) simulation.alphaTarget(0);
            event.subject.fx = null;
            event.subject.fy = null;
        }}
    </script>
</body>
</html>"""
    
    Path(output_path).write_text(html)


def _node_type_group(node_type: NodeType) -> int:
    """Map node type to numeric group for D3 coloring."""
    mapping = {
        NodeType.AGENT: 1,
        NodeType.SPATIAL_EXTENT: 2,
        NodeType.ENCOUNTER: 3,
        NodeType.FAMILIARITY: 4,
        NodeType.AFFECT: 5,
        NodeType.PRACTICE: 6,
    }
    return mapping.get(node_type, 0)
