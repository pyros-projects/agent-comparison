from __future__ import annotations

import json
import logging
from typing import List

import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

from .embeddings import EmbeddingService
from .llm import LLMService, LLMUnavailable
from .models import TheoryArgument, TheoryQueryRequest, TheoryResponse
from .storage import Storage

logger = logging.getLogger(__name__)


class TheoryService:
    def __init__(
        self,
        storage: Storage,
        embeddings: EmbeddingService,
        llm: LLMService,
    ) -> None:
        self.storage = storage
        self.embeddings = embeddings
        self.llm = llm

    async def run(self, request: TheoryQueryRequest) -> TheoryResponse:
        papers = [paper for paper in self.storage.list_papers() if paper.vector]
        if not papers:
            return TheoryResponse(
                hypothesis=request.hypothesis,
                llm_available=self.llm.available,
                message="No vectorized papers available yet.",
            )
        query_vec = await self.embeddings.embed(request.hypothesis)
        ranked = self._rank(papers, query_vec, request.top_k * 2)
        if not self.llm.available:
            return TheoryResponse(
                hypothesis=request.hypothesis,
                llm_available=False,
                pro=[],
                contra=[],
                message="Theory mode disabled until the LLM is reachable.",
            )
        context = "\n".join(
            f"[{paper.id}] {paper.title} :: {paper.abstract}" for paper, _ in ranked
        )
        system = "You split evidence into pro and contra JSON arrays."
        user = (
            "Hypothesis: {hypothesis}\n"
            "Provide JSON {pro:[{paper_id,title,relevance,argument,quotes}], contra:[...]}."
            f"Evidence:\n{context[:6000]}"
        ).format(hypothesis=request.hypothesis)
        try:
            raw = await self.llm.complete(system, user)
            payload = json.loads(raw)
        except (LLMUnavailable, json.JSONDecodeError) as exc:
            logger.warning("Theory mode using fallback", exc_info=exc)
            return TheoryResponse(
                hypothesis=request.hypothesis,
                llm_available=False,
                message="Unable to contact LLM for theory mode.",
            )
        pro = [TheoryArgument(**item) for item in payload.get("pro", [])]
        contra = [TheoryArgument(**item) for item in payload.get("contra", [])]
        return TheoryResponse(
            hypothesis=request.hypothesis,
            llm_available=True,
            pro=pro,
            contra=contra,
        )

    def _rank(self, papers, query_vec, limit):
        matrix = np.array([paper.vector for paper in papers])
        scores = cosine_similarity([query_vec], matrix)[0]
        scored = sorted(zip(papers, scores), key=lambda item: item[1], reverse=True)
        return scored[:limit]

