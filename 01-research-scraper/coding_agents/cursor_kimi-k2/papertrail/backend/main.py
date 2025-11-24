import logging
import os
from contextlib import asynccontextmanager
from typing import Dict, Any

from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from dotenv import load_dotenv

from .api.papers import router as papers_router
from .api.search import router as search_router
from .api.theory import router as theory_router
from .api.dashboard import router as dashboard_router
from .services.websocket_manager import WebSocketManager
from .services.continuous_import import ContinuousImportService
from .services.backfill_worker import BackfillWorker
from .utils.logging_config import setup_logging

# Load environment variables
load_dotenv()

# Setup logging
setup_logging()
logger = logging.getLogger(__name__)

# Global services
websocket_manager = WebSocketManager()
continuous_import_service = ContinuousImportService()
backfill_worker = BackfillWorker()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifespan with proper startup/shutdown"""
    logger.info("Starting PaperTrail application...")
    
    # Start background services
    await continuous_import_service.start()
    await backfill_worker.start()
    
    logger.info("PaperTrail application started successfully")
    yield
    
    # Cleanup on shutdown
    logger.info("Shutting down PaperTrail application...")
    await continuous_import_service.stop()
    await backfill_worker.stop()
    logger.info("PaperTrail application shut down complete")

# Create FastAPI app
app = FastAPI(
    title="PaperTrail",
    description="Research Paper Catalog with GraphRAG and Continuous Ingestion",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routers
app.include_router(papers_router, prefix="/api/papers", tags=["papers"])
app.include_router(search_router, prefix="/api/search", tags=["search"])
app.include_router(theory_router, prefix="/api/theory", tags=["theory"])
app.include_router(dashboard_router, prefix="/api/dashboard", tags=["dashboard"])

# WebSocket endpoint for real-time updates
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket_manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            # Handle incoming WebSocket messages if needed
            logger.debug(f"Received WebSocket message: {data}")
    except WebSocketDisconnect:
        websocket_manager.disconnect(websocket)

# Health check endpoint
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "services": {
            "continuous_import": continuous_import_service.is_running,
            "backfill_worker": backfill_worker.is_running,
            "websocket_connections": len(websocket_manager.active_connections)
        }
    }

# Mount static files for frontend
app.mount("/static", StaticFiles(directory="frontend/public"), name="static")

if __name__ == "__main__":
    import uvicorn
    host = os.getenv("BACKEND_HOST", "0.0.0.0")
    port = int(os.getenv("BACKEND_PORT", 8000))
    uvicorn.run(app, host=host, port=port)
