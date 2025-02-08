import logging
import psutil
from datetime import datetime
from fastapi import FastAPI, WebSocket, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from backend.app.api.v1 import agents, projects
from backend.app.services.test_data import init_test_data
from backend.app.websockets.operations import router as websocket_router, handle_websocket
from backend.app.core.database import engine, init_db, get_db
from sqlalchemy.ext.asyncio import AsyncSession
from prometheus_client import start_http_server

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="AI Staff Dev Agent API",
    description="Backend API for AI Staff Development Agent",
    version="1.0.0"
)

# Start Prometheus metrics server
start_http_server(9090)

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

@app.get("/health")
async def health_check(db: AsyncSession = Depends(get_db)):
    """Health check endpoint for Docker."""
    try:
        # Test database connection
        await db.execute("SELECT 1")
        
        # Get system metrics
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        return {
            "status": "healthy",
            "database": "connected",
            "timestamp": datetime.utcnow().isoformat(),
            "system": {
                "memory_percent": memory.percent,
                "disk_percent": disk.percent,
                "cpu_percent": psutil.cpu_percent(interval=1),
            }
        }
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        raise HTTPException(
            status_code=503,
            detail=f"Service unhealthy: {str(e)}"
        )

@app.on_event("startup")
async def startup_event():
    """Initialize database, test data, and verify connections on startup."""
    try:
        logger.info("Starting application initialization...")
        
        # Initialize database with retries
        logger.info("Initializing database...")
        await init_db()
        
        # Test database connection
        logger.info("Testing database connection...")
        async with engine.begin() as conn:
            await conn.execute("SELECT 1")
        logger.info("Database connection successful")
        
        # Initialize test data
        logger.info("Initializing test data...")
        await init_test_data()
        logger.info("Test data initialization complete")
        
        logger.info("Application startup complete")
    except Exception as e:
        logger.error(f"Startup failed: {str(e)}")
        raise

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown."""
    try:
        logger.info("Shutting down application...")
        await engine.dispose()
        logger.info("Cleanup complete")
    except Exception as e:
        logger.error(f"Shutdown error: {str(e)}")
        raise
