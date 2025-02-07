from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from typing import List

app = FastAPI(title="AiStaff Dashboard API")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# WebSocket connections store
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)

manager = ConnectionManager()

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            await manager.broadcast(f"Message: {data}")
    except:
        manager.disconnect(websocket)

@app.get("/api/v1/health")
async def health_check():
    return {"status": "healthy"}

@app.get("/api/v1/agents")
async def list_agents():
    # Placeholder - will integrate with core agent system
    return [
        {
            "id": "1",
            "name": "DevAgent",
            "status": "active",
            "is_active": True,
            "is_available": True,
            "capabilities": ["code_review", "testing", "deployment"],
            "last_heartbeat": "2025-02-07T11:30:00Z",
            "version": "1.0.0",
            "metadata": {}
        },
        {
            "id": "2",
            "name": "TestAgent",
            "status": "inactive",
            "is_active": False,
            "is_available": False,
            "capabilities": ["testing", "monitoring"],
            "last_heartbeat": "2025-02-07T11:00:00Z",
            "version": "1.0.0",
            "metadata": {}
        }
    ]

@app.get("/api/v1/agents/{agent_id}/metrics")
async def get_agent_metrics(agent_id: str):
    # Placeholder metrics
    return {
        "operations_completed": 150,
        "operations_failed": 3,
        "average_response_time": 0.5,
        "error_rate": 0.02,
        "resource_utilization": {
            "cpu": 45,
            "memory": 60
        }
    }

@app.post("/api/v1/agents/{agent_id}/maintenance")
async def schedule_maintenance(agent_id: str):
    # Placeholder maintenance scheduling
    return {"status": "scheduled"}
