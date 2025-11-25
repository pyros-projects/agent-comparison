"""FastAPI application for PaperTrail."""

import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pathlib import Path

from researcher.config import Config
from researcher.services import (
    get_import_manager,
    get_backfill_worker,
)
from researcher.api.routes import papers, search, imports, dashboard, websocket

logger = logging.getLogger("papertrail.api")


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan handler."""
    logger.info("Starting PaperTrail application...")
    
    # Start import manager for active tasks
    import_manager = get_import_manager()
    await import_manager.start_active_tasks()
    
    # Start backfill worker
    backfill_worker = get_backfill_worker()
    await backfill_worker.start()
    
    logger.info("PaperTrail application started")
    
    yield
    
    # Shutdown
    logger.info("Shutting down PaperTrail...")
    await import_manager.stop_all_tasks()
    await backfill_worker.stop()
    logger.info("PaperTrail shutdown complete")


app = FastAPI(
    title="PaperTrail",
    description="Research Paper Catalog with GraphRAG-based search",
    version="0.1.0",
    lifespan=lifespan,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(papers.router, prefix="/api/papers", tags=["papers"])
app.include_router(search.router, prefix="/api/search", tags=["search"])
app.include_router(imports.router, prefix="/api/imports", tags=["imports"])
app.include_router(dashboard.router, prefix="/api/dashboard", tags=["dashboard"])
app.include_router(websocket.router, tags=["websocket"])

# Serve static frontend files
FRONTEND_DIR = Config.BASE_DIR / "frontend" / "dist"

if FRONTEND_DIR.exists():
    app.mount("/assets", StaticFiles(directory=FRONTEND_DIR / "assets"), name="assets")
    
    @app.get("/{full_path:path}")
    async def serve_frontend(full_path: str):
        """Serve frontend files."""
        # Check if file exists
        file_path = FRONTEND_DIR / full_path
        if file_path.exists() and file_path.is_file():
            return FileResponse(file_path)
        # Return index.html for SPA routing
        return FileResponse(FRONTEND_DIR / "index.html")


@app.get("/api/health")
async def health_check():
    """Health check endpoint."""
    from researcher.services import get_llm_service, get_embedding_service
    
    llm = get_llm_service()
    embedding = get_embedding_service()
    
    return {
        "status": "healthy",
        "llm_available": llm.available,
        "embedding_fallback": embedding.using_fallback,
    }
