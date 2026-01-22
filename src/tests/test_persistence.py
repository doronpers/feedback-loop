"""
Unit tests for persistence backends and configuration.

Tests cover:
- SQLite backend operations (CRUD, migrations, health checks)
- PostgreSQL backend configuration (mock)
- Config module with environment variable loading
- Backend factory pattern
"""

import json
import os
import sqlite3
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, Mock, patch

import pytest

from feedback_loop.config import APIConfig, DatabaseConfig, FeedbackLoopConfig, DatabaseType
from feedback_loop.persistence import (
    PersistenceBackend,
    SQLiteBackend,
    PostgreSQLBackend,
    get_backend,
)


# ============================================================================
# Test Fixtures
# ============================================================================


@pytest.fixture
def temp_db_path(tmp_path):
    """Create a temporary database file path."""
    db_path = tmp_path / "test.db"
    return str(db_path)


@pytest.fixture
def sqlite_backend(temp_db_path):
    """Create a SQLite backend with temporary database."""
    # Pass the path directly without the sqlite:/// prefix
    backend = SQLiteBackend(temp_db_path)
    backend.connect()
    backend.migrate()
    yield backend
    backend.disconnect()


# ============================================================================
# Configuration Tests
# ============================================================================


class TestDatabaseConfig:
    """Test DatabaseConfig Pydantic model."""

    def test_sqlite_config_defaults(self):
        """Test SQLite config with default values."""
        config = DatabaseConfig(type=DatabaseType.SQLITE)
        assert config.type == DatabaseType.SQLITE
        assert config.auto_migrate is True
        assert config.pool_size == 5
        assert config.uri.startswith("sqlite:///")

    def test_sqlite_config_custom_path(self):
        """Test SQLite config with custom path."""
        config = DatabaseConfig(
            type=DatabaseType.SQLITE,
            path=Path("/tmp/custom_metrics.db")
        )
        assert isinstance(config.path, Path)
        assert config.uri.startswith("sqlite:///")

    def test_postgresql_config(self):
        """Test PostgreSQL config."""
        config = DatabaseConfig(
            type=DatabaseType.POSTGRESQL,
            uri="postgresql://user:pass@localhost/db"
        )
        assert config.type == DatabaseType.POSTGRESQL
        assert "postgresql" in config.uri

    def test_database_config_from_dict(self):
        """Test creating config from dict."""
        data = {
            "type": "sqlite",
            "path": "/tmp/metrics_test.db",
            "auto_migrate": True,
            "pool_size": 10
        }
        config = DatabaseConfig(**data)
        assert config.pool_size == 10


class TestAPIConfig:
    """Test APIConfig Pydantic model."""

    def test_api_config_defaults(self):
        """Test API config with default values."""
        config = APIConfig()
        assert config.port == 8000
        assert config.debug is False
        assert config.log_level == "INFO"

    def test_api_config_from_dict(self):
        """Test creating API config from dict."""
        data = {
            "host": "0.0.0.0",
            "port": 9000,
            "debug": True,
            "log_level": "DEBUG"
        }
        config = APIConfig(**data)
        assert config.host == "0.0.0.0"
        assert config.port == 9000


class TestFeedbackLoopConfig:
    """Test FeedbackLoopConfig main config class."""

    def test_from_env_sqlite_defaults(self, monkeypatch):
        """Test loading from environment with SQLite defaults."""
        for key in ["FL_DB_TYPE", "FL_DB_URI", "FL_DB_PATH"]:
            monkeypatch.delenv(key, raising=False)

        config = FeedbackLoopConfig.from_env()
        assert config.database.type == DatabaseType.SQLITE
        assert config.database.auto_migrate is True

    def test_from_env_custom_db_type(self, monkeypatch):
        """Test loading custom database type from environment."""
        monkeypatch.setenv("FL_DB_TYPE", "postgresql")
        monkeypatch.setenv("FL_DB_URI", "postgresql://localhost/test")

        config = FeedbackLoopConfig.from_env()
        assert config.database.type == DatabaseType.POSTGRESQL

    def test_get_db_uri(self):
        """Test getting database URI."""
        config = FeedbackLoopConfig(
            database=DatabaseConfig(
                type=DatabaseType.SQLITE,
                path=Path("/tmp/test_metrics.db")
            )
        )
        uri = config.get_db_uri()
        assert uri.startswith("sqlite:///")


# ============================================================================
# SQLite Backend Tests
# ============================================================================


class TestSQLiteBackend:
    """Test SQLite persistence backend."""

    def test_backend_initialization(self, sqlite_backend):
        """Test backend connects and creates schema."""
        assert sqlite_backend is not None

    def test_backend_health_check(self, sqlite_backend):
        """Test health check returns diagnostics."""
        health = sqlite_backend.health_check()
        assert health["status"] == "ok"
        assert health["backend"] == "sqlite"
        assert "total_metrics" in health
        assert health["total_metrics"] == 0

    def test_store_metric(self, sqlite_backend):
        """Test storing a metric."""
        metric_data = {"id": "test_1", "type": "test_metric", "value": 42}
        sqlite_backend.store_metric(metric_data)

        health = sqlite_backend.health_check()
        assert health["total_metrics"] == 1

    def test_store_multiple_metrics(self, sqlite_backend):
        """Test storing multiple metrics."""
        for i in range(5):
            metric_data = {"id": f"counter_{i}", "type": "counter_metric", "value": i}
            sqlite_backend.store_metric(metric_data)

        health = sqlite_backend.health_check()
        assert health["total_metrics"] == 5

    def test_list_metrics(self, sqlite_backend):
        """Test listing metrics by type."""
        sqlite_backend.store_metric({"id": "a1", "type": "type_a", "data": "a1"})
        sqlite_backend.store_metric({"id": "b1", "type": "type_b", "data": "b1"})
        sqlite_backend.store_metric({"id": "a2", "type": "type_a", "data": "a2"})

        type_a_metrics = sqlite_backend.list_metrics(metric_type="type_a")
        assert len(type_a_metrics) == 2

        type_b_metrics = sqlite_backend.list_metrics(metric_type="type_b")
        assert len(type_b_metrics) == 1

    def test_get_metric(self, sqlite_backend):
        """Test retrieving specific metrics."""
        stored_data = {"id": "test_id", "type": "named_metric", "value": 99}
        sqlite_backend.store_metric(stored_data)

        metrics = sqlite_backend.list_metrics(metric_type="named_metric")
        assert len(metrics) > 0
        assert metrics[0]["type"] == "named_metric"
        assert metrics[0]["value"] == 99

    def test_get_stats(self, sqlite_backend):
        """Test getting statistics."""
        for i in range(3):
            sqlite_backend.store_metric({"id": f"stat_{i}", "type": "stat_metric", "iteration": i})

        stats = sqlite_backend.get_stats()
        assert "total_metrics" in stats
        assert stats["total_metrics"] == 3

    def test_metric_data_is_json_serializable(self, sqlite_backend):
        """Test that stored data remains JSON-serializable."""
        complex_data = {
            "id": "complex_1",
            "type": "complex",
            "nested": {"values": [1, 2, 3]},
            "timestamp": "2024-01-01T00:00:00Z",
            "flag": True
        }
        sqlite_backend.store_metric(complex_data)

        metrics = sqlite_backend.list_metrics(metric_type="complex")
        assert len(metrics) > 0
        # The returned metric should have the same structure as stored
        assert metrics[0]["nested"]["values"] == [1, 2, 3]

    def test_backend_disconnect(self, sqlite_backend):
        """Test backend disconnects cleanly."""
        sqlite_backend.disconnect()


class TestPostgreSQLBackend:
    """Test PostgreSQL backend configuration (mock)."""

    def test_backend_methods_exist(self):
        """Test that required methods exist."""
        uri = "postgresql://user:pass@localhost/db"
        try:
            backend = PostgreSQLBackend(uri)
            assert hasattr(backend, "connect")
            assert hasattr(backend, "disconnect")
            assert hasattr(backend, "migrate")
            assert hasattr(backend, "store_metric")
            assert hasattr(backend, "list_metrics")
            assert hasattr(backend, "get_stats")
            assert hasattr(backend, "health_check")
        except ImportError:
            pytest.skip("sqlalchemy not installed")


# ============================================================================
# Backend Factory Tests
# ============================================================================


class TestBackendFactory:
    """Test persistence backend factory."""

    def test_factory_creates_sqlite_backend(self, temp_db_path):
        """Test factory creates SQLite backend from URI."""
        uri = f"sqlite:///{temp_db_path}"
        backend = get_backend(uri)
        assert isinstance(backend, SQLiteBackend)
        # The backend should have the correct path
        assert backend.db_path == temp_db_path

    def test_factory_raises_on_unknown_scheme(self):
        """Test factory raises on unknown database scheme."""
        with pytest.raises(ValueError, match="Unsupported database"):
            get_backend("unknown://localhost/db")


# ============================================================================
# Integration Tests
# ============================================================================


class TestPersistenceIntegration:
    """Integration tests for persistence layer."""

    def test_workflow_store_and_retrieve(self, sqlite_backend):
        """Test complete workflow: store metric and retrieve it."""
        metric = {"id": "user_123", "type": "user_action", "action": "pattern_applied", "success": True}
        sqlite_backend.store_metric(metric)

        metrics = sqlite_backend.list_metrics(metric_type="user_action")
        assert len(metrics) == 1
        # The retrieved metric should have the same structure as stored
        assert metrics[0]["success"] is True
        assert metrics[0]["action"] == "pattern_applied"

    def test_workflow_config_to_backend(self, temp_db_path):
        """Test workflow: config -> backend creation -> store -> health check."""
        config = FeedbackLoopConfig(
            database=DatabaseConfig(
                type=DatabaseType.SQLITE,
                path=Path(temp_db_path)
            )
        )

        uri = config.get_db_uri()
        backend = get_backend(uri)
        backend.connect()
        backend.migrate()

        backend.store_metric({"id": "wf1", "type": "workflow_test", "value": "success"})

        health = backend.health_check()
        assert health["status"] == "ok"
        assert health["total_metrics"] == 1

        backend.disconnect()

    def test_persistence_abstraction(self, sqlite_backend):
        """Test that backend implements full PersistenceBackend interface."""
        assert isinstance(sqlite_backend, PersistenceBackend)

        required_methods = [
            "connect",
            "disconnect",
            "migrate",
            "store_metric",
            "list_metrics",
            "get_stats",
            "health_check",
        ]

        for method in required_methods:
            assert hasattr(sqlite_backend, method)
            assert callable(getattr(sqlite_backend, method))


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
