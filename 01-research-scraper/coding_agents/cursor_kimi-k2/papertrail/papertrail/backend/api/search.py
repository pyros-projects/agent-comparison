from fastapi import APIRouter, HTTPException
from typing import List, Optional
import logging

from ..models.database import PaperDB, EmbeddingDB
from ..models.schemas import Paper, SearchResult
from ..services.embedding_service import EmbeddingService
from ..services.graphrag_service import GraphRAGService

router = APIRouter()
logger = logging.getLogger(__name__)
paper_db = PaperDB()
embedding_db = EmbeddingDB()
embedding_service = EmbeddingService()
graphrag_service = GraphRAGService()

@router.get("/semantic", response_model=List[SearchResult])
async def semantic_search(
    query: str,
    limit: int = 10,
    threshold: float = 0.7
):
    """Semantic search using vector embeddings"""
    try:
        if not query.strip():
            return []
            
        # Get query embedding
        query_embedding = await embedding_service.get_embedding(query)
        if not query_embedding:
            raise HTTPException(status_code=503, detail="Embedding service unavailable")
        
        # Search for similar papers
        results = embedding_db.search_similar(
            query_embedding,
            limit=limit,
            threshold=threshold
        )
        
        # Get full paper details
        papers = []
        for result in results:
            paper = paper_db.get_paper(result['paper_id'])
            if paper:
                papers.append(SearchResult(
                    paper=paper,
                    similarity_score=result['similarity']
                ))
        
        return papers
    except Exception as e:
        logger.error(f"Error in semantic search: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/similar/{paper_id}", response_model=List[SearchResult])
async def find_similar_papers(
    paper_id: str,
    limit: int = 5
):
    """Find papers similar to a given paper"""
    try:
        paper = paper_db.get_paper(paper_id)
        if not paper:
            raise HTTPException(status_code=404, detail="Paper not found")
        
        # Get paper embedding
        paper_embedding = embedding_db.get_embedding(paper_id)
        if not paper_embedding:
            return []
        
        # Find similar papers
        results = embedding_db.search_similar(
            paper_embedding,
            limit=limit + 1,  # +1 to exclude the paper itself
            threshold=0.5
        )
        
        # Filter out the original paper and get details
        papers = []
        for result in results:
            if result['paper_id'] != paper_id:
                similar_paper = paper_db.get_paper(result['paper_id'])
                if similar_paper:
                    papers.append(SearchResult(
                        paper=similar_paper,
                        similarity_score=result['similarity']
                    ))
        
        return papers[:limit]
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error finding similar papers for {paper_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/text", response_model=List[Paper])
async def text_search(
    query: str,
    limit: int = 50
):
    """Text-based search across paper content"""
    try:
        if not query.strip():
            return []
        
        papers = paper_db.text_search(query, limit=limit)
        return papers
    except Exception as e:
        logger.error(f"Error in text search: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/graph/{paper_id}")
async def get_paper_graph(paper_id: str):
    """Get relationship graph for a paper"""
    try:
        paper = paper_db.get_paper(paper_id)
        if not paper:
            raise HTTPException(status_code=404, detail="Paper not found")
        
        graph = graphrag_service.get_paper_graph(paper_id)
        return graph
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting graph for paper {paper_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))
