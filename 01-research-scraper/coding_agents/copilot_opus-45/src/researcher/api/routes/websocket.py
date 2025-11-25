"""WebSocket routes for real-time updates."""

import logging
import asyncio
from typing import Set
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
import json

from researcher.services import (
    get_import_manager,
    get_backfill_worker,
    get_ingestion_service,
)

logger = logging.getLogger("papertrail.api.websocket")

router = APIRouter()


class ConnectionManager:
    """WebSocket connection manager."""

    def __init__(self) -> None:
        """Initialize connection manager."""
        self.active_connections: Set[WebSocket] = set()

    async def connect(self, websocket: WebSocket) -> None:
        """Accept and add a new connection."""
        await websocket.accept()
        self.active_connections.add(websocket)
        logger.info(f"WebSocket connected. Total connections: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket) -> None:
        """Remove a connection."""
        self.active_connections.discard(websocket)
        logger.info(f"WebSocket disconnected. Total connections: {len(self.active_connections)}")

    async def broadcast(self, message: dict) -> None:
        """Broadcast message to all connections."""
        if not self.active_connections:
            return
        
        message_json = json.dumps(message)
        disconnected = set()
        
        for connection in self.active_connections:
            try:
                await connection.send_text(message_json)
            except Exception as e:
                logger.warning(f"Failed to send message: {e}")
                disconnected.add(connection)
        
        # Remove disconnected clients
        self.active_connections -= disconnected


# Global connection manager
manager = ConnectionManager()


async def on_paper_imported(task_id: str, paper_data: dict) -> None:
    """Callback when a paper is imported."""
    await manager.broadcast({
        "type": "paper_imported",
        "task_id": task_id,
        "paper": paper_data,
    })


async def on_import_status_update(task_id: str, status: str) -> None:
    """Callback when import task status changes."""
    await manager.broadcast({
        "type": "import_status",
        "task_id": task_id,
        "status": status,
    })


async def on_backfill_complete(paper_id: str, field: str) -> None:
    """Callback when backfill is complete for a paper."""
    await manager.broadcast({
        "type": "backfill_complete",
        "paper_id": paper_id,
        "field": field,
    })


# Set up callbacks
def setup_callbacks() -> None:
    """Set up WebSocket callbacks for services."""
    import_manager = get_import_manager()
    import_manager.set_callbacks(
        on_paper_imported=on_paper_imported,
        on_status_update=on_import_status_update,
    )
    
    backfill_worker = get_backfill_worker()
    backfill_worker.set_callback(on_backfill_complete=on_backfill_complete)


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time updates."""
    await manager.connect(websocket)
    
    # Set up callbacks on first connection
    setup_callbacks()
    
    try:
        while True:
            # Handle incoming messages
            data = await websocket.receive_text()
            message = json.loads(data)
            
            if message.get("type") == "ping":
                await websocket.send_text(json.dumps({"type": "pong"}))
            
            elif message.get("type") == "ingest":
                # Handle manual ingestion request
                arxiv_url = message.get("arxiv_url")
                if arxiv_url:
                    async def progress_callback(msg: str, progress: float):
                        await websocket.send_text(json.dumps({
                            "type": "ingest_progress",
                            "message": msg,
                            "progress": progress,
                        }))
                    
                    ingestion_service = get_ingestion_service()
                    try:
                        paper = await ingestion_service.ingest_paper(
                            arxiv_url,
                            progress_callback=progress_callback,
                        )
                        if paper:
                            await websocket.send_text(json.dumps({
                                "type": "ingest_complete",
                                "paper_id": paper.id,
                                "title": paper.title,
                            }))
                        else:
                            await websocket.send_text(json.dumps({
                                "type": "ingest_error",
                                "message": "Failed to ingest paper",
                            }))
                    except Exception as e:
                        await websocket.send_text(json.dumps({
                            "type": "ingest_error",
                            "message": str(e),
                        }))
    
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        manager.disconnect(websocket)
