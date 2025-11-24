import asyncio
import logging
from typing import Dict, Any

class ContinuousImportService:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.is_running = False
        self.tasks = {}

    async def start(self):
        self.logger.info('Starting continuous import service...')
        self.is_running = True

    async def stop(self):
        self.logger.info('Stopping continuous import service...')
        self.is_running = False

    def is_running(self):
        return self.is_running
