"""Dashboard API routes."""

import logging
import os
from datetime import datetime, timedelta

from fastapi import APIRouter
from pydantic import BaseModel

from researcher.models import DashboardStats
from researcher.config import Config
from researcher.services import (
    get_database,
    get_llm_service,
    get_embedding_service,
    get_embedding_store,
    get_import_manager,
    get_graph_service,
)

logger = logging.getLogger("papertrail.api.dashboard")

router = APIRouter()


class ActivityItem(BaseModel):
    """Activity timeline item."""
    timestamp: str
    action: str
    paper_id: str
    paper_title: str


class TopicCluster(BaseModel):
    """Topic cluster."""
    id: int
    main_category: str
    paper_count: int
    papers: list[dict]


class DashboardResponse(BaseModel):
    """Dashboard data response."""
    stats: DashboardStats
    recent_activity: list[ActivityItem]
    topic_clusters: list[TopicCluster]
    growth_data: list[dict]


@router.get("", response_model=DashboardResponse)
async def get_dashboard():
    """Get dashboard statistics and data."""
    logger.debug("Getting dashboard data")
    
    db = get_database()
    llm_service = get_llm_service()
    embedding_service = get_embedding_service()
    import_manager = get_import_manager()
    graph_service = get_graph_service()
    
    # Calculate storage size
    storage_size = 0.0
    if Config.DB_PATH.exists():
        storage_size = Config.DB_PATH.stat().st_size / (1024 * 1024)  # MB
    
    # Get papers by time period
    now = datetime.now()
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    week_start = today_start - timedelta(days=7)
    
    papers_today = db.get_papers_since(today_start)
    papers_this_week = db.get_papers_since(week_start)
    
    # Get papers with placeholders
    papers_with_placeholders = db.get_papers_with_placeholders()
    
    # Build stats
    stats = DashboardStats(
        total_papers=db.get_papers_count(),
        storage_size_mb=round(storage_size, 2),
        papers_by_category=db.get_papers_by_category(),
        papers_today=len(papers_today),
        papers_this_week=len(papers_this_week),
        active_import_tasks=len(import_manager.get_running_tasks()),
        papers_with_placeholders=len(papers_with_placeholders),
        llm_available=llm_service.available,
        embedding_using_fallback=embedding_service.using_fallback,
    )
    
    # Recent activity (last 20 papers)
    recent_papers = db.get_all_papers(limit=20)
    recent_activity = []
    for paper in recent_papers:
        recent_activity.append(ActivityItem(
            timestamp=paper.created_at.isoformat() if paper.created_at else "",
            action="added",
            paper_id=paper.id,
            paper_title=paper.title[:100],
        ))
    
    # Topic clusters
    clusters_data = graph_service.get_topic_clusters()
    topic_clusters = []
    for cluster in clusters_data[:10]:  # Top 10 clusters
        topic_clusters.append(TopicCluster(
            id=cluster["id"],
            main_category=cluster["main_category"],
            paper_count=cluster["paper_count"],
            papers=cluster["papers"][:5],
        ))
    
    # Growth data (papers per day for last 7 days)
    growth_data = []
    for i in range(7):
        day_start = today_start - timedelta(days=i)
        day_end = day_start + timedelta(days=1)
        
        papers_on_day = [
            p for p in papers_this_week
            if p.created_at and day_start <= p.created_at < day_end
        ]
        
        growth_data.append({
            "date": day_start.strftime("%Y-%m-%d"),
            "count": len(papers_on_day),
        })
    
    growth_data.reverse()  # Oldest first
    
    return DashboardResponse(
        stats=stats,
        recent_activity=recent_activity,
        topic_clusters=topic_clusters,
        growth_data=growth_data,
    )


@router.get("/status")
async def get_system_status():
    """Get system status and service availability."""
    llm_service = get_llm_service()
    embedding_service = get_embedding_service()
    import_manager = get_import_manager()
    
    return {
        "llm": {
            "available": llm_service.available,
            "model": Config.DEFAULT_MODEL if llm_service.available else None,
        },
        "embedding": {
            "using_fallback": embedding_service.using_fallback,
            "model": Config.FALLBACK_EMBEDDING_MODEL if embedding_service.using_fallback else Config.DEFAULT_EMBEDDING_MODEL,
        },
        "import_tasks": {
            "active_count": len(import_manager.get_running_tasks()),
            "active_ids": import_manager.get_running_tasks(),
        },
    }


@router.get("/graph")
async def get_full_graph():
    """Get full knowledge graph data for visualization."""
    graph_service = get_graph_service()
    return graph_service.get_graph_data()


class KeywordCount(BaseModel):
    """Keyword with count for word cloud."""
    keyword: str
    count: int


@router.get("/keywords", response_model=list[KeywordCount])
async def get_all_keywords():
    """Get all keywords with counts for word cloud."""
    db = get_database()
    papers = db.get_all_papers(limit=1000)
    
    keyword_counts: dict[str, int] = {}
    for paper in papers:
        for kw in paper.keywords:
            if kw and not kw.startswith("<"):  # Skip placeholders
                kw_lower = kw.lower().strip()
                keyword_counts[kw_lower] = keyword_counts.get(kw_lower, 0) + 1
    
    # Sort by count descending
    sorted_keywords = sorted(
        keyword_counts.items(),
        key=lambda x: x[1],
        reverse=True
    )
    
    return [
        KeywordCount(keyword=kw, count=count)
        for kw, count in sorted_keywords[:100]  # Top 100
    ]


class EmbeddingClusterData(BaseModel):
    """Paper position in embedding space for cluster visualization."""
    paper_id: str
    title: str
    category: str
    x: float
    y: float
    keywords: list[str]


@router.get("/embedding-clusters", response_model=list[EmbeddingClusterData])
async def get_embedding_clusters():
    """Get 2D projections of paper embeddings for cluster visualization."""
    db = get_database()
    embedding_store = get_embedding_store()
    
    papers = db.get_all_papers(limit=200)
    
    if len(papers) < 2:
        return []
    
    # Get embeddings for all papers
    embeddings = []
    paper_data = []
    
    for paper in papers:
        emb = embedding_store.get_embedding(paper.id)
        if emb is not None:
            embeddings.append(emb)
            paper_data.append({
                "paper_id": paper.id,
                "title": paper.title[:80],
                "category": paper.primary_category,
                "keywords": paper.keywords[:5],
            })
    
    if len(embeddings) < 2:
        return []
    
    # Simple 2D projection using first 2 principal components
    # (Using a basic approach without sklearn for simplicity)
    import numpy as np
    
    embeddings_array = np.array(embeddings)
    
    # Center the data
    mean = np.mean(embeddings_array, axis=0)
    centered = embeddings_array - mean
    
    # Simple PCA: use first 2 dimensions of centered data
    # For better results, compute actual principal components
    # But this approximation works for visualization
    
    # Compute covariance and get top 2 eigenvectors
    try:
        cov = np.cov(centered.T)
        eigenvalues, eigenvectors = np.linalg.eigh(cov)
        
        # Get indices of top 2 eigenvalues
        idx = np.argsort(eigenvalues)[::-1][:2]
        top_eigenvectors = eigenvectors[:, idx]
        
        # Project to 2D
        projected = centered @ top_eigenvectors
        
        # Normalize to [0, 1] range
        x_min, x_max = projected[:, 0].min(), projected[:, 0].max()
        y_min, y_max = projected[:, 1].min(), projected[:, 1].max()
        
        x_range = x_max - x_min if x_max != x_min else 1
        y_range = y_max - y_min if y_max != y_min else 1
        
        results = []
        for i, p in enumerate(paper_data):
            results.append(EmbeddingClusterData(
                paper_id=p["paper_id"],
                title=p["title"],
                category=p["category"],
                x=float((projected[i, 0] - x_min) / x_range),
                y=float((projected[i, 1] - y_min) / y_range),
                keywords=p["keywords"],
            ))
        
        return results
    except Exception as e:
        logger.error(f"Error computing embedding clusters: {e}")
        return []
