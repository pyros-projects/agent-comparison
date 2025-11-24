from __future__ import annotations

import asyncio
import logging
from typing import List

import litellm
from sentence_transformers import SentenceTransformer

from .config import settings

logger = logging.getLogger(__name__)


class EmbeddingService:
    """Handles semantic vector generation with fallback support."""

    def __init__(self) -> None:
        self._hf_model: SentenceTransformer | None = None
        self.provider: str | None = None

    async def embed(self, text: str) -> List[float]:
        if not text.strip():
            return []
        if settings.enable_litellm and settings.default_embedding_model:
            try:
                response = await litellm.aembedding(
                    model=settings.default_embedding_model,
                    input=text,
                )
                data = response["data"][0]["embedding"]
                self.provider = settings.default_embedding_model
                return list(map(float, data))
            except Exception as exc:  # noqa: BLE001
                logger.warning("litellm embedding failed, falling back", exc_info=exc)
        if settings.enable_sentence_transformers:
            return await asyncio.to_thread(self._hf_infer, text)
        raise RuntimeError("No embedding backend available")

    def _hf_infer(self, text: str) -> List[float]:
        if not self._hf_model:
            self._hf_model = SentenceTransformer("all-MiniLM-L6-v2")
            self.provider = "all-MiniLM-L6-v2"
        vector = self._hf_model.encode(text)
        return vector.tolist()

    async def embed_many(self, texts: list[str]) -> list[list[float]]:
        results: list[list[float]] = []
        for text in texts:
            results.append(await self.embed(text))
        return results

