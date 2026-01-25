# LLM Robustness Guide

This guide describes the LLM wrapper introduced to improve reliability and observability when calling LLM providers.

## Goals

- Configurable timeouts and retries
- Exponential backoff with optional jitter
- Clear retryable/non-retryable failure classification
- Testability via provider adapters (mocks)

## Configuration

Set LLM settings via environment variables using the `FL_` prefix.

- `FL_LLM_PROVIDER` (default: `openai`)
- `FL_LLM_MODEL` (default: `gpt-4`)
- `FL_LLM_API_KEY_ENV` (default: `OPENAI_API_KEY`)
- `FL_LLM_TIMEOUT_SECONDS` (default: `30`)
- `FL_LLM_MAX_RETRIES` (default: `3`)
- `FL_LLM_BACKOFF_BASE` (default: `0.5`)
- `FL_LLM_MAX_BACKOFF` (default: `10.0`)
- `FL_LLM_JITTER` (default: `true`)

## Using the Client

The `LLMClient` is intentionally small and accepts a `provider` object for testability. In production, provider adapters can be implemented to wrap `openai` (or other) SDKs.

Example:

```python
from feedback_loop.llm import LLMClient
client = LLMClient(provider=MyOpenAIAdapter(), config=get_config().llm)
res = client.call("Summarize the test failures and recommend actions")
```

## Testing

- Use `MockProvider` to simulate provider behavior (errors, timeouts, successes)
- Tests should assert retry behavior, timeout handling, and abort on non-retryable errors

## Future Work

- Add telemetry hooks to integrate with metrics collector
- Add async implementation for high-throughput scenarios
- Add circuit-breaker to short-circuit saturated providers
