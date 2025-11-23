"""Pydantic models for PaperTrail application."""

from datetime import datetime
from enum import Enum
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class PaperStatus(str, Enum):
    """Paper reading status."""
    NEW = "new"
    READ = "read"
    STARRED = "starred"


class Author(BaseModel):
    """Paper author."""
    name: str
    affiliation: Optional[str] = None


class Paper(BaseModel):
    """Research paper model."""
    id: str = Field(..., description="Unique identifier (arXiv ID)")
    title: str
    authors: List[Author]
    abstract: str
    arxiv_id: str
    arxiv_url: str
    pdf_url: str
    published: datetime
    updated: Optional[datetime] = None
    categories: List[str] = Field(default_factory=list)
    primary_category: Optional[str] = None
    
    # Content
    full_text: Optional[str] = None
    
    # LLM-generated fields (may be placeholders)
    summary: Optional[str] = Field(None, description="AI-generated summary or '<summary>' placeholder")
    key_contributions: Optional[List[str]] = Field(None, description="Key contributions or None")
    methodology: Optional[str] = Field(None, description="Methodology summary or '<methodology>' placeholder")
    results: Optional[str] = Field(None, description="Results summary or '<results>' placeholder")
    keywords: Optional[List[str]] = Field(None, description="Extracted keywords or None")
    
    # Metadata
    status: PaperStatus = PaperStatus.NEW
    notes: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Flags
    needs_llm_processing: bool = Field(False, description="True if any field has placeholders")


class PaperEmbedding(BaseModel):
    """Paper embedding for semantic search."""
    paper_id: str
    embedding: List[float]
    model: str
    created_at: datetime = Field(default_factory=datetime.utcnow)


class PaperRelationship(BaseModel):
    """Relationship between two papers."""
    source_id: str
    target_id: str
    relationship_type: str  # "cites", "cited_by", "shared_author", "topic_similarity"
    weight: float = 1.0
    metadata: Optional[Dict[str, Any]] = None


class ContinuousImportFilter(BaseModel):
    """Filter configuration for continuous import."""
    arxiv_categories: Optional[List[str]] = Field(None, description="Filter by arXiv categories")
    semantic_query: Optional[str] = Field(None, description="Semantic abstract matching query")
    text_query: Optional[str] = Field(None, description="Text search in title/abstract")
    min_relevance_score: Optional[float] = Field(None, description="Minimum similarity score for semantic filter")


class ContinuousImportTask(BaseModel):
    """Continuous arXiv import task."""
    id: str
    name: str
    filters: ContinuousImportFilter
    check_interval_seconds: int = 300  # Default: 5 minutes
    max_results_per_check: int = 10
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)
    last_check: Optional[datetime] = None
    papers_imported: int = 0


class BackfillQueueItem(BaseModel):
    """Item in backfill queue for LLM processing."""
    paper_id: str
    fields_to_fill: List[str]  # ["summary", "keywords", etc.]
    priority: int = 0
    created_at: datetime = Field(default_factory=datetime.utcnow)
    attempts: int = 0


class SearchRequest(BaseModel):
    """Semantic search request."""
    query: str
    limit: int = 10


class TheoryRequest(BaseModel):
    """Theory mode analysis request."""
    hypothesis: str
    limit_per_side: int = 5


class TheoryArgument(BaseModel):
    """Argument for or against a theory."""
    paper_id: str
    paper_title: str
    relevance_score: float
    argument_type: str  # "pro" or "contra"
    summary: str
    key_quotes: Optional[List[str]] = None


class DashboardStats(BaseModel):
    """Dashboard statistics."""
    total_papers: int
    papers_by_category: Dict[str, int]
    papers_by_status: Dict[str, int]
    storage_size_mb: float
    recent_papers: List[Paper]
    active_import_tasks: int
    papers_imported_today: int
    papers_imported_week: int
    collection_growth: List[Dict[str, Any]]  # Date-based growth data


class IngestionProgress(BaseModel):
    """Real-time ingestion progress update."""
    paper_id: str
    status: str  # "fetching", "extracting", "embedding", "analyzing", "complete", "error"
    message: str
    progress_percent: Optional[int] = None
