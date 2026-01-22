"""LLM wrapper and robustness utilities.

Provides a configurable LLMClient with retries, exponential backoff, timeouts,
and pluggable provider adapters for testing and production use.
"""

import concurrent.futures
import logging
import math
import random
import time
from typing import Any, Callable, Dict, Optional

from .config import get_config

logger = logging.getLogger(__name__)


class LLMProviderInterface:
    """Interface for provider adapters.

    Implementors must provide a `call` method that accepts a prompt and
    keyword args and returns the provider's response (synchronously).
    """

    def call(self, prompt: str, **kwargs) -> Any:  # pragma: no cover - implemented by adapters
        raise NotImplementedError


class MockProvider(LLMProviderInterface):
    """A simple mock provider useful for tests.

    Initialize with a list of side effects (exceptions or results) to simulate
    provider behavior across calls.
    """

    def __init__(self, side_effects: Optional[list] = None):
        self.side_effects = side_effects or []
        self.calls = 0

    def call(self, prompt: str, **kwargs) -> Any:
        self.calls += 1
        if self.calls <= len(self.side_effects):
            effect = self.side_effects[self.calls - 1]
            if isinstance(effect, Exception):
                raise effect
            return effect
        return {"text": f"echo:{prompt}"}


class LLMClient:
    """Robust LLM client with retries and timeouts.

    Parameters:
        provider: A provider adapter implementing `call(prompt, **kwargs)`.
        config: Optional LLMConfig instance from `get_config().llm`.
        telemetry_callback: Optional callable to receive telemetry events. Signature:
            callable(event: Dict[str, Any]) -> None
    """

    def __init__(self, provider: Optional[LLMProviderInterface] = None, config=None, telemetry_callback: Optional[Callable[[Dict[str, Any]], None]] = None):
        self.config = config or get_config().llm  # type: ignore[attr-defined]
        self.provider = provider
        if self.provider is None:
            # Default: create a MockProvider that echoes (safe default for dev/test)
            self.provider = MockProvider()
        self.telemetry_callback = telemetry_callback

    def _emit_telemetry(self, payload: Dict[str, Any]) -> None:
        """Emit telemetry event if a callback was provided."""
        try:
            if self.telemetry_callback:
                # Don't let telemetry errors disrupt LLM calls
                self.telemetry_callback(payload)
        except Exception:
            logger.exception("Telemetry callback raised an exception")

    def _is_retryable(self, exc: Exception) -> bool:
        # Determine retryability by exception class name matching configured list
        retry_names = set(self.config.retryable_exceptions or [])
        return exc.__class__.__name__ in retry_names

    def _backoff_delay(self, attempt: int) -> float:
        base = float(self.config.backoff_base)
        delay = base * (2 ** attempt)
        if self.config.jitter:
            jitter = random.random() * base
            delay = delay + jitter
        return min(delay, float(self.config.max_backoff))

    def call(self, prompt: str, **kwargs) -> Any:
        """Call the underlying provider with retries, timeout, and backoff.

        Returns provider response on success, otherwise raises the last exception.
        """
        max_attempts = int(self.config.max_retries) + 1
        timeout = float(self.config.timeout_seconds)

        last_exc: Optional[Exception] = None

        for attempt in range(max_attempts):
            try:
                logger.debug("LLMClient attempt %d for prompt", attempt + 1)
                # Use a thread to enforce timeout
                start = time.time()
                with concurrent.futures.ThreadPoolExecutor(max_workers=1) as ex:
                    fut = ex.submit(self.provider.call, prompt, **kwargs)
                    result = fut.result(timeout=timeout)
                    duration = time.time() - start
                    logger.debug("LLMClient received result on attempt %d", attempt + 1)

                    # Emit telemetry for success
                    self._emit_telemetry(
                        {
                            "event": "llm_call",
                            "success": True,
                            "attempts": attempt + 1,
                            "duration": duration,
                            "provider": str(self.config.provider),
                            "model": str(self.config.model),
                        }
                    )

                    return result

            except Exception as exc:  # Broad catch to wrap provider errors
                last_exc = exc
                # TimeoutError from concurrent.futures is considered retryable
                if isinstance(exc, concurrent.futures.TimeoutError):
                    err = TimeoutError("LLM provider call timed out")
                    last_exc = err
                logger.warning("LLM provider error on attempt %d: %s", attempt + 1, str(last_exc))

                # If not retryable, raise immediately
                if not self._is_retryable(last_exc) and not isinstance(last_exc, TimeoutError):
                    logger.debug("Exception not retryable, aborting")
                    # Emit telemetry for non-retryable error
                    self._emit_telemetry(
                        {
                            "event": "llm_call",
                            "success": False,
                            "attempts": attempt + 1,
                            "error": str(last_exc),
                            "provider": str(self.config.provider),
                            "model": str(self.config.model),
                        }
                    )
                    raise last_exc

                # If this was final attempt, break and raise
                if attempt + 1 >= max_attempts:
                    logger.error("LLM provider exhausted retries (%d), giving up", max_attempts)
                    # Emit telemetry for exhausted retries
                    duration = time.time() - start if 'start' in locals() else None
                    self._emit_telemetry(
                        {
                            "event": "llm_call",
                            "success": False,
                            "attempts": attempt + 1,
                            "error": str(last_exc),
                            "duration": duration,
                            "provider": str(self.config.provider),
                            "model": str(self.config.model),
                        }
                    )
                    break

                # Backoff before next attempt
                delay = self._backoff_delay(attempt)
                logger.info("Retrying LLM call after %.2fs", delay)
                time.sleep(delay)

        # If we get here, raise the last exception
        if last_exc:
            raise last_exc
        raise RuntimeError("LLM call failed without exception")


def get_llm_client(provider: Optional[LLMProviderInterface] = None, telemetry_callback: Optional[Callable[[Dict[str, Any]], None]] = None) -> LLMClient:
    """Factory helper to create an LLMClient using global config.

    Imports `get_config` at call time so tests can patch `feedback_loop.config.get_config`.

    Accepts an optional `telemetry_callback` which will be attached to the
    created `LLMClient` so callers (eg, modules in `metrics/`) can forward
    telemetry into their homes (like `MetricsCollector`).
    """
    from .config import get_config as _get_config  # local import to allow test monkeypatching

    cfg = _get_config().llm  # type: ignore[attr-defined]
    return LLMClient(provider=provider, config=cfg, telemetry_callback=telemetry_callback)
    def _is_retryable(self, exc: Exception) -> bool:
        # Determine retryability by exception class name matching configured list
        retry_names = set(self.config.retryable_exceptions or [])
        return exc.__class__.__name__ in retry_names

    def _backoff_delay(self, attempt: int) -> float:
        base = float(self.config.backoff_base)
        delay = base * (2 ** attempt)
        if self.config.jitter:
            jitter = random.random() * base
            delay = delay + jitter
        return min(delay, float(self.config.max_backoff))

    def call(self, prompt: str, **kwargs) -> Any:
        """Call the underlying provider with retries, timeout, and backoff.

        Returns provider response on success, otherwise raises the last exception.
        """
        max_attempts = int(self.config.max_retries) + 1
        timeout = float(self.config.timeout_seconds)

        last_exc: Optional[Exception] = None

        for attempt in range(max_attempts):
            try:
                logger.debug("LLMClient attempt %d for prompt", attempt + 1)
                # Use a thread to enforce timeout
                start = time.time()
                with concurrent.futures.ThreadPoolExecutor(max_workers=1) as ex:
                    fut = ex.submit(self.provider.call, prompt, **kwargs)
                    result = fut.result(timeout=timeout)
                    duration = time.time() - start
                    logger.debug("LLMClient received result on attempt %d", attempt + 1)

                    # Emit telemetry for success
                    self._emit_telemetry(
                        {
                            "event": "llm_call",
                            "success": True,
                            "attempts": attempt + 1,
                            "duration": duration,
                            "provider": str(self.config.provider),
                            "model": str(self.config.model),
                        }
                    )

                    return result

            except Exception as exc:  # Broad catch to wrap provider errors
                last_exc = exc
                # TimeoutError from concurrent.futures is considered retryable
                if isinstance(exc, concurrent.futures.TimeoutError):
                    err = TimeoutError("LLM provider call timed out")
                    last_exc = err
                logger.warning("LLM provider error on attempt %d: %s", attempt + 1, str(last_exc))

                # If not retryable, raise immediately
                if not self._is_retryable(last_exc) and not isinstance(last_exc, TimeoutError):
                    logger.debug("Exception not retryable, aborting")
                    # Emit telemetry for non-retryable error
                    self._emit_telemetry(
                        {
                            "event": "llm_call",
                            "success": False,
                            "attempts": attempt + 1,
                            "error": str(last_exc),
                            "provider": str(self.config.provider),
                            "model": str(self.config.model),
                        }
                    )
                    raise last_exc

                # If this was final attempt, break and raise
                if attempt + 1 >= max_attempts:
                    logger.error("LLM provider exhausted retries (%d), giving up", max_attempts)
                    # Emit telemetry for exhausted retries
                    duration = time.time() - start if 'start' in locals() else None
                    self._emit_telemetry(
                        {
                            "event": "llm_call",
                            "success": False,
                            "attempts": attempt + 1,
                            "error": str(last_exc),
                            "duration": duration,
                            "provider": str(self.config.provider),
                            "model": str(self.config.model),
                        }
                    )
                    break

                # Backoff before next attempt
                delay = self._backoff_delay(attempt)
                logger.info("Retrying LLM call after %.2fs", delay)
                time.sleep(delay)

        # If we get here, raise the last exception
        if last_exc:
            raise last_exc
        raise RuntimeError("LLM call failed without exception")
