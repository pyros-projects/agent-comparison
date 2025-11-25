from __future__ import annotations

import asyncio
from collections import deque
from typing import AsyncIterator, Deque

from .models import EventMessage


class EventBus:
    """Simple pub/sub fan-out used for WebSocket streaming."""

    def __init__(self, history: int = 200) -> None:
        self._subscribers: set[asyncio.Queue[EventMessage]] = set()
        self._lock = asyncio.Lock()
        self._history: Deque[EventMessage] = deque(maxlen=history)

    async def publish(self, event: EventMessage) -> None:
        async with self._lock:
            self._history.append(event)
            subscribers = list(self._subscribers)
        for queue in subscribers:
            await queue.put(event)

    async def subscribe(self) -> AsyncIterator[EventMessage]:
        queue: asyncio.Queue[EventMessage] = asyncio.Queue()
        async with self._lock:
            self._subscribers.add(queue)
            history = list(self._history)
        for item in history:
            await queue.put(item)
        try:
            while True:
                event = await queue.get()
                yield event
        finally:
            async with self._lock:
                self._subscribers.discard(queue)

