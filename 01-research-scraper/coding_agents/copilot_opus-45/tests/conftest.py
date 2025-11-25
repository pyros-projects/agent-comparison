"""Test fixtures for PaperTrail tests."""

import os
import tempfile
from pathlib import Path
from typing import Generator
from unittest.mock import MagicMock

import pytest
from fastapi.testclient import TestClient

# Set test environment variables before imports
os.environ["PAPERTRAIL_DATA_DIR"] = tempfile.mkdtemp()


@pytest.fixture
def temp_data_dir(tmp_path: Path) -> Generator[Path, None, None]:
    """Create a temporary data directory for tests."""
    from researcher.config import Config
    
    original_dir = Config.DATA_DIR
    Config.DATA_DIR = tmp_path
    
    yield tmp_path
    
    Config.DATA_DIR = original_dir


@pytest.fixture
def test_client(temp_data_dir: Path) -> Generator[TestClient, None, None]:
    """Create a test client for the FastAPI app."""
    from researcher.api.app import app
    
    with TestClient(app) as client:
        yield client


@pytest.fixture
def mock_llm_service() -> MagicMock:
    """Create a mock LLM service."""
    mock = MagicMock()
    mock.is_available.return_value = False
    mock.generate_summary.return_value = "<summary>"
    mock.extract_keywords.return_value = []
    mock.analyze_theory.return_value = {
        "pro_arguments": [],
        "contra_arguments": [],
        "analysis_summary": "",
    }
    return mock


@pytest.fixture
def sample_paper_data() -> dict:
    """Return sample paper data for testing."""
    return {
        "arxiv_id": "2301.00000",
        "title": "Test Paper: A Study of Testing",
        "authors": ["Alice Author", "Bob Builder"],
        "abstract": "This is a test abstract for testing purposes.",
        "categories": ["cs.AI", "cs.LG"],
        "primary_category": "cs.AI",
        "pdf_url": "https://arxiv.org/pdf/2301.00000.pdf",
        "published": "2023-01-01T00:00:00",
        "updated": "2023-01-02T00:00:00",
    }


@pytest.fixture
def sample_paper(sample_paper_data: dict):
    """Create a sample Paper model."""
    from researcher.models import Paper
    
    return Paper(
        id="test-paper-1",
        **sample_paper_data,
        full_text="This is the full text of the paper.",
        summary="This is a summary.",
        keywords=["testing", "research"],
        embedding=[0.1] * 384,
        status="new",
    )
