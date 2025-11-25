"""Search and Theory Mode API routes."""

import logging
from typing import Optional

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

from researcher.models import TheoryAnalysisResult, TheoryArgument
from researcher.services import (
    get_database,
    get_embedding_store,
    get_llm_service,
)

logger = logging.getLogger("papertrail.api.search")

router = APIRouter()


class SearchQuery(BaseModel):
    """Search query model."""
    query: str
    top_k: int = 20


class SearchResult(BaseModel):
    """Search result."""
    paper_id: str
    title: str
    abstract: str
    score: float
    primary_category: str
    authors: list[str]


class SearchResponse(BaseModel):
    """Search response."""
    query: str
    results: list[SearchResult]
    total: int


class TheoryQuery(BaseModel):
    """Theory analysis query."""
    theory: str


class TheoryResponse(BaseModel):
    """Theory analysis response."""
    theory: str
    pro_arguments: list[dict]
    contra_arguments: list[dict]
    analysis_summary: str
    llm_available: bool
    error: Optional[str] = None


@router.post("/semantic", response_model=SearchResponse)
async def semantic_search(query: SearchQuery):
    """Perform semantic search across papers."""
    logger.info(f"Semantic search: {query.query}")
    
    db = get_database()
    embedding_store = get_embedding_store()
    
    # Search by embedding similarity
    results = embedding_store.search_similar(query.query, top_k=query.top_k)
    
    search_results = []
    for paper_id, score in results:
        paper = db.get_paper(paper_id)
        if paper:
            search_results.append(SearchResult(
                paper_id=paper.id,
                title=paper.title,
                abstract=paper.abstract[:500],
                score=score,
                primary_category=paper.primary_category,
                authors=paper.authors[:5],
            ))
    
    return SearchResponse(
        query=query.query,
        results=search_results,
        total=len(search_results),
    )


@router.get("/text")
async def text_search(
    q: str = Query(..., min_length=1),
    limit: int = Query(20, ge=1, le=100),
):
    """Perform text search across papers."""
    logger.info(f"Text search: {q}")
    
    db = get_database()
    papers = db.search_papers_text(q)
    
    results = []
    for paper in papers[:limit]:
        results.append({
            "paper_id": paper.id,
            "title": paper.title,
            "abstract": paper.abstract[:500],
            "primary_category": paper.primary_category,
            "authors": paper.authors[:5],
        })
    
    return {
        "query": q,
        "results": results,
        "total": len(papers),
    }


@router.post("/theory", response_model=TheoryResponse)
async def analyze_theory(query: TheoryQuery):
    """Analyze papers for/against a theory (Theory Mode)."""
    logger.info(f"Theory analysis: {query.theory}")
    
    llm_service = get_llm_service()
    db = get_database()
    embedding_store = get_embedding_store()
    
    # Check LLM availability
    if not llm_service.available:
        logger.warning("LLM unavailable for theory analysis")
        return TheoryResponse(
            theory=query.theory,
            pro_arguments=[],
            contra_arguments=[],
            analysis_summary="",
            llm_available=False,
            error="Theory Mode requires an active LLM connection. Please check your API configuration.",
        )
    
    # Find relevant papers using semantic search
    relevant_ids = embedding_store.search_similar(query.theory, top_k=30)
    
    papers_data = []
    for paper_id, score in relevant_ids:
        paper = db.get_paper(paper_id)
        if paper and score > 0.3:  # Only include somewhat relevant papers
            papers_data.append({
                "id": paper.id,
                "arxiv_id": paper.arxiv_id,
                "title": paper.title,
                "abstract": paper.abstract,
                "primary_category": paper.primary_category,
            })
    
    if not papers_data:
        return TheoryResponse(
            theory=query.theory,
            pro_arguments=[],
            contra_arguments=[],
            analysis_summary="No relevant papers found in the database.",
            llm_available=True,
        )
    
    # Analyze with LLM
    result = await llm_service.analyze_theory(query.theory, papers_data)
    
    if "error" in result and result["error"]:
        return TheoryResponse(
            theory=query.theory,
            pro_arguments=[],
            contra_arguments=[],
            analysis_summary="",
            llm_available=False,
            error=result["error"],
        )
    
    return TheoryResponse(
        theory=query.theory,
        pro_arguments=result.get("pro_arguments", []),
        contra_arguments=result.get("contra_arguments", []),
        analysis_summary=result.get("analysis_summary", ""),
        llm_available=True,
    )


@router.get("/theory/status")
async def theory_mode_status():
    """Check if Theory Mode is available."""
    llm_service = get_llm_service()
    
    return {
        "available": llm_service.available,
        "message": "Theory Mode is ready" if llm_service.available else "Theory Mode requires an active LLM connection",
    }
