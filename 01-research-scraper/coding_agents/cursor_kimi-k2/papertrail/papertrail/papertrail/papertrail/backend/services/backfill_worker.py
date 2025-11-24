import logging

class BackfillWorker:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.is_running = False

    async def start(self):
        self.logger.info('Starting backfill worker...')
        self.is_running = True

    async def stop(self):
        self.logger.info('Stopping backfill worker...')
        self.is_running = False

    def is_running(self):
        return self.is_running
