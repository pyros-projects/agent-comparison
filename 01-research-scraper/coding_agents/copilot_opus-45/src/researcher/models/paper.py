"""Paper and related data models."""

from datetime import datetime
from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field


class PaperStatus(str, Enum):
    """Paper reading status."""
    NEW = "new"
    READ = "read"
    STARRED = "starred"


class Paper(BaseModel):
    """Research paper model."""
    id: str = Field(..., description="Unique paper ID (arXiv ID)")
    arxiv_id: str = Field(..., description="arXiv ID")
    title: str
    authors: list[str] = Field(default_factory=list)
    abstract: str = ""
    summary: str = ""  # AI-generated, may be placeholder
    keywords: list[str] = Field(default_factory=list)  # AI-extracted
    categories: list[str] = Field(default_factory=list)
    primary_category: str = ""
    published: Optional[datetime] = None
    updated: Optional[datetime] = None
    pdf_url: str = ""
    full_text: str = ""  # Extracted from PDF
    
    # New AI-generated fields
    questions_answered: list[str] = Field(default_factory=list)  # Questions this paper answers
    theories_supported: list[str] = Field(default_factory=list)  # Theories this paper supports
    
    # Status tracking
    status: PaperStatus = PaperStatus.NEW
    notes: str = ""  # User annotations
    manual_tags: list[str] = Field(default_factory=list)
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    
    # Placeholder tracking
    has_placeholder_summary: bool = False
    has_placeholder_keywords: bool = False
    has_placeholder_questions: bool = False
    has_placeholder_theories: bool = False
    
    # Embedding status
    has_embedding: bool = False


class PaperCreate(BaseModel):
    """Model for creating a paper from arXiv link."""
    arxiv_url: str = Field(..., description="arXiv URL or ID")


class PaperUpdate(BaseModel):
    """Model for updating a paper."""
    status: Optional[PaperStatus] = None
    notes: Optional[str] = None
    manual_tags: Optional[list[str]] = None


class PaperSearchResult(BaseModel):
    """Search result with similarity score."""
    paper: Paper
    score: float = 0.0
    highlights: list[str] = Field(default_factory=list)


class ImportTask(BaseModel):
    """Continuous import task configuration."""
    id: str
    name: str
    category: Optional[str] = None  # arXiv category filter
    semantic_query: Optional[str] = None  # Semantic matching query
    text_search: Optional[str] = None  # Text search filter
    check_interval: int = 60  # seconds
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.now)
    last_run: Optional[datetime] = None
    papers_imported: int = 0
    errors: int = 0


class ImportTaskCreate(BaseModel):
    """Model for creating an import task."""
    name: str
    category: Optional[str] = None
    semantic_query: Optional[str] = None
    text_search: Optional[str] = None
    check_interval: int = 60


class BackfillQueueItem(BaseModel):
    """Queue item for backfilling placeholder content."""
    paper_id: str
    field: str  # 'summary' or 'keywords'
    created_at: datetime = Field(default_factory=datetime.now)
    attempts: int = 0
    last_error: Optional[str] = None


class GraphRelationship(BaseModel):
    """Relationship between papers in the knowledge graph."""
    source_id: str
    target_id: str
    relationship_type: str  # 'citation', 'author', 'topic', 'similar'
    weight: float = 1.0
    metadata: dict = Field(default_factory=dict)


class TheoryArgument(BaseModel):
    """Argument for or against a theory."""
    paper_id: str
    paper_title: str
    stance: str  # 'pro' or 'contra'
    relevance_score: float
    summary: str
    key_quotes: list[str] = Field(default_factory=list)


class TheoryAnalysisResult(BaseModel):
    """Result of theory mode analysis."""
    theory: str
    pro_arguments: list[TheoryArgument]
    contra_arguments: list[TheoryArgument]
    analysis_summary: str = ""


class DashboardStats(BaseModel):
    """Dashboard statistics."""
    total_papers: int = 0
    storage_size_mb: float = 0.0
    papers_by_category: dict[str, int] = Field(default_factory=dict)
    papers_today: int = 0
    papers_this_week: int = 0
    active_import_tasks: int = 0
    papers_with_placeholders: int = 0
    llm_available: bool = False
    embedding_using_fallback: bool = False
