from typing import List, Optional
from pydantic import BaseModel

class Paper(BaseModel):
    id: str
    title: str
    authors: List[str]
    abstract: str
    arxiv_id: str
    published_date: str
    categories: List[str]
    summary: Optional[str] = None
    keywords: List[str] = []
    starred: bool = False
    read: bool = False
    created_at: str

class PaperCreate(BaseModel):
    title: str
    authors: List[str]
    abstract: str
    arxiv_id: str
    published_date: str
    categories: List[str]

class PaperUpdate(BaseModel):
    starred: Optional[bool] = None
    read: Optional[bool] = None

class SearchResult(BaseModel):
    paper: Paper
    similarity_score: float

class TheoryArgument(BaseModel):
    paper: Paper
    relevance_score: float
    argument_summary: str
    key_quotes: List[str]
    stance: str

class TheoryAnalysis(BaseModel):
    theory: str
    pro_arguments: List[TheoryArgument]
    con_arguments: List[TheoryArgument]
    total_papers_analyzed: int
