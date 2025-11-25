"""Paper ingestion service."""

import logging
import asyncio
from datetime import datetime
from typing import Optional, Callable, Any

from researcher.config import Config
from researcher.models import Paper, BackfillQueueItem
from researcher.services.database import get_database
from researcher.services.embedding import get_embedding_service
from researcher.services.embedding_store import get_embedding_store
from researcher.services.llm import get_llm_service
from researcher.services.arxiv import get_arxiv_service, extract_arxiv_id
from researcher.services.graph import get_graph_service, GraphRelationship

logger = logging.getLogger("papertrail.ingestion")


class IngestionService:
    """Service for ingesting papers."""

    def __init__(self) -> None:
        """Initialize ingestion service."""
        self.db = get_database()
        self.embedding_service = get_embedding_service()
        self.embedding_store = get_embedding_store()
        self.llm_service = get_llm_service()
        self.arxiv_service = get_arxiv_service()
        self.graph_service = get_graph_service()

    def _get_all_existing_keywords(self) -> list[str]:
        """Get all unique keywords from existing papers."""
        papers = self.db.get_all_papers(limit=1000)
        all_keywords = set()
        for paper in papers:
            for kw in paper.keywords:
                if kw and not kw.startswith("<"):
                    all_keywords.add(kw.lower())
        return list(all_keywords)

    def _normalize_keywords(self, new_keywords: list[str], existing_keywords: list[str]) -> list[str]:
        """Normalize keywords against existing ones using fuzzy matching."""
        normalized = []
        existing_lower = {kw.lower(): kw for kw in existing_keywords}
        
        for kw in new_keywords:
            kw_lower = kw.lower().strip()
            
            # Check for exact match (case-insensitive)
            if kw_lower in existing_lower:
                normalized.append(existing_lower[kw_lower])
                continue
            
            # Check for common variations
            matched = False
            for existing_kw in existing_lower:
                # Check if one contains the other
                if kw_lower in existing_kw or existing_kw in kw_lower:
                    # Prefer shorter form
                    if len(existing_kw) <= len(kw_lower):
                        normalized.append(existing_lower[existing_kw])
                    else:
                        normalized.append(kw)
                    matched = True
                    break
                
                # Check for common abbreviation patterns (LLM vs Large Language Model)
                kw_words = set(kw_lower.replace("-", " ").split())
                existing_words = set(existing_kw.replace("-", " ").split())
                
                # If significant word overlap
                overlap = len(kw_words & existing_words)
                if overlap >= 2 or (overlap >= 1 and max(len(kw_words), len(existing_words)) <= 2):
                    normalized.append(existing_lower[existing_kw])
                    matched = True
                    break
            
            if not matched:
                normalized.append(kw)
        
        return list(set(normalized))  # Remove duplicates

    def _find_keyword_connections(self, paper_id: str, keywords: list[str]) -> list[dict]:
        """Find papers that share keywords with the given paper."""
        papers = self.db.get_all_papers(limit=1000)
        connections = []
        keywords_lower = set(kw.lower() for kw in keywords if kw and not kw.startswith("<"))
        
        for paper in papers:
            if paper.id == paper_id:
                continue
            
            paper_keywords = set(kw.lower() for kw in paper.keywords if kw and not kw.startswith("<"))
            shared = keywords_lower & paper_keywords
            
            if shared:
                # Weight based on proportion of shared keywords
                weight = len(shared) / max(len(keywords_lower), 1)
                weight = min(weight, 1.0)  # Cap at 1.0
                
                if weight >= 0.2:  # At least 20% keyword overlap
                    connections.append({
                        "paper_id": paper.id,
                        "shared_keywords": list(shared),
                        "weight": weight,
                    })
        
        # Sort by weight and return top connections
        connections.sort(key=lambda x: x["weight"], reverse=True)
        return connections[:10]

    async def ingest_paper(
        self,
        arxiv_url_or_id: str,
        progress_callback: Optional[Callable[[str, float], Any]] = None,
        extract_pdf: bool = True,
    ) -> Optional[Paper]:
        """
        Ingest a single paper from arXiv.
        
        Args:
            arxiv_url_or_id: arXiv URL or ID
            progress_callback: Optional callback for progress updates (message, progress 0-1)
            extract_pdf: Whether to extract full text from PDF
        
        Returns:
            Ingested paper or None if failed
        """
        arxiv_id = extract_arxiv_id(arxiv_url_or_id)
        logger.info(f"Starting ingestion for: {arxiv_id}")

        # Check if paper already exists
        if self.db.paper_exists(arxiv_id):
            logger.info(f"Paper already exists: {arxiv_id}")
            if progress_callback:
                await progress_callback(f"Paper {arxiv_id} already exists", 1.0)
            return self.db.get_paper_by_arxiv_id(arxiv_id)

        # Step 1: Fetch metadata
        if progress_callback:
            await progress_callback(f"Fetching metadata for {arxiv_id}...", 0.1)
        
        paper_data = await self.arxiv_service.fetch_paper(arxiv_id)
        if not paper_data:
            logger.error(f"Failed to fetch paper: {arxiv_id}")
            if progress_callback:
                await progress_callback(f"Failed to fetch paper {arxiv_id}", 1.0)
            return None

        # Step 2: Extract PDF text (optional)
        full_text = ""
        if extract_pdf:
            if progress_callback:
                await progress_callback(f"Extracting PDF text...", 0.3)
            full_text = await self.arxiv_service.fetch_pdf_text(paper_data["pdf_url"])

        # Step 3: Generate summary (LLM)
        if progress_callback:
            await progress_callback(f"Generating summary...", 0.5)
        
        summary = await self.llm_service.generate_summary(
            paper_data["title"],
            paper_data["abstract"],
            full_text,
        )
        has_placeholder_summary = summary == Config.PLACEHOLDER_SUMMARY

        # Step 4: Extract keywords (LLM) with normalization
        if progress_callback:
            await progress_callback(f"Extracting keywords...", 0.6)
        
        # Get existing keywords for normalization
        existing_keywords = self._get_all_existing_keywords()
        keywords = await self.llm_service.extract_keywords(
            paper_data["title"],
            paper_data["abstract"],
            existing_keywords,
        )
        has_placeholder_keywords = keywords == [Config.PLACEHOLDER_KEYWORDS]
        
        # Normalize keywords against existing ones
        if not has_placeholder_keywords:
            keywords = self._normalize_keywords(keywords, existing_keywords)

        # Step 4b: Extract questions and theories (LLM)
        if progress_callback:
            await progress_callback(f"Extracting questions and theories...", 0.65)
        
        qt_result = await self.llm_service.extract_questions_and_theories(
            paper_data["title"],
            paper_data["abstract"],
            full_text,
        )
        questions_answered = qt_result.get("questions_answered", [])
        theories_supported = qt_result.get("theories_supported", [])
        has_placeholder_questions = questions_answered == [Config.PLACEHOLDER_ANALYSIS]
        has_placeholder_theories = theories_supported == [Config.PLACEHOLDER_ANALYSIS]

        # Step 5: Generate embedding
        if progress_callback:
            await progress_callback(f"Generating embedding...", 0.7)
        
        # Create embedding from title + abstract
        embedding_text = f"{paper_data['title']} {paper_data['abstract']}"
        embedding = self.embedding_service.embed(embedding_text)
        self.embedding_store.add_embedding(arxiv_id, embedding)

        # Step 6: Create paper object
        paper = Paper(
            id=arxiv_id,
            arxiv_id=arxiv_id,
            title=paper_data["title"],
            authors=paper_data["authors"],
            abstract=paper_data["abstract"],
            summary=summary,
            keywords=keywords,
            questions_answered=questions_answered,
            theories_supported=theories_supported,
            categories=paper_data["categories"],
            primary_category=paper_data["primary_category"],
            published=datetime.fromisoformat(paper_data["published"]) if paper_data.get("published") else None,
            updated=datetime.fromisoformat(paper_data["updated"]) if paper_data.get("updated") else None,
            pdf_url=paper_data["pdf_url"],
            full_text=full_text[:50000],  # Limit text storage
            has_placeholder_summary=has_placeholder_summary,
            has_placeholder_keywords=has_placeholder_keywords,
            has_placeholder_questions=has_placeholder_questions,
            has_placeholder_theories=has_placeholder_theories,
            has_embedding=True,
        )

        # Step 7: Save to database
        if progress_callback:
            await progress_callback(f"Saving paper...", 0.8)
        
        self.db.add_paper(paper)

        # Step 8: Add to backfill queue if needed
        if has_placeholder_summary:
            self.db.add_to_backfill_queue(BackfillQueueItem(
                paper_id=arxiv_id,
                field="summary",
            ))
        if has_placeholder_keywords:
            self.db.add_to_backfill_queue(BackfillQueueItem(
                paper_id=arxiv_id,
                field="keywords",
            ))

        # Step 9: Add to graph and extract relationships
        if progress_callback:
            await progress_callback(f"Building relationships...", 0.9)
        
        self.graph_service.add_paper(paper)
        
        # Find and add author connections
        author_connections = self.graph_service.find_author_connections(paper.id)
        for conn in author_connections:
            rel = GraphRelationship(
                source_id=paper.id,
                target_id=conn["paper_id"],
                relationship_type="author",
                weight=0.8,
                metadata={"shared_authors": conn["shared_authors"]},
            )
            self.graph_service.add_relationship(rel)

        # Find similar papers by embedding
        similar = self.embedding_store.search_similar_to_paper(paper.id, top_k=5)
        for similar_id, score in similar:
            if score > 0.7:  # Only strong similarities
                rel = GraphRelationship(
                    source_id=paper.id,
                    target_id=similar_id,
                    relationship_type="similar",
                    weight=score,
                    metadata={},
                )
                self.graph_service.add_relationship(rel)

        # Find keyword-based relationships (papers with shared keywords)
        if not has_placeholder_keywords:
            keyword_connections = self._find_keyword_connections(paper.id, keywords)
            for conn in keyword_connections:
                rel = GraphRelationship(
                    source_id=paper.id,
                    target_id=conn["paper_id"],
                    relationship_type="topic",
                    weight=conn["weight"],
                    metadata={"shared_keywords": conn["shared_keywords"]},
                )
                self.graph_service.add_relationship(rel)

        if progress_callback:
            await progress_callback(f"Ingestion complete: {paper.title[:50]}...", 1.0)

        logger.info(f"Successfully ingested paper: {arxiv_id}")
        return paper

    async def ingest_batch(
        self,
        arxiv_ids: list[str],
        progress_callback: Optional[Callable[[str, float], Any]] = None,
    ) -> list[Paper]:
        """Ingest multiple papers."""
        papers = []
        total = len(arxiv_ids)
        
        for i, arxiv_id in enumerate(arxiv_ids):
            if progress_callback:
                await progress_callback(
                    f"Processing {i+1}/{total}: {arxiv_id}",
                    i / total,
                )
            
            paper = await self.ingest_paper(arxiv_id, extract_pdf=False)
            if paper:
                papers.append(paper)
            
            # Small delay between papers
            await asyncio.sleep(0.5)
        
        return papers


# Factory function
def get_ingestion_service() -> IngestionService:
    """Get the ingestion service."""
    return IngestionService()
