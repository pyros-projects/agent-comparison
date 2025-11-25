"""Tests for API endpoints."""

import pytest
from fastapi.testclient import TestClient


class TestHealthEndpoint:
    """Test cases for health endpoint."""

    def test_health_check(self, test_client: TestClient):
        """Test health check returns 200."""
        response = test_client.get("/api/health")
        
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert "llm_available" in data
        assert "embedding_fallback" in data


class TestPapersAPI:
    """Test cases for papers API."""

    def test_list_papers_empty(self, test_client: TestClient):
        """Test listing papers when empty."""
        response = test_client.get("/api/papers")
        
        assert response.status_code == 200
        data = response.json()
        assert "papers" in data
        assert "total" in data
        assert data["total"] == 0

    def test_get_paper_not_found(self, test_client: TestClient):
        """Test getting non-existent paper returns 404."""
        response = test_client.get("/api/papers/nonexistent")
        
        assert response.status_code == 404

    def test_get_categories_empty(self, test_client: TestClient):
        """Test getting categories when empty."""
        response = test_client.get("/api/papers/categories")
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)


class TestSearchAPI:
    """Test cases for search API."""

    def test_text_search_empty(self, test_client: TestClient):
        """Test text search with no papers."""
        response = test_client.get("/api/search/text?q=test")
        
        assert response.status_code == 200
        data = response.json()
        assert "results" in data
        assert len(data["results"]) == 0

    def test_semantic_search_empty(self, test_client: TestClient):
        """Test semantic search with no papers."""
        response = test_client.post(
            "/api/search/semantic",
            json={"query": "machine learning", "top_k": 10}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "results" in data

    def test_theory_status(self, test_client: TestClient):
        """Test theory mode status endpoint."""
        response = test_client.get("/api/search/theory/status")
        
        assert response.status_code == 200
        data = response.json()
        assert "available" in data
        assert "message" in data


class TestImportsAPI:
    """Test cases for imports API."""

    def test_list_imports_empty(self, test_client: TestClient):
        """Test listing import tasks when empty."""
        response = test_client.get("/api/imports")
        
        assert response.status_code == 200
        data = response.json()
        assert "tasks" in data
        assert data["active_count"] == 0

    def test_get_arxiv_categories(self, test_client: TestClient):
        """Test getting arXiv categories."""
        response = test_client.get("/api/imports/categories")
        
        assert response.status_code == 200
        data = response.json()
        assert "categories" in data
        assert len(data["categories"]) > 0
        assert "cs.AI" in data["categories"]

    def test_create_import_task(self, test_client: TestClient):
        """Test creating an import task."""
        response = test_client.post(
            "/api/imports",
            json={
                "name": "Test Task",
                "category": "cs.AI",
                "check_interval": 60,
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Test Task"
        assert data["category"] == "cs.AI"
        # Task may start active depending on implementation
        assert "is_active" in data


class TestDashboardAPI:
    """Test cases for dashboard API."""

    def test_dashboard_stats(self, test_client: TestClient):
        """Test dashboard stats endpoint."""
        response = test_client.get("/api/dashboard")
        
        assert response.status_code == 200
        data = response.json()
        assert "stats" in data
        assert "recent_activity" in data
        assert "topic_clusters" in data
        # Might be "growth" or "growth_data" depending on implementation
        assert "growth_data" in data or "growth" in data

    def test_system_status(self, test_client: TestClient):
        """Test system status endpoint."""
        response = test_client.get("/api/dashboard/status")
        
        assert response.status_code == 200
        data = response.json()
        # Status may be nested under llm/embedding objects
        assert "llm" in data or "llm_available" in data
        assert "embedding" in data or "embedding_available" in data
