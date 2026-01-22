"""Tests for LLM robustness wrapper."""

import time
from unittest.mock import Mock

import pytest

from feedback_loop.llm import LLMClient, MockProvider
from feedback_loop.config import LLMConfig


class TransientError(Exception):
    pass


def test_llm_retries_and_eventually_succeeds(monkeypatch):
    # Provider fails twice with transient error, then succeeds
    provider = MockProvider(side_effects=[TransientError("transient"), TransientError("transient"), {"text": "ok"}])
    cfg = LLMConfig(max_retries=3, backoff_base=0.0, timeout_seconds=1, retryable_exceptions=["TransientError"], jitter=False)

    telemetry_events = []
    def telemetry_cb(ev):
        telemetry_events.append(ev)

    client = LLMClient(provider=provider, config=cfg, telemetry_callback=telemetry_cb)

    res = client.call("hello")

    assert res == {"text": "ok"}
    assert provider.calls == 3
    # Telemetry should record the successful call
    assert len(telemetry_events) == 1
    ev = telemetry_events[0]
    assert ev["event"] == "llm_call"
    assert ev["success"] is True
    assert ev["attempts"] == 3


def test_llm_non_retryable_exception_bubbles_up():
    provider = MockProvider(side_effects=[ValueError("bad request")])
    cfg = LLMConfig(max_retries=2, retryable_exceptions=["TransientError"], timeout_seconds=1)

    client = LLMClient(provider=provider, config=cfg)

    with pytest.raises(ValueError):
        client.call("bad")


def test_llm_timeout_is_retryable(monkeypatch):
    # Provider that sleeps longer than timeout to trigger TimeoutError
    class SlowProvider(MockProvider):
        def call(self, prompt: str, **kwargs):
            time.sleep(0.2)
            return {"text": "done"}

    cfg = LLMConfig(max_retries=1, timeout_seconds=0.05, backoff_base=0.0, retryable_exceptions=["TimeoutError"], jitter=False)
    provider = SlowProvider()

    telemetry_events = []
    def telemetry_cb(ev):
        telemetry_events.append(ev)

    client = LLMClient(provider=provider, config=cfg, telemetry_callback=telemetry_cb)

    with pytest.raises(TimeoutError):
        client.call("slow")

    # Telemetry should record the failure
    assert len(telemetry_events) == 1
    ev = telemetry_events[0]
    assert ev["event"] == "llm_call"
    assert ev["success"] is False
    assert ev["attempts"] >= 1

def test_llm_non_retryable_exception_bubbles_up():
    provider = MockProvider(side_effects=[ValueError("bad request")])
    cfg = LLMConfig(max_retries=2, retryable_exceptions=["TransientError"], timeout_seconds=1)

    client = LLMClient(provider=provider, config=cfg)

    with pytest.raises(ValueError):
        client.call("bad")


def test_llm_timeout_is_retryable(monkeypatch):
    # Provider that sleeps longer than timeout to trigger TimeoutError
    class SlowProvider(MockProvider):
        def call(self, prompt: str, **kwargs):
            time.sleep(0.2)
            return {"text": "done"}

    cfg = LLMConfig(max_retries=1, timeout_seconds=0.05, backoff_base=0.0, retryable_exceptions=["TimeoutError"], jitter=False)
    provider = SlowProvider()
    client = LLMClient(provider=provider, config=cfg)

    with pytest.raises(TimeoutError):
        client.call("slow")
