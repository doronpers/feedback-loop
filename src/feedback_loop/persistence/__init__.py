"""
Persistence Layer

Abstract interface and implementations for storing and retrieving metrics.
Supports SQLite (development) and PostgreSQL (production).
"""

import json
import logging
from abc import ABC, abstractmethod
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class PersistenceBackend(ABC):
    """Abstract base class for persistence backends."""

    @abstractmethod
    def connect(self) -> None:
        """Connect to the database."""
        pass

    @abstractmethod
    def disconnect(self) -> None:
        """Disconnect from the database."""
        pass

    @abstractmethod
    def migrate(self) -> None:
        """Run database migrations (create tables, etc)."""
        pass

    @abstractmethod
    def store_metric(self, metric: Dict[str, Any]) -> str:
        """Store a metric and return its ID.

        Args:
            metric: Metric data dictionary

        Returns:
            ID of stored metric
        """
        pass

    @abstractmethod
    def list_metrics(
        self, metric_type: Optional[str] = None, limit: int = 100
    ) -> List[Dict[str, Any]]:
        """List metrics.

        Args:
            metric_type: Filter by metric type (optional)
            limit: Maximum number of metrics to return

        Returns:
            List of metric dictionaries
        """
        pass

    @abstractmethod
    def get_metric(self, metric_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific metric by ID.

        Args:
            metric_id: Metric ID

        Returns:
            Metric dictionary or None if not found
        """
        pass

    @abstractmethod
    def get_stats(self) -> Dict[str, Any]:
        """Get database statistics.

        Returns:
            Dictionary with stats (row counts, etc)
        """
        pass

    @abstractmethod
    def health_check(self) -> Dict[str, Any]:
        """Check database health and return diagnostics.

        Returns:
            Health status dictionary
        """
        pass


class SQLiteBackend(PersistenceBackend):
    """SQLite persistence backend (for development and small deployments)."""

    def __init__(self, db_path: str):
        """Initialize SQLite backend.

        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = db_path
        self.connection = None

    def connect(self) -> None:
        """Connect to SQLite database."""
        import sqlite3

        try:
            self.connection = sqlite3.connect(self.db_path)
            self.connection.row_factory = sqlite3.Row
            logger.info(f"Connected to SQLite database: {self.db_path}")
        except Exception as e:
            logger.error(f"Failed to connect to SQLite: {e}")
            raise

    def disconnect(self) -> None:
        """Disconnect from SQLite database."""
        if self.connection:
            self.connection.close()
            logger.info("Disconnected from SQLite database")

    def migrate(self) -> None:
        """Create tables if they don't exist."""
        if not self.connection:
            raise RuntimeError("Not connected to database")

        cursor = self.connection.cursor()

        # Create metrics table
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS metrics (
                id TEXT PRIMARY KEY,
                type TEXT NOT NULL,
                data JSON NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """
        )

        # Create index for faster queries
        cursor.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_metrics_type
            ON metrics(type)
        """
        )

        self.connection.commit()
        logger.info("Database migration completed")

    def store_metric(self, metric: Dict[str, Any]) -> str:
        """Store a metric in SQLite.

        Args:
            metric: Metric data dictionary (must have 'id' and 'type')

        Returns:
            ID of stored metric
        """
        if not self.connection:
            raise RuntimeError("Not connected to database")

        metric_id = metric.get("id", str(datetime.utcnow().timestamp()))
        metric_type = metric.get("type", "unknown")
        metric_data = json.dumps(metric)

        cursor = self.connection.cursor()
        cursor.execute(
            """
            INSERT OR REPLACE INTO metrics (id, type, data, updated_at)
            VALUES (?, ?, ?, CURRENT_TIMESTAMP)
        """,
            (metric_id, metric_type, metric_data),
        )
        self.connection.commit()

        logger.debug(f"Stored metric {metric_id} ({metric_type})")
        return metric_id

    def list_metrics(
        self, metric_type: Optional[str] = None, limit: int = 100
    ) -> List[Dict[str, Any]]:
        """List metrics from SQLite.

        Args:
            metric_type: Filter by metric type (optional)
            limit: Maximum number of metrics to return

        Returns:
            List of metric dictionaries
        """
        if not self.connection:
            raise RuntimeError("Not connected to database")

        cursor = self.connection.cursor()

        if metric_type:
            cursor.execute(
                """
                SELECT data FROM metrics
                WHERE type = ?
                ORDER BY created_at DESC
                LIMIT ?
            """,
                (metric_type, limit),
            )
        else:
            cursor.execute(
                """
                SELECT data FROM metrics
                ORDER BY created_at DESC
                LIMIT ?
            """,
                (limit,),
            )

        rows = cursor.fetchall()
        return [json.loads(row[0]) for row in rows]

    def get_metric(self, metric_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific metric by ID.

        Args:
            metric_id: Metric ID

        Returns:
            Metric dictionary or None if not found
        """
        if not self.connection:
            raise RuntimeError("Not connected to database")

        cursor = self.connection.cursor()
        cursor.execute("SELECT data FROM metrics WHERE id = ?", (metric_id,))
        row = cursor.fetchone()

        if row:
            return json.loads(row[0])
        return None

    def get_stats(self) -> Dict[str, Any]:
        """Get database statistics.

        Returns:
            Dictionary with row counts and file size
        """
        if not self.connection:
            raise RuntimeError("Not connected to database")

        cursor = self.connection.cursor()
        cursor.execute("SELECT COUNT(*) FROM metrics")
        total_metrics = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(DISTINCT type) FROM metrics")
        metric_types = cursor.fetchone()[0]

        # Get file size
        db_file = Path(self.db_path)
        file_size = db_file.stat().st_size if db_file.exists() else 0

        return {
            "backend": "sqlite",
            "total_metrics": total_metrics,
            "metric_types": metric_types,
            "file_size_bytes": file_size,
            "database_path": str(self.db_path),
        }

    def health_check(self) -> Dict[str, Any]:
        """Check database health.

        Returns:
            Health status dictionary
        """
        try:
            if not self.connection:
                return {
                    "status": "disconnected",
                    "backend": "sqlite",
                    "error": "Not connected",
                }

            stats = self.get_stats()
            return {
                "status": "ok",
                "backend": "sqlite",
                **stats,
            }
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return {
                "status": "error",
                "backend": "sqlite",
                "error": str(e),
            }


class PostgreSQLBackend(PersistenceBackend):
    """PostgreSQL persistence backend (for production deployments)."""

    def __init__(self, connection_string: str, pool_size: int = 5):
        """Initialize PostgreSQL backend.

        Args:
            connection_string: PostgreSQL connection string
            pool_size: Connection pool size
        """
        self.connection_string = connection_string
        self.pool_size = pool_size
        self.connection = None
        self.engine = None

    def connect(self) -> None:
        """Connect to PostgreSQL database."""
        try:
            import sqlalchemy
            from sqlalchemy import create_engine

            self.engine = create_engine(
                self.connection_string,
                pool_size=self.pool_size,
                pool_recycle=3600,
            )

            # Test connection
            with self.engine.connect() as conn:
                conn.execute(sqlalchemy.text("SELECT 1"))

            logger.info(f"Connected to PostgreSQL database")
        except Exception as e:
            logger.error(f"Failed to connect to PostgreSQL: {e}")
            raise

    def disconnect(self) -> None:
        """Disconnect from PostgreSQL database."""
        if self.engine:
            self.engine.dispose()
            logger.info("Disconnected from PostgreSQL database")

    def migrate(self) -> None:
        """Create tables if they don't exist."""
        if not self.engine:
            raise RuntimeError("Not connected to database")

        import sqlalchemy
        from sqlalchemy import text

        with self.engine.connect() as conn:
            conn.execute(
                text(
                    """
                CREATE TABLE IF NOT EXISTS metrics (
                    id TEXT PRIMARY KEY,
                    type TEXT NOT NULL,
                    data JSONB NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """
                )
            )

            conn.execute(
                text(
                    """
                CREATE INDEX IF NOT EXISTS idx_metrics_type
                ON metrics(type)
            """
                )
            )

            conn.commit()

        logger.info("Database migration completed")

    def store_metric(self, metric: Dict[str, Any]) -> str:
        """Store a metric in PostgreSQL.

        Args:
            metric: Metric data dictionary

        Returns:
            ID of stored metric
        """
        if not self.engine:
            raise RuntimeError("Not connected to database")

        import sqlalchemy
        from sqlalchemy import text

        metric_id = metric.get("id", str(datetime.utcnow().timestamp()))
        metric_type = metric.get("type", "unknown")
        metric_data = json.dumps(metric)

        with self.engine.connect() as conn:
            conn.execute(
                text(
                    """
                INSERT INTO metrics (id, type, data)
                VALUES (:id, :type, :data)
                ON CONFLICT (id) DO UPDATE SET
                    data = :data,
                    updated_at = CURRENT_TIMESTAMP
            """
                ),
                {"id": metric_id, "type": metric_type, "data": metric_data},
            )
            conn.commit()

        logger.debug(f"Stored metric {metric_id} ({metric_type})")
        return metric_id

    def list_metrics(
        self, metric_type: Optional[str] = None, limit: int = 100
    ) -> List[Dict[str, Any]]:
        """List metrics from PostgreSQL.

        Args:
            metric_type: Filter by metric type (optional)
            limit: Maximum number of metrics to return

        Returns:
            List of metric dictionaries
        """
        if not self.engine:
            raise RuntimeError("Not connected to database")

        import sqlalchemy
        from sqlalchemy import text

        with self.engine.connect() as conn:
            if metric_type:
                result = conn.execute(
                    text(
                        """
                    SELECT data FROM metrics
                    WHERE type = :type
                    ORDER BY created_at DESC
                    LIMIT :limit
                """
                    ),
                    {"type": metric_type, "limit": limit},
                )
            else:
                result = conn.execute(
                    text(
                        """
                    SELECT data FROM metrics
                    ORDER BY created_at DESC
                    LIMIT :limit
                """
                    ),
                    {"limit": limit},
                )

            rows = result.fetchall()
            return [json.loads(row[0]) for row in rows]

    def get_metric(self, metric_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific metric by ID.

        Args:
            metric_id: Metric ID

        Returns:
            Metric dictionary or None if not found
        """
        if not self.engine:
            raise RuntimeError("Not connected to database")

        import sqlalchemy
        from sqlalchemy import text

        with self.engine.connect() as conn:
            result = conn.execute(
                text("SELECT data FROM metrics WHERE id = :id"),
                {"id": metric_id},
            )
            row = result.fetchone()

        if row:
            return json.loads(row[0])
        return None

    def get_stats(self) -> Dict[str, Any]:
        """Get database statistics.

        Returns:
            Dictionary with row counts
        """
        if not self.engine:
            raise RuntimeError("Not connected to database")

        import sqlalchemy
        from sqlalchemy import text

        with self.engine.connect() as conn:
            result = conn.execute(text("SELECT COUNT(*) FROM metrics"))
            total_metrics = result.scalar()

            result = conn.execute(
                text("SELECT COUNT(DISTINCT type) FROM metrics")
            )
            metric_types = result.scalar()

        return {
            "backend": "postgresql",
            "total_metrics": total_metrics,
            "metric_types": metric_types,
        }

    def health_check(self) -> Dict[str, Any]:
        """Check database health.

        Returns:
            Health status dictionary
        """
        try:
            if not self.engine:
                return {
                    "status": "disconnected",
                    "backend": "postgresql",
                    "error": "Not connected",
                }

            stats = self.get_stats()
            return {
                "status": "ok",
                "backend": "postgresql",
                **stats,
            }
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return {
                "status": "error",
                "backend": "postgresql",
                "error": str(e),
            }


def get_backend(db_uri: str) -> PersistenceBackend:
    """Create appropriate backend based on database URI.

    Args:
        db_uri: Database URI (e.g., sqlite:///path/to/db or postgresql://...)

    Returns:
        PersistenceBackend instance

    Raises:
        ValueError: If database type is not supported
    """
    if db_uri.startswith("sqlite://"):
        # Extract path from URI
        # sqlite:///path/to/db -> /path/to/db
        path = db_uri.replace("sqlite:///", "")
        return SQLiteBackend(path)

    elif db_uri.startswith("postgresql://"):
        return PostgreSQLBackend(db_uri)

    else:
        raise ValueError(f"Unsupported database URI: {db_uri}")
