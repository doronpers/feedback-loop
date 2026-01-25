"""Tests for the telemetry -> MetricsCollector bridge for LLM telemetry."""

from feedback_loop.llm import LLMClient, MockProvider
from metrics.collector import MetricsCollector


def test_llm_telemetry_records_to_metrics_collector():
    collector = MetricsCollector()
    cb = collector.get_telemetry_callback()

    provider = MockProvider(side_effects=[{"text": "ok", "provider": "mock", "model": "mock-v1"}])
    client = LLMClient(provider=provider, telemetry_callback=cb)

    # Perform a call which should emit telemetry
    result = client.call("hello world")
    assert isinstance(result, dict) or hasattr(result, "get")

    # Telemetry should be recorded
    assert "llm_calls" in collector.data
    assert len(collector.data["llm_calls"]) == 1
    entry = collector.data["llm_calls"][0]
    # Provider/model are read from client config; ensure fields exist and types are correct
    assert "provider" in entry and entry["provider"] is not None
    assert "model" in entry
    assert entry["success"] is True
    assert entry["attempts"] >= 1


def test_code_reviewer_uses_llm_client_and_records_telemetry():
    collector = MetricsCollector()
    provider = MockProvider(side_effects=[{"text": "This is a review.", "provider": "mock", "model": "mock-v1"}])
    client = LLMClient(provider=provider, telemetry_callback=collector.get_telemetry_callback())

    from metrics.code_reviewer import CodeReviewer

    reviewer = CodeReviewer(llm_client=client, metrics_collector=collector)
    res = reviewer.review_code('print("hello")')

    assert "review" in res
    assert res["review"] == "This is a review."

    # The review flow may make multiple LLM calls (review + debrief). Ensure
    # at least one telemetry entry was recorded and is marked successful.
    assert len(collector.data["llm_calls"]) >= 1
    entry = collector.data["llm_calls"][0]
    assert entry["success"] is True
