from datetime import datetime
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from enum import Enum

class PaperStatus(str, Enum):
    NEW = "new"
    READ = "read"
    STARRED = "starred"

class TaskStatus(str, Enum):
    RUNNING = "running"
    STOPPED = "stopped"
    ERROR = "error"

class Paper(BaseModel):
    """Schema for research papers"""
    id: str = Field(..., description="arXiv ID")
    title: str
    authors: List[str]
    abstract: str
    categories: List[str]
    published_date: datetime
    pdf_url: str
    pdf_content: Optional[str] = None
    status: PaperStatus = PaperStatus.NEW
    
    # AI-generated fields (can be placeholders)
    summary: Optional[str] = None  # Can be "<summary>" placeholder
    keywords: List[str] = Field(default_factory=list)
    key_contributions: Optional[str] = None
    methodology: Optional[str] = None
    results: Optional[str] = None
    further_research: Optional[str] = None
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    file_size: Optional[int] = None
    
    # User annotations
    notes: Optional[str] = None
    tags: List[str] = Field(default_factory=list)

class Embedding(BaseModel):
    """Schema for paper embeddings"""
    paper_id: str
    embedding: List[float]
    model_name: str
    created_at: datetime = Field(default_factory=datetime.utcnow)

class Relationship(BaseModel):
    """Schema for paper relationships in GraphRAG"""
    source_paper_id: str
    target_paper_id: str
    relationship_type: str  # 'citation', 'topic_similarity', 'author_connection', 'semantic_similarity'
    strength: float = Field(..., ge=0.0, le=1.0)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.utcnow)

class ContinuousImportTask(BaseModel):
    """Schema for continuous import tasks"""
    id: str
    name: str
    status: TaskStatus = TaskStatus.STOPPED
    
    # Filter configuration
    categories: List[str] = Field(default_factory=list)
    semantic_query: Optional[str] = None
    text_search: Optional[str] = None
    check_interval: int = Field(default=300)  # seconds
    
    # Runtime data
    last_check: Optional[datetime] = None
    papers_imported_today: int = 0
    papers_imported_total: int = 0
    error_count: int = 0
    last_error: Optional[str] = None
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class BackfillQueueItem(BaseModel):
    """Schema for items in the LLM backfill queue"""
    paper_id: str
    fields_to_fill: List[str]  # Which placeholder fields need filling
    priority: int = Field(default=1)  # 1=high, 2=medium, 3=low
    attempts: int = 0
    max_attempts: int = 3
    last_error: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class SearchResult(BaseModel):
    """Schema for search results"""
    paper: Paper
    score: float
    highlights: Dict[str, Any] = Field(default_factory=dict)

class TheoryAnalysisResult(BaseModel):
    """Schema for theory mode analysis results"""
    theory_statement: str
    pro_arguments: List[Dict[str, Any]] = Field(default_factory=list)
    contra_arguments: List[Dict[str, Any]] = Field(default_factory=list)
    summary: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
