from __future__ import annotations

import asyncio
import json
import logging
from typing import Any, Dict, Iterable, List

import litellm

from .config import settings
from .models import Paper, TheoryArgument

logger = logging.getLogger(__name__)


class LLMUnavailable(RuntimeError):
    """Raised when the primary LLM cannot be reached."""


class LLMService:
    def __init__(self) -> None:
        self._available = bool(settings.default_model and settings.enable_litellm)
        self._lock = asyncio.Lock()

    @property
    def available(self) -> bool:
        return self._available

    async def complete(self, system_prompt: str, user_prompt: str) -> str:
        if not self._available:
            raise LLMUnavailable("LLM not configured")
        try:
            response = await litellm.acompletion(
                model=settings.default_model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=0.2,
            )
        except Exception as exc:  # noqa: BLE001
            logger.error("LLM call failed", exc_info=exc)
            self._available = False
            raise LLMUnavailable from exc
        text = response["choices"][0]["message"]["content"].strip()
        return text

    async def summarize_paper(self, paper: Paper) -> dict[str, str]:
        system = "You are an expert AI research analyst who writes JSON summaries."
        user = (
            "Provide a JSON object with keys summary, methodology, results, further_work, keywords.\n"
            f"Title: {paper.title}\nAuthors: {', '.join(paper.authors)}\n"
            f"Abstract: {paper.abstract}\nFull text (truncated): {paper.content[:4000]}"
        )
        try:
            raw = await self.complete(system, user)
            data = json.loads(raw)
        except (LLMUnavailable, json.JSONDecodeError):
            return {
                "summary": "<summary>",
                "methodology": "<methodology>",
                "results": "<results>",
                "further_work": "<further_work>",
                "keywords": [],
            }
        keywords = data.get("keywords") or []
        if isinstance(keywords, str):
            keywords = [kw.strip() for kw in keywords.split(",") if kw.strip()]
        return {
            "summary": data.get("summary", "<summary>"),
            "methodology": data.get("methodology", "<methodology>"),
            "results": data.get("results", "<results>"),
            "further_work": data.get("further_work", "<further_work>"),
            "keywords": keywords,
        }

    async def theory_arguments(
        self,
        hypothesis: str,
        papers: Iterable[Paper],
        side: str,
    ) -> List[TheoryArgument]:
        text_blob = "\n".join(
            f"[{paper.id}] {paper.title} :: {paper.abstract}" for paper in papers
        )
        system = "You summarize research evidence as structured JSON."
        user = (
            "Hypothesis: {hypothesis}\n"
            f"Side: {side}\n"
            "Return JSON list with objects {paper_id, argument, relevance, quotes}."
            f"Evidence:\n{text_blob[:7000]}"
        )
        try:
            raw = await self.complete(system, user)
            payload = json.loads(raw)
        except (LLMUnavailable, json.JSONDecodeError):
            return []
        arguments: List[TheoryArgument] = []
        for item in payload:
            try:
                arguments.append(
                    TheoryArgument(
                        paper_id=item.get("paper_id"),
                        title=item.get("title", ""),
                        relevance=float(item.get("relevance", 0.0)),
                        argument=item.get("argument", ""),
                        quotes=item.get("quotes", []),
                    )
                )
            except Exception:  # noqa: BLE001
                continue
        return arguments

    def placeholder_theory(self, hypothesis: str) -> dict[str, Any]:
        return {
            "hypothesis": hypothesis,
            "llm_available": False,
            "message": "Theory mode temporarily disabled because the primary LLM is unavailable.",
            "pro": [],
            "contra": [],
        }

