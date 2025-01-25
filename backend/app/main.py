from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1 import agents, projects, chat
from app.websockets.operations import handle_websocket

app = FastAPI(
    title="AI Staff Dev Agent API",
    description="Backend API for AI Staff Development Agent",
    version="1.0.0"
)

# Configure CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    allow_websockets=True  # Enable WebSocket support
)

# Include routers
app.include_router(agents.router, prefix="/api/v1")
app.include_router(projects.router, prefix="/api/v1")
app.include_router(chat.router, prefix="/api/v1")

@app.get("/")
async def root():
    return {"message": "AI Staff Dev Agent API"}

@app.websocket("/ws/operations")
async def operations_websocket(websocket: WebSocket):
    """WebSocket endpoint for real-time operation monitoring"""
    await handle_websocket(websocket)
