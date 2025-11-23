"""Background backfill worker for LLM processing."""

import asyncio
from datetime import datetime

from researcher.database import db
from researcher.llm import llm_service
from researcher.logger import setup_logger

logger = setup_logger(__name__)


class BackfillWorker:
    """Background worker to process backfill queue."""
    
    def __init__(self):
        """Initialize backfill worker."""
        self.running = False
        self.task_handle = None
    
    async def start(self):
        """Start the backfill worker."""
        if self.running:
            logger.warning("Backfill worker already running")
            return
        
        logger.info("Starting backfill worker")
        self.running = True
        self.task_handle = asyncio.create_task(self._run())
    
    def stop(self):
        """Stop the backfill worker."""
        logger.info("Stopping backfill worker")
        self.running = False
        if self.task_handle:
            self.task_handle.cancel()
    
    async def _run(self):
        """Main worker loop."""
        try:
            while self.running:
                # Check if LLM is available
                if not llm_service.is_available():
                    logger.debug("LLM unavailable, backfill worker sleeping")
                    await asyncio.sleep(60)  # Check every minute
                    continue
                
                # Get backfill queue
                queue = db.get_backfill_queue()
                
                if not queue:
                    logger.debug("Backfill queue empty, sleeping")
                    await asyncio.sleep(30)  # Check every 30 seconds
                    continue
                
                logger.info(f"Processing {len(queue)} items in backfill queue")
                
                # Process items
                for item in queue:
                    if not self.running:
                        break
                    
                    try:
                        await self._process_item(item)
                    except Exception as e:
                        logger.error(f"Error processing backfill item {item.paper_id}: {e}")
                        # Update attempts
                        item.attempts += 1
                        if item.attempts >= 3:
                            logger.warning(f"Removing {item.paper_id} from queue after 3 attempts")
                            db.remove_backfill_item(item.paper_id)
                
                await asyncio.sleep(5)  # Small delay between batches
                
        except asyncio.CancelledError:
            logger.info("Backfill worker cancelled")
        except Exception as e:
            logger.error(f"Backfill worker error: {e}", exc_info=True)
    
    async def _process_item(self, item):
        """Process a single backfill item.
        
        Args:
            item: BackfillQueueItem to process
        """
        logger.info(f"Processing backfill for paper: {item.paper_id}")
        
        # Get paper
        paper = db.get_paper(item.paper_id)
        if not paper:
            logger.warning(f"Paper not found: {item.paper_id}")
            db.remove_backfill_item(item.paper_id)
            return
        
        # Generate summary
        summary_data = llm_service.generate_paper_summary(
            paper.title,
            paper.abstract,
            paper.full_text
        )
        
        # Update paper
        updates = {}
        if "summary" in item.fields_to_fill and summary_data.get("summary"):
            updates["summary"] = summary_data["summary"]
        if "methodology" in item.fields_to_fill and summary_data.get("methodology"):
            updates["methodology"] = summary_data["methodology"]
        if "results" in item.fields_to_fill and summary_data.get("results"):
            updates["results"] = summary_data["results"]
        if "keywords" in item.fields_to_fill and summary_data.get("keywords"):
            updates["keywords"] = summary_data["keywords"]
        if "key_contributions" in item.fields_to_fill and summary_data.get("key_contributions"):
            updates["key_contributions"] = summary_data["key_contributions"]
        
        # Mark as not needing processing if successful
        if not summary_data.get("needs_llm_processing", True):
            updates["needs_llm_processing"] = False
        
        if updates:
            db.update_paper(item.paper_id, updates)
            logger.info(f"✓ Backfilled paper: {paper.title}")
        
        # Remove from queue
        db.remove_backfill_item(item.paper_id)


# Global backfill worker instance
backfill_worker = BackfillWorker()
