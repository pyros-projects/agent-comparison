import logging
import arxiv
import requests
import asyncio
from datetime import datetime
from typing import Optional, Dict, Any
import PyPDF2
import io
from ..models.schemas import Paper, PaperStatus
from ..models.database import db

logger = logging.getLogger(__name__)

class ArxivService:
    """Service for fetching papers from arXiv"""
    
    def __init__(self):
        self.client = arxiv.Client()
    
    async def fetch_paper_by_id(self, arxiv_id: str) -> Optional[Paper]:
        """Fetch a single paper by arXiv ID"""
        try:
            # Clean arXiv ID
            arxiv_id = arxiv_id.strip()
            if arxiv_id.startswith('http'):
                # Extract ID from URL
                arxiv_id = arxiv_id.split('/')[-1]
            if arxiv_id.endswith('.pdf'):
                arxiv_id = arxiv_id[:-4]
            
            logger.info(f"Fetching paper with ID: {arxiv_id}")
            
            # Search for the paper
            search = arxiv.Search(id_list=[arxiv_id])
            results = list(self.client.results(search))
            
            if not results:
                logger.warning(f"No paper found with ID: {arxiv_id}")
                return None
            
            arxiv_paper = results[0]
            
            # Check if paper already exists
            existing = db.papers.get(db.papers.id == arxiv_id)
            if existing:
                logger.info(f"Paper {arxiv_id} already exists, skipping")
                return None
            
            # Create paper object
            paper = Paper(
                id=arxiv_id,
                title=arxiv_paper.title,
                authors=[str(author) for author in arxiv_paper.authors],
                abstract=arxiv_paper.summary,
                categories=list(arxiv_paper.categories),
                published_date=arxiv_paper.published,
                pdf_url=arxiv_paper.pdf_url,
                status=PaperStatus.NEW
            )
            
            # Store paper in database
            db.papers.insert(paper.model_dump())
            logger.info(f"Paper {arxiv_id} stored successfully")
            
            return paper
            
        except Exception as e:
            logger.error(f"Failed to fetch paper {arxiv_id}: {e}")
            return None
    
    async def fetch_paper_content(self, paper: Paper) -> Optional[str]:
        """Fetch and extract text content from PDF"""
        try:
            logger.info(f"Fetching PDF content for paper {paper.id}")
            
            # Download PDF
            response = requests.get(paper.pdf_url, timeout=30)
            response.raise_for_status()
            
            # Extract text from PDF
            pdf_file = io.BytesIO(response.content)
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            
            text_content = ""
            for page_num, page in enumerate(pdf_reader.pages):
                try:
                    text = page.extract_text()
                    if text:
                        text_content += f"

--- Page {page_num + 1} ---

{text}"
                except Exception as e:
                    logger.warning(f"Failed to extract text from page {page_num + 1}: {e}")
            
            if text_content.strip():
                # Update paper with content
                paper.pdf_content = text_content
                paper.file_size = len(response.content)
                paper.updated_at = datetime.utcnow()
                
                db.papers.update(paper.model_dump(), db.papers.id == paper.id)
                logger.info(f"PDF content extracted for paper {paper.id}, size: {len(text_content)} chars")
                
                return text_content
            else:
                logger.warning(f"No text content extracted from PDF for paper {paper.id}")
                return None
                
        except Exception as e:
            logger.error(f"Failed to fetch PDF content for paper {paper.id}: {e}")
            return None
    
    async def search_papers(self, 
                          categories: Optional[list] = None,
                          query: Optional[str] = None,
                          max_results: int = 50) -> list:
        """Search for papers on arXiv"""
        try:
            # Build search query
            search_query = ""
            
            if query:
                search_query += f"all:{query}"
            
            if categories:
                cat_query = " OR ".join([f"cat:{cat}" for cat in categories])
                if search_query:
                    search_query += f" AND ({cat_query})"
                else:
                    search_query = cat_query
            
            logger.info(f"Searching arXiv with query: {search_query}")
            
            search = arxiv.Search(
                query=search_query,
                max_results=max_results,
                sort_by=arxiv.SortCriterion.SubmittedDate,
                sort_order=arxiv.SortOrder.Descending
            )
            
            results = list(self.client.results(search))
            logger.info(f"Found {len(results)} papers from arXiv search")
            
            return results
            
        except Exception as e:
            logger.error(f"Failed to search arXiv: {e}")
            return []

# Global arXiv service instance
arxiv_service = ArxivService()
