import logging
from datetime import datetime
from typing import List, Dict, Any, Optional
from tinydb import TinyDB, Query
from tinydb.storages import JSONStorage
from tinydb.middlewares import CachingMiddleware
import os

logger = logging.getLogger(__name__)

class PaperTrailDB:
    """TinyDB wrapper for PaperTrail database operations"""
    
    def __init__(self, data_dir: str = "data"):
        os.makedirs(data_dir, exist_ok=True)
        
        # Initialize databases with caching for better performance
        self.db = TinyDB(os.path.join(data_dir, "papers.json"), 
                        storage=CachingMiddleware(JSONStorage))
        self.embeddings_db = TinyDB(os.path.join(data_dir, "embeddings.json"),
                                   storage=CachingMiddleware(JSONStorage))
        self.relationships_db = TinyDB(os.path.join(data_dir, "relationships.json"),
                                     storage=CachingMiddleware(JSONStorage))
        self.tasks_db = TinyDB(os.path.join(data_dir, "tasks.json"),
                              storage=CachingMiddleware(JSONStorage))
        self.backfill_queue_db = TinyDB(os.path.join(data_dir, "backfill_queue.json"),
                                       storage=CachingMiddleware(JSONStorage))
        
        # Get tables
        self.papers = self.db.table('papers')
        self.embeddings = self.embeddings_db.table('embeddings')
        self.relationships = self.relationships_db.table('relationships')
        self.continuous_tasks = self.tasks_db.table('continuous_tasks')
        self.backfill_queue = self.backfill_queue_db.table('backfill_queue')
        
        logger.info("Database initialized successfully")
    
    def close(self):
        """Close all database connections"""
        self.db.close()
        self.embeddings_db.close()
        self.relationships_db.close()
        self.tasks_db.close()
        self.backfill_queue_db.close()
        logger.info("Database connections closed")

# Global database instance
db = PaperTrailDB()
