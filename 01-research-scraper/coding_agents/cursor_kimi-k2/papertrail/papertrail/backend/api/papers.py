from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import List, Optional
import logging

from ..models.database import PaperDB
from ..models.schemas import Paper, PaperCreate, PaperUpdate
from ..services.paper_service import PaperService
from ..services.websocket_manager import WebSocketManager

router = APIRouter()
logger = logging.getLogger(__name__)
paper_service = PaperService()
paper_db = PaperDB()

@router.get("/", response_model=List[Paper])
async def get_papers(
    skip: int = 0,
    limit: int = 100,
    search: Optional[str] = None,
    category: Optional[str] = None,
    status: Optional[str] = None,
    starred: Optional[bool] = None
):
    """Get papers with filtering and pagination"""
    try:
        papers = paper_db.get_papers(
            skip=skip,
            limit=limit,
            search=search,
            category=category,
            status=status,
            starred=starred
        )
        return papers
    except Exception as e:
        logger.error(f"Error getting papers: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{paper_id}", response_model=Paper)
async def get_paper(paper_id: str):
    """Get a specific paper by ID"""
    try:
        paper = paper_db.get_paper(paper_id)
        if not paper:
            raise HTTPException(status_code=404, detail="Paper not found")
        return paper
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting paper {paper_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/", response_model=Paper)
async def create_paper(
    paper: PaperCreate,
    background_tasks: BackgroundTasks
):
    """Create a new paper (manual ingestion)"""
    try:
        new_paper = paper_service.create_paper(paper)
        
        # Start background processing
        background_tasks.add_task(
            paper_service.process_paper_async,
            new_paper.id,
            WebSocketManager()
        )
        
        return new_paper
    except Exception as e:
        logger.error(f"Error creating paper: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/ingest", response_model=dict)
async def ingest_paper(
    arxiv_url: str,
    background_tasks: BackgroundTasks
):
    """Ingest paper from arXiv URL"""
    try:
        paper = await paper_service.ingest_from_arxiv(arxiv_url)
        
        # Start background processing
        background_tasks.add_task(
            paper_service.process_paper_async,
            paper.id,
            WebSocketManager()
        )
        
        return {"paper_id": paper.id, "status": "processing"}
    except Exception as e:
        logger.error(f"Error ingesting paper from {arxiv_url}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/{paper_id}", response_model=Paper)
async def update_paper(paper_id: str, paper_update: PaperUpdate):
    """Update a paper"""
    try:
        updated_paper = paper_db.update_paper(paper_id, paper_update)
        if not updated_paper:
            raise HTTPException(status_code=404, detail="Paper not found")
        return updated_paper
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating paper {paper_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{paper_id}")
async def delete_paper(paper_id: str):
    """Delete a paper"""
    try:
        success = paper_db.delete_paper(paper_id)
        if not success:
            raise HTTPException(status_code=404, detail="Paper not found")
        return {"message": "Paper deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting paper {paper_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{paper_id}/star")
async def star_paper(paper_id: str):
    """Star/unstar a paper"""
    try:
        paper = paper_db.toggle_star(paper_id)
        if not paper:
            raise HTTPException(status_code=404, detail="Paper not found")
        return paper
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error starring paper {paper_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{paper_id}/mark-read")
async def mark_paper_read(paper_id: str):
    """Mark paper as read"""
    try:
        paper = paper_db.mark_as_read(paper_id)
        if not paper:
            raise HTTPException(status_code=404, detail="Paper not found")
        return paper
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error marking paper {paper_id} as read: {e}")
        raise HTTPException(status_code=500, detail=str(e))
