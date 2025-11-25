"""arXiv integration service."""

import logging
import re
import asyncio
from datetime import datetime
from typing import Optional
import httpx
import feedparser

from researcher.config import Config

logger = logging.getLogger("papertrail.arxiv")

# arXiv API base URL - use HTTPS to avoid redirects
ARXIV_API_URL = "https://export.arxiv.org/api/query"

# arXiv categories
ARXIV_CATEGORIES = [
    "cs.AI",  # Artificial Intelligence
    "cs.CL",  # Computation and Language
    "cs.CV",  # Computer Vision
    "cs.LG",  # Machine Learning
    "cs.NE",  # Neural and Evolutionary Computing
    "cs.RO",  # Robotics
    "stat.ML",  # Machine Learning (Statistics)
    "cs.IR",  # Information Retrieval
    "cs.SE",  # Software Engineering
    "cs.DB",  # Databases
]


def extract_arxiv_id(url_or_id: str) -> str:
    """Extract arXiv ID from URL or return ID directly."""
    # Handle various arXiv URL formats
    patterns = [
        r"arxiv\.org/abs/(\d+\.\d+)",
        r"arxiv\.org/pdf/(\d+\.\d+)",
        r"^(\d+\.\d+)$",
        r"^(\d+\.\d+)v\d+$",
    ]
    
    for pattern in patterns:
        match = re.search(pattern, url_or_id)
        if match:
            return match.group(1)
    
    # Try to extract from full URL
    if "arxiv.org" in url_or_id:
        parts = url_or_id.split("/")
        for part in parts:
            if re.match(r"\d+\.\d+", part):
                return part.split("v")[0]  # Remove version
    
    return url_or_id


class ArxivService:
    """Service for interacting with arXiv API."""

    def __init__(self) -> None:
        """Initialize arXiv service."""
        self._client: Optional[httpx.AsyncClient] = None
        self._last_request_time = 0.0

    async def _get_client(self) -> httpx.AsyncClient:
        """Get or create HTTP client."""
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(timeout=30.0, follow_redirects=True)
        return self._client

    async def _rate_limit(self) -> None:
        """Respect arXiv rate limiting."""
        import time
        elapsed = time.time() - self._last_request_time
        if elapsed < Config.ARXIV_RATE_LIMIT:
            await asyncio.sleep(Config.ARXIV_RATE_LIMIT - elapsed)
        self._last_request_time = time.time()

    async def fetch_paper(self, arxiv_id: str) -> Optional[dict]:
        """Fetch paper metadata from arXiv."""
        arxiv_id = extract_arxiv_id(arxiv_id)
        logger.info(f"Fetching paper from arXiv: {arxiv_id}")
        
        await self._rate_limit()
        
        try:
            client = await self._get_client()
            response = await client.get(
                ARXIV_API_URL,
                params={
                    "id_list": arxiv_id,
                    "max_results": 1,
                },
            )
            response.raise_for_status()
            
            feed = feedparser.parse(response.text)
            
            if not feed.entries:
                logger.warning(f"No paper found for ID: {arxiv_id}")
                return None
            
            entry = feed.entries[0]
            
            # Parse authors
            authors = []
            if hasattr(entry, "authors"):
                authors = [a.get("name", "") for a in entry.authors]
            
            # Parse categories
            categories = []
            primary_category = ""
            if hasattr(entry, "tags"):
                categories = [t.get("term", "") for t in entry.tags]
                if categories:
                    primary_category = categories[0]
            
            # Parse dates
            published = None
            updated = None
            if hasattr(entry, "published"):
                try:
                    published = datetime.fromisoformat(
                        entry.published.replace("Z", "+00:00")
                    )
                except (ValueError, TypeError):
                    pass
            if hasattr(entry, "updated"):
                try:
                    updated = datetime.fromisoformat(
                        entry.updated.replace("Z", "+00:00")
                    )
                except (ValueError, TypeError):
                    pass
            
            # Get PDF URL
            pdf_url = f"https://arxiv.org/pdf/{arxiv_id}.pdf"
            for link in entry.get("links", []):
                if link.get("type") == "application/pdf":
                    pdf_url = link.get("href", pdf_url)
                    break
            
            paper_data = {
                "id": arxiv_id,
                "arxiv_id": arxiv_id,
                "title": entry.get("title", "").replace("\n", " ").strip(),
                "authors": authors,
                "abstract": entry.get("summary", "").replace("\n", " ").strip(),
                "categories": categories,
                "primary_category": primary_category,
                "published": published.isoformat() if published else None,
                "updated": updated.isoformat() if updated else None,
                "pdf_url": pdf_url,
            }
            
            logger.info(f"Fetched paper: {paper_data['title'][:50]}...")
            return paper_data
        except httpx.HTTPError as e:
            logger.error(f"HTTP error fetching paper {arxiv_id}: {e}")
            return None
        except Exception as e:
            logger.error(f"Error fetching paper {arxiv_id}: {e}")
            return None

    async def fetch_pdf_text(self, pdf_url: str) -> str:
        """Fetch and extract text from PDF."""
        logger.info(f"Fetching PDF: {pdf_url}")
        
        await self._rate_limit()
        
        try:
            client = await self._get_client()
            response = await client.get(pdf_url, follow_redirects=True)
            response.raise_for_status()
            
            # Extract text using pypdf
            from pypdf import PdfReader
            from io import BytesIO
            
            pdf_file = BytesIO(response.content)
            reader = PdfReader(pdf_file)
            
            text_parts = []
            for page in reader.pages:
                text = page.extract_text()
                if text:
                    text_parts.append(text)
            
            full_text = "\n".join(text_parts)
            logger.info(f"Extracted {len(full_text)} characters from PDF")
            return full_text
        except Exception as e:
            logger.error(f"Error extracting PDF text: {e}")
            return ""

    async def search_papers(
        self,
        query: Optional[str] = None,
        category: Optional[str] = None,
        max_results: int = 20,
        start: int = 0,
        sort_by: str = "submittedDate",
        sort_order: str = "descending",
    ) -> list[dict]:
        """Search for papers on arXiv with retry logic for rate limits."""
        logger.info(
            f"Searching arXiv: query={query}, category={category}, start={start}, max={max_results}"
        )
        
        # Build search query
        search_parts = []
        if query:
            search_parts.append(f"all:{query}")
        if category:
            search_parts.append(f"cat:{category}")
        
        search_query = " AND ".join(search_parts) if search_parts else "cat:cs.AI"
        
        # Retry logic for rate limiting
        max_retries = 3
        retry_delay = 10.0  # Start with 10 seconds on 429
        
        for attempt in range(max_retries):
            await self._rate_limit()
            
            try:
                client = await self._get_client()
                response = await client.get(
                    ARXIV_API_URL,
                    params={
                        "search_query": search_query,
                        "start": start,
                        "max_results": max_results,
                        "sortBy": sort_by,
                        "sortOrder": sort_order,
                    },
                )
                
                # Handle rate limiting with retry
                if response.status_code == 429:
                    wait_time = retry_delay * (2 ** attempt)  # Exponential backoff
                    logger.warning(f"Rate limited by arXiv (429), waiting {wait_time}s before retry {attempt + 1}/{max_retries}")
                    await asyncio.sleep(wait_time)
                    continue
                
                response.raise_for_status()
                
                feed = feedparser.parse(response.text)
                papers = []
                
                logger.debug(f"arXiv API returned {len(feed.entries)} entries")
                
                for entry in feed.entries:
                    # Parse arXiv ID from entry ID URL
                    entry_id = entry.get("id", "")
                    arxiv_id = entry_id.split("/abs/")[-1].split("v")[0] if "/abs/" in entry_id else ""
                    
                    if not arxiv_id:
                        logger.debug(f"Could not parse arxiv_id from entry: {entry_id}")
                        continue
                    
                    # Parse authors
                    authors = []
                    if hasattr(entry, "authors"):
                        authors = [a.get("name", "") for a in entry.authors]
                    
                    # Parse categories
                    categories = []
                    primary_category = ""
                    if hasattr(entry, "tags"):
                        categories = [t.get("term", "") for t in entry.tags]
                        if categories:
                            primary_category = categories[0]
                    
                    # Parse dates
                    published = None
                    if hasattr(entry, "published"):
                        try:
                            published = datetime.fromisoformat(
                                entry.published.replace("Z", "+00:00")
                            )
                        except (ValueError, TypeError):
                            pass
                    
                    papers.append({
                        "id": arxiv_id,
                        "arxiv_id": arxiv_id,
                        "title": entry.get("title", "").replace("\n", " ").strip(),
                        "authors": authors,
                        "abstract": entry.get("summary", "").replace("\n", " ").strip(),
                        "categories": categories,
                        "primary_category": primary_category,
                        "published": published.isoformat() if published else None,
                        "pdf_url": f"https://arxiv.org/pdf/{arxiv_id}.pdf",
                    })
                
                logger.info(f"Found {len(papers)} papers from arXiv")
                return papers
                
            except httpx.HTTPStatusError as e:
                if e.response.status_code == 429 and attempt < max_retries - 1:
                    wait_time = retry_delay * (2 ** attempt)
                    logger.warning(f"Rate limited (429), waiting {wait_time}s before retry")
                    await asyncio.sleep(wait_time)
                    continue
                logger.error(f"HTTP error searching arXiv: {e}")
                return []
            except httpx.HTTPError as e:
                logger.error(f"HTTP error searching arXiv: {e}")
                return []
            except Exception as e:
                logger.error(f"Error searching arXiv: {e}")
                return []
        
        logger.error("Max retries reached for arXiv API")
        return []

    async def close(self) -> None:
        """Close HTTP client."""
        if self._client:
            await self._client.aclose()


# Singleton instance
_arxiv_service: Optional[ArxivService] = None


def get_arxiv_service() -> ArxivService:
    """Get the arXiv service instance."""
    global _arxiv_service
    if _arxiv_service is None:
        _arxiv_service = ArxivService()
    return _arxiv_service
