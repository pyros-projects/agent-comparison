"""Tests for database service - Model validation tests."""

import pytest
from datetime import datetime, timezone

from researcher.models import Paper, PaperStatus


class TestDatabaseService:
    """Test cases for Paper model and database operations."""

    def test_paper_model_creation(self):
        """Test creating a Paper model."""
        paper = Paper(
            id="test-1",
            arxiv_id="2301.00001",
            title="Test Paper",
            authors=["Author One"],
            abstract="Test abstract",
            categories=["cs.AI"],
            primary_category="cs.AI",
            pdf_url="https://arxiv.org/pdf/2301.00001.pdf",
            published=datetime.now(timezone.utc),
            status=PaperStatus.NEW,
        )
        
        assert paper.id == "test-1"
        assert paper.title == "Test Paper"
        assert paper.arxiv_id == "2301.00001"
        assert paper.status == PaperStatus.NEW

    def test_paper_status_values(self):
        """Test PaperStatus enum values."""
        assert PaperStatus.NEW.value == "new"
        assert PaperStatus.READ.value == "read"
        assert PaperStatus.STARRED.value == "starred"

    def test_paper_defaults(self):
        """Test Paper model defaults."""
        paper = Paper(
            id="test-2",
            arxiv_id="2301.00002",
            title="Test Paper 2",
            authors=[],
            abstract="",
            categories=[],
            primary_category="",
            pdf_url="",
        )
        
        assert paper.summary == ""
        assert paper.keywords == []
        assert paper.status == PaperStatus.NEW
        assert paper.notes == ""
        assert paper.manual_tags == []
        assert paper.has_placeholder_summary is False
        assert paper.has_placeholder_keywords is False
        assert paper.has_embedding is False

    def test_paper_serialization(self):
        """Test Paper model serialization."""
        paper = Paper(
            id="test-3",
            arxiv_id="2301.00003",
            title="Serialization Test",
            authors=["Alice", "Bob"],
            abstract="Test abstract",
            categories=["cs.AI", "cs.LG"],
            primary_category="cs.AI",
            pdf_url="https://arxiv.org/pdf/2301.00003.pdf",
            summary="Test summary",
            keywords=["test", "keywords"],
            status=PaperStatus.STARRED,
        )
        
        data = paper.model_dump()
        
        assert data["id"] == "test-3"
        assert data["title"] == "Serialization Test"
        assert data["authors"] == ["Alice", "Bob"]
        assert data["status"] == "starred"

    def test_paper_from_dict(self):
        """Test creating Paper from dict."""
        data = {
            "id": "test-4",
            "arxiv_id": "2301.00004",
            "title": "From Dict Test",
            "authors": ["Charlie"],
            "abstract": "Dict abstract",
            "categories": ["cs.CV"],
            "primary_category": "cs.CV",
            "pdf_url": "https://arxiv.org/pdf/2301.00004.pdf",
            "status": "read",
        }
        
        paper = Paper(**data)
        
        assert paper.id == "test-4"
        assert paper.status == PaperStatus.READ

    def test_paper_update_status(self):
        """Test updating paper status."""
        paper = Paper(
            id="test-5",
            arxiv_id="2301.00005",
            title="Status Test",
            authors=[],
            abstract="",
            categories=[],
            primary_category="",
            pdf_url="",
        )
        
        assert paper.status == PaperStatus.NEW
        
        paper.status = PaperStatus.READ
        assert paper.status == PaperStatus.READ
        
        paper.status = PaperStatus.STARRED
        assert paper.status == PaperStatus.STARRED

    def test_paper_placeholder_flags(self):
        """Test placeholder tracking flags."""
        paper = Paper(
            id="test-6",
            arxiv_id="2301.00006",
            title="Placeholder Test",
            authors=[],
            abstract="",
            categories=[],
            primary_category="",
            pdf_url="",
            summary="<summary>",
            has_placeholder_summary=True,
            keywords=[],
            has_placeholder_keywords=True,
        )
        
        assert paper.has_placeholder_summary is True
        assert paper.has_placeholder_keywords is True

    def test_paper_notes_and_tags(self):
        """Test paper notes and manual tags."""
        paper = Paper(
            id="test-7",
            arxiv_id="2301.00007",
            title="Notes Test",
            authors=[],
            abstract="",
            categories=[],
            primary_category="",
            pdf_url="",
            notes="My research notes",
            manual_tags=["important", "review-later"],
        )
        
        assert paper.notes == "My research notes"
        assert "important" in paper.manual_tags
        assert "review-later" in paper.manual_tags
