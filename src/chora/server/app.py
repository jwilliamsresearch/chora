"""
Chora API Server.

This module exposes the Platial Graph as a HTTP service.
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from chora.adapters import InMemoryAdapter

# Global state (for now, until we use full persistence)
# In production, this would load from Neo4j/PostGIS
graph_adapter = InMemoryAdapter()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle events: connect/disconnect DBs."""
    graph_adapter.connect()
    yield
    graph_adapter.disconnect()

def create_app() -> FastAPI:
    """Factory to create the FastAPI application."""
    app = FastAPI(
        title="Chora Server",
        description="Platial Operating System API",
        version="0.1.0",
        lifespan=lifespan
    )
    
    # Import routes here to avoid circular dependencies
    from chora.server import api
    app.include_router(api.router)
    
    return app

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("chora.server.app:create_app", factory=True, reload=True)
