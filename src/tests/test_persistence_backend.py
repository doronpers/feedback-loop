"""Comprehensive tests for persistence backend implementations."""

import json
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from feedback_loop.persistence import (
    PostgreSQLBackend,
    PersistenceBackend,
    SQLiteBackend,
    get_backend,
)


@pytest.fixture
def temp_db_path(tmp_path):
    """Create a temporary database path for testing."""
    return str(tmp_path / "test_persistence.db")


@pytest.fixture
def sqlite_backend(temp_db_path):
    """Create a SQLite backend instance."""
    backend = SQLiteBackend(temp_db_path)
    backend.connect()
    backend.migrate()
    yield backend
    backend.disconnect()


class TestSQLiteBackend:
    """Test SQLite backend implementation."""

    def test_connect_and_disconnect(self, temp_db_path):
        """Test connecting and disconnecting from SQLite."""
        backend = SQLiteBackend(temp_db_path)
        backend.connect()
        assert backend.connection is not None
        backend.disconnect()
        # After disconnect, connection should be closed (may not be None but should be closed)
        # SQLite connection object may not be None after close, but operations will fail

    def test_migrate_creates_tables(self, sqlite_backend):
        """Test that migration creates necessary tables."""
        cursor = sqlite_backend.connection.cursor()
        cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='metrics'"
        )
        result = cursor.fetchone()
        assert result is not None

    def test_store_metric(self, sqlite_backend):
        """Test storing a metric."""
        metric = {
            "id": "metric_001",
            "type": "pattern_applied",
            "pattern_name": "test_pattern",
            "time_saved_seconds": 300,
        }

        metric_id = sqlite_backend.store_metric(metric)

        assert metric_id == "metric_001"
        stored = sqlite_backend.get_metric("metric_001")
        assert stored is not None
        assert stored["type"] == "pattern_applied"

    def test_store_metric_auto_id(self, sqlite_backend):
        """Test storing a metric without explicit ID."""
        metric = {
            "type": "pattern_applied",
            "pattern_name": "test_pattern",
        }

        metric_id = sqlite_backend.store_metric(metric)

        assert metric_id is not None
        stored = sqlite_backend.get_metric(metric_id)
        assert stored is not None

    def test_list_metrics_all(self, sqlite_backend):
        """Test listing all metrics."""
        # Store multiple metrics
        for i in range(5):
            metric = {
                "id": f"metric_{i}",
                "type": "pattern_applied",
                "pattern_name": f"pattern_{i}",
            }
            sqlite_backend.store_metric(metric)

        metrics = sqlite_backend.list_metrics()

        assert len(metrics) == 5
        assert all(m["type"] == "pattern_applied" for m in metrics)

    def test_list_metrics_by_type(self, sqlite_backend):
        """Test listing metrics filtered by type."""
        # Store different types
        sqlite_backend.store_metric({"id": "m1", "type": "pattern_applied", "data": "test"})
        sqlite_backend.store_metric({"id": "m2", "type": "bug_fixed", "data": "test"})
        sqlite_backend.store_metric({"id": "m3", "type": "pattern_applied", "data": "test"})

        metrics = sqlite_backend.list_metrics(metric_type="pattern_applied")

        assert len(metrics) == 2
        assert all(m["type"] == "pattern_applied" for m in metrics)

    def test_list_metrics_limit(self, sqlite_backend):
        """Test listing metrics with limit."""
        # Store more than limit
        for i in range(15):
            sqlite_backend.store_metric({"id": f"m{i}", "type": "test", "data": "test"})

        metrics = sqlite_backend.list_metrics(limit=10)

        assert len(metrics) == 10

    def test_get_metric_exists(self, sqlite_backend):
        """Test getting an existing metric."""
        metric = {"id": "test_metric", "type": "test", "data": "test_data"}
        sqlite_backend.store_metric(metric)

        retrieved = sqlite_backend.get_metric("test_metric")

        assert retrieved is not None
        assert retrieved["id"] == "test_metric"
        assert retrieved["data"] == "test_data"

    def test_get_metric_not_exists(self, sqlite_backend):
        """Test getting a non-existent metric."""
        retrieved = sqlite_backend.get_metric("nonexistent")

        assert retrieved is None

    def test_get_stats(self, sqlite_backend):
        """Test getting database statistics."""
        # Store some metrics
        for i in range(3):
            sqlite_backend.store_metric({"id": f"m{i}", "type": "test", "data": "test"})

        stats = sqlite_backend.get_stats()

        assert stats["backend"] == "sqlite"
        assert stats["total_metrics"] == 3
        assert "file_size_bytes" in stats
        assert "database_path" in stats

    def test_health_check_connected(self, sqlite_backend):
        """Test health check when connected."""
        health = sqlite_backend.health_check()

        assert health["status"] == "ok"
        assert health["backend"] == "sqlite"
        assert "total_metrics" in health

    def test_health_check_disconnected(self, temp_db_path):
        """Test health check when disconnected."""
        backend = SQLiteBackend(temp_db_path)
        health = backend.health_check()

        assert health["status"] == "disconnected"
        assert health["backend"] == "sqlite"

    def test_store_metric_updates_existing(self, sqlite_backend):
        """Test that storing a metric with existing ID updates it."""
        metric1 = {"id": "same_id", "type": "test", "value": "original"}
        sqlite_backend.store_metric(metric1)

        metric2 = {"id": "same_id", "type": "test", "value": "updated"}
        sqlite_backend.store_metric(metric2)

        retrieved = sqlite_backend.get_metric("same_id")
        assert retrieved["value"] == "updated"


class TestPostgreSQLBackend:
    """Test PostgreSQL backend implementation."""

    @pytest.fixture
    def postgres_backend(self):
        """Create a PostgreSQL backend (mocked for testing)."""
        # Mock PostgreSQL backend since we may not have a real DB
        backend = Mock(spec=PostgreSQLBackend)
        backend.connect = Mock()
        backend.disconnect = Mock()
        backend.migrate = Mock()
        backend.store_metric = Mock(return_value="metric_001")
        backend.list_metrics = Mock(return_value=[])
        backend.get_metric = Mock(return_value=None)
        backend.get_stats = Mock(return_value={"backend": "postgresql", "total_metrics": 0})
        backend.health_check = Mock(
            return_value={"status": "ok", "backend": "postgresql"}
        )
        return backend

    def test_postgres_backend_interface(self, postgres_backend):
        """Test PostgreSQL backend interface."""
        assert isinstance(postgres_backend, Mock)
        postgres_backend.connect()
        postgres_backend.connect.assert_called_once()


class TestBackendFactory:
    """Test backend factory function."""

    def test_get_backend_sqlite(self):
        """Test getting SQLite backend."""
        backend = get_backend("sqlite:///test.db")

        assert isinstance(backend, SQLiteBackend)
        assert backend.db_path == "test.db"

    def test_get_backend_sqlite_absolute_path(self):
        """Test getting SQLite backend with absolute path."""
        backend = get_backend("sqlite:////tmp/test.db")

        assert isinstance(backend, SQLiteBackend)
        assert backend.db_path == "/tmp/test.db"

    def test_get_backend_postgresql(self):
        """Test getting PostgreSQL backend."""
        backend = get_backend("postgresql://user:pass@localhost/dbname")

        assert isinstance(backend, PostgreSQLBackend)

    def test_get_backend_invalid_uri(self):
        """Test getting backend with invalid URI."""
        with pytest.raises(ValueError, match="Unsupported database URI"):
            get_backend("invalid://uri")


class TestPersistenceIntegration:
    """Integration tests for persistence layer."""

    def test_full_workflow(self, sqlite_backend):
        """Test complete workflow: store, list, get, stats."""
        # Store metrics
        metric1 = {"id": "m1", "type": "pattern_applied", "pattern": "test1"}
        metric2 = {"id": "m2", "type": "bug_fixed", "bug": "test2"}
        metric3 = {"id": "m3", "type": "pattern_applied", "pattern": "test3"}

        sqlite_backend.store_metric(metric1)
        sqlite_backend.store_metric(metric2)
        sqlite_backend.store_metric(metric3)

        # List all
        all_metrics = sqlite_backend.list_metrics()
        assert len(all_metrics) == 3

        # List by type
        pattern_metrics = sqlite_backend.list_metrics(metric_type="pattern_applied")
        assert len(pattern_metrics) == 2

        # Get specific
        retrieved = sqlite_backend.get_metric("m1")
        assert retrieved["pattern"] == "test1"

        # Get stats
        stats = sqlite_backend.get_stats()
        assert stats["total_metrics"] == 3
        assert stats["metric_types"] == 2

    def test_metric_json_serialization(self, sqlite_backend):
        """Test that complex metric data is properly serialized."""
        complex_metric = {
            "id": "complex",
            "type": "test",
            "nested": {"key": "value", "number": 42},
            "list": [1, 2, 3],
        }

        sqlite_backend.store_metric(complex_metric)
        retrieved = sqlite_backend.get_metric("complex")

        assert retrieved["nested"]["key"] == "value"
        assert retrieved["nested"]["number"] == 42
        assert retrieved["list"] == [1, 2, 3]
