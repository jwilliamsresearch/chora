"""
Timeline Visualization for Chora

Generate timeline visualizations of encounters, familiarity, and affect over time.
"""
from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any

from chora.core import PlatialGraph
from chora.core.types import NodeType, NodeId


def export_timeline_data(
    graph: PlatialGraph, 
    agent_id: NodeId
) -> list[dict]:
    """
    Export timeline data for an agent's encounters.
    
    Returns a list of events sorted by time.
    """
    events = []
    
    for node in graph.nodes(NodeType.ENCOUNTER):
        if hasattr(node, 'agent_id') and str(node.agent_id) == str(agent_id):
            event = {
                "time": str(getattr(node, 'start_time', '')),
                "timestamp": getattr(node, 'start_time', datetime.now()).isoformat() if hasattr(node, 'start_time') else None,
                "extent_id": str(getattr(node, 'extent_id', '')),
                "activity": getattr(node, 'activity', 'unknown'),
                "id": str(node.id)
            }
            
            # Try to get extent name
            try:
                extent = graph.get_node(node.extent_id)
                event["extent_name"] = getattr(extent, 'name', str(node.extent_id)[:20])
            except Exception:
                event["extent_name"] = str(getattr(node, 'extent_id', ''))[:20]
            
            events.append(event)
    
    # Sort by timestamp
    events.sort(key=lambda e: e.get('timestamp') or '')
    
    return events


def export_timeline_html(
    graph: PlatialGraph,
    agent_id: NodeId,
    output_path: str | Path,
    title: str = "Encounter Timeline"
) -> None:
    """
    Generate an interactive HTML timeline visualization.
    """
    events = export_timeline_data(graph, agent_id)
    events_json = json.dumps(events, indent=2, default=str)
    
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
            padding: 2rem;
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
            color: #eee;
            min-height: 100vh;
        }}
        h1 {{
            color: #00d9ff;
            margin-bottom: 2rem;
        }}
        .timeline {{
            position: relative;
            max-width: 800px;
            margin: 0 auto;
        }}
        .timeline::before {{
            content: '';
            position: absolute;
            left: 50%;
            transform: translateX(-50%);
            width: 4px;
            height: 100%;
            background: linear-gradient(to bottom, #00d9ff, #aa96da);
            border-radius: 2px;
        }}
        .event {{
            position: relative;
            width: 45%;
            padding: 1rem 1.5rem;
            background: rgba(255,255,255,0.05);
            border-radius: 8px;
            margin-bottom: 1.5rem;
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255,255,255,0.1);
        }}
        .event:nth-child(odd) {{
            left: 0;
        }}
        .event:nth-child(even) {{
            left: 55%;
        }}
        .event::before {{
            content: '';
            position: absolute;
            width: 16px;
            height: 16px;
            background: #00d9ff;
            border-radius: 50%;
            top: 1.5rem;
        }}
        .event:nth-child(odd)::before {{
            right: -8%;
            transform: translateX(50%);
        }}
        .event:nth-child(even)::before {{
            left: -8%;
            transform: translateX(-50%);
        }}
        .event-time {{
            font-size: 0.8rem;
            color: #00d9ff;
            margin-bottom: 0.5rem;
        }}
        .event-place {{
            font-size: 1.1rem;
            font-weight: 600;
            margin-bottom: 0.25rem;
        }}
        .event-activity {{
            font-size: 0.9rem;
            color: #aaa;
        }}
        .stats {{
            display: flex;
            gap: 2rem;
            margin-bottom: 2rem;
            justify-content: center;
        }}
        .stat {{
            text-align: center;
            background: rgba(255,255,255,0.05);
            padding: 1rem 2rem;
            border-radius: 8px;
        }}
        .stat-value {{
            font-size: 2rem;
            color: #00d9ff;
            font-weight: bold;
        }}
        .stat-label {{
            font-size: 0.9rem;
            color: #888;
        }}
        @media (max-width: 600px) {{
            .event {{
                width: 100%;
                left: 0 !important;
            }}
            .timeline::before {{
                left: 1rem;
            }}
            .event::before {{
                left: -1.5rem !important;
                right: auto !important;
                transform: none !important;
            }}
        }}
    </style>
</head>
<body>
    <h1>📍 {title}</h1>
    
    <div class="stats">
        <div class="stat">
            <div class="stat-value" id="total-count">0</div>
            <div class="stat-label">Total Encounters</div>
        </div>
        <div class="stat">
            <div class="stat-value" id="unique-places">0</div>
            <div class="stat-label">Unique Places</div>
        </div>
        <div class="stat">
            <div class="stat-value" id="date-range">-</div>
            <div class="stat-label">Date Range</div>
        </div>
    </div>
    
    <div class="timeline" id="timeline"></div>
    
    <script>
        const events = {events_json};
        const container = document.getElementById('timeline');
        
        // Stats
        document.getElementById('total-count').textContent = events.length;
        const uniquePlaces = new Set(events.map(e => e.extent_name));
        document.getElementById('unique-places').textContent = uniquePlaces.size;
        
        if (events.length > 0) {{
            const first = events[0].timestamp?.split('T')[0] || '-';
            const last = events[events.length-1].timestamp?.split('T')[0] || '-';
            document.getElementById('date-range').textContent = 
                first === last ? first : `${{first.slice(5)}} - ${{last.slice(5)}}`;
        }}
        
        // Render events
        events.forEach((e, i) => {{
            const time = e.timestamp ? new Date(e.timestamp).toLocaleString() : e.time;
            container.innerHTML += `
                <div class="event">
                    <div class="event-time">${{time}}</div>
                    <div class="event-place">${{e.extent_name}}</div>
                    <div class="event-activity">${{e.activity}}</div>
                </div>
            `;
        }});
    </script>
</body>
</html>"""
    
    Path(output_path).write_text(html)
