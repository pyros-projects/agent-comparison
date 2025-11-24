from fastapi import APIRouter, HTTPException
from typing import Dict, List, Any
import logging
from datetime import datetime, timedelta

from ..models.database import PaperDB, ContinuousImportDB
from ..services.continuous_import import ContinuousImportService

router = APIRouter()
logger = logging.getLogger(__name__)
paper_db = PaperDB()
import_db = ContinuousImportDB()
import_service = ContinuousImportService()

@router.get("/stats")
async def get_dashboard_stats():
    """Get dashboard statistics"""
    try:
        total_papers = paper_db.count_papers()
        
        # Get papers by category
        papers_by_category = paper_db.get_papers_by_category()
        
        # Get recent papers (last 7 days)
        week_ago = datetime.now() - timedelta(days=7)
        recent_papers = paper_db.get_papers_since(week_ago)
        
        # Get storage info (approximate)
        storage_size = paper_db.get_storage_size()
        
        # Get import task status
        import_tasks = import_db.get_all_tasks()
        active_tasks = [t for t in import_tasks if t.get('status') == 'running']
        
        return {
            "total_papers": total_papers,
            "papers_by_category": papers_by_category,
            "recent_papers_count": len(recent_papers),
            "storage_size_mb": storage_size,
            "active_import_tasks": len(active_tasks),
            "import_tasks": import_tasks
        }
    except Exception as e:
        logger.error(f"Error getting dashboard stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/activity")
async def get_recent_activity():
    """Get recent activity timeline"""
    try:
        # Get recent papers
        recent_papers = paper_db.get_papers(limit=20, sort_by="date")
        
        # Get recent import activity
        import_activity = import_db.get_recent_activity(limit=50)
        
        # Combine and sort by timestamp
        activity = []
        
        for paper in recent_papers:
            activity.append({
                "type": "paper_added",
                "timestamp": paper.created_at,
                "paper": paper,
                "description": f"Added paper: {paper.title[:50]}..."
            })
        
        for task in import_activity:
            activity.append({
                "type": "import_task",
                "timestamp": task.get('last_run', datetime.now()),
                "task": task,
                "description": f"Import task {task.get('name', 'unnamed')} processed {task.get('papers_imported', 0)} papers"
            })
        
        # Sort by timestamp descending
        activity.sort(key=lambda x: x["timestamp"], reverse=True)
        
        return activity[:50]
    except Exception as e:
        logger.error(f"Error getting recent activity: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/topics")
async def get_topic_clusters():
    """Get topic clusters visualization data"""
    try:
        # Get papers with embeddings
        papers = paper_db.get_papers(limit=100)
        
        # Simple topic clustering based on categories and keywords
        topics = {}
        
        for paper in papers:
            # Use categories as primary clustering
            for category in paper.categories:
                if category not in topics:
                    topics[category] = {
                        "name": category,
                        "papers": [],
                        "count": 0
                    }
                topics[category]["papers"].append(paper.id)
                topics[category]["count"] += 1
        
        # Convert to list and sort by count
        topic_list = list(topics.values())
        topic_list.sort(key=lambda x: x["count"], reverse=True)
        
        return topic_list[:20]  # Top 20 topics
    except Exception as e:
        logger.error(f"Error getting topic clusters: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/growth")
async def get_collection_growth():
    """Get collection growth over time"""
    try:
        # Get papers grouped by date
        growth_data = paper_db.get_growth_data(days=30)
        
        return {
            "daily_growth": growth_data,
            "total_growth": sum(day["count"] for day in growth_data)
        }
    except Exception as e:
        logger.error(f"Error getting collection growth: {e}")
        raise HTTPException(status_code=500, detail=str(e))
