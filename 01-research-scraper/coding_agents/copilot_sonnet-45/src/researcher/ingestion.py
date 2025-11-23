"""arXiv paper ingestion service."""

import re
from datetime import datetime
from typing import Optional, Callable, List
import arxiv
import httpx
from PyPDF2 import PdfReader
from io import BytesIO

from researcher.models import Paper, Author, PaperEmbedding, IngestionProgress
from researcher.database import db
from researcher.embeddings import embedding_service
from researcher.llm import llm_service
from researcher.logger import setup_logger

logger = setup_logger(__name__)


class ArxivIngestionService:
    """Service for fetching and processing arXiv papers."""
    
    def __init__(self):
        """Initialize ingestion service."""
        self.client = arxiv.Client()
    
    async def ingest_paper(
        self,
        arxiv_url: str,
        progress_callback: Optional[Callable[[IngestionProgress], None]] = None
    ) -> Paper:
        """Ingest a paper from arXiv URL.
        
        Args:
            arxiv_url: arXiv URL or ID
            progress_callback: Optional callback for progress updates
            
        Returns:
            Ingested Paper object
        """
        # Extract arXiv ID from URL
        arxiv_id = self._extract_arxiv_id(arxiv_url)
        logger.info(f"Starting ingestion for arXiv ID: {arxiv_id}")
        
        # Check if paper already exists
        if db.paper_exists(arxiv_id):
            logger.info(f"Paper already exists: {arxiv_id}")
            existing = db.get_all_papers()
            for p in existing:
                if p.arxiv_id == arxiv_id:
                    return p
        
        try:
            # Fetch metadata
            if progress_callback:
                await progress_callback(IngestionProgress(
                    paper_id=arxiv_id,
                    status="fetching",
                    message="Fetching paper metadata from arXiv",
                    progress_percent=10
                ))
            
            paper_data = await self._fetch_metadata(arxiv_id)
            logger.info(f"Fetched metadata for: {paper_data['title']}")
            
            # Extract PDF text
            if progress_callback:
                await progress_callback(IngestionProgress(
                    paper_id=arxiv_id,
                    status="extracting",
                    message="Extracting text from PDF",
                    progress_percent=30
                ))
            
            full_text = await self._extract_pdf_text(paper_data['pdf_url'])
            paper_data['full_text'] = full_text
            logger.info(f"Extracted {len(full_text)} characters from PDF")
            
            # Generate embedding
            if progress_callback:
                await progress_callback(IngestionProgress(
                    paper_id=arxiv_id,
                    status="embedding",
                    message="Generating embeddings",
                    progress_percent=50
                ))
            
            embedding = embedding_service.generate_embedding(
                f"{paper_data['title']} {paper_data['abstract']}"
            )
            logger.info(f"Generated embedding (dim: {len(embedding)})")
            
            # Generate LLM summary
            if progress_callback:
                await progress_callback(IngestionProgress(
                    paper_id=arxiv_id,
                    status="analyzing",
                    message="Generating AI summary",
                    progress_percent=70
                ))
            
            summary_data = llm_service.generate_paper_summary(
                paper_data['title'],
                paper_data['abstract'],
                full_text
            )
            paper_data.update(summary_data)
            
            # Create paper object
            paper = Paper(**paper_data)
            
            # Save to database
            if progress_callback:
                await progress_callback(IngestionProgress(
                    paper_id=arxiv_id,
                    status="saving",
                    message="Saving to database",
                    progress_percent=90
                ))
            
            db.insert_paper(paper)
            
            # Save embedding
            paper_embedding = PaperEmbedding(
                paper_id=paper.id,
                embedding=embedding,
                model=embedding_service.current_model
            )
            db.insert_embedding(paper_embedding)
            
            # Add to backfill queue if needed
            if paper.needs_llm_processing:
                fields = []
                if paper.summary == "<summary>":
                    fields.append("summary")
                if paper.methodology == "<methodology>":
                    fields.append("methodology")
                if paper.results == "<results>":
                    fields.append("results")
                if fields:
                    llm_service.add_to_backfill_queue(paper.id, fields)
            
            if progress_callback:
                await progress_callback(IngestionProgress(
                    paper_id=arxiv_id,
                    status="complete",
                    message="Paper ingested successfully",
                    progress_percent=100
                ))
            
            logger.info(f"✓ Successfully ingested paper: {paper.title}")
            return paper
            
        except Exception as e:
            logger.error(f"Error ingesting paper {arxiv_id}: {e}", exc_info=True)
            if progress_callback:
                await progress_callback(IngestionProgress(
                    paper_id=arxiv_id,
                    status="error",
                    message=f"Error: {str(e)}",
                    progress_percent=0
                ))
            raise
    
    def _extract_arxiv_id(self, arxiv_url: str) -> str:
        """Extract arXiv ID from URL or return as-is if already an ID.
        
        Args:
            arxiv_url: arXiv URL or ID
            
        Returns:
            arXiv ID
        """
        # Match patterns like: 2103.12345, 2103.12345v1, arxiv.org/abs/2103.12345
        pattern = r'(?:arxiv\.org/(?:abs|pdf)/)?(\d{4}\.\d{4,5}(?:v\d+)?)'
        match = re.search(pattern, arxiv_url)
        if match:
            return match.group(1)
        return arxiv_url
    
    async def _fetch_metadata(self, arxiv_id: str) -> dict:
        """Fetch paper metadata from arXiv.
        
        Args:
            arxiv_id: arXiv ID
            
        Returns:
            Dictionary with paper metadata
        """
        search = arxiv.Search(id_list=[arxiv_id])
        paper = next(self.client.results(search))
        
        return {
            "id": arxiv_id,
            "title": paper.title,
            "authors": [Author(name=str(author)) for author in paper.authors],
            "abstract": paper.summary,
            "arxiv_id": arxiv_id,
            "arxiv_url": paper.entry_id,
            "pdf_url": paper.pdf_url,
            "published": paper.published,
            "updated": paper.updated,
            "categories": paper.categories,
            "primary_category": paper.primary_category
        }
    
    async def _extract_pdf_text(self, pdf_url: str) -> str:
        """Extract text from PDF.
        
        Args:
            pdf_url: URL to PDF file
            
        Returns:
            Extracted text content
        """
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(pdf_url, timeout=30.0)
                response.raise_for_status()
                
                pdf_bytes = BytesIO(response.content)
                reader = PdfReader(pdf_bytes)
                
                text = ""
                for page in reader.pages:
                    text += page.extract_text() + "\n"
                
                return text.strip()
        except Exception as e:
            logger.warning(f"Failed to extract PDF text: {e}")
            return ""
    
    async def search_arxiv(
        self,
        query: Optional[str] = None,
        category: Optional[str] = None,
        max_results: int = 10
    ) -> List[dict]:
        """Search arXiv for papers.
        
        Args:
            query: Search query
            category: arXiv category filter
            max_results: Maximum number of results
            
        Returns:
            List of paper metadata dictionaries
        """
        logger.info(f"Searching arXiv: query='{query}', category='{category}', max={max_results}")
        
        # Build search query
        search_query = query or "all"
        if category:
            search_query = f"cat:{category}"
            if query:
                search_query = f"({query}) AND cat:{category}"
        
        search = arxiv.Search(
            query=search_query,
            max_results=max_results,
            sort_by=arxiv.SortCriterion.SubmittedDate,
            sort_order=arxiv.SortOrder.Descending
        )
        
        results = []
        for paper in self.client.results(search):
            results.append({
                "id": paper.get_short_id(),
                "title": paper.title,
                "authors": [Author(name=str(author)) for author in paper.authors],
                "abstract": paper.summary,
                "arxiv_id": paper.get_short_id(),
                "arxiv_url": paper.entry_id,
                "pdf_url": paper.pdf_url,
                "published": paper.published,
                "updated": paper.updated,
                "categories": paper.categories,
                "primary_category": paper.primary_category
            })
        
        logger.info(f"Found {len(results)} papers")
        return results


# Global ingestion service instance
ingestion_service = ArxivIngestionService()
