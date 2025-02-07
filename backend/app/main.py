from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1 import agents, projects
from app.services.test_data import init_test_data
from app.websockets.operations import router as websocket_router, handle_websocket

app = FastAPI(
    title="AI Staff Dev Agent API",
    description="Backend API for AI Staff Development Agent",
    version="1.0.0"
)

# Configure CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],  # Frontend URLs
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    allow_websockets=True
)

# Include essential routers only
app.include_router(agents.router, prefix="/api/v1")
app.include_router(projects.router, prefix="/api/v1")
app.include_router(websocket_router)

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    client_id = str(id(websocket))  # Use websocket id as client id
    await handle_websocket(websocket, client_id)

@app.get("/")
async def root():
    return {"message": "AI Staff Dev Agent API"}

@app.on_event("startup")
async def startup_event():
    """Initialize test data on startup."""
    await init_test_data()
