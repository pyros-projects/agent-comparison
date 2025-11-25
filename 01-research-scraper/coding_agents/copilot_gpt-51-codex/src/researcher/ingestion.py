from __future__ import annotations

import asyncio
import datetime as dt
import logging
import re
import xml.etree.ElementTree as ET
from typing import Any, Dict, Iterable, List, Optional

import httpx
from io import BytesIO

from pypdf import PdfReader

from .config import settings
from .embeddings import EmbeddingService
from .events import EventBus
from .graph import GraphService
from .llm import LLMService
from .models import EventMessage, EventType, ImportTaskConfig, ImportTaskStatus, ManualIngestRequest, Paper
from .storage import Storage

logger = logging.getLogger(__name__)
ARXIV_PATTERN = re.compile(r"arxiv\.org/(abs|pdf)/(?P<id>[\w\.\-]+)")


def normalize_arxiv_id(url: str) -> str:
    """Extract the canonical arXiv identifier from any supported link."""
    match = ARXIV_PATTERN.search(url)
    if match:
        return match.group("id")
    return url.split("/")[-1]


class IngestionService:
    def __init__(
        self,
        storage: Storage,
        embeddings: EmbeddingService,
        llm: LLMService,
        graph: GraphService,
        bus: EventBus,
    ) -> None:
        self.storage = storage
        self.embeddings = embeddings
        self.llm = llm
        self.graph = graph
        self.bus = bus

    async def ingest_manual(self, payload: ManualIngestRequest) -> Paper:
        arxiv_id = normalize_arxiv_id(payload.arxiv_url)
        existing = self.storage.get_paper_by_arxiv(arxiv_id)
        if existing:
            logger.info("Paper already ingested", extra={"arxiv_id": arxiv_id})
            await self.bus.publish(
                EventMessage(
                    type=EventType.STATUS,
                    payload={"arxiv_id": arxiv_id, "status": "duplicate"},
                )
            )
            return existing
        metadata = await self._fetch_metadata(arxiv_id)
        pdf_text = await self._download_pdf(metadata["pdf_url"])
        paper = Paper(
            arxiv_id=arxiv_id,
            title=metadata["title"],
            authors=metadata["authors"],
            abstract=metadata["abstract"],
            categories=metadata["categories"],
            pdf_url=metadata["pdf_url"],
            published_at=metadata["published_at"],
            tags=payload.tags or [],
            content=pdf_text,
        )
        vector = await self.embeddings.embed("\n".join([paper.title, paper.abstract, pdf_text[:5000]]))
        paper.vector = vector
        llm_fields = await self.llm.summarize_paper(paper)
        paper.summary = llm_fields["summary"]
        paper.methodology = llm_fields["methodology"]
        paper.results = llm_fields["results"]
        paper.further_work = llm_fields["further_work"]
        paper.keywords = llm_fields["keywords"]
        paper.placeholders = "<summary>" in paper.summary
        stored = self.storage.upsert_paper(paper)
        self.graph.rebuild()
        await self.bus.publish(
            EventMessage(
                type=EventType.PAPER_INGESTED,
                payload={"paper_id": stored.id, "title": stored.title},
            )
        )
        return stored

    async def _fetch_metadata(self, arxiv_id: str) -> Dict[str, Any]:
        params = {"id_list": arxiv_id}
        async with httpx.AsyncClient() as client:
            response = await client.get("https://export.arxiv.org/api/query", params=params, timeout=30)
            response.raise_for_status()
        root = ET.fromstring(response.text)
        entry = root.find("{http://www.w3.org/2005/Atom}entry")
        if entry is None:
            raise ValueError(f"Paper {arxiv_id} not found")
        ns = "{http://www.w3.org/2005/Atom}"
        title = (entry.find(f"{ns}title").text or "").strip()
        abstract = (entry.find(f"{ns}summary").text or "").strip()
        published_text = entry.find(f"{ns}published").text or dt.datetime.now(dt.timezone.utc).isoformat()
        published_at = dt.datetime.fromisoformat(published_text.replace("Z", "+00:00"))
        authors = [auth.find(f"{ns}name").text or "" for auth in entry.findall(f"{ns}author")]
        categories = [cat.attrib.get("term", "") for cat in entry.findall("{http://arxiv.org/schemas/atom}category")]
        pdf_url = ""
        for link in entry.findall(f"{ns}link"):
            if link.attrib.get("title") == "pdf" or link.attrib.get("type") == "application/pdf":
                pdf_url = link.attrib.get("href", "")
                break
        if not pdf_url:
            pdf_url = f"https://arxiv.org/pdf/{arxiv_id}.pdf"
        return {
            "title": title,
            "abstract": abstract,
            "published_at": published_at,
            "authors": authors,
            "categories": [cat for cat in categories if cat],
            "pdf_url": pdf_url,
        }

    async def _download_pdf(self, pdf_url: str) -> str:
        async with httpx.AsyncClient() as client:
            response = await client.get(pdf_url, timeout=60)
            response.raise_for_status()
        text = await asyncio.to_thread(self._extract_pdf_text, response.content)
        return text

    def _extract_pdf_text(self, data: bytes) -> str:
        reader = PdfReader(BytesIO(data))
        pages: List[str] = []
        for page in reader.pages[:10]:  # keep extraction manageable
            snippet = page.extract_text() or ""
            pages.append(snippet)
        return "\n".join(pages)

class ContinuousImportManager:
    def __init__(
        self,
        storage: Storage,
        ingestion: IngestionService,
        bus: EventBus,
    ) -> None:
        self.storage = storage
        self.ingestion = ingestion
        self.bus = bus
        self._tasks: dict[str, asyncio.Task[None]] = {}
        self._lock = asyncio.Lock()

    def is_active(self, task_id: str) -> bool:
        return task_id in self._tasks and not self._tasks[task_id].done()

    async def start_task(self, config: ImportTaskConfig) -> ImportTaskConfig:
        now = dt.datetime.now(dt.timezone.utc)
        config.next_run_at = now
        self.storage.upsert_task(config)
        async with self._lock:
            task = asyncio.create_task(self._runner(config))
            self._tasks[config.id] = task
        await self.bus.publish(
            EventMessage(
                type=EventType.TASK_UPDATED,
                payload={
                    "task_id": config.id,
                    "status": config.status.value,
                    "next_run_at": config.next_run_at.isoformat() if config.next_run_at else None,
                },
            )
        )
        return config

    async def stop_task(self, task_id: str) -> None:
        async with self._lock:
            task = self._tasks.get(task_id)
            if task:
                task.cancel()
                self._tasks.pop(task_id, None)
        existing = self.storage.get_task(task_id)
        if existing:
            existing.status = ImportTaskStatus.STOPPED
            existing.next_run_at = None
            self.storage.upsert_task(existing)
        await self.bus.publish(
            EventMessage(
                type=EventType.TASK_UPDATED,
                payload={"task_id": task_id, "status": "stopped", "next_run_at": None},
            )
        )

    async def _runner(self, config: ImportTaskConfig) -> None:
        backoff = settings.continuous_import_poll_seconds
        while True:
            try:
                await self._poll_once(config)
                await asyncio.sleep(config.interval_seconds)
            except asyncio.CancelledError:
                raise
            except Exception as exc:  # noqa: BLE001
                logger.exception("Continuous import failure", exc_info=exc)
                await asyncio.sleep(min(backoff * 2, 1800))

    async def _poll_once(self, config: ImportTaskConfig) -> None:
        papers = await self._query_arxiv(config)
        imported = 0
        skipped = 0
        for entry in papers:
            try:
                arxiv_id = entry.get("arxiv_id") or normalize_arxiv_id(entry["id"])
                if self.storage.get_paper_by_arxiv(arxiv_id):
                    skipped += 1
                    await self.bus.publish(
                        EventMessage(
                            type=EventType.STATUS,
                            payload={
                                "task_id": config.id,
                                "arxiv_id": arxiv_id,
                                "status": "skipped",
                            },
                        )
                    )
                    continue
                await self.ingestion.ingest_manual(
                    ManualIngestRequest(arxiv_url=entry["id"])  # type: ignore[arg-type]
                )
                imported += 1
            except Exception as exc:  # noqa: BLE001
                logger.warning("Import task failed for paper", extra={"paper": entry.get("id")}, exc_info=exc)
        now = dt.datetime.now(dt.timezone.utc)
        config.total_imported += imported
        config.total_attempted += len(papers)
        config.last_run_at = now
        config.next_run_at = now + dt.timedelta(seconds=config.interval_seconds)
        self.storage.upsert_task(config)
        await self.bus.publish(
            EventMessage(
                type=EventType.TASK_UPDATED,
                payload={
                    "task_id": config.id,
                    "status": config.status.value,
                    "imported": imported,
                    "skipped": skipped,
                    "next_run_at": config.next_run_at.isoformat() if config.next_run_at else None,
                },
            )
        )
        await self.bus.publish(
            EventMessage(
                type=EventType.STATUS,
                payload={
                    "task_id": config.id,
                    "message": "Next import scheduled",
                    "next_run_at": config.next_run_at.isoformat() if config.next_run_at else None,
                },
            )
        )

    async def _query_arxiv(self, config: ImportTaskConfig) -> List[Dict[str, Any]]:
        params = {
            "search_query": self._build_query(config),
            "sortBy": "submittedDate",
            "sortOrder": "descending",
            "max_results": settings.continuous_import_batch_size,
        }
        async with httpx.AsyncClient() as client:
            response = await client.get("https://export.arxiv.org/api/query", params=params, timeout=30)
            response.raise_for_status()
        root = ET.fromstring(response.text)
        entries: List[Dict[str, Any]] = []
        ns = "{http://www.w3.org/2005/Atom}"
        for entry in root.findall(f"{ns}entry"):
            raw_id = entry.find(f"{ns}id").text or ""
            entries.append({"id": raw_id, "arxiv_id": normalize_arxiv_id(raw_id)})
        return entries

    def _build_query(self, config: ImportTaskConfig) -> str:
        parts: List[str] = []
        if config.category_filter:
            parts.append(f"cat:{config.category_filter}")
        if config.text_filter:
            parts.append(config.text_filter)
        return " AND ".join(parts) or "all"

