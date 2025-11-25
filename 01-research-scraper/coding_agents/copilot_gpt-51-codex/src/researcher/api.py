from __future__ import annotations

import asyncio
import logging
from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

from .config import settings
from .embeddings import EmbeddingService
from .events import EventBus
from .graph import GraphService
from .ingestion import ContinuousImportManager, IngestionService
from .llm import LLMService
from .models import (
    DashboardStats,
    EventMessage,
    EventType,
    GraphResponse,
    ImportTaskConfig,
    ManualIngestRequest,
    Paper,
    PaperStatus,
    SearchQuery,
    TheoryQueryRequest,
    TheoryResponse,
)
from .storage import Storage
from .theory import TheoryService

logger = logging.getLogger(__name__)


class AppContainer:
    def __init__(self) -> None:
        self.storage = Storage(settings.data_dir / "papertrail.json")
        self.bus = EventBus(history=settings.websocket_history)
        self.embeddings = EmbeddingService()
        self.llm = LLMService()
        self.graph = GraphService(self.storage)
        self.ingestion = IngestionService(self.storage, self.embeddings, self.llm, self.graph, self.bus)
        self.tasks = ContinuousImportManager(self.storage, self.ingestion, self.bus)
        self.theory = TheoryService(self.storage, self.embeddings, self.llm)
        self._backfill_task: asyncio.Task | None = None

    async def start_background(self) -> None:
        if self._backfill_task is None:
            self._backfill_task = asyncio.create_task(self._backfill_worker())
        for task in self.storage.list_tasks():
            if task.status.value == "running" and not self.tasks.is_active(task.id):
                await self.tasks.start_task(task)

    async def _backfill_worker(self) -> None:
        while True:
            await asyncio.sleep(settings.background_backfill_interval)
            if not self.llm.available:
                continue
            for paper in self.storage.list_papers():
                if not paper.placeholders:
                    continue
                logger.info("Backfilling paper", extra={"paper_id": paper.id})
                fields = await self.llm.summarize_paper(paper)
                paper.summary = fields["summary"]
                paper.methodology = fields["methodology"]
                paper.results = fields["results"]
                paper.further_work = fields["further_work"]
                paper.keywords = fields["keywords"]
                paper.placeholders = "<summary>" in paper.summary
                self.storage.upsert_paper(paper)
                await self.bus.publish(
                    EventMessage(
                        type=EventType.BACKFILL,
                        payload={"paper_id": paper.id},
                    )
                )


container = AppContainer()


async def get_container() -> AppContainer:
    return container


def create_app() -> FastAPI:
    app = FastAPI(title=settings.app_name)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.on_event("startup")
    async def _startup() -> None:  # noqa: WPS430
        await container.start_background()
        logger.info("Application started")

    @app.get("/health")
    async def health() -> dict[str, str]:
        return {"status": "ok"}

    @app.get("/status")
    async def status(ctx: Annotated[AppContainer, Depends(get_container)]) -> dict:
        return {
            "llm_available": ctx.llm.available,
            "embedding_provider": ctx.embeddings.provider,
            "tasks": [task.model_dump() for task in ctx.storage.list_tasks()],
        }

    @app.post("/ingest", response_model=Paper)
    async def ingest(
        payload: ManualIngestRequest,
        ctx: Annotated[AppContainer, Depends(get_container)],
    ) -> Paper:
        try:
            return await ctx.ingestion.ingest_manual(payload)
        except Exception as exc:  # noqa: BLE001
            raise HTTPException(status_code=400, detail=str(exc)) from exc

    @app.get("/papers", response_model=dict)
    async def list_papers(
        ctx: Annotated[AppContainer, Depends(get_container)],
        text: str | None = None,
        category: str | None = None,
        status: PaperStatus | None = None,
        starred: bool | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> dict:
        params = SearchQuery(text=text, category=category, status=status, starred=starred, limit=limit, offset=offset)
        items, total = ctx.storage.search(params)
        return {"items": [item.model_dump() for item in items], "total": total}

    @app.get("/papers/{paper_id}", response_model=Paper)
    async def get_paper(paper_id: str, ctx: Annotated[AppContainer, Depends(get_container)]) -> Paper:
        paper = ctx.storage.get_paper(paper_id)
        if not paper:
            raise HTTPException(status_code=404, detail="Paper not found")
        return paper

    @app.patch("/papers/{paper_id}", response_model=Paper)
    async def update_paper(
        paper_id: str,
        ctx: Annotated[AppContainer, Depends(get_container)],
        status: PaperStatus | None = None,
        starred: bool | None = None,
    ) -> Paper:
        try:
            return ctx.storage.update_paper_status(paper_id, status=status, starred=starred)
        except KeyError as exc:
            raise HTTPException(status_code=404, detail="Paper not found") from exc

    @app.post("/papers/{paper_id}/notes", response_model=Paper)
    async def add_note(
        paper_id: str,
        note: dict,
        ctx: Annotated[AppContainer, Depends(get_container)],
    ) -> Paper:
        text = note.get("text")
        if not text:
            raise HTTPException(status_code=400, detail="Missing note text")
        try:
            return ctx.storage.add_note(paper_id, text)
        except KeyError as exc:
            raise HTTPException(status_code=404, detail="Paper not found") from exc

    @app.get("/papers/{paper_id}/similar")
    async def similar(paper_id: str, ctx: Annotated[AppContainer, Depends(get_container)]):
        paper = ctx.storage.get_paper(paper_id)
        if not paper:
            raise HTTPException(status_code=404, detail="Paper not found")
        matches = ctx.graph.similar_papers(paper)
        return [
            {"paper_id": candidate.id, "title": candidate.title, "score": score}
            for candidate, score in matches
        ]

    @app.get("/papers/{paper_id}/graph", response_model=GraphResponse)
    async def graph(paper_id: str, ctx: Annotated[AppContainer, Depends(get_container)]) -> GraphResponse:
        return ctx.graph.neighbors(paper_id)

    @app.post("/tasks", response_model=ImportTaskConfig)
    async def start_task(
        config: ImportTaskConfig,
        ctx: Annotated[AppContainer, Depends(get_container)],
    ) -> ImportTaskConfig:
        await ctx.tasks.start_task(config)
        return config

    @app.patch("/tasks/{task_id}")
    async def stop_task(task_id: str, ctx: Annotated[AppContainer, Depends(get_container)]):
        await ctx.tasks.stop_task(task_id)
        return {"status": "stopped"}

    @app.get("/tasks")
    async def list_tasks(ctx: Annotated[AppContainer, Depends(get_container)]):
        return [task.model_dump() for task in ctx.storage.list_tasks()]

    @app.get("/dashboard", response_model=DashboardStats)
    async def dashboard(ctx: Annotated[AppContainer, Depends(get_container)]) -> DashboardStats:
        data = ctx.storage.build_dashboard()
        graph_clusters = ctx.graph.cluster_summary()
        data["graph_clusters"] = graph_clusters
        return DashboardStats(**data)

    @app.post("/theory", response_model=TheoryResponse)
    async def theory(payload: TheoryQueryRequest, ctx: Annotated[AppContainer, Depends(get_container)]):
        result = await ctx.theory.run(payload)
        return result

    @app.websocket("/ws/events")
    async def ws(websocket: WebSocket, ctx: Annotated[AppContainer, Depends(get_container)]):
        await websocket.accept()
        try:
            async for event in ctx.bus.subscribe():
                await websocket.send_json(event.model_dump())
        except WebSocketDisconnect:
            logger.info("WebSocket disconnected")

    return app


app = create_app()
