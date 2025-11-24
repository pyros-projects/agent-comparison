from fastapi import APIRouter, HTTPException
from typing import List, Optional
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get('/', response_model=list)
async def get_papers(skip: int = 0, limit: int = 100, search: Optional[str] = None):
    return []

@router.get('/{paper_id}')
async def get_paper(paper_id: str):
    return {'id': paper_id, 'title': 'Sample Paper', 'authors': ['Author 1'], 'abstract': 'Sample abstract'}

@router.post('/ingest')
async def ingest_paper(arxiv_url: str):
    return {'paper_id': '123', 'status': 'processing'}

@router.post('/{paper_id}/star')
async def star_paper(paper_id: str):
    return {'id': paper_id, 'starred': True}
