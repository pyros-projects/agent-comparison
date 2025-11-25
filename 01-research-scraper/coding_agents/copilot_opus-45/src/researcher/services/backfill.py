"""Background backfill worker for filling placeholder content."""

import logging
import asyncio
from datetime import datetime
from typing import Optional, Callable, Any

from researcher.config import Config
from researcher.services.database import get_database
from researcher.services.llm import get_llm_service

logger = logging.getLogger("papertrail.backfill")


class BackfillWorker:
    """Background worker to fill placeholder content when LLM becomes available."""

    _instance: Optional["BackfillWorker"] = None

    def __new__(cls) -> "BackfillWorker":
        """Singleton pattern."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self) -> None:
        """Initialize backfill worker."""
        if self._initialized:
            return

        self._running = False
        self._task_handle: Optional[asyncio.Task] = None
        self._check_interval = 60  # Check every minute
        self._on_backfill_complete: Optional[Callable[[str, str], Any]] = None
        self._initialized = True
        logger.info("Backfill worker initialized")

    def set_callback(
        self,
        on_backfill_complete: Optional[Callable[[str, str], Any]] = None,
    ) -> None:
        """Set callback for backfill events."""
        self._on_backfill_complete = on_backfill_complete

    async def start(self) -> None:
        """Start the backfill worker."""
        if self._running:
            return

        self._running = True
        self._task_handle = asyncio.create_task(self._run_loop())
        logger.info("Backfill worker started")

    async def stop(self) -> None:
        """Stop the backfill worker."""
        self._running = False
        if self._task_handle:
            self._task_handle.cancel()
            try:
                await self._task_handle
            except asyncio.CancelledError:
                pass
        logger.info("Backfill worker stopped")

    async def _run_loop(self) -> None:
        """Main loop for backfill worker."""
        db = get_database()
        llm_service = get_llm_service()

        while self._running:
            try:
                # Check if LLM is available
                if not llm_service.available:
                    # Try to refresh availability
                    llm_service.refresh_availability()
                    
                    if not llm_service.available:
                        logger.debug("LLM not available, skipping backfill cycle")
                        await asyncio.sleep(self._check_interval)
                        continue

                # Get items from backfill queue
                queue_items = db.get_backfill_queue(limit=5)
                
                if not queue_items:
                    logger.debug("Backfill queue empty")
                    await asyncio.sleep(self._check_interval)
                    continue

                logger.info(f"Processing {len(queue_items)} backfill items")

                for item in queue_items:
                    if not self._running:
                        break

                    paper = db.get_paper(item.paper_id)
                    if not paper:
                        # Paper no longer exists, remove from queue
                        db.remove_from_backfill_queue(item.paper_id, item.field)
                        continue

                    try:
                        if item.field == "summary":
                            # Generate summary
                            summary = await llm_service.generate_summary(
                                paper.title,
                                paper.abstract,
                                paper.full_text,
                            )
                            
                            if summary != Config.PLACEHOLDER_SUMMARY:
                                db.update_paper(
                                    paper.id,
                                    {
                                        "summary": summary,
                                        "has_placeholder_summary": False,
                                    },
                                )
                                db.remove_from_backfill_queue(item.paper_id, "summary")
                                logger.info(f"Backfilled summary for: {paper.id}")
                                
                                if self._on_backfill_complete:
                                    await self._on_backfill_complete(paper.id, "summary")
                            else:
                                # LLM became unavailable, increment attempts
                                db.update_backfill_item(
                                    item.paper_id,
                                    "summary",
                                    {"attempts": item.attempts + 1},
                                )

                        elif item.field == "keywords":
                            # Extract keywords
                            keywords = await llm_service.extract_keywords(
                                paper.title,
                                paper.abstract,
                            )
                            
                            if keywords != [Config.PLACEHOLDER_KEYWORDS]:
                                db.update_paper(
                                    paper.id,
                                    {
                                        "keywords": keywords,
                                        "has_placeholder_keywords": False,
                                    },
                                )
                                db.remove_from_backfill_queue(item.paper_id, "keywords")
                                logger.info(f"Backfilled keywords for: {paper.id}")
                                
                                if self._on_backfill_complete:
                                    await self._on_backfill_complete(paper.id, "keywords")
                            else:
                                db.update_backfill_item(
                                    item.paper_id,
                                    "keywords",
                                    {"attempts": item.attempts + 1},
                                )

                    except Exception as e:
                        logger.error(f"Error backfilling {item.field} for {item.paper_id}: {e}")
                        db.update_backfill_item(
                            item.paper_id,
                            item.field,
                            {
                                "attempts": item.attempts + 1,
                                "last_error": str(e),
                            },
                        )

                    # Small delay between items
                    await asyncio.sleep(1)

            except Exception as e:
                logger.error(f"Error in backfill loop: {e}")

            await asyncio.sleep(self._check_interval)

    @property
    def is_running(self) -> bool:
        """Check if worker is running."""
        return self._running


# Singleton instance
def get_backfill_worker() -> BackfillWorker:
    """Get the backfill worker instance."""
    return BackfillWorker()
