"""FastAPI main application."""

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
from typing import List, Optional
import os
from datetime import datetime, timedelta

from researcher.models import (
    Paper, SearchRequest, TheoryRequest, ContinuousImportTask,
    ContinuousImportFilter, DashboardStats, PaperStatus
)
from researcher.database import db
from researcher.ingestion import ingestion_service
from researcher.search import search_service, theory_service
from researcher.graph import graph_service
from researcher.continuous_import import continuous_import_service
from researcher.backfill import backfill_worker
from researcher.llm import llm_service
from researcher.embeddings import embedding_service
from researcher.logger import setup_logger

logger = setup_logger(__name__)


# WebSocket connection manager
class ConnectionManager:
    """Manage WebSocket connections."""
    
    def __init__(self):
        self.active_connections: List[WebSocket] = []
    
    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(f"WebSocket connected, total: {len(self.active_connections)}")
    
    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)
        logger.info(f"WebSocket disconnected, total: {len(self.active_connections)}")
    
    async def broadcast(self, message: dict):
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception as e:
                logger.error(f"Error broadcasting to WebSocket: {e}")


manager = ConnectionManager()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    logger.info("Starting PaperTrail application")
    
    # Start backfill worker
    await backfill_worker.start()
    
    # Start continuous import tasks
    await continuous_import_service.start_all_active_tasks()
    
    yield
    
    # Cleanup
    logger.info("Shutting down PaperTrail application")
    backfill_worker.stop()
    db.close()


app = FastAPI(
    title="PaperTrail API",
    description="Research paper catalog with GraphRAG and semantic search",
    version="0.1.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Health check
@app.get("/api/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "llm_available": llm_service.is_available(),
        "embedding_available": embedding_service.is_available(),
        "embedding_model": embedding_service.current_model,
        "backfill_queue_size": len(db.get_backfill_queue())
    }


# Paper endpoints
@app.get("/api/papers", response_model=List[Paper])
async def get_papers(
    status: Optional[str] = None,
    category: Optional[str] = None,
    text_query: Optional[str] = None
):
    """Get all papers with optional filters."""
    logger.info(f"GET /api/papers - status={status}, category={category}, text={text_query}")
    
    categories = [category] if category else None
    papers = search_service.filter_papers(status, categories, text_query)
    
    return papers


@app.get("/api/papers/{paper_id}", response_model=Paper)
async def get_paper(paper_id: str):
    """Get a specific paper."""
    logger.info(f"GET /api/papers/{paper_id}")
    
    paper = db.get_paper(paper_id)
    if not paper:
        raise HTTPException(status_code=404, detail="Paper not found")
    
    return paper


@app.post("/api/papers/{paper_id}")
async def update_paper(paper_id: str, updates: dict):
    """Update paper fields."""
    logger.info(f"POST /api/papers/{paper_id} - updates: {list(updates.keys())}")
    
    success = db.update_paper(paper_id, updates)
    if not success:
        raise HTTPException(status_code=404, detail="Paper not found")
    
    return {"status": "success"}


@app.post("/api/ingest")
async def ingest_paper(request: dict):
    """Ingest a paper from arXiv URL."""
    arxiv_url = request.get("arxiv_url")
    if not arxiv_url:
        raise HTTPException(status_code=400, detail="arxiv_url required")
    
    logger.info(f"POST /api/ingest - URL: {arxiv_url}")
    
    # Progress callback to broadcast updates
    async def progress_callback(progress):
        await manager.broadcast({
            "type": "ingestion_progress",
            "data": progress.model_dump()
        })
    
    try:
        paper = await ingestion_service.ingest_paper(arxiv_url, progress_callback)
        
        # Build relationships
        graph_service.build_relationships(paper)
        
        return {"status": "success", "paper_id": paper.id}
    except Exception as e:
        logger.error(f"Ingestion failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Search endpoints
@app.post("/api/search")
async def search_papers(request: SearchRequest):
    """Semantic search for papers."""
    logger.info(f"POST /api/search - query: '{request.query}'")
    
    results = search_service.semantic_search(request)
    return results


@app.get("/api/papers/{paper_id}/similar")
async def get_similar_papers(paper_id: str, limit: int = 5):
    """Get similar papers."""
    logger.info(f"GET /api/papers/{paper_id}/similar")
    
    results = search_service.get_similar_papers(paper_id, limit)
    return results


@app.get("/api/papers/{paper_id}/related")
async def get_related_papers(paper_id: str, max_results: int = 10):
    """Get related papers from graph."""
    logger.info(f"GET /api/papers/{paper_id}/related")
    
    related = graph_service.get_related_papers(paper_id, max_results)
    
    # Fetch paper details
    results = []
    for paper_id, weight, rel_type in related:
        paper = db.get_paper(paper_id)
        if paper:
            results.append({
                "paper": paper,
                "relationship_type": rel_type,
                "weight": weight
            })
    
    return results


@app.get("/api/papers/{paper_id}/graph")
async def get_paper_graph(paper_id: str, depth: int = 1):
    """Get graph visualization data for a paper."""
    logger.info(f"GET /api/papers/{paper_id}/graph - depth={depth}")
    
    graph_data = graph_service.get_graph_data(paper_id, depth)
    return graph_data


# Theory mode
@app.post("/api/theory")
async def analyze_theory(request: TheoryRequest):
    """Analyze theory with pro/contra arguments."""
    logger.info(f"POST /api/theory - hypothesis: '{request.hypothesis}'")
    
    if not llm_service.is_available():
        raise HTTPException(
            status_code=503,
            detail="LLM unavailable - Theory mode requires LLM for argument extraction"
        )
    
    results = theory_service.analyze_theory(request)
    return results


# Continuous import tasks
@app.get("/api/tasks", response_model=List[ContinuousImportTask])
async def get_tasks():
    """Get all continuous import tasks."""
    logger.info("GET /api/tasks")
    
    tasks = db.get_all_tasks()
    return tasks


@app.post("/api/tasks")
async def create_task(request: dict):
    """Create a new continuous import task."""
    logger.info(f"POST /api/tasks - name: {request.get('name')}")
    
    task = continuous_import_service.create_task(
        name=request["name"],
        filters=ContinuousImportFilter(**request.get("filters", {})),
        check_interval_seconds=request.get("check_interval_seconds", 300),
        max_results_per_check=request.get("max_results_per_check", 10),
        start_immediately=request.get("start_immediately", True)
    )
    
    return task


@app.post("/api/tasks/{task_id}/start")
async def start_task(task_id: str):
    """Start a continuous import task."""
    logger.info(f"POST /api/tasks/{task_id}/start")
    
    task = db.get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    db.update_task(task_id, {"is_active": True})
    task = db.get_task(task_id)
    await continuous_import_service.start_task(task)
    
    return {"status": "started"}


@app.post("/api/tasks/{task_id}/stop")
async def stop_task(task_id: str):
    """Stop a continuous import task."""
    logger.info(f"POST /api/tasks/{task_id}/stop")
    
    await continuous_import_service.stop_task(task_id)
    
    return {"status": "stopped"}


@app.delete("/api/tasks/{task_id}")
async def delete_task(task_id: str):
    """Delete a continuous import task."""
    logger.info(f"DELETE /api/tasks/{task_id}")
    
    await continuous_import_service.stop_task(task_id)
    success = db.delete_task(task_id)
    
    if not success:
        raise HTTPException(status_code=404, detail="Task not found")
    
    return {"status": "deleted"}


# Dashboard
@app.get("/api/dashboard", response_model=DashboardStats)
async def get_dashboard_stats():
    """Get dashboard statistics."""
    logger.info("GET /api/dashboard")
    
    papers = db.get_all_papers()
    
    # Count by category
    papers_by_category = {}
    for paper in papers:
        for category in paper.categories:
            papers_by_category[category] = papers_by_category.get(category, 0) + 1
    
    # Count by status
    papers_by_status = {
        "new": sum(1 for p in papers if p.status == PaperStatus.NEW),
        "read": sum(1 for p in papers if p.status == PaperStatus.READ),
        "starred": sum(1 for p in papers if p.status == PaperStatus.STARRED)
    }
    
    # Recent papers
    recent = sorted(papers, key=lambda p: p.created_at, reverse=True)[:10]
    
    # Active tasks
    active_tasks = len(db.get_active_tasks())
    
    # Papers imported today/week
    now = datetime.utcnow()
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    week_start = today_start - timedelta(days=7)
    
    papers_today = sum(1 for p in papers if p.created_at >= today_start)
    papers_week = sum(1 for p in papers if p.created_at >= week_start)
    
    # Collection growth (simplified)
    growth = []
    for i in range(7):
        day = now - timedelta(days=i)
        day_start = day.replace(hour=0, minute=0, second=0, microsecond=0)
        day_end = day_start + timedelta(days=1)
        count = sum(1 for p in papers if day_start <= p.created_at < day_end)
        growth.append({
            "date": day_start.isoformat(),
            "count": count
        })
    
    # Storage size (approximate)
    storage_size = 0.0
    if os.path.exists("data"):
        for root, dirs, files in os.walk("data"):
            storage_size += sum(os.path.getsize(os.path.join(root, f)) for f in files)
    storage_size_mb = storage_size / (1024 * 1024)
    
    return DashboardStats(
        total_papers=len(papers),
        papers_by_category=papers_by_category,
        papers_by_status=papers_by_status,
        storage_size_mb=storage_size_mb,
        recent_papers=recent,
        active_import_tasks=active_tasks,
        papers_imported_today=papers_today,
        papers_imported_week=papers_week,
        collection_growth=growth
    )


# WebSocket endpoint
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time updates."""
    await manager.connect(websocket)
    try:
        while True:
            # Keep connection alive
            data = await websocket.receive_text()
            logger.debug(f"WebSocket received: {data}")
    except WebSocketDisconnect:
        manager.disconnect(websocket)


# Serve frontend (if built)
if os.path.exists("frontend/dist"):
    app.mount("/", StaticFiles(directory="frontend/dist", html=True), name="frontend")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
