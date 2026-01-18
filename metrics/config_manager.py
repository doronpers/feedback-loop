"""Configuration management for feedback-loop automation."""

import json
import logging
import os
from pathlib import Path
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)


class ConfigManager:
    """Manages feedback-loop configuration."""

    DEFAULT_CONFIG_PATH = ".feedback-loop/config.json"
    _instance: Optional["ConfigManager"] = None

    def __init__(self, config_path: Optional[str] = None):
        """Initialize config manager.

        Args:
            config_path: Optional path to config file (default: .feedback-loop/config.json)
        """
        self.config_path = Path(config_path or self.DEFAULT_CONFIG_PATH)
        self._config = self._load_config()

    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from file or return defaults."""
        if not self.config_path.exists():
            return self._default_config()

        try:
            with open(self.config_path, "r") as f:
                config = json.load(f)
                # Merge with defaults to ensure all keys exist
                default = self._default_config()
                return self._merge_config(default, config)
        except (json.JSONDecodeError, IOError) as e:
            logger.warning(f"Failed to load config: {e}, using defaults")
            return self._default_config()

    def _merge_config(self, default: Dict[str, Any], user: Dict[str, Any]) -> Dict[str, Any]:
        """Merge user config with defaults recursively."""
        result = default.copy()
        for key, value in user.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._merge_config(result[key], value)
            else:
                result[key] = value
        return result

    def _default_config(self) -> Dict[str, Any]:
        """Return default configuration."""
        return {
            "version": "1.0",
            "auto_init": False,
            "auto_metrics": {"enabled": False, "output_file": "data/metrics_data.json"},
            "auto_analyze": {
                "enabled": True,
                "threshold_failures": 1,
                "show_dashboard": False,
                "quiet": False,
            },
            "git_hooks": {
                "post_commit_analyze": {"enabled": False, "quiet": True},
                "post_merge_analyze": {"enabled": False, "since_merge_base": True},
            },
            "watcher": {
                "enabled": False,
                "debounce_seconds": 2,
                "watch_paths": [".", "tests", "examples"],
                "ignore_patterns": ["__pycache__", "*.pyc", ".git"],
                "auto_analyze": True,
                "auto_sync_patterns": True,
            },
            "daemon": {"enabled": False},
            "scheduler": {"enabled": False},
            "patterns": {
                "auto_sync_from_markdown": False,
                "markdown_path": "AI_PATTERNS.md",
                "patterns_file": "data/patterns.json",
            },
            "triggers": {
                "after_commits": 5,
                "after_failures": 3,
                "effectiveness_threshold": 0.5,
            },
            "code_review": {
                "max_code_size": 50000,
                "max_tokens": 2048,
                "max_tokens_explain": 1500,
                "max_tokens_suggest": 2048,
                "max_tokens_debrief": 1500,
            },
            "council_review": {
                "prefer_local": True,
                "http_base_url": "http://localhost:8000/api/consult",
                "http_timeout_seconds": 60,
                "domain": "coding",
                "mode": "synthesis",
                "temperature": 0.4,
                "max_tokens": 1200,
                "provider": None,
            },
            "analysis": {"time_window_days": 30},
            "pattern_matching": {
                "rules": {
                    "numpy_json_serialization": ["numpy", "json"],
                    "bounds_checking": ["list_access"],
                    "specific_exceptions": ["exception"],
                    "logger_debug": ["logging"],
                    "metadata_categorization": ["categorization"],
                    "temp_file_handling": ["file"],
                    "large_file_processing": ["large_file", "file"],
                },
                "keyword_rules": {
                    "numpy_json_serialization": ["numpy", "json", "serialize", "array", "api"],
                    "bounds_checking": ["list", "array", "index", "first", "last", "access"],
                    "specific_exceptions": ["exception", "error", "try", "catch", "handle"],
                    "logger_debug": ["log", "debug", "print", "logging"],
                    "metadata_categorization": ["categorize", "classify", "metadata", "type"],
                    "temp_file_handling": ["temp", "file", "temporary", "cleanup"],
                    "large_file_processing": ["large", "file", "upload", "stream", "memory"],
                    "fastapi": ["fastapi", "endpoint", "api", "route", "upload"],
                },
            },
        }

    def get(self, key_path: str, default: Any = None) -> Any:
        """Get config value by dot-separated path.

        Args:
            key_path: Dot-separated path (e.g., "auto_metrics.enabled")
            default: Default value if key not found

        Returns:
            Config value or default
        """
        keys = key_path.split(".")
        value: Any = self._config
        for key in keys:
            if isinstance(value, dict):
                value = value.get(key)
                if value is None:
                    return default
            else:
                return default
        return value if value is not None else default

    def set(self, key_path: str, value: Any) -> None:
        """Set config value by dot-separated path.

        Args:
            key_path: Dot-separated path (e.g., "auto_metrics.enabled")
            value: Value to set
        """
        keys = key_path.split(".")
        config = self._config
        for key in keys[:-1]:
            if key not in config:
                config[key] = {}
            config = config[key]
        config[keys[-1]] = value
        self._save_config()

    def _save_config(self) -> None:
        """Save configuration to file."""
        try:
            self.config_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.config_path, "w") as f:
                json.dump(self._config, f, indent=2)
        except IOError as e:
            logger.error(f"Failed to save config: {e}")

    def should_auto_enable_metrics(self) -> bool:
        """Check if metrics should be auto-enabled.

        Returns:
            True if metrics should be auto-enabled
        """
        # Check config file
        if self.get("auto_metrics.enabled", False):
            return True

        # Check environment variable
        if os.getenv("FEEDBACK_LOOP_AUTO_METRICS") == "1":
            return True

        # Check if data/metrics_data.json exists (project has used metrics before)
        metrics_file = self.get("auto_metrics.output_file", "data/metrics_data.json")
        if Path(metrics_file).exists():
            return True

        # Check if .feedback-loop/auto-metrics marker exists
        marker = Path(".feedback-loop/auto-metrics")
        if marker.exists():
            return True

        return False

    def should_auto_analyze(self, failure_count: int) -> bool:
        """Check if analysis should run automatically.

        Args:
            failure_count: Number of test failures

        Returns:
            True if analysis should run
        """
        if not self.get("auto_analyze.enabled", True):
            return False

        threshold = self.get("auto_analyze.threshold_failures", 1)
        return failure_count >= threshold

    def is_quiet(self) -> bool:
        """Check if output should be quiet.

        Returns:
            True if quiet mode enabled
        """
        return self.get("auto_analyze.quiet", False)

    def should_show_dashboard(self) -> bool:
        """Check if dashboard should be shown.

        Returns:
            True if dashboard should be shown
        """
        return self.get("auto_analyze.show_dashboard", False)

    @classmethod
    def get_instance(cls, config_path: Optional[str] = None) -> "ConfigManager":
        """Get singleton config manager instance.

        Args:
            config_path: Optional config path

        Returns:
            ConfigManager instance
        """
        if not hasattr(cls, "_instance") or cls._instance is None:
            cls._instance = cls(config_path)
        return cls._instance
