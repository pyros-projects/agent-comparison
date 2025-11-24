from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any
import logging

from ..models.database import PaperDB
from ..models.schemas import TheoryAnalysis, TheoryArgument
from ..services.llm_service import LLMService
from ..services.embedding_service import EmbeddingService

router = APIRouter()
logger = logging.getLogger(__name__)
paper_db = PaperDB()
llm_service = LLMService()
embedding_service = EmbeddingService()

@router.post("/analyze", response_model=TheoryAnalysis)
async def analyze_theory(
    theory: str,
    max_papers: int = 20
):
    """Analyze a theory/hypothesis against the paper collection"""
    try:
        if not llm_service.is_available():
            raise HTTPException(
                status_code=503,
                detail="LLM service unavailable. Theory mode is disabled."
            )
        
        if not theory.strip():
            raise HTTPException(status_code=400, detail="Theory statement is required")
        
        # Get all papers with embeddings
        papers = paper_db.get_papers(limit=max_papers * 2)  # Get more to filter
        
        # Get theory embedding
        theory_embedding = await embedding_service.get_embedding(theory)
        if not theory_embedding:
            raise HTTPException(status_code=503, detail="Embedding service unavailable")
        
        # Analyze each paper for relevance to the theory
        pro_arguments = []
        con_arguments = []
        
        for paper in papers:
            if not paper.summary or paper.summary.startswith("<"):  # Skip placeholders
                continue
                
            # Get paper embedding
            paper_embedding = await embedding_service.get_embedding(
                f"{paper.title} {paper.abstract}"
            )
            if not paper_embedding:
                continue
            
            # Calculate relevance
            relevance = embedding_service.calculate_similarity(
                theory_embedding, paper_embedding
            )
            
            if relevance < 0.3:  # Skip low relevance papers
                continue
            
            # Analyze paper's stance on the theory
            analysis = await llm_service.analyze_theory_stance(
                theory=theory,
                paper_title=paper.title,
                paper_abstract=paper.abstract,
                paper_summary=paper.summary
            )
            
            if analysis:
                argument = TheoryArgument(
                    paper=paper,
                    relevance_score=relevance,
                    argument_summary=analysis.get("summary", ""),
                    key_quotes=analysis.get("quotes", []),
                    stance=analysis.get("stance", "neutral")
                )
                
                if analysis.get("stance") == "supporting":
                    pro_arguments.append(argument)
                elif analysis.get("stance") == "contradicting":
                    con_arguments.append(argument)
        
        # Sort by relevance
        pro_arguments.sort(key=lambda x: x.relevance_score, reverse=True)
        con_arguments.sort(key=lambda x: x.relevance_score, reverse=True)
        
        return TheoryAnalysis(
            theory=theory,
            pro_arguments=pro_arguments[:max_papers//2],
            con_arguments=con_arguments[:max_papers//2],
            total_papers_analyzed=len(papers)
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error analyzing theory: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/status")
async def get_theory_mode_status():
    """Get the status of theory mode (LLM availability)"""
    try:
        is_available = llm_service.is_available()
        return {
            "theory_mode_available": is_available,
            "message": "Theory mode is available" if is_available else "LLM service unavailable"
        }
    except Exception as e:
        logger.error(f"Error checking theory mode status: {e}")
        raise HTTPException(status_code=500, detail=str(e))
