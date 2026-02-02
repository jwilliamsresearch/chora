"""
Example: Running the Chora API Server and interacting with it.

Usage:
    python examples/server_demo.py
    
Requires:
    pip install httpx uvicorn fastapi
"""
import time
import threading
import uvicorn
import httpx
from chora.server.app import create_app

def run_server():
    """Run server in a separate thread."""
    uvicorn.run(create_app(), port=8001, log_level="error")

def client_simulation():
    """Simulate a client script."""
    base_url = "http://localhost:8001"
    
    # Wait for startup
    time.sleep(2)
    
    print(f"📡 Connecting to {base_url}...")
    
    with httpx.Client(base_url=base_url) as client:
        # 1. Create Agent
        print("Creating Agent 'Alice'...")
        resp = client.post("/agents/", json={"name": "Alice"})
        agent_id = resp.json()
        print(f" -> ID: {agent_id}")
        
        # 2. Create Extent
        print("Creating Extent 'Hyde Park'...")
        resp = client.post("/extents/", json={
            "name": "Hyde Park",
            "min_x": -0.1, "min_y": 51.5,
            "max_x": -0.09, "max_y": 51.51
        })
        extent_id = resp.json()
        print(f" -> ID: {extent_id}")
        
        # 3. Embed Description (Vector Memory)
        desc = "A large green park in central London suitable for walking."
        print(f"Embedding description: '{desc}'...")
        vec_resp = client.post("/vectors/embed", params={"text": desc})
        vec = vec_resp.json()
        print(f" -> Vector (first 5 dims): {vec[:5]}...")

        # 4. Log Encounter
        print("Logging Encounter...")
        enc_resp = client.post("/encounters/", json={
            "agent_id": agent_id,
            "extent_id": extent_id,
            "duration_minutes": 45
        })
        print(f" -> Encounter ID: {enc_resp.json()}")

        # 5. Get Place State
        print("Querying Place Familiarity...")
        place_resp = client.get(f"/places/{agent_id}/{extent_id}")
        print(f" -> {place_resp.json()}")

if __name__ == "__main__":
    # Start server thread
    server_thread = threading.Thread(target=run_server, daemon=True)
    server_thread.start()
    
    try:
        client_simulation()
    except Exception as e:
        print(f"Error: {e}")
        print("Make sure httpx is installed: pip install httpx")
