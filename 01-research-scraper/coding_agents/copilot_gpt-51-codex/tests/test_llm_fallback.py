import datetime as dt

import pytest

from researcher.llm import LLMService
from researcher.models import Paper


def build_paper() -> Paper:
    return Paper(
        arxiv_id="1234.5678",
        title="Fallback Paper",
        authors=["Tester"],
        abstract="Abstract",
        categories=["cs.CL"],
        pdf_url="https://arxiv.org/pdf/1234.5678.pdf",
        published_at=dt.datetime.now(dt.timezone.utc),
        content="body",
    )


@pytest.mark.asyncio
async def test_llm_returns_placeholders_when_unavailable():
    service = LLMService()
    paper = build_paper()

    result = await service.summarize_paper(paper)

    assert result["summary"].startswith("<")
    assert result["methodology"].startswith("<")
