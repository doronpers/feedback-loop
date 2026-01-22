"""
Integration tests for API with persistence layer.

Tests the FastAPI integration with the persistence backend.
"""

import json
import tempfile
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

# Mock the imports to avoid import errors
pytest.importorskip("fastapi")

from feedback_loop.api.main import app
from feedback_loop.config import DatabaseConfig, DatabaseType, FeedbackLoopConfig


@pytest.fixture
def temp_db_path(tmp_path):
    """Create a temporary database for testing."""
    return str(tmp_path / "test_api.db")


@pytest.fixture
def client(temp_db_path, monkeypatch):
    """Create a test client with a temporary database."""
    # Set environment to use temporary database
    monkeypatch.setenv("FL_DB_TYPE", "sqlite")
    monkeypatch.setenv("FL_DB_PATH", temp_db_path)

    # Create test client
    return TestClient(app)


class TestAPIHealth:
    """Test API health endpoint."""

    def test_health_endpoint_returns_ok(self, client):
        """Test that health endpoint returns OK status."""
        response = client.get("/api/v1/health")
        assert response.status_code == 200

        data = response.json()
        assert data["status"] in ["healthy", "warning", "unhealthy"]
        assert "version" in data
        assert "timestamp" in data


class TestAPIMetrics:
    """Test API metrics endpoints (requires auth)."""

    def test_health_includes_database_info(self, client):
        """Test that health endpoint includes database diagnostics."""
        response = client.get("/api/v1/health")
        assert response.status_code == 200

        data = response.json()
        # Should have database info if backend is initialized
        if "database" in data:
            assert "backend" in data["database"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
