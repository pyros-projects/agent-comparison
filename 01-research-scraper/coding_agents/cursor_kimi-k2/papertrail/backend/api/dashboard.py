from fastapi import APIRouter, HTTPException
from typing import Dict, List, Any
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get('/stats')
async def get_dashboard_stats():
    return {
        'total_papers': 0,
        'papers_by_category': {},
        'recent_papers_count': 0,
        'storage_size_mb': 0,
        'active_import_tasks': 0,
        'import_tasks': []
    }

@router.get('/activity')
async def get_recent_activity():
    return []

@router.get('/topics')
async def get_topic_clusters():
    return []

@router.get('/growth')
async def get_collection_growth():
    return {'daily_growth': [], 'total_growth': 0}
