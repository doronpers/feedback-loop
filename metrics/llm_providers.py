"""
LLM Provider Abstraction Layer

Provides unified interface for multiple LLM providers (Claude, GPT-4, Gemini).
Makes it easy to switch between providers or use multiple simultaneously.
"""

import logging
import os
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Callable, Dict, List, Optional
from types import SimpleNamespace

# Import the LLMClient interface so we can wrap legacy providers when a
# telemetry_callback is supplied. We do a local import inside functions to
# avoid heavy startup costs for packages that may be missing in test envs.
try:
    from feedback_loop.llm import LLMProviderInterface
except Exception:
    LLMProviderInterface = None  # type: ignore

logger = logging.getLogger(__name__)


@dataclass
class LLMResponse:
    """Unified response from any LLM provider."""

    text: str
    model: str
    provider: str
    tokens_used: Optional[int] = None
    metadata: Optional[Dict[str, Any]] = None

    def __post_init__(self):  # noqa: D105
        if self.metadata is None:
            self.metadata = {}


class LLMProvider(ABC):
    """Abstract base class for LLM providers."""

    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        """Initialize provider with API key and model.

        Args:
            api_key: API key for the provider
            model: Model name to use (provider-specific)
        """
        self.api_key = api_key
        self.model = model
        self.client = None

    @abstractmethod
    def generate(self, prompt: str, max_tokens: int = 4096, **kwargs) -> LLMResponse:
        """Generate response from the LLM.

        Args:
            prompt: Input prompt
            max_tokens: Maximum tokens to generate
            **kwargs: Provider-specific parameters

        Returns:
            LLMResponse with generated text
        """
        pass

    @abstractmethod
    def is_available(self) -> bool:
        """Check if provider is available (API key set, package installed)."""
        pass

    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Return provider name."""
        pass


class ClaudeProvider(LLMProvider):
    """Anthropic Claude LLM provider."""

    def __init__(self, api_key: Optional[str] = None, model: str = "claude-sonnet-4-5-20250929"):
        """Initialize Claude provider.

        Args:
            api_key: Anthropic API key (uses ANTHROPIC_API_KEY env var if not provided)
            model: Claude model to use
        """
        super().__init__(api_key or os.environ.get("ANTHROPIC_API_KEY"), model)

        if self.is_available():
            try:
                import anthropic

                self.client = anthropic.Anthropic(api_key=self.api_key)
                logger.info(f"Claude provider initialized with model: {self.model}")
            except Exception as e:
                logger.warning(f"Failed to initialize Claude client: {e}")
                self.client = None

    def generate(self, prompt: str, max_tokens: int = 4096, **kwargs) -> LLMResponse:
        """Generate response using Claude API."""
        if not self.is_available() or not self.client:
            raise RuntimeError("Claude provider not available")

        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=max_tokens,
                messages=[{"role": "user", "content": prompt}],
                **kwargs,
            )

            return LLMResponse(
                text=response.content[0].text,
                model=self.model,
                provider="claude",
                tokens_used=response.usage.input_tokens + response.usage.output_tokens,
                metadata={
                    "input_tokens": response.usage.input_tokens,
                    "output_tokens": response.usage.output_tokens,
                },
            )
        except Exception as e:
            logger.error(f"Claude API error: {e}")
            raise

    def is_available(self) -> bool:
        """Check if Claude is available."""
        try:
            import anthropic  # noqa: F401

            return self.api_key is not None
        except ImportError:
            return False

    @property
    def provider_name(self) -> str:
        return "claude"


class OpenAIProvider(LLMProvider):
    """OpenAI GPT LLM provider."""

    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-4o"):
        """Initialize OpenAI provider.

        Args:
            api_key: OpenAI API key (uses OPENAI_API_KEY env var if not provided)
            model: OpenAI model to use
        """
        super().__init__(api_key or os.environ.get("OPENAI_API_KEY"), model)

        if self.is_available():
            try:
                import openai

                self.client = openai.OpenAI(api_key=self.api_key)
                logger.info(f"OpenAI provider initialized with model: {self.model}")
            except Exception as e:
                logger.warning(f"Failed to initialize OpenAI client: {e}")
                self.client = None

    def generate(self, prompt: str, max_tokens: int = 4096, **kwargs) -> LLMResponse:
        """Generate response using OpenAI API."""
        if not self.is_available() or not self.client:
            raise RuntimeError("OpenAI provider not available")

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                max_tokens=max_tokens,
                messages=[{"role": "user", "content": prompt}],
                **kwargs,
            )

            return LLMResponse(
                text=response.choices[0].message.content,
                model=self.model,
                provider="openai",
                tokens_used=response.usage.total_tokens if response.usage else None,
                metadata={
                    "input_tokens": (response.usage.prompt_tokens if response.usage else None),
                    "output_tokens": (response.usage.completion_tokens if response.usage else None),
                },
            )
        except Exception as e:
            logger.error(f"OpenAI API error: {e}")
            raise

    def is_available(self) -> bool:
        """Check if OpenAI is available."""
        try:
            import openai  # noqa: F401

            return self.api_key is not None
        except ImportError:
            return False

    @property
    def provider_name(self) -> str:
        return "openai"


class GeminiProvider(LLMProvider):
    """Google Gemini LLM provider.

    Note: Uses the newer google.genai package (recommended) with fallback
    to google.generativeai if available.
    """

    def __init__(self, api_key: Optional[str] = None, model: str = "gemini-2.0-flash-exp"):
        """Initialize Gemini provider.

        Args:
            api_key: Google API key (uses GEMINI_API_KEY env var if not provided,
                     falls back to GOOGLE_API_KEY for backward compatibility)
            model: Gemini model to use
        """
        # Check GEMINI_API_KEY first, then fall back to GOOGLE_API_KEY for backward compatibility
        env_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
        super().__init__(api_key or env_key, model)
        self._using_new_api = False

        if self.is_available():
            try:
                # Try new google.genai package first
                try:
                    import google.genai as genai

                    self._using_new_api = True
                    logger.info("Using new google.genai package")
                except ImportError:
                    # Fallback to deprecated package
                    import google.generativeai as genai

                    logger.warning(
                        "Using deprecated google.generativeai package. "
                        "Please migrate to google.genai: pip install google-genai"
                    )

                genai.configure(api_key=self.api_key)
                self.client = genai.GenerativeModel(self.model)
                logger.info(f"Gemini provider initialized with model: {self.model}")
            except Exception as e:
                logger.warning(f"Failed to initialize Gemini client: {e}")
                self.client = None

    def generate(self, prompt: str, max_tokens: int = 4096, **kwargs) -> LLMResponse:
        """Generate response using Gemini API."""
        if not self.is_available() or not self.client:
            raise RuntimeError("Gemini provider not available")

        try:
            # Gemini uses different parameter naming
            generation_config = {
                "max_output_tokens": max_tokens,
            }

            response = self.client.generate_content(prompt, generation_config=generation_config)

            return LLMResponse(
                text=response.text,
                model=self.model,
                provider="gemini",
                tokens_used=None,  # Gemini doesn't always provide token counts
                metadata={
                    "finish_reason": (
                        response.candidates[0].finish_reason if response.candidates else None
                    )
                },
            )
        except Exception as e:
            logger.error(f"Gemini API error: {e}")
            raise

    def is_available(self) -> bool:
        """Check if Gemini is available."""
        if self.api_key is None:
            return False
        try:
            # Try new package first
            try:
                import google.genai  # noqa: F401

                return True
            except ImportError:
                # Fallback to deprecated package
                import google.generativeai  # noqa: F401

                return True
        except ImportError:
            return False

    @property
    def provider_name(self) -> str:
        return "gemini"


class LLMManager:
    """Manages multiple LLM providers with automatic fallback.

    This manager now accepts an optional `telemetry_callback` parameter in
    `generate(...)` to allow callers to route telemetry into their own
    collectors (eg, `MetricsCollector.get_telemetry_callback()`). When a
    telemetry callback is provided, the manager wraps the legacy provider in a
    small adapter and calls it via the `LLMClient` to get retry/timeout/telemetry
    behavior.
    """

    def __init__(self, preferred_provider: Optional[str] = None):
        """Initialize LLM manager.

        Args:
            preferred_provider: Preferred provider name ("claude", "openai", "gemini")
        """
        self.providers: Dict[str, LLMProvider] = {}
        self._initialize_providers()

        self.preferred_provider = preferred_provider or os.environ.get("FL_LLM_PROVIDER", "claude")
        logger.info(f"LLM Manager initialized with preferred provider: {self.preferred_provider}")

    def _initialize_providers(self):
        """Initialize all available providers."""
        # Try to initialize each provider
        for provider_class in [ClaudeProvider, OpenAIProvider, GeminiProvider]:
            try:
                provider = provider_class()
                if provider.is_available():
                    self.providers[provider.provider_name] = provider
                    logger.info(f"Provider {provider.provider_name} is available")
            except Exception as e:
                logger.debug(f"Could not initialize {provider_class.__name__}: {e}")

    def generate(
        self,
        prompt: str,
        provider: Optional[str] = None,
        fallback: bool = True,
        telemetry_callback: Optional[Callable[[Dict[str, Any]], None]] = None,
        **kwargs,
    ) -> LLMResponse:
        """Generate response using specified or preferred provider.

        Args:
            prompt: Input prompt
            provider: Specific provider to use (None = use preferred)
            fallback: If True, try other providers on failure
            telemetry_callback: Optional callable to receive LLM telemetry events
            **kwargs: Provider-specific parameters

        Returns:
            LLMResponse-like object with generated text

        Raises:
            RuntimeError: If no providers are available or all fail
        """
        if not self.providers:
            raise RuntimeError("No LLM providers available. Set API keys and install packages.")

        # Determine which provider to use
        target_provider = provider or self.preferred_provider

        # Helper to use telemetry-enabled path when a callback is provided
        def _call_with_telemetry(prov_name: str, prov_obj: LLMProvider):
            # Lazy import to avoid heavy deps at module import time
            try:
                from feedback_loop.llm import get_llm_client
            except Exception as e:
                logger.debug("Could not import LLM client for telemetry: %s", e)
                raise

            # Adapter that turns legacy `.generate()` into `.call()` for LLMClient
            class ProviderAdapter:
                def __init__(self, provider_instance):
                    self._p = provider_instance

                def call(self, prompt: str, **kwargs):
                    res = self._p.generate(prompt, **kwargs)
                    # Normalize into a dict-like response
                    return {
                        "text": getattr(res, "text", None),
                        "provider": getattr(res, "provider", None),
                        "model": getattr(res, "model", None),
                        "tokens_used": getattr(res, "tokens_used", None),
                        "metadata": getattr(res, "metadata", None),
                    }

            adapter = ProviderAdapter(prov_obj)
            client = get_llm_client(provider=adapter, telemetry_callback=telemetry_callback)
            out = client.call(prompt, **kwargs)
            # Normalize client output into a simple object with attributes like the
            # legacy `LLMResponse` so existing callers keep working.
            return SimpleNamespace(text=out.get("text"), provider=out.get("provider"), model=out.get("model"))

        # Try preferred provider first
        if target_provider in self.providers:
            try:
                if telemetry_callback is not None:
                    return _call_with_telemetry(target_provider, self.providers[target_provider])
                return self.providers[target_provider].generate(prompt, **kwargs)
            except Exception as e:
                logger.warning(f"Provider {target_provider} failed: {e}")
                if not fallback:
                    raise

        # Fallback to other providers
        if fallback:
            for name, prov in self.providers.items():
                if name == target_provider:
                    continue  # Already tried
                try:
                    logger.info(f"Falling back to provider: {name}")
                    if telemetry_callback is not None:
                        return _call_with_telemetry(name, prov)
                    return prov.generate(prompt, **kwargs)
                except Exception as e:
                    logger.warning(f"Provider {name} failed: {e}")
                    continue

        raise RuntimeError("All LLM providers failed")

    def list_available_providers(self) -> List[str]:
        """Get list of available provider names."""
        return list(self.providers.keys())

    def get_provider(self, name: str) -> Optional[LLMProvider]:
        """Get specific provider by name."""
        return self.providers.get(name)

    def is_any_available(self) -> bool:
        """Check if any provider is available."""
        return len(self.providers) > 0


# Global instance for easy access
_manager: Optional[LLMManager] = None


def get_llm_manager() -> LLMManager:
    """Get or create global LLM manager instance."""
    global _manager
    if _manager is None:
        _manager = LLMManager()
    return _manager
