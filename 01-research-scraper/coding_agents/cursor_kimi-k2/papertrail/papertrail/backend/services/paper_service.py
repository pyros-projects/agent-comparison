import logging
import asyncio
from typing import Optional, List, Dict, Any
from datetime import datetime
from ..models.database import db
from ..models.schemas import Paper, PaperStatus
from .arxiv_service import arxiv_service
from .embedding_service import embedding_service
from .llm_service import llm_service

logger = logging.getLogger(__name__)

class PaperService:
    """Service for paper ingestion and processing"""
    
    def __init__(self):
        self.processing_queue = set()
    
    async def ingest_paper(self, arxiv_id: str) -> Optional[Paper]:
        """Ingest a single paper from arXiv"""
        try:
            logger.info(f"Starting ingestion for paper: {arxiv_id}")
            
            # Check if already processing
            if arxiv_id in self.processing_queue:
                logger.info(f"Paper {arxiv_id} already being processed")
                return None
            
            self.processing_queue.add(arxiv_id)
            
            # Fetch paper metadata
            paper = await arxiv_service.fetch_paper_by_id(arxiv_id)
            if not paper:
                logger.warning(f"Failed to fetch paper {arxiv_id}")
                return None
            
            # Fetch PDF content
            await arxiv_service.fetch_paper_content(paper)
            
            # Generate embedding
            text_for_embedding = f"{paper.title} {paper.abstract}"
            if paper.pdf_content:
                text_for_embedding += f" {paper.pdf_content[:2000]}"
            
            await embedding_service.generate_embedding(text_for_embedding, paper.id)
            
            # Generate LLM summary (with fallback to placeholders)
            paper_data = paper.model_dump()
            summary_data = await llm_service.generate_paper_summary(paper_data)
            
            # Update paper with LLM data
            paper.summary = summary_data.get("summary", "<summary>")
            paper.keywords = summary_data.get("keywords", [])
            paper.key_contributions = summary_data.get("key_contributions", "<key_contributions>")
            paper.methodology = summary_data.get("methodology", "<methodology>")
            paper.results = summary_data.get("results", "<results>")
            paper.further_research = summary_data.get("further_research", "<further_research>")
            paper.updated_at = datetime.utcnow()
            
            # Update in database
            db.papers.update(paper.model_dump(), db.papers.id == paper.id)
            
            logger.info(f"Successfully ingested paper: {arxiv_id}")
            return paper
            
        except Exception as e:
            logger.error(f"Failed to ingest paper {arxiv_id}: {e}")
            return None
        finally:
            self.processing_queue.discard(arxiv_id)
    
    def get_paper(self, paper_id: str) -> Optional[Paper]:
        """Get a paper by ID"""
        try:
            result = db.papers.get(db.papers.id == paper_id)
            if result:
                return Paper(**result)
            return None
        except Exception as e:
            logger.error(f"Failed to get paper {paper_id}: {e}")
            return None
    
    def list_papers(self, skip: int = 0, limit: int = 50, 
                   status: Optional[PaperStatus] = None) -> List[Paper]:
        """List papers with pagination and filtering"""
        try:
            query = db.papers.all()
            
            if status:
                query = [p for p in query if p.get('status') == status]
            
            # Sort by published date descending
            query.sort(key=lambda x: x.get('published_date', ''), reverse=True)
            
            papers = [Paper(**p) for p in query[skip:skip + limit]]
            return papers
            
        except Exception as e:
            logger.error(f"Failed to list papers: {e}")
            return []
    
    def update_paper_status(self, paper_id: str, status: PaperStatus) -> bool:
        """Update paper status"""
        try:
            paper = self.get_paper(paper_id)
            if not paper:
                return False
            
            paper.status = status
            paper.updated_at = datetime.utcnow()
            
            db.papers.update(paper.model_dump(), db.papers.id == paper_id)
            logger.info(f"Updated paper {paper_id} status to {status}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to update paper status: {e}")
            return False

# Global paper service instance
paper_service = PaperService()
