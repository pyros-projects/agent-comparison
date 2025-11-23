"""Continuous arXiv import background service."""

import asyncio
import uuid
from datetime import datetime
from typing import Optional, Set

from researcher.models import ContinuousImportTask, ContinuousImportFilter
from researcher.database import db
from researcher.ingestion import ingestion_service
from researcher.embeddings import embedding_service
from researcher.logger import setup_logger

logger = setup_logger(__name__)


class ContinuousImportService:
    """Background service for continuous arXiv monitoring."""
    
    def __init__(self):
        """Initialize continuous import service."""
        self.running_tasks: Set[str] = set()
        self.task_handles: dict = {}
    
    async def start_task(self, task: ContinuousImportTask):
        """Start a continuous import task.
        
        Args:
            task: Import task configuration
        """
        if task.id in self.running_tasks:
            logger.warning(f"Task {task.id} already running")
            return
        
        logger.info(f"Starting continuous import task: {task.name} (ID: {task.id})")
        self.running_tasks.add(task.id)
        
        # Create asyncio task
        handle = asyncio.create_task(self._run_task(task))
        self.task_handles[task.id] = handle
    
    async def stop_task(self, task_id: str):
        """Stop a running task.
        
        Args:
            task_id: Task ID to stop
        """
        if task_id not in self.running_tasks:
            logger.warning(f"Task {task_id} not running")
            return
        
        logger.info(f"Stopping task: {task_id}")
        self.running_tasks.remove(task_id)
        
        # Cancel asyncio task
        if task_id in self.task_handles:
            self.task_handles[task_id].cancel()
            del self.task_handles[task_id]
        
        # Update task status
        db.update_task(task_id, {"is_active": False})
    
    async def _run_task(self, task: ContinuousImportTask):
        """Run continuous import task loop.
        
        Args:
            task: Import task configuration
        """
        logger.info(f"Task {task.name} started with {task.check_interval_seconds}s interval")
        
        try:
            while task.id in self.running_tasks:
                # Get latest task config
                task = db.get_task(task.id)
                if not task or not task.is_active:
                    break
                
                logger.debug(f"Task {task.name}: checking for new papers")
                
                try:
                    # Search arXiv with filters
                    papers = await self._search_with_filters(task.filters, task.max_results_per_check)
                    
                    # Filter out existing papers
                    new_papers = [p for p in papers if not db.paper_exists(p['arxiv_id'])]
                    
                    logger.info(f"Task {task.name}: found {len(new_papers)} new papers")
                    
                    # Ingest new papers
                    for paper_data in new_papers:
                        try:
                            await ingestion_service.ingest_paper(paper_data['arxiv_url'])
                            db.update_task(task.id, {
                                "papers_imported": task.papers_imported + 1,
                                "last_check": datetime.utcnow().isoformat()
                            })
                        except Exception as e:
                            logger.error(f"Failed to ingest {paper_data['arxiv_id']}: {e}")
                    
                    # Update last check time
                    db.update_task(task.id, {"last_check": datetime.utcnow().isoformat()})
                    
                except Exception as e:
                    logger.error(f"Task {task.name} error: {e}")
                
                # Wait for next check
                await asyncio.sleep(task.check_interval_seconds)
                
        except asyncio.CancelledError:
            logger.info(f"Task {task.name} cancelled")
        except Exception as e:
            logger.error(f"Task {task.name} failed: {e}", exc_info=True)
        finally:
            if task.id in self.running_tasks:
                self.running_tasks.remove(task.id)
    
    async def _search_with_filters(
        self,
        filters: ContinuousImportFilter,
        max_results: int
    ) -> list:
        """Search arXiv with filters applied.
        
        Args:
            filters: Filter configuration
            max_results: Maximum results to return
            
        Returns:
            List of matching papers
        """
        # Build search query
        query = None
        category = None
        
        if filters.arxiv_categories:
            category = filters.arxiv_categories[0]  # Use first category
        
        if filters.text_query:
            query = filters.text_query
        
        # Search arXiv
        papers = await ingestion_service.search_arxiv(
            query=query,
            category=category,
            max_results=max_results
        )
        
        # Apply semantic filter if specified
        if filters.semantic_query and filters.min_relevance_score:
            query_embedding = embedding_service.generate_embedding(filters.semantic_query)
            filtered = []
            
            for paper in papers:
                paper_text = f"{paper['title']} {paper['abstract']}"
                paper_embedding = embedding_service.generate_embedding(paper_text)
                similarity = embedding_service.compute_similarity(query_embedding, paper_embedding)
                
                if similarity >= filters.min_relevance_score:
                    filtered.append(paper)
            
            papers = filtered
        
        return papers
    
    def create_task(
        self,
        name: str,
        filters: ContinuousImportFilter,
        check_interval_seconds: int = 300,
        max_results_per_check: int = 10,
        start_immediately: bool = True
    ) -> ContinuousImportTask:
        """Create a new continuous import task.
        
        Args:
            name: Task name
            filters: Filter configuration
            check_interval_seconds: Check interval in seconds
            max_results_per_check: Max results per check
            start_immediately: Start task immediately
            
        Returns:
            Created task
        """
        task = ContinuousImportTask(
            id=str(uuid.uuid4()),
            name=name,
            filters=filters,
            check_interval_seconds=check_interval_seconds,
            max_results_per_check=max_results_per_check,
            is_active=start_immediately
        )
        
        db.insert_task(task)
        logger.info(f"Created task: {name} (ID: {task.id})")
        
        if start_immediately:
            asyncio.create_task(self.start_task(task))
        
        return task
    
    async def start_all_active_tasks(self):
        """Start all active tasks from database."""
        tasks = db.get_active_tasks()
        logger.info(f"Starting {len(tasks)} active tasks")
        
        for task in tasks:
            await self.start_task(task)
    
    def get_running_task_ids(self) -> list:
        """Get list of currently running task IDs."""
        return list(self.running_tasks)


# Global continuous import service instance
continuous_import_service = ContinuousImportService()
