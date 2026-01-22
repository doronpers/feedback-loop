"""
Configuration Management

Pydantic models for type-safe, validated configuration.
Loads from environment variables with sensible defaults.
"""

import os
from enum import Enum
from pathlib import Path
from typing import Optional

from pydantic import BaseModel, Field, validator


class DatabaseType(str, Enum):
    """Supported database types."""

    SQLITE = "sqlite"
    POSTGRESQL = "postgresql"


class DatabaseConfig(BaseModel):
    """Database configuration.

    Supports both SQLite (for development/demos) and PostgreSQL (for production).
    """

    type: DatabaseType = Field(
        default=DatabaseType.SQLITE,
        description="Database type: sqlite or postgresql",
    )

    uri: Optional[str] = Field(
        default=None,
        description="Database connection URI (e.g., sqlite:///data/metrics.db or postgresql://user:pass@host/db)",
    )

    path: Optional[Path] = Field(
        default=None,
        description="SQLite file path (alternative to uri for SQLite)",
    )

    auto_migrate: bool = Field(
        default=True,
        description="Automatically run migrations on startup",
    )

    pool_size: int = Field(
        default=5,
        description="Connection pool size (PostgreSQL only)",
    )

    @validator("uri", pre=True, always=True)
    def set_uri(cls, v, values):
        """Generate URI if not provided."""
        if v:
            return v

        db_type = values.get("type", DatabaseType.SQLITE)

        if db_type == DatabaseType.SQLITE:
            path = values.get("path") or Path("data/metrics.db")
            # Ensure absolute path
            if not path.is_absolute():
                path = Path.cwd() / path
            path.parent.mkdir(parents=True, exist_ok=True)
            return f"sqlite:///{path}"

        # PostgreSQL - URI is required
        return None

    class Config:
        """Pydantic config."""

        use_enum_values = False


class APIConfig(BaseModel):
    """API configuration."""

    host: str = Field(
        default="127.0.0.1",
        description="API host",
    )

    port: int = Field(
        default=8000,
        description="API port",
    )

    debug: bool = Field(
        default=False,
        description="Enable debug mode",
    )

    reload: bool = Field(
        default=False,
        description="Enable auto-reload on code changes",
    )

    log_level: str = Field(
        default="INFO",
        description="Logging level",
    )


class LLMProvider(str, Enum):
    """Supported LLM providers."""

    OPENAI = "openai"
    LOCAL = "local"
    OTHER = "other"


class LLMConfig(BaseModel):
    """Configuration for LLM providers and client behavior."""

    provider: LLMProvider = Field(
        default=LLMProvider.OPENAI,
        description="Default LLM provider",
    )

    model: str = Field(
        default="gpt-4",
        description="Model name or identifier",
    )

    api_key_env: Optional[str] = Field(
        default="OPENAI_API_KEY",
        description="Environment variable name for provider API key",
    )

    timeout_seconds: float = Field(
        default=30.0,
        description="Request timeout in seconds (seconds can be fractional)",
    )

    max_retries: int = Field(
        default=3,
        description="Maximum number of retry attempts for transient errors",
    )

    backoff_base: float = Field(
        default=0.5,
        description="Base backoff (seconds) for exponential backoff",
    )

    max_backoff: float = Field(
        default=10.0,
        description="Maximum backoff cap (seconds)",
    )

    jitter: bool = Field(
        default=True,
        description="Randomized jitter for backoff delays",
    )

    retryable_exceptions: Optional[list] = Field(
        default_factory=lambda: ["TimeoutError", "ConnectionError"],
        description="Exception class names considered retryable",
    )

    class Config:
        use_enum_values = False


class FeedbackLoopConfig(BaseModel):
    """Main application configuration.

    Loads from environment variables with FL_ prefix.
    Example:
        FL_DB_TYPE=sqlite
        FL_DB_PATH=data/metrics.db
        FL_API_DEBUG=true
    """

    database: DatabaseConfig = Field(
        default_factory=DatabaseConfig,
        description="Database configuration",
    )

    api: APIConfig = Field(
        default_factory=APIConfig,
        description="API configuration",
    )

    metrics_enabled: bool = Field(
        default=True,
        description="Enable metrics collection",
    )

    llm: LLMConfig = Field(
        default_factory=LLMConfig,
        description="LLM configuration",
    )

    @classmethod
    def from_env(cls) -> "FeedbackLoopConfig":
        """Create config from environment variables.

        Environment variables:
            FL_DB_TYPE: Database type (sqlite, postgresql)
            FL_DB_URI: Database connection URI
            FL_DB_PATH: SQLite file path (relative to project root)
            FL_DB_AUTO_MIGRATE: Auto-run migrations (true/false)
            FL_DB_POOL_SIZE: Connection pool size
            FL_API_HOST: API host
            FL_API_PORT: API port
            FL_API_DEBUG: Debug mode (true/false)
            FL_API_RELOAD: Auto-reload (true/false)
            FL_API_LOG_LEVEL: Log level
            FL_METRICS_ENABLED: Enable metrics (true/false)
        """
        # Parse database config
        db_type_str = os.getenv("FL_DB_TYPE", "sqlite").lower()
        db_type = DatabaseType.SQLITE
        if db_type_str == "postgresql":
            db_type = DatabaseType.POSTGRESQL

        db_path = os.getenv("FL_DB_PATH")
        if db_path:
            db_path = Path(db_path)

        db_auto_migrate = os.getenv("FL_DB_AUTO_MIGRATE", "true").lower() == "true"
        db_pool_size = int(os.getenv("FL_DB_POOL_SIZE", "5"))

        database_config = DatabaseConfig(
            type=db_type,
            uri=os.getenv("FL_DB_URI"),
            path=db_path,
            auto_migrate=db_auto_migrate,
            pool_size=db_pool_size,
        )

        # Parse API config
        api_config = APIConfig(
            host=os.getenv("FL_API_HOST", "127.0.0.1"),
            port=int(os.getenv("FL_API_PORT", "8000")),
            debug=os.getenv("FL_API_DEBUG", "false").lower() == "true",
            reload=os.getenv("FL_API_RELOAD", "false").lower() == "true",
            log_level=os.getenv("FL_API_LOG_LEVEL", "INFO"),
        )

        # Main config
        metrics_enabled = os.getenv("FL_METRICS_ENABLED", "true").lower() == "true"

        # Parse LLM config
        llm_provider = os.getenv("FL_LLM_PROVIDER", "openai").lower()
        llm_model = os.getenv("FL_LLM_MODEL", "gpt-4")
        llm_api_key_env = os.getenv("FL_LLM_API_KEY_ENV", "OPENAI_API_KEY")
        llm_timeout = float(os.getenv("FL_LLM_TIMEOUT_SECONDS", "30"))
        llm_max_retries = int(os.getenv("FL_LLM_MAX_RETRIES", "3"))
        llm_backoff_base = float(os.getenv("FL_LLM_BACKOFF_BASE", "0.5"))
        llm_max_backoff = float(os.getenv("FL_LLM_MAX_BACKOFF", "10.0"))
        llm_jitter = os.getenv("FL_LLM_JITTER", "true").lower() == "true"
        llm_retryable_exceptions = os.getenv("FL_LLM_RETRYABLE_EXCEPTIONS", "TimeoutError,ConnectionError")
        llm_retryable_exceptions_list = [s.strip() for s in llm_retryable_exceptions.split(",") if s.strip()]

        llm_config = LLMConfig(
            provider=llm_provider,
            model=llm_model,
            api_key_env=llm_api_key_env,
            timeout_seconds=llm_timeout,
            max_retries=llm_max_retries,
            backoff_base=llm_backoff_base,
            max_backoff=llm_max_backoff,
            jitter=llm_jitter,
            retryable_exceptions=llm_retryable_exceptions_list,
        )

        return cls(
            database=database_config,
            api=api_config,
            metrics_enabled=metrics_enabled,
            llm=llm_config,
        )

    @classmethod
    def default(cls) -> "FeedbackLoopConfig":
        """Create default configuration."""
        return cls()

    def get_db_uri(self) -> str:
        """Get the database URI."""
        if not self.database.uri:
            raise ValueError(
                "Database URI not configured. Set FL_DB_URI or FL_DB_PATH environment variable."
            )
        return self.database.uri


# Global config instance
_config: Optional[FeedbackLoopConfig] = None


def get_config() -> FeedbackLoopConfig:
    """Get the global config instance (singleton)."""
    global _config
    if _config is None:
        _config = FeedbackLoopConfig.from_env()
    return _config


def set_config(config: FeedbackLoopConfig) -> None:
    """Set the global config instance (mainly for testing)."""
    global _config
    _config = config


def reset_config() -> None:
    """Reset config to None (mainly for testing)."""
    global _config
    _config = None
