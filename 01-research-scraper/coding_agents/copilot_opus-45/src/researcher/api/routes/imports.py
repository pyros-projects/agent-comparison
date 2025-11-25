"""Import tasks API routes."""

import logging
from typing import Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from researcher.models import ImportTask, ImportTaskCreate
from researcher.services import get_database, get_import_manager, ARXIV_CATEGORIES

logger = logging.getLogger("papertrail.api.imports")

router = APIRouter()


class ImportTaskResponse(BaseModel):
    """Import task response."""
    id: str
    name: str
    category: Optional[str]
    semantic_query: Optional[str]
    text_search: Optional[str]
    check_interval: int
    is_active: bool
    papers_imported: int
    errors: int
    last_run: Optional[str]


class ImportTaskListResponse(BaseModel):
    """List of import tasks."""
    tasks: list[ImportTaskResponse]
    active_count: int


class LogEntry(BaseModel):
    """Log entry for import task."""
    timestamp: str
    level: str
    message: str
    details: dict


class ImportedPaper(BaseModel):
    """Imported paper info."""
    paper_id: str
    arxiv_id: str
    title: str
    category: str
    imported_at: str


class ImportTaskDetailResponse(BaseModel):
    """Detailed import task response with logs."""
    id: str
    name: str
    category: Optional[str]
    semantic_query: Optional[str]
    text_search: Optional[str]
    check_interval: int
    is_active: bool
    papers_imported: int
    errors: int
    last_run: Optional[str]
    logs: list[LogEntry]
    imported_papers: list[ImportedPaper]


@router.get("/categories")
async def get_arxiv_categories():
    """Get available arXiv categories for filtering."""
    return {
        "categories": ARXIV_CATEGORIES,
    }


@router.get("", response_model=ImportTaskListResponse)
async def list_import_tasks():
    """List all import tasks."""
    logger.debug("Listing import tasks")
    
    db = get_database()
    import_manager = get_import_manager()
    
    tasks = db.get_all_import_tasks()
    running_ids = set(import_manager.get_running_tasks())
    
    task_responses = []
    for task in tasks:
        task_responses.append(ImportTaskResponse(
            id=task.id,
            name=task.name,
            category=task.category,
            semantic_query=task.semantic_query,
            text_search=task.text_search,
            check_interval=task.check_interval,
            is_active=task.id in running_ids,
            papers_imported=task.papers_imported,
            errors=task.errors,
            last_run=task.last_run.isoformat() if task.last_run else None,
        ))
    
    return ImportTaskListResponse(
        tasks=task_responses,
        active_count=len(running_ids),
    )


@router.post("", response_model=ImportTaskResponse)
async def create_import_task(task_create: ImportTaskCreate):
    """Create a new import task."""
    logger.info(f"Creating import task: {task_create.name}")
    
    import_manager = get_import_manager()
    
    try:
        task = await import_manager.create_task(task_create)
        
        return ImportTaskResponse(
            id=task.id,
            name=task.name,
            category=task.category,
            semantic_query=task.semantic_query,
            text_search=task.text_search,
            check_interval=task.check_interval,
            is_active=task.is_active,
            papers_imported=task.papers_imported,
            errors=task.errors,
            last_run=task.last_run.isoformat() if task.last_run else None,
        )
    except Exception as e:
        logger.error(f"Error creating import task: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{task_id}/start")
async def start_import_task(task_id: str):
    """Start an import task."""
    logger.info(f"Starting import task: {task_id}")
    
    import_manager = get_import_manager()
    
    success = await import_manager.start_task(task_id)
    if not success:
        raise HTTPException(status_code=404, detail="Task not found")
    
    return {"status": "started", "task_id": task_id}


@router.post("/{task_id}/stop")
async def stop_import_task(task_id: str):
    """Stop an import task."""
    logger.info(f"Stopping import task: {task_id}")
    
    import_manager = get_import_manager()
    
    await import_manager.stop_task(task_id)
    
    return {"status": "stopped", "task_id": task_id}


@router.delete("/{task_id}")
async def delete_import_task(task_id: str):
    """Delete an import task."""
    logger.info(f"Deleting import task: {task_id}")
    
    import_manager = get_import_manager()
    
    success = await import_manager.delete_task(task_id)
    if not success:
        raise HTTPException(status_code=404, detail="Task not found")
    
    return {"status": "deleted", "task_id": task_id}


@router.get("/{task_id}", response_model=ImportTaskResponse)
async def get_import_task(task_id: str):
    """Get a specific import task."""
    db = get_database()
    import_manager = get_import_manager()
    
    task = db.get_import_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    running_ids = set(import_manager.get_running_tasks())
    
    return ImportTaskResponse(
        id=task.id,
        name=task.name,
        category=task.category,
        semantic_query=task.semantic_query,
        text_search=task.text_search,
        check_interval=task.check_interval,
        is_active=task.id in running_ids,
        papers_imported=task.papers_imported,
        errors=task.errors,
        last_run=task.last_run.isoformat() if task.last_run else None,
    )


@router.get("/{task_id}/detail", response_model=ImportTaskDetailResponse)
async def get_import_task_detail(task_id: str):
    """Get detailed info for an import task including logs."""
    db = get_database()
    import_manager = get_import_manager()
    
    task = db.get_import_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    running_ids = set(import_manager.get_running_tasks())
    
    # Get logs and imported papers from runner
    logs = import_manager.get_task_logs(task_id)
    imported_papers = import_manager.get_task_imported_papers(task_id)
    
    return ImportTaskDetailResponse(
        id=task.id,
        name=task.name,
        category=task.category,
        semantic_query=task.semantic_query,
        text_search=task.text_search,
        check_interval=task.check_interval,
        is_active=task.id in running_ids,
        papers_imported=task.papers_imported,
        errors=task.errors,
        last_run=task.last_run.isoformat() if task.last_run else None,
        logs=[LogEntry(**log) for log in logs],
        imported_papers=[ImportedPaper(**p) for p in imported_papers],
    )
