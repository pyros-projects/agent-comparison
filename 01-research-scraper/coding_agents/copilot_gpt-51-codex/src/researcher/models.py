from __future__ import annotations

import datetime as dt
import uuid
from enum import Enum
from typing import Any, List, Optional

from pydantic import BaseModel, Field


class PaperStatus(str, Enum):
    NEW = "new"
    READ = "read"
    STARRED = "starred"


class Note(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    created_at: dt.datetime = Field(default_factory=lambda: dt.datetime.now(dt.timezone.utc))
    text: str


class Paper(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    arxiv_id: str
    title: str
    authors: List[str]
    abstract: str
    categories: List[str] = Field(default_factory=list)
    pdf_url: str
    published_at: dt.datetime
    status: PaperStatus = Field(default=PaperStatus.NEW)
    starred: bool = Field(default=False)
    tags: List[str] = Field(default_factory=list)
    keywords: List[str] = Field(default_factory=list)
    summary: str = Field(default="<summary>")
    methodology: str = Field(default="<methodology>")
    results: str = Field(default="<results>")
    further_work: str = Field(default="<further_work>")
    notes: List[Note] = Field(default_factory=list)
    content: str = Field(default="")
    vector: List[float] = Field(default_factory=list)
    related_ids: List[str] = Field(default_factory=list)
    placeholders: bool = Field(default=True)
    created_at: dt.datetime = Field(default_factory=lambda: dt.datetime.now(dt.timezone.utc))
    updated_at: dt.datetime = Field(default_factory=lambda: dt.datetime.now(dt.timezone.utc))


class PaperListResponse(BaseModel):
    items: List[Paper]
    total: int


class ManualIngestRequest(BaseModel):
    arxiv_url: str
    tags: List[str] | None = None


class ImportTaskStatus(str, Enum):
    RUNNING = "running"
    STOPPED = "stopped"


class ImportTaskConfig(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    category_filter: str | None = None
    text_filter: str | None = None
    semantic_filter: str | None = None
    interval_seconds: int = 900
    created_at: dt.datetime = Field(default_factory=lambda: dt.datetime.now(dt.timezone.utc))
    status: ImportTaskStatus = Field(default=ImportTaskStatus.RUNNING)
    total_imported: int = 0
    total_attempted: int = 0
    last_run_at: dt.datetime | None = None


class TheoryQueryRequest(BaseModel):
    hypothesis: str
    top_k: int = Field(default=5, ge=1, le=20)


class TheoryArgument(BaseModel):
    paper_id: str
    title: str
    relevance: float
    argument: str
    quotes: List[str] = Field(default_factory=list)


class TheoryResponse(BaseModel):
    hypothesis: str
    llm_available: bool
    pro: List[TheoryArgument] = Field(default_factory=list)
    contra: List[TheoryArgument] = Field(default_factory=list)
    message: str | None = None


class SimilarPaper(BaseModel):
    paper_id: str
    title: str
    score: float


class GraphNode(BaseModel):
    id: str
    label: str
    category: str


class GraphEdge(BaseModel):
    source: str
    target: str
    reason: str
    weight: float


class GraphResponse(BaseModel):
    nodes: List[GraphNode]
    edges: List[GraphEdge]


class DashboardStats(BaseModel):
    total_papers: int
    starred: int
    read: int
    categories: dict[str, int]
    recent_activity: List[dict[str, Any]]
    tasks: List[ImportTaskConfig]


class EventType(str, Enum):
    PAPER_INGESTED = "paper_ingested"
    TASK_UPDATED = "task_updated"
    THEORY_RESULT = "theory_result"
    BACKFILL = "backfill"
    ERROR = "error"
    STATUS = "status"


class EventMessage(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    type: EventType
    payload: dict[str, Any]
    created_at: dt.datetime = Field(default_factory=lambda: dt.datetime.now(dt.timezone.utc))


class SearchQuery(BaseModel):
    text: str | None = None
    category: str | None = None
    status: PaperStatus | None = None
    starred: bool | None = None
    limit: int = 50
    offset: int = 0


class SearchResponse(BaseModel):
    items: List[Paper]
    total: int

