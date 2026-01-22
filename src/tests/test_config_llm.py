"""Tests for LLM config parsing from environment."""

import os
from pathlib import Path

import pytest

from feedback_loop.config import FeedbackLoopConfig, LLMProvider


def test_from_env_llm_parsing(monkeypatch):
    monkeypatch.setenv("FL_LLM_PROVIDER", "local")
    monkeypatch.setenv("FL_LLM_MODEL", "mini-1")
    monkeypatch.setenv("FL_LLM_API_KEY_ENV", "MY_KEY")
    monkeypatch.setenv("FL_LLM_TIMEOUT_SECONDS", "1.5")
    monkeypatch.setenv("FL_LLM_MAX_RETRIES", "2")
    monkeypatch.setenv("FL_LLM_BACKOFF_BASE", "0.1")
    monkeypatch.setenv("FL_LLM_MAX_BACKOFF", "2.0")
    monkeypatch.setenv("FL_LLM_JITTER", "false")
    monkeypatch.setenv("FL_LLM_RETRYABLE_EXCEPTIONS", "TimeoutError,CustomTransientError")

    config = FeedbackLoopConfig.from_env()
    assert config.llm.provider == LLMProvider.LOCAL
    assert config.llm.model == "mini-1"
    assert config.llm.api_key_env == "MY_KEY"
    assert config.llm.timeout_seconds == 1.5
    assert config.llm.max_retries == 2
    assert config.llm.backoff_base == 0.1
    assert config.llm.max_backoff == 2.0
    assert config.llm.jitter is False
    assert "CustomTransientError" in config.llm.retryable_exceptions
