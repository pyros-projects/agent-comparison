"""Database service using TinyDB."""

import logging
from datetime import datetime, timedelta
from typing import Optional
from tinydb import TinyDB, Query
from tinydb.storages import JSONStorage

from researcher.config import Config
from researcher.models import (
    Paper,
    PaperStatus,
    ImportTask,
    BackfillQueueItem,
    GraphRelationship,
)

logger = logging.getLogger("papertrail.database")


class DatabaseService:
    """TinyDB-based database service."""

    _instance: Optional["DatabaseService"] = None

    def __new__(cls) -> "DatabaseService":
        """Singleton pattern."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self) -> None:
        """Initialize database connection."""
        if self._initialized:
            return

        logger.info(f"Initializing database at {Config.DB_PATH}")
        # Don't use CachingMiddleware to ensure data is persisted immediately
        self.db = TinyDB(Config.DB_PATH, storage=JSONStorage)
        self.papers = self.db.table("papers")
        self.import_tasks = self.db.table("import_tasks")
        self.backfill_queue = self.db.table("backfill_queue")
        self.relationships = self.db.table("relationships")
        self._initialized = True
        logger.info("Database initialized successfully")

    # Paper operations
    def add_paper(self, paper: Paper) -> Paper:
        """Add a new paper to the database."""
        logger.info(f"Adding paper: {paper.arxiv_id} - {paper.title[:50]}...")
        paper_dict = paper.model_dump(mode="json")
        self.papers.insert(paper_dict)
        logger.debug(f"Paper added successfully: {paper.arxiv_id}")
        return paper

    def get_paper(self, paper_id: str) -> Optional[Paper]:
        """Get a paper by ID."""
        logger.debug(f"Fetching paper: {paper_id}")
        PaperQuery = Query()
        result = self.papers.get(PaperQuery.id == paper_id)
        if result:
            return Paper(**result)
        logger.debug(f"Paper not found: {paper_id}")
        return None

    def get_paper_by_arxiv_id(self, arxiv_id: str) -> Optional[Paper]:
        """Get a paper by arXiv ID."""
        logger.debug(f"Fetching paper by arXiv ID: {arxiv_id}")
        PaperQuery = Query()
        result = self.papers.get(PaperQuery.arxiv_id == arxiv_id)
        if result:
            return Paper(**result)
        return None

    def paper_exists(self, arxiv_id: str) -> bool:
        """Check if a paper already exists."""
        PaperQuery = Query()
        return self.papers.contains(PaperQuery.arxiv_id == arxiv_id)

    def update_paper(self, paper_id: str, updates: dict) -> Optional[Paper]:
        """Update a paper."""
        logger.info(f"Updating paper: {paper_id}")
        PaperQuery = Query()
        updates["updated_at"] = datetime.now().isoformat()
        self.papers.update(updates, PaperQuery.id == paper_id)
        return self.get_paper(paper_id)

    def delete_paper(self, paper_id: str) -> bool:
        """Delete a paper."""
        logger.info(f"Deleting paper: {paper_id}")
        PaperQuery = Query()
        removed = self.papers.remove(PaperQuery.id == paper_id)
        return len(removed) > 0

    def get_all_papers(
        self,
        status: Optional[PaperStatus] = None,
        category: Optional[str] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> list[Paper]:
        """Get all papers with optional filters."""
        logger.debug(f"Fetching papers: status={status}, category={category}")
        PaperQuery = Query()

        if status and category:
            results = self.papers.search(
                (PaperQuery.status == status.value)
                & (PaperQuery.primary_category == category)
            )
        elif status:
            results = self.papers.search(PaperQuery.status == status.value)
        elif category:
            results = self.papers.search(PaperQuery.primary_category == category)
        else:
            results = self.papers.all()

        # Sort by created_at descending
        results = sorted(
            results,
            key=lambda x: x.get("created_at", ""),
            reverse=True,
        )

        logger.debug(f"Found {len(results)} papers")
        return [Paper(**r) for r in results[offset : offset + limit]]

    def get_papers_count(self) -> int:
        """Get total paper count."""
        return len(self.papers)

    def get_papers_with_placeholders(self) -> list[Paper]:
        """Get papers that have placeholder content."""
        PaperQuery = Query()
        results = self.papers.search(
            (PaperQuery.has_placeholder_summary == True)
            | (PaperQuery.has_placeholder_keywords == True)
        )
        return [Paper(**r) for r in results]

    def get_papers_by_category(self) -> dict[str, int]:
        """Get paper counts by category."""
        results = self.papers.all()
        category_counts: dict[str, int] = {}
        for paper in results:
            cat = paper.get("primary_category", "unknown")
            category_counts[cat] = category_counts.get(cat, 0) + 1
        return category_counts

    def get_papers_since(self, since: datetime) -> list[Paper]:
        """Get papers created since a date."""
        results = self.papers.all()
        papers = []
        for r in results:
            created_at_str = r.get("created_at", "")
            if created_at_str:
                try:
                    created_at = datetime.fromisoformat(created_at_str)
                    if created_at >= since:
                        papers.append(Paper(**r))
                except (ValueError, TypeError):
                    pass
        return papers

    def search_papers_text(self, query: str) -> list[Paper]:
        """Simple text search across title and abstract."""
        logger.debug(f"Text search: {query}")
        results = self.papers.all()
        query_lower = query.lower()
        matches = []
        for r in results:
            title = r.get("title", "").lower()
            abstract = r.get("abstract", "").lower()
            if query_lower in title or query_lower in abstract:
                matches.append(Paper(**r))
        logger.debug(f"Found {len(matches)} matches")
        return matches

    # Import task operations
    def add_import_task(self, task: ImportTask) -> ImportTask:
        """Add a new import task."""
        logger.info(f"Adding import task: {task.name}")
        task_dict = task.model_dump(mode="json")
        self.import_tasks.insert(task_dict)
        return task

    def get_import_task(self, task_id: str) -> Optional[ImportTask]:
        """Get an import task by ID."""
        TaskQuery = Query()
        result = self.import_tasks.get(TaskQuery.id == task_id)
        if result:
            return ImportTask(**result)
        return None

    def get_all_import_tasks(self) -> list[ImportTask]:
        """Get all import tasks."""
        results = self.import_tasks.all()
        return [ImportTask(**r) for r in results]

    def get_active_import_tasks(self) -> list[ImportTask]:
        """Get active import tasks."""
        TaskQuery = Query()
        results = self.import_tasks.search(TaskQuery.is_active == True)
        return [ImportTask(**r) for r in results]

    def update_import_task(self, task_id: str, updates: dict) -> Optional[ImportTask]:
        """Update an import task."""
        logger.debug(f"Updating import task: {task_id}")
        TaskQuery = Query()
        self.import_tasks.update(updates, TaskQuery.id == task_id)
        return self.get_import_task(task_id)

    def delete_import_task(self, task_id: str) -> bool:
        """Delete an import task."""
        logger.info(f"Deleting import task: {task_id}")
        TaskQuery = Query()
        removed = self.import_tasks.remove(TaskQuery.id == task_id)
        return len(removed) > 0

    # Backfill queue operations
    def add_to_backfill_queue(self, item: BackfillQueueItem) -> BackfillQueueItem:
        """Add item to backfill queue."""
        logger.debug(f"Adding to backfill queue: {item.paper_id} - {item.field}")
        item_dict = item.model_dump(mode="json")
        self.backfill_queue.insert(item_dict)
        return item

    def get_backfill_queue(self, limit: int = 10) -> list[BackfillQueueItem]:
        """Get items from backfill queue."""
        results = self.backfill_queue.all()
        # Sort by created_at ascending (oldest first)
        results = sorted(results, key=lambda x: x.get("created_at", ""))
        return [BackfillQueueItem(**r) for r in results[:limit]]

    def remove_from_backfill_queue(self, paper_id: str, field: str) -> bool:
        """Remove item from backfill queue."""
        logger.debug(f"Removing from backfill queue: {paper_id} - {field}")
        ItemQuery = Query()
        removed = self.backfill_queue.remove(
            (ItemQuery.paper_id == paper_id) & (ItemQuery.field == field)
        )
        return len(removed) > 0

    def update_backfill_item(
        self, paper_id: str, field: str, updates: dict
    ) -> None:
        """Update a backfill queue item."""
        ItemQuery = Query()
        self.backfill_queue.update(
            updates,
            (ItemQuery.paper_id == paper_id) & (ItemQuery.field == field),
        )

    # Relationship operations
    def add_relationship(self, rel: GraphRelationship) -> GraphRelationship:
        """Add a relationship to the graph."""
        logger.debug(
            f"Adding relationship: {rel.source_id} -> {rel.target_id} ({rel.relationship_type})"
        )
        rel_dict = rel.model_dump(mode="json")
        self.relationships.insert(rel_dict)
        return rel

    def get_relationships_for_paper(
        self, paper_id: str
    ) -> list[GraphRelationship]:
        """Get all relationships for a paper."""
        RelQuery = Query()
        results = self.relationships.search(
            (RelQuery.source_id == paper_id) | (RelQuery.target_id == paper_id)
        )
        return [GraphRelationship(**r) for r in results]

    def get_all_relationships(self) -> list[GraphRelationship]:
        """Get all relationships."""
        results = self.relationships.all()
        return [GraphRelationship(**r) for r in results]

    def relationship_exists(
        self, source_id: str, target_id: str, rel_type: str
    ) -> bool:
        """Check if a relationship exists."""
        RelQuery = Query()
        return self.relationships.contains(
            (RelQuery.source_id == source_id)
            & (RelQuery.target_id == target_id)
            & (RelQuery.relationship_type == rel_type)
        )

    def close(self) -> None:
        """Close the database connection."""
        logger.info("Closing database connection")
        self.db.close()


# Singleton instance
def get_database() -> DatabaseService:
    """Get the database service instance."""
    return DatabaseService()
