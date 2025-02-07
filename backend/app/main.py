import asyncio
from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1 import agents, projects, chat, metrics
from app.websockets.operations import handle_websocket
from app.websockets.metrics import handle_metrics_websocket, metrics_ws_manager
from app.services.operation_queue import queue as operation_queue
from app.services.metrics_collector import collector as metrics_collector

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
    allow_headers=["*"]  # WebSocket support is enabled by default with allow_credentials=True
)

# Include routers
app.include_router(agents.router, prefix="/api/v1")
app.include_router(projects.router, prefix="/api/v1")
app.include_router(chat.router, prefix="/api/v1")
app.include_router(metrics.router, prefix="/api/v1")

@app.get("/")
async def root():
    return {"message": "AI Staff Dev Agent API"}

@app.websocket("/ws/operations")
async def operations_websocket(websocket: WebSocket):
    """WebSocket endpoint for real-time operation monitoring"""
    await handle_websocket(websocket)

@app.websocket("/ws/metrics")
async def metrics_websocket(websocket: WebSocket, client_id: str, subscriptions: str = None):
    """WebSocket endpoint for real-time metrics monitoring"""
    subs = set(subscriptions.split(",")) if subscriptions else None
    await handle_metrics_websocket(websocket, client_id, subs)

@app.on_event("startup")
async def startup_event():
    """Start the operation queue and metrics collection on application startup"""
    await operation_queue.start()
    await metrics_collector.start()  # This now starts the collection task
    # Start metrics broadcast task
    asyncio.create_task(metrics_ws_manager.broadcast_system_metrics())

@app.on_event("shutdown")
async def shutdown_event():
    """Stop the operation queue and metrics collection on application shutdown"""
    await metrics_collector.stop()  # This handles cleanup including DB connection
    await operation_queue.stop()
