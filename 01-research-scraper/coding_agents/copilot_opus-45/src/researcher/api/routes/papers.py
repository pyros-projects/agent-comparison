"""Papers API routes."""

import logging
from typing import Optional
from datetime import datetime

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

from researcher.models import Paper, PaperCreate, PaperUpdate, PaperStatus, PaperSearchResult
from researcher.services import (
    get_database,
    get_ingestion_service,
    get_embedding_store,
    get_graph_service,
    get_llm_service,
)

logger = logging.getLogger("papertrail.api.papers")

router = APIRouter()


class PaperListResponse(BaseModel):
    """Response for paper list."""
    papers: list[Paper]
    total: int
    page: int
    page_size: int


class SimilarPaperResponse(BaseModel):
    """Similar paper with score."""
    paper: Paper
    score: float


class RelatedPaperResponse(BaseModel):
    """Related paper from graph."""
    paper_id: str
    title: str
    relationship_type: str
    weight: float
    category: str


class GraphDataResponse(BaseModel):
    """Graph data for visualization."""
    nodes: list[dict]
    edges: list[dict]


@router.get("", response_model=PaperListResponse)
async def list_papers(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    status: Optional[PaperStatus] = None,
    category: Optional[str] = None,
    search: Optional[str] = None,
):
    """List all papers with pagination and filters."""
    logger.info(f"Listing papers: page={page}, status={status}, category={category}")
    
    db = get_database()
    offset = (page - 1) * page_size
    
    if search:
        papers = db.search_papers_text(search)
        # Apply additional filters
        if status:
            papers = [p for p in papers if p.status == status]
        if category:
            papers = [p for p in papers if p.primary_category == category]
        total = len(papers)
        papers = papers[offset:offset + page_size]
    else:
        papers = db.get_all_papers(
            status=status,
            category=category,
            limit=page_size,
            offset=offset,
        )
        total = db.get_papers_count()
    
    return PaperListResponse(
        papers=papers,
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get("/categories")
async def get_categories():
    """Get list of paper categories with counts."""
    db = get_database()
    return db.get_papers_by_category()


@router.post("", response_model=Paper)
async def ingest_paper(paper_create: PaperCreate):
    """Ingest a new paper from arXiv."""
    logger.info(f"Ingesting paper: {paper_create.arxiv_url}")
    
    ingestion_service = get_ingestion_service()
    
    try:
        paper = await ingestion_service.ingest_paper(
            paper_create.arxiv_url,
            extract_pdf=True,
        )
        
        if not paper:
            raise HTTPException(status_code=400, detail="Failed to ingest paper")
        
        return paper
    except Exception as e:
        logger.error(f"Error ingesting paper: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{paper_id}", response_model=Paper)
async def get_paper(paper_id: str):
    """Get a paper by ID."""
    logger.debug(f"Getting paper: {paper_id}")
    
    db = get_database()
    paper = db.get_paper(paper_id)
    
    if not paper:
        raise HTTPException(status_code=404, detail="Paper not found")
    
    return paper


@router.patch("/{paper_id}", response_model=Paper)
async def update_paper(paper_id: str, update: PaperUpdate):
    """Update a paper."""
    logger.info(f"Updating paper: {paper_id}")
    
    db = get_database()
    
    # Check paper exists
    paper = db.get_paper(paper_id)
    if not paper:
        raise HTTPException(status_code=404, detail="Paper not found")
    
    # Build update dict
    updates = {}
    if update.status is not None:
        updates["status"] = update.status.value
    if update.notes is not None:
        updates["notes"] = update.notes
    if update.manual_tags is not None:
        updates["manual_tags"] = update.manual_tags
    
    updated = db.update_paper(paper_id, updates)
    return updated


@router.delete("/{paper_id}")
async def delete_paper(paper_id: str):
    """Delete a paper."""
    logger.info(f"Deleting paper: {paper_id}")
    
    db = get_database()
    embedding_store = get_embedding_store()
    
    # Check paper exists
    paper = db.get_paper(paper_id)
    if not paper:
        raise HTTPException(status_code=404, detail="Paper not found")
    
    # Delete paper and embedding
    db.delete_paper(paper_id)
    embedding_store.remove_embedding(paper_id)
    
    return {"status": "deleted", "paper_id": paper_id}


@router.get("/{paper_id}/similar", response_model=list[SimilarPaperResponse])
async def get_similar_papers(paper_id: str, limit: int = Query(10, ge=1, le=50)):
    """Get similar papers based on embedding similarity."""
    logger.debug(f"Finding similar papers for: {paper_id}")
    
    db = get_database()
    embedding_store = get_embedding_store()
    
    # Check paper exists
    paper = db.get_paper(paper_id)
    if not paper:
        raise HTTPException(status_code=404, detail="Paper not found")
    
    # Find similar papers
    similar = embedding_store.search_similar_to_paper(paper_id, top_k=limit)
    
    results = []
    for sim_id, score in similar:
        sim_paper = db.get_paper(sim_id)
        if sim_paper:
            results.append(SimilarPaperResponse(paper=sim_paper, score=score))
    
    return results


@router.get("/{paper_id}/related", response_model=list[RelatedPaperResponse])
async def get_related_papers(paper_id: str, limit: int = Query(20, ge=1, le=50)):
    """Get related papers from knowledge graph."""
    logger.debug(f"Finding related papers for: {paper_id}")
    
    db = get_database()
    graph_service = get_graph_service()
    
    # Check paper exists
    paper = db.get_paper(paper_id)
    if not paper:
        raise HTTPException(status_code=404, detail="Paper not found")
    
    # Get related from graph
    related = graph_service.get_related_papers(paper_id, max_papers=limit)
    
    results = []
    for rel in related:
        results.append(RelatedPaperResponse(
            paper_id=rel["paper_id"],
            title=rel.get("title", ""),
            relationship_type=rel.get("relationship_type", "similar"),
            weight=rel.get("weight", 0.5),
            category=rel.get("category", ""),
        ))
    
    return results


@router.get("/{paper_id}/graph", response_model=GraphDataResponse)
async def get_paper_graph(paper_id: str):
    """Get graph data for visualization around a paper."""
    logger.debug(f"Getting graph data for: {paper_id}")
    
    db = get_database()
    graph_service = get_graph_service()
    
    # Check paper exists
    paper = db.get_paper(paper_id)
    if not paper:
        raise HTTPException(status_code=404, detail="Paper not found")
    
    graph_data = graph_service.get_graph_data(paper_id)
    return GraphDataResponse(**graph_data)


@router.get("/{paper_id}/bibtex")
async def export_bibtex(paper_id: str):
    """Export paper as BibTeX."""
    db = get_database()
    paper = db.get_paper(paper_id)
    
    if not paper:
        raise HTTPException(status_code=404, detail="Paper not found")
    
    # Generate BibTeX
    authors_str = " and ".join(paper.authors) if paper.authors else "Unknown"
    year = paper.published.year if paper.published else "Unknown"
    
    bibtex = f"""@article{{{paper.arxiv_id},
    title = {{{paper.title}}},
    author = {{{authors_str}}},
    year = {{{year}}},
    eprint = {{{paper.arxiv_id}}},
    archivePrefix = {{arXiv}},
    primaryClass = {{{paper.primary_category}}},
    abstract = {{{paper.abstract[:500]}...}}
}}"""
    
    return {"bibtex": bibtex}


class ContraPaperResponse(BaseModel):
    """Paper that argues against a theory supported by another paper."""
    paper: Paper
    theory: str
    relevance_score: float
    reason: str


@router.get("/{paper_id}/contra", response_model=list[ContraPaperResponse])
async def get_contra_papers(paper_id: str, limit: int = Query(10, ge=1, le=50)):
    """Get papers that argue against theories supported by this paper."""
    logger.debug(f"Finding contra papers for: {paper_id}")
    
    db = get_database()
    embedding_store = get_embedding_store()
    
    # Get the paper
    paper = db.get_paper(paper_id)
    if not paper:
        raise HTTPException(status_code=404, detail="Paper not found")
    
    # Get theories this paper supports
    theories = paper.theories_supported
    if not theories or theories == ["<analysis>"]:
        return []
    
    # Find papers with opposing theories
    all_papers = db.get_all_papers(limit=500)
    contra_papers = []
    
    for other_paper in all_papers:
        if other_paper.id == paper_id:
            continue
        
        other_theories = other_paper.theories_supported
        if not other_theories or other_theories == ["<analysis>"]:
            continue
        
        # Check for opposing theories using simple heuristics
        # Papers that support opposing concepts might be contra
        for theory in theories:
            theory_lower = theory.lower()
            for other_theory in other_theories:
                other_lower = other_theory.lower()
                
                # Look for opposing language patterns
                opposing_pairs = [
                    ("increase", "decrease"),
                    ("improve", "degrade"),
                    ("beneficial", "harmful"),
                    ("effective", "ineffective"),
                    ("superior", "inferior"),
                    ("positive", "negative"),
                    ("support", "contradict"),
                    ("confirm", "refute"),
                    ("necessary", "unnecessary"),
                    ("sufficient", "insufficient"),
                ]
                
                is_contra = False
                reason = ""
                
                for pos, neg in opposing_pairs:
                    if (pos in theory_lower and neg in other_lower) or \
                       (neg in theory_lower and pos in other_lower):
                        is_contra = True
                        reason = f"Opposing positions: '{theory[:50]}...' vs '{other_theory[:50]}...'"
                        break
                
                if is_contra:
                    # Calculate relevance based on keyword overlap
                    paper_keywords = set(kw.lower() for kw in paper.keywords)
                    other_keywords = set(kw.lower() for kw in other_paper.keywords)
                    overlap = len(paper_keywords & other_keywords)
                    relevance = min(overlap / max(len(paper_keywords), 1), 1.0)
                    
                    contra_papers.append(ContraPaperResponse(
                        paper=other_paper,
                        theory=theory,
                        relevance_score=relevance,
                        reason=reason,
                    ))
                    break
    
    # Sort by relevance and return top results
    contra_papers.sort(key=lambda x: x.relevance_score, reverse=True)
    return contra_papers[:limit]


class ReprocessResponse(BaseModel):
    """Response for reprocessing operations."""
    processed: int
    skipped: int
    errors: int
    message: str


@router.post("/reprocess/questions-theories", response_model=ReprocessResponse)
async def reprocess_questions_theories(
    paper_ids: Optional[list[str]] = None,
    force: bool = Query(False, description="Force reprocess even if already has content")
):
    """
    Retroactively extract questions answered and theories supported from existing papers.
    If paper_ids is None, processes all papers. Use force=True to overwrite existing values.
    """
    logger.info(f"Starting questions/theories reprocessing (force={force})")
    
    db = get_database()
    llm_service = get_llm_service()
    
    if not llm_service.available:
        raise HTTPException(status_code=503, detail="LLM service not available")
    
    # Get papers to process
    if paper_ids:
        papers = [db.get_paper(pid) for pid in paper_ids]
        papers = [p for p in papers if p is not None]
    else:
        papers = db.get_all_papers(limit=1000)
    
    processed = 0
    skipped = 0
    errors = 0
    
    for paper in papers:
        # Skip if already has content and not forcing
        has_questions = paper.questions_answered and paper.questions_answered != ["<analysis>"]
        has_theories = paper.theories_supported and paper.theories_supported != ["<analysis>"]
        
        if (has_questions and has_theories) and not force:
            skipped += 1
            continue
        
        try:
            # Extract questions and theories
            result = await llm_service.extract_questions_and_theories(
                paper.title,
                paper.abstract,
                paper.full_text[:5000] if paper.full_text else ""
            )
            
            # Update paper
            db.update_paper(paper.id, {
                "questions_answered": result.get("questions_answered", []),
                "theories_supported": result.get("theories_supported", []),
                "has_placeholder_questions": False,
                "has_placeholder_theories": False,
            })
            processed += 1
            logger.debug(f"Processed questions/theories for {paper.id}")
            
        except Exception as e:
            logger.error(f"Error processing {paper.id}: {e}")
            errors += 1
    
    return ReprocessResponse(
        processed=processed,
        skipped=skipped,
        errors=errors,
        message=f"Processed {processed} papers, skipped {skipped}, errors {errors}"
    )


@router.post("/reprocess/keywords", response_model=ReprocessResponse)
async def reprocess_keywords(
    paper_ids: Optional[list[str]] = None,
    force: bool = Query(False, description="Force reprocess even if already has keywords")
):
    """
    Retroactively normalize keywords across all papers to ensure consistency.
    This merges similar keywords (e.g., 'LLM' and 'Large Language Model') into canonical forms.
    """
    logger.info(f"Starting keyword normalization reprocessing (force={force})")
    
    db = get_database()
    ingestion_service = get_ingestion_service()
    
    # Get papers to process
    if paper_ids:
        papers = [db.get_paper(pid) for pid in paper_ids]
        papers = [p for p in papers if p is not None]
    else:
        papers = db.get_all_papers(limit=1000)
    
    # Build global keyword index
    existing_keywords = ingestion_service._get_all_existing_keywords()
    
    processed = 0
    skipped = 0
    errors = 0
    
    for paper in papers:
        # Skip if no keywords or placeholder
        if not paper.keywords or paper.keywords == ["<keywords>"]:
            skipped += 1
            continue
        
        try:
            # Normalize keywords
            normalized = ingestion_service._normalize_keywords(
                paper.keywords,
                existing_keywords
            )
            
            # Only update if changed
            if set(normalized) != set(paper.keywords):
                db.update_paper(paper.id, {"keywords": normalized})
                processed += 1
                logger.debug(f"Normalized keywords for {paper.id}: {paper.keywords} -> {normalized}")
                
                # Update global index with normalized keywords
                for kw in normalized:
                    if kw.lower() not in [k.lower() for k in existing_keywords]:
                        existing_keywords.append(kw)
            else:
                skipped += 1
                
        except Exception as e:
            logger.error(f"Error normalizing {paper.id}: {e}")
            errors += 1
    
    return ReprocessResponse(
        processed=processed,
        skipped=skipped,
        errors=errors,
        message=f"Normalized {processed} papers, skipped {skipped}, errors {errors}"
    )


@router.post("/reprocess/relationships", response_model=ReprocessResponse)
async def reprocess_relationships(rebuild_graph: bool = Query(True, description="Rebuild entire graph from scratch")):
    """
    Retroactively rebuild the knowledge graph relationships based on keywords.
    This creates connections between papers that share keywords.
    """
    logger.info("Starting relationship graph rebuild")
    
    db = get_database()
    graph_service = get_graph_service()
    ingestion_service = get_ingestion_service()
    
    if rebuild_graph:
        # Clear and rebuild from scratch
        graph_service.rebuild_graph()
    
    papers = db.get_all_papers(limit=1000)
    
    processed = 0
    errors = 0
    relationships_created = 0
    
    for paper in papers:
        if not paper.keywords or paper.keywords == ["<keywords>"]:
            continue
            
        try:
            # Find keyword-based connections
            connections = ingestion_service._find_keyword_connections(paper.id, paper.keywords)
            
            for conn in connections:
                graph_service.add_relationship(
                    paper.id,
                    conn["paper_id"],
                    "shared_keyword",
                    conn["weight"],
                    metadata={"shared_keywords": conn.get("shared_keywords", [])}
                )
                relationships_created += 1
            
            processed += 1
            
        except Exception as e:
            logger.error(f"Error processing relationships for {paper.id}: {e}")
            errors += 1
    
    return ReprocessResponse(
        processed=processed,
        skipped=0,
        errors=errors,
        message=f"Rebuilt relationships for {processed} papers, created {relationships_created} connections"
    )


@router.post("/reprocess/embeddings", response_model=ReprocessResponse)
async def reprocess_embeddings(
    paper_ids: Optional[list[str]] = None,
    force: bool = Query(False, description="Force regenerate even if embedding exists")
):
    """
    Retroactively regenerate embeddings for papers.
    Useful if embedding model changed or embeddings are missing.
    """
    logger.info(f"Starting embedding reprocessing (force={force})")
    
    db = get_database()
    embedding_store = get_embedding_store()
    ingestion_service = get_ingestion_service()
    
    # Get papers to process
    if paper_ids:
        papers = [db.get_paper(pid) for pid in paper_ids]
        papers = [p for p in papers if p is not None]
    else:
        papers = db.get_all_papers(limit=1000)
    
    processed = 0
    skipped = 0
    errors = 0
    
    for paper in papers:
        # Skip if already has embedding and not forcing
        if paper.has_embedding and not force:
            skipped += 1
            continue
        
        try:
            # Generate embedding
            text = f"{paper.title}\n\n{paper.abstract}"
            embedding = ingestion_service.embedding_service.embed_text(text)
            
            if embedding is not None:
                # Store embedding
                embedding_store.add_embedding(paper.id, embedding)
                
                # Update paper
                db.update_paper(paper.id, {"has_embedding": True})
                processed += 1
                logger.debug(f"Generated embedding for {paper.id}")
            else:
                errors += 1
                
        except Exception as e:
            logger.error(f"Error generating embedding for {paper.id}: {e}")
            errors += 1
    
    return ReprocessResponse(
        processed=processed,
        skipped=skipped,
        errors=errors,
        message=f"Generated {processed} embeddings, skipped {skipped}, errors {errors}"
    )
