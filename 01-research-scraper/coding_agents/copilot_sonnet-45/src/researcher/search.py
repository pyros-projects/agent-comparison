"""Search and retrieval services."""

from typing import List, Dict, Any, Optional
import numpy as np

from researcher.models import Paper, SearchRequest, TheoryRequest, TheoryArgument
from researcher.database import db
from researcher.embeddings import embedding_service
from researcher.llm import llm_service
from researcher.logger import setup_logger

logger = setup_logger(__name__)


class SearchService:
    """Semantic search and retrieval service."""
    
    def semantic_search(self, request: SearchRequest) -> List[Dict[str, Any]]:
        """Perform semantic search across papers.
        
        Args:
            request: Search request with query and limit
            
        Returns:
            List of papers with relevance scores
        """
        logger.info(f"Semantic search: '{request.query}' (limit: {request.limit})")
        
        # Generate query embedding
        query_embedding = embedding_service.generate_embedding(request.query)
        
        # Get all embeddings
        all_embeddings = db.get_all_embeddings()
        
        # Compute similarities
        results = []
        for paper_embedding in all_embeddings:
            similarity = embedding_service.compute_similarity(
                query_embedding,
                paper_embedding.embedding
            )
            
            paper = db.get_paper(paper_embedding.paper_id)
            if paper:
                results.append({
                    "paper": paper,
                    "relevance_score": float(similarity)
                })
        
        # Sort by relevance
        results.sort(key=lambda x: x["relevance_score"], reverse=True)
        
        logger.info(f"Found {len(results)} results, returning top {request.limit}")
        return results[:request.limit]
    
    def filter_papers(
        self,
        status: Optional[str] = None,
        categories: Optional[List[str]] = None,
        text_query: Optional[str] = None
    ) -> List[Paper]:
        """Filter papers by various criteria.
        
        Args:
            status: Filter by status (new, read, starred)
            categories: Filter by arXiv categories
            text_query: Text search in title/abstract
            
        Returns:
            List of matching papers
        """
        logger.debug(f"Filtering papers: status={status}, categories={categories}, text={text_query}")
        
        papers = db.get_all_papers()
        
        # Apply filters
        if status:
            papers = [p for p in papers if p.status == status]
        
        if categories:
            papers = [p for p in papers if any(cat in p.categories for cat in categories)]
        
        if text_query:
            query_lower = text_query.lower()
            papers = [
                p for p in papers
                if query_lower in p.title.lower() or query_lower in p.abstract.lower()
            ]
        
        logger.debug(f"Filtered to {len(papers)} papers")
        return papers
    
    def get_similar_papers(self, paper_id: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Find papers similar to a given paper.
        
        Args:
            paper_id: Paper ID
            limit: Maximum number of results
            
        Returns:
            List of similar papers with scores
        """
        logger.info(f"Finding similar papers to: {paper_id}")
        
        # Get paper embedding
        paper_embedding = db.get_embedding(paper_id)
        if not paper_embedding:
            logger.warning(f"No embedding found for paper: {paper_id}")
            return []
        
        # Get all other embeddings
        all_embeddings = db.get_all_embeddings()
        
        results = []
        for other_embedding in all_embeddings:
            if other_embedding.paper_id == paper_id:
                continue
            
            similarity = embedding_service.compute_similarity(
                paper_embedding.embedding,
                other_embedding.embedding
            )
            
            paper = db.get_paper(other_embedding.paper_id)
            if paper:
                results.append({
                    "paper": paper,
                    "similarity_score": float(similarity)
                })
        
        # Sort by similarity
        results.sort(key=lambda x: x["similarity_score"], reverse=True)
        
        return results[:limit]


class TheoryService:
    """Theory mode - argument extraction service."""
    
    def analyze_theory(self, request: TheoryRequest) -> Dict[str, List[TheoryArgument]]:
        """Analyze papers to find pro/contra arguments for a hypothesis.
        
        Args:
            request: Theory request with hypothesis
            
        Returns:
            Dictionary with 'pro' and 'contra' argument lists
        """
        logger.info(f"Theory analysis: '{request.hypothesis}'")
        
        # Check LLM availability
        if not llm_service.is_available():
            logger.warning("LLM unavailable, cannot perform theory analysis")
            return {"pro": [], "contra": []}
        
        # Get all papers
        papers = db.get_all_papers()
        
        # First, use semantic search to find relevant papers
        query_embedding = embedding_service.generate_embedding(request.hypothesis)
        all_embeddings = db.get_all_embeddings()
        
        # Score papers by relevance
        paper_scores = []
        for paper_embedding in all_embeddings:
            similarity = embedding_service.compute_similarity(
                query_embedding,
                paper_embedding.embedding
            )
            paper = db.get_paper(paper_embedding.paper_id)
            if paper:
                paper_scores.append((paper, similarity))
        
        # Sort by relevance and take top candidates
        paper_scores.sort(key=lambda x: x[1], reverse=True)
        top_papers = paper_scores[:request.limit_per_side * 3]  # Get more candidates
        
        # Prepare papers for LLM analysis
        papers_for_analysis = []
        for paper, score in top_papers:
            papers_for_analysis.append({
                "id": paper.id,
                "title": paper.title,
                "abstract": paper.abstract,
                "full_text": paper.full_text
            })
        
        # Extract arguments using LLM
        arguments = llm_service.extract_arguments(request.hypothesis, papers_for_analysis)
        
        # Separate pro and contra
        pro_args = []
        contra_args = []
        
        for arg in arguments:
            theory_arg = TheoryArgument(**arg)
            if arg["argument_type"] == "pro":
                pro_args.append(theory_arg)
            elif arg["argument_type"] == "contra":
                contra_args.append(theory_arg)
        
        # Sort by relevance and limit
        pro_args.sort(key=lambda x: x.relevance_score, reverse=True)
        contra_args.sort(key=lambda x: x.relevance_score, reverse=True)
        
        result = {
            "pro": pro_args[:request.limit_per_side],
            "contra": contra_args[:request.limit_per_side]
        }
        
        logger.info(f"Theory analysis complete: {len(result['pro'])} pro, {len(result['contra'])} contra")
        return result


# Global service instances
search_service = SearchService()
theory_service = TheoryService()
