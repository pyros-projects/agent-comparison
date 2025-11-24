from __future__ import annotations

import datetime as dt
from pathlib import Path
from typing import Iterable, Optional

from tinydb import Query, TinyDB

from .models import ImportTaskConfig, Note, Paper, PaperStatus, SearchQuery


class Storage:
    """TinyDB-backed persistence helper."""

    def __init__(self, db_path: Path) -> None:
        self.db = TinyDB(db_path, ensure_ascii=True)
        self.papers = self.db.table("papers")
        self.tasks = self.db.table("tasks")
        self.activity = self.db.table("activity")

    # Paper helpers -----------------------------------------------------
    def upsert_paper(self, paper: Paper) -> Paper:
        self.papers.upsert(paper.model_dump(mode="json"), Query().id == paper.id)
        self.activity.insert(
            {
                "ts": dt.datetime.now(dt.timezone.utc).isoformat(),
                "type": "paper",
                "paper_id": paper.id,
                "title": paper.title,
            }
        )
        return paper

    def get_paper_by_arxiv(self, arxiv_id: str) -> Optional[Paper]:
        row = self.papers.get(Query().arxiv_id == arxiv_id)
        return Paper.model_validate(row) if row else None

    def get_paper(self, paper_id: str) -> Optional[Paper]:
        row = self.papers.get(Query().id == paper_id)
        return Paper.model_validate(row) if row else None

    def list_papers(self) -> Iterable[Paper]:
        for row in self.papers.all():
            yield Paper.model_validate(row)

    def search(self, params: SearchQuery) -> tuple[list[Paper], int]:
        rows = self.papers.all()
        items: list[Paper] = []
        for row in rows:
            paper = Paper.model_validate(row)
            if params.category and params.category not in paper.categories:
                continue
            if params.status and paper.status != params.status:
                continue
            if params.starred is not None and paper.starred != params.starred:
                continue
            if params.text:
                blob = " ".join([paper.title, paper.abstract, paper.summary]).lower()
                if params.text.lower() not in blob:
                    continue
            items.append(paper)
        total = len(items)
        sliced = items[params.offset: params.offset + params.limit]
        return (sliced, total)

    def update_paper_status(
        self,
        paper_id: str,
        *,
        status: PaperStatus | None = None,
        starred: bool | None = None,
    ) -> Paper:
        paper = self.get_paper(paper_id)
        if not paper:
            raise KeyError(paper_id)
        if status:
            paper.status = status
        if starred is not None:
            paper.starred = starred
        paper.updated_at = dt.datetime.now(dt.timezone.utc)
        self.upsert_paper(paper)
        return paper

    def add_note(self, paper_id: str, text: str) -> Paper:
        paper = self.get_paper(paper_id)
        if not paper:
            raise KeyError(paper_id)
        paper.notes.append(
            Note(
                created_at=dt.datetime.now(dt.timezone.utc),
                text=text,
            )
        )
        paper.updated_at = dt.datetime.now(dt.timezone.utc)
        self.upsert_paper(paper)
        return paper

    # Task helpers ------------------------------------------------------
    def upsert_task(self, task: ImportTaskConfig) -> ImportTaskConfig:
        self.tasks.upsert(task.model_dump(mode="json"), Query().id == task.id)
        return task

    def get_task(self, task_id: str) -> Optional[ImportTaskConfig]:
        row = self.tasks.get(Query().id == task_id)
        return ImportTaskConfig.model_validate(row) if row else None

    def list_tasks(self) -> list[ImportTaskConfig]:
        return [ImportTaskConfig.model_validate(row) for row in self.tasks.all()]

    # Dashboard ---------------------------------------------------------
    def build_dashboard(self) -> dict:
        rows = list(self.list_papers())
        categories: dict[str, int] = {}
        starred = 0
        read = 0
        for paper in rows:
            for cat in paper.categories:
                categories[cat] = categories.get(cat, 0) + 1
            if paper.starred:
                starred += 1
            if paper.status == PaperStatus.READ:
                read += 1
        activity = self.activity.all()[-50:]
        return {
            "total_papers": len(rows),
            "starred": starred,
            "read": read,
            "categories": categories,
            "recent_activity": activity,
            "tasks": self.list_tasks(),
        }

