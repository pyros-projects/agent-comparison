"""Continuous import task manager."""

import logging
from datetime import datetime
from typing import Optional, Callable, Any
from uuid import uuid4
from collections import deque
import asyncio

from researcher.config import Config
from researcher.models import ImportTask, ImportTaskCreate
from researcher.services.database import get_database
from researcher.services.arxiv import get_arxiv_service
from researcher.services.ingestion import get_ingestion_service
from researcher.services.embedding import get_embedding_service
from researcher.services.embedding_store import get_embedding_store

logger = logging.getLogger("papertrail.import_manager")


class TaskLogEntry:
    """A log entry for an import task."""
    
    def __init__(self, level: str, message: str, details: Optional[dict] = None):
        self.timestamp = datetime.now().isoformat()
        self.level = level
        self.message = message
        self.details = details or {}
    
    def to_dict(self) -> dict:
        return {
            "timestamp": self.timestamp,
            "level": self.level,
            "message": self.message,
            "details": self.details,
        }


class ImportTaskRunner:
    """Runner for a single import task."""

    def __init__(
        self,
        task: ImportTask,
        on_paper_imported: Optional[Callable[[str, dict], Any]] = None,
        on_status_update: Optional[Callable[[str, str], Any]] = None,
        on_log: Optional[Callable[[str, dict], Any]] = None,
    ) -> None:
        """Initialize task runner."""
        self.task = task
        self.on_paper_imported = on_paper_imported
        self.on_status_update = on_status_update
        self.on_log = on_log
        self._running = False
        self._task_handle: Optional[asyncio.Task] = None
        self._logs: deque = deque(maxlen=100)  # Keep last 100 logs
        self._imported_papers: deque = deque(maxlen=50)  # Keep last 50 imported
        self._current_offset = 0  # For pagination through arXiv results
        self._max_offset = 500  # Max papers to go through

    def _log(self, level: str, message: str, details: Optional[dict] = None) -> None:
        """Add a log entry."""
        entry = TaskLogEntry(level, message, details)
        self._logs.append(entry)
        logger.log(
            getattr(logging, level.upper(), logging.INFO),
            f"Task {self.task.name}: {message}"
        )
        if self.on_log:
            asyncio.create_task(self.on_log(self.task.id, entry.to_dict()))

    def get_logs(self) -> list[dict]:
        """Get all log entries."""
        return [log.to_dict() for log in self._logs]

    def get_imported_papers(self) -> list[dict]:
        """Get recently imported papers."""
        return list(self._imported_papers)

    async def start(self) -> None:
        """Start the import task."""
        if self._running:
            self._log("warning", "Task already running")
            return

        self._running = True
        self._task_handle = asyncio.create_task(self._run_loop())
        self._log("info", "Import task started")

    async def stop(self) -> None:
        """Stop the import task."""
        self._running = False
        if self._task_handle:
            self._task_handle.cancel()
            try:
                await self._task_handle
            except asyncio.CancelledError:
                pass
        self._log("info", "Import task stopped")

    async def _run_loop(self) -> None:
        """Main loop for the import task."""
        db = get_database()
        arxiv_service = get_arxiv_service()
        ingestion_service = get_ingestion_service()
        embedding_service = get_embedding_service()

        while self._running:
            try:
                if self.on_status_update:
                    await self.on_status_update(self.task.id, "checking")

                self._log("info", f"Searching arXiv (offset={self._current_offset})", {
                    "category": self.task.category,
                    "text_search": self.task.text_search,
                    "semantic_query": self.task.semantic_query,
                    "offset": self._current_offset,
                })

                # Build search query - use offset to get different papers each time
                papers = await arxiv_service.search_papers(
                    query=self.task.text_search,
                    category=self.task.category,
                    max_results=Config.MAX_PAPERS_PER_FETCH,
                    start=self._current_offset,
                )

                self._log("info", f"arXiv returned {len(papers)} papers", {
                    "paper_count": len(papers),
                    "papers": [p.get("arxiv_id", "?") for p in papers[:5]] if papers else [],
                })

                if not papers:
                    self._log("warning", "No papers returned from arXiv API")
                    # Reset offset if we've gone too far
                    if self._current_offset > 0:
                        self._log("info", "Resetting offset to 0")
                        self._current_offset = 0
                else:
                    # Increment offset for next run to find older papers
                    self._current_offset += len(papers)
                    if self._current_offset >= self._max_offset:
                        self._current_offset = 0
                        self._log("info", "Reached max offset, cycling back to newest")

                # Filter by semantic query if provided
                if self.task.semantic_query and papers:
                    self._log("info", f"Filtering by semantic query: {self.task.semantic_query}")
                    query_embedding = embedding_service.embed(self.task.semantic_query)
                    
                    # Score papers by semantic similarity
                    scored_papers = []
                    for paper in papers:
                        text = f"{paper['title']} {paper['abstract']}"
                        paper_embedding = embedding_service.embed(text)
                        score = embedding_service.similarity(query_embedding, paper_embedding)
                        if score > 0.3:  # Lower threshold for more results
                            scored_papers.append((paper, score))
                    
                    # Sort by score and take top papers
                    scored_papers.sort(key=lambda x: x[1], reverse=True)
                    papers = [p[0] for p in scored_papers[:20]]
                    self._log("info", f"{len(papers)} papers passed semantic filter", {
                        "threshold": 0.3,
                        "filtered_count": len(papers),
                    })

                # Filter out already known papers
                new_papers = []
                known_count = 0
                for paper in papers:
                    if not db.paper_exists(paper["arxiv_id"]):
                        new_papers.append(paper)
                    else:
                        known_count += 1

                self._log("info", f"Filtered: {len(new_papers)} new, {known_count} already known", {
                    "new_papers": len(new_papers),
                    "known_papers": known_count,
                })

                if new_papers:
                    self._log("info", f"Starting ingestion of {len(new_papers)} papers")
                    
                    # Ingest new papers
                    for paper_data in new_papers:
                        if not self._running:
                            break
                        
                        try:
                            if self.on_status_update:
                                await self.on_status_update(
                                    self.task.id,
                                    f"importing:{paper_data['arxiv_id']}",
                                )
                            
                            self._log("info", f"Ingesting paper: {paper_data['arxiv_id']}", {
                                "arxiv_id": paper_data["arxiv_id"],
                                "title": paper_data.get("title", "")[:100],
                            })
                            
                            paper = await ingestion_service.ingest_paper(
                                paper_data["arxiv_id"],
                                extract_pdf=False,
                            )
                            
                            if paper:
                                self._log("info", f"Successfully imported: {paper.title[:60]}...", {
                                    "paper_id": paper.id,
                                    "title": paper.title,
                                    "category": paper.primary_category,
                                })
                                
                                # Track imported paper
                                self._imported_papers.append({
                                    "paper_id": paper.id,
                                    "arxiv_id": paper.arxiv_id,
                                    "title": paper.title,
                                    "category": paper.primary_category,
                                    "imported_at": datetime.now().isoformat(),
                                })
                                
                                if self.on_paper_imported:
                                    await self.on_paper_imported(
                                        self.task.id,
                                        {
                                            "paper_id": paper.id,
                                            "title": paper.title,
                                            "category": paper.primary_category,
                                        },
                                    )
                            
                            # Update task stats
                            self.task.papers_imported += 1
                            db.update_import_task(
                                self.task.id,
                                {
                                    "papers_imported": self.task.papers_imported,
                                    "last_run": datetime.now().isoformat(),
                                },
                            )
                        except Exception as e:
                            self._log("error", f"Failed to import {paper_data['arxiv_id']}: {str(e)}", {
                                "arxiv_id": paper_data["arxiv_id"],
                                "error": str(e),
                            })
                            self.task.errors += 1
                            db.update_import_task(
                                self.task.id,
                                {"errors": self.task.errors},
                            )
                else:
                    self._log("info", "No new papers to import this cycle")

                # Update last run time
                db.update_import_task(
                    self.task.id,
                    {"last_run": datetime.now().isoformat()},
                )

                if self.on_status_update:
                    await self.on_status_update(self.task.id, "waiting")

                self._log("info", f"Cycle complete, waiting {self.task.check_interval}s")

            except Exception as e:
                self._log("error", f"Error in import cycle: {str(e)}", {"error": str(e)})
                self.task.errors += 1
                db.update_import_task(
                    self.task.id,
                    {"errors": self.task.errors},
                )

            # Wait for next check interval
            if self._running:
                await asyncio.sleep(self.task.check_interval)


class ImportManager:
    """Manager for continuous import tasks."""

    _instance: Optional["ImportManager"] = None

    def __new__(cls) -> "ImportManager":
        """Singleton pattern."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self) -> None:
        """Initialize import manager."""
        if self._initialized:
            return

        self._runners: dict[str, ImportTaskRunner] = {}
        self._on_paper_imported: Optional[Callable[[str, dict], Any]] = None
        self._on_status_update: Optional[Callable[[str, str], Any]] = None
        self._on_log: Optional[Callable[[str, dict], Any]] = None
        self._initialized = True
        logger.info("Import manager initialized")

    def set_callbacks(
        self,
        on_paper_imported: Optional[Callable[[str, dict], Any]] = None,
        on_status_update: Optional[Callable[[str, str], Any]] = None,
        on_log: Optional[Callable[[str, dict], Any]] = None,
    ) -> None:
        """Set callbacks for import events."""
        self._on_paper_imported = on_paper_imported
        self._on_status_update = on_status_update
        self._on_log = on_log

    def get_task_logs(self, task_id: str) -> list[dict]:
        """Get logs for a specific task."""
        if task_id in self._runners:
            return self._runners[task_id].get_logs()
        return []

    def get_task_imported_papers(self, task_id: str) -> list[dict]:
        """Get imported papers for a specific task."""
        if task_id in self._runners:
            return self._runners[task_id].get_imported_papers()
        return []

    async def create_task(self, task_create: ImportTaskCreate) -> ImportTask:
        """Create and start a new import task."""
        task = ImportTask(
            id=str(uuid4()),
            name=task_create.name,
            category=task_create.category,
            semantic_query=task_create.semantic_query,
            text_search=task_create.text_search,
            check_interval=task_create.check_interval,
            is_active=True,
        )

        db = get_database()
        db.add_import_task(task)

        # Create and start runner
        runner = ImportTaskRunner(
            task,
            on_paper_imported=self._on_paper_imported,
            on_status_update=self._on_status_update,
            on_log=self._on_log,
        )
        self._runners[task.id] = runner
        await runner.start()

        logger.info(f"Created import task: {task.name} ({task.id})")
        return task

    async def start_task(self, task_id: str) -> bool:
        """Start an existing task."""
        db = get_database()
        task = db.get_import_task(task_id)
        
        if not task:
            logger.error(f"Task not found: {task_id}")
            return False

        if task_id in self._runners:
            await self._runners[task_id].start()
        else:
            runner = ImportTaskRunner(
                task,
                on_paper_imported=self._on_paper_imported,
                on_status_update=self._on_status_update,
                on_log=self._on_log,
            )
            self._runners[task_id] = runner
            await runner.start()

        db.update_import_task(task_id, {"is_active": True})
        return True

    async def stop_task(self, task_id: str) -> bool:
        """Stop a running task."""
        if task_id in self._runners:
            await self._runners[task_id].stop()
            del self._runners[task_id]
        
        db = get_database()
        db.update_import_task(task_id, {"is_active": False})
        return True

    async def delete_task(self, task_id: str) -> bool:
        """Delete a task."""
        await self.stop_task(task_id)
        
        db = get_database()
        return db.delete_import_task(task_id)

    def get_running_tasks(self) -> list[str]:
        """Get IDs of running tasks."""
        return list(self._runners.keys())

    async def start_active_tasks(self) -> None:
        """Start all active tasks from database."""
        db = get_database()
        tasks = db.get_active_import_tasks()
        
        for task in tasks:
            if task.id not in self._runners:
                runner = ImportTaskRunner(
                    task,
                    on_paper_imported=self._on_paper_imported,
                    on_status_update=self._on_status_update,
                    on_log=self._on_log,
                )
                self._runners[task.id] = runner
                await runner.start()

        logger.info(f"Started {len(tasks)} active import tasks")

    async def stop_all_tasks(self) -> None:
        """Stop all running tasks."""
        for task_id in list(self._runners.keys()):
            await self.stop_task(task_id)
        logger.info("Stopped all import tasks")


# Singleton instance
def get_import_manager() -> ImportManager:
    """Get the import manager instance."""
    return ImportManager()
