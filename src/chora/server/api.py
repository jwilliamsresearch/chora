"""
API Routes for Chora Server.
"""
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
from datetime import datetime

from chora.core import Agent, SpatialExtent, Encounter, PlatialEdge
from chora.derive import update_familiarity, extract_place
from chora.server.app import graph_adapter

router = APIRouter()

# --- Pydantic Models for Input/Output ---

class AgentCreate(BaseModel):
    name: str

class ExtentCreate(BaseModel):
    name: str
    min_x: float
    min_y: float
    max_x: float
    max_y: float

class EncounterCreate(BaseModel):
    agent_id: str
    extent_id: str
    start_time: Optional[datetime] = None
    duration_minutes: float = 60.0

class PlaceResponse(BaseModel):
    extent_id: str
    familiarity: float
    character: str

# --- Endpoints ---

@router.post("/agents/", response_model=str)
async def create_agent(agent: AgentCreate):
    """Register a new agent in the graph."""
    # Note: Chora core objects don't strictly separate create inputs yet
    # but for API we use Pydantic.
    a = Agent.individual(agent.name)
    graph_adapter.add_node(a)
    return str(a.id)

@router.post("/extents/", response_model=str)
async def create_extent(extent: ExtentCreate):
    """Register a spatial extent."""
    e = SpatialExtent.from_bounds(
        extent.min_x, extent.min_y, 
        extent.max_x, extent.max_y, 
        name=extent.name
    )
    graph_adapter.add_node(e)
    return str(e.id)

from fastapi import WebSocket, WebSocketDisconnect
from chora.server.hub import manager

@router.websocket("/ws/stream")
async def websocket_endpoint(websocket: WebSocket):
    """
    Real-time stream of events.
    Clients receive JSON updates when new encounters are logged.
    """
    await manager.connect(websocket)
    try:
        while True:
            # Keep listener open (or implement bi-directional chat later)
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)

@router.post("/encounters/", response_model=str)
async def log_encounter(enc: EncounterCreate):
    """Log an interaction between agent and extent."""
    if not enc.start_time:
        enc.start_time = datetime.now()
        
    encounter = Encounter(
        agent_id=enc.agent_id,
        extent_id=enc.extent_id,
        start_time=enc.start_time
    )
    # Must add to graph
    graph_adapter.add_node(encounter)
    
    @router.post("/vectors/embed", response_model=List[float])
async def create_embedding(text: str):
    """
    Get the vector embedding for a text string.
    Uses the server-side 'Real' embedder (all-MiniLM-L6-v2).
    """
    from chora.embeddings import get_embedding_model
    model = get_embedding_model()
    return model.embed_text(text)
    
    # Broadcast event
    await manager.broadcast(f"New Encounter: Agent {enc.agent_id} at {enc.extent_id}")
    
    return str(encounter.id)

@router.get("/places/{agent_id}/{extent_id}", response_model=PlaceResponse)
async def get_emergent_place(agent_id: str, extent_id: str):
    """
    Get the emergent place (familiarity, etc) for an agent at an extent.
    
    This derives the state on-the-fly.
    """
    # NOTE: extract_place requires a PlatialGraph object, not an Adapter.
    # We need to construct a PlatialGraph view from the adapter.
    # For InMemoryAdapter, we can cheat if we expose the inner graph.
    # Or load relevant subgraph.
    
    # Hack for InMemory:
    if hasattr(graph_adapter, "_graph"):
        g = graph_adapter._graph
    else:
        # Load full graph (expensive)
        g = graph_adapter.load_graph("default")
        
    try:
        place = extract_place(g, extent_id, agent_id)
        return PlaceResponse(
            extent_id=str(place.extent.id),
            familiarity=place.familiarity_score,
            character=place.character
        )
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))
