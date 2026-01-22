"""Tests for LLMManager telemetry integration via ProviderAdapter."""

from types import SimpleNamespace
from metrics.llm_providers import LLMManager
from metrics.collector import MetricsCollector


class DummyProvider:
    def generate(self, prompt: str, max_tokens: int = 1024, **kwargs):
        return SimpleNamespace(text="dummy response", provider="dummy", model="dummy-v1")


def test_llm_manager_generate_with_telemetry():
    mgr = LLMManager(preferred_provider="dummy")
    # Inject our dummy provider directly to avoid requiring real SDKs
    mgr.providers = {"dummy": DummyProvider()}

    collector = MetricsCollector()
    cb = collector.get_telemetry_callback()

    resp = mgr.generate("hello", provider="dummy", telemetry_callback=cb)

    assert hasattr(resp, "text")
    assert resp.text == "dummy response"

    # Telemetry should have been recorded
    assert "llm_calls" in collector.data
    assert len(collector.data["llm_calls"]) == 1
    entry = collector.data["llm_calls"][0]
    assert entry["success"] is True
    assert entry["provider"] == "dummy" or entry["provider"] is not None
