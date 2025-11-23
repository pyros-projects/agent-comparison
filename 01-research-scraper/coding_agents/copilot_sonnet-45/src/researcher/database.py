"""Database layer using TinyDB."""

import os
from datetime import datetime
from typing import List, Optional, Dict, Any
from tinydb import TinyDB, Query
from tinydb.storages import JSONStorage
from tinydb.middlewares import CachingMiddleware

from researcher.models import (
    Paper, PaperEmbedding, PaperRelationship,
    ContinuousImportTask, BackfillQueueItem
)
from researcher.config import settings


class Database:
    """TinyDB database wrapper for PaperTrail."""
    
    def __init__(self):
        """Initialize database connections."""
        # Ensure data directory exists
        os.makedirs(os.path.dirname(settings.db_path), exist_ok=True)
        
        # Initialize databases with caching
        self.papers_db = TinyDB(
            settings.db_path,
            storage=CachingMiddleware(JSONStorage),
            indent=2
        )
        self.embeddings_db = TinyDB(
            settings.embeddings_db_path,
            storage=CachingMiddleware(JSONStorage),
            indent=2
        )
        self.graph_db = TinyDB(
            settings.graph_db_path,
            storage=CachingMiddleware(JSONStorage),
            indent=2
        )
        self.tasks_db = TinyDB(
            settings.tasks_db_path,
            storage=CachingMiddleware(JSONStorage),
            indent=2
        )
        self.backfill_db = TinyDB(
            settings.backfill_db_path,
            storage=CachingMiddleware(JSONStorage),
            indent=2
        )
        
        # Tables
        self.papers = self.papers_db.table('papers')
        self.embeddings = self.embeddings_db.table('embeddings')
        self.relationships = self.graph_db.table('relationships')
        self.tasks = self.tasks_db.table('tasks')
        self.backfill = self.backfill_db.table('backfill')
    
    # Paper operations
    def insert_paper(self, paper: Paper) -> str:
        """Insert a new paper."""
        paper_dict = paper.model_dump(mode='json')
        self.papers.insert(paper_dict)
        return paper.id
    
    def get_paper(self, paper_id: str) -> Optional[Paper]:
        """Get paper by ID."""
        query = Query()
        result = self.papers.get(query.id == paper_id)
        return Paper(**result) if result else None
    
    def update_paper(self, paper_id: str, updates: Dict[str, Any]) -> bool:
        """Update paper fields."""
        query = Query()
        result = self.papers.update(updates, query.id == paper_id)
        return len(result) > 0
    
    def get_all_papers(self) -> List[Paper]:
        """Get all papers."""
        return [Paper(**p) for p in self.papers.all()]
    
    def paper_exists(self, arxiv_id: str) -> bool:
        """Check if paper exists by arXiv ID."""
        query = Query()
        return self.papers.contains(query.arxiv_id == arxiv_id)
    
    def get_papers_needing_llm(self) -> List[Paper]:
        """Get papers that need LLM processing."""
        query = Query()
        results = self.papers.search(query.needs_llm_processing == True)
        return [Paper(**p) for p in results]
    
    def search_papers(self, **filters) -> List[Paper]:
        """Search papers by filters."""
        query = Query()
        conditions = []
        
        if 'status' in filters:
            conditions.append(query.status == filters['status'])
        if 'categories' in filters:
            conditions.append(query.categories.any(filters['categories']))
        
        if conditions:
            results = self.papers.search(conditions[0] if len(conditions) == 1 else query.fragment(*conditions))
        else:
            results = self.papers.all()
        
        return [Paper(**p) for p in results]
    
    # Embedding operations
    def insert_embedding(self, embedding: PaperEmbedding) -> None:
        """Insert paper embedding."""
        self.embeddings.insert(embedding.model_dump(mode='json'))
    
    def get_embedding(self, paper_id: str) -> Optional[PaperEmbedding]:
        """Get embedding for paper."""
        query = Query()
        result = self.embeddings.get(query.paper_id == paper_id)
        return PaperEmbedding(**result) if result else None
    
    def get_all_embeddings(self) -> List[PaperEmbedding]:
        """Get all embeddings."""
        return [PaperEmbedding(**e) for e in self.embeddings.all()]
    
    # Relationship operations
    def insert_relationship(self, relationship: PaperRelationship) -> None:
        """Insert paper relationship."""
        self.relationships.insert(relationship.model_dump(mode='json'))
    
    def get_relationships(self, paper_id: str) -> List[PaperRelationship]:
        """Get all relationships for a paper."""
        query = Query()
        results = self.relationships.search(
            (query.source_id == paper_id) | (query.target_id == paper_id)
        )
        return [PaperRelationship(**r) for r in results]
    
    def get_all_relationships(self) -> List[PaperRelationship]:
        """Get all relationships."""
        return [PaperRelationship(**r) for r in self.relationships.all()]
    
    # Import task operations
    def insert_task(self, task: ContinuousImportTask) -> str:
        """Insert continuous import task."""
        self.tasks.insert(task.model_dump(mode='json'))
        return task.id
    
    def get_task(self, task_id: str) -> Optional[ContinuousImportTask]:
        """Get task by ID."""
        query = Query()
        result = self.tasks.get(query.id == task_id)
        return ContinuousImportTask(**result) if result else None
    
    def get_all_tasks(self) -> List[ContinuousImportTask]:
        """Get all import tasks."""
        return [ContinuousImportTask(**t) for t in self.tasks.all()]
    
    def get_active_tasks(self) -> List[ContinuousImportTask]:
        """Get active import tasks."""
        query = Query()
        results = self.tasks.search(query.is_active == True)
        return [ContinuousImportTask(**t) for t in results]
    
    def update_task(self, task_id: str, updates: Dict[str, Any]) -> bool:
        """Update task fields."""
        query = Query()
        result = self.tasks.update(updates, query.id == task_id)
        return len(result) > 0
    
    def delete_task(self, task_id: str) -> bool:
        """Delete task."""
        query = Query()
        result = self.tasks.remove(query.id == task_id)
        return len(result) > 0
    
    # Backfill queue operations
    def insert_backfill_item(self, item: BackfillQueueItem) -> None:
        """Add item to backfill queue."""
        self.backfill.insert(item.model_dump(mode='json'))
    
    def get_backfill_queue(self) -> List[BackfillQueueItem]:
        """Get all backfill queue items, sorted by priority."""
        items = [BackfillQueueItem(**i) for i in self.backfill.all()]
        return sorted(items, key=lambda x: (-x.priority, x.created_at))
    
    def remove_backfill_item(self, paper_id: str) -> bool:
        """Remove item from backfill queue."""
        query = Query()
        result = self.backfill.remove(query.paper_id == paper_id)
        return len(result) > 0
    
    def close(self):
        """Close all database connections."""
        self.papers_db.close()
        self.embeddings_db.close()
        self.graph_db.close()
        self.tasks_db.close()
        self.backfill_db.close()


# Global database instance
db = Database()
