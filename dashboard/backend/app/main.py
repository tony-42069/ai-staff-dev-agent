from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="AiStaff Dashboard API")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/health")
async def health_check():
    return {"status": "healthy"}

@app.get("/api/agents")
async def list_agents():
    # Placeholder - will integrate with core agent system
    return {
        "agents": [
            {"id": 1, "name": "DevAgent", "status": "active"},
            {"id": 2, "name": "TestAgent", "status": "inactive"}
        ]
    }