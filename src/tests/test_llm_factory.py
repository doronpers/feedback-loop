"""Tests for LLM client factory helper."""

import pytest

from feedback_loop.llm import get_llm_client, MockProvider
from feedback_loop.config import FeedbackLoopConfig, LLMConfig


def test_get_llm_client_default_config(monkeypatch):
    # Ensure get_config() returns a config with llm field
    cfg = FeedbackLoopConfig()
    cfg.llm = LLMConfig(timeout_seconds=0.5, max_retries=1)

    monkeypatch.setattr("feedback_loop.config.get_config", lambda: cfg)

    client = get_llm_client()
    assert client.config.timeout_seconds == 0.5
    assert client.config.max_retries == 1


def test_get_llm_client_with_provider():
    provider = MockProvider()
    client = get_llm_client(provider=provider)
    assert client.provider is provider
