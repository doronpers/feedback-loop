"""
Tests for LLM Providers Module

Tests multi-LLM support, provider abstraction, and fallback logic.
"""

import os
from unittest.mock import MagicMock, Mock, patch

import pytest

from metrics.llm_providers import (ClaudeProvider, GeminiProvider, LLMManager,
                                   LLMProvider, LLMResponse, OpenAIProvider,
                                   get_llm_manager)


class TestLLMResponse:
    """Test LLMResponse dataclass."""

    def test_llm_response_creation(self):
        """Test creating LLMResponse."""
        response = LLMResponse(text="Hello world", model="claude-3", provider="claude")

        assert response.text == "Hello world"
        assert response.model == "claude-3"
        assert response.provider == "claude"
        assert response.tokens_used is None
        assert response.metadata == {}

    def test_llm_response_with_metadata(self):
        """Test LLMResponse with metadata."""
        response = LLMResponse(
            text="Test",
            model="gpt-4",
            provider="openai",
            tokens_used=100,
            metadata={"input_tokens": 50, "output_tokens": 50},
        )

        assert response.tokens_used == 100
        assert response.metadata["input_tokens"] == 50


class TestClaudeProvider:
    """Test Claude provider."""

    def test_provider_name(self):
        """Test provider name."""
        provider = ClaudeProvider(api_key="test")
        assert provider.provider_name == "claude"

    def test_is_available_with_key(self):
        """Test availability check with API key."""
        with patch.dict(os.environ, {"ANTHROPIC_API_KEY": "test_key"}):
            provider = ClaudeProvider()
            # Will be True if anthropic is installed, False otherwise
            assert isinstance(provider.is_available(), bool)

    def test_is_available_without_key(self):
        """Test availability check without API key."""
        with patch.dict(os.environ, {}, clear=True):
            provider = ClaudeProvider(api_key=None)
            if "anthropic" not in str(type(provider).__module__):
                # If anthropic not installed
                assert provider.is_available() is False


class TestOpenAIProvider:
    """Test OpenAI provider."""

    def test_provider_name(self):
        """Test provider name."""
        provider = OpenAIProvider(api_key="test")
        assert provider.provider_name == "openai"

    def test_default_model(self):
        """Test default model."""
        provider = OpenAIProvider(api_key="test")
        assert provider.model == "gpt-4o"


class TestGeminiProvider:
    """Test Gemini provider."""

    def test_provider_name(self):
        """Test provider name."""
        provider = GeminiProvider(api_key="test")
        assert provider.provider_name == "gemini"

    def test_default_model(self):
        """Test default model."""
        provider = GeminiProvider(api_key="test")
        assert provider.model == "gemini-2.0-flash-exp"


class TestLLMManager:
    """Test LLM Manager."""

    def test_manager_initialization(self):
        """Test manager initialization."""
        manager = LLMManager()
        assert isinstance(manager.providers, dict)
        assert manager.preferred_provider in ["claude", "openai", "gemini"]

    def test_list_available_providers(self):
        """Test listing available providers."""
        manager = LLMManager()
        providers = manager.list_available_providers()
        assert isinstance(providers, list)
        # May be empty if no API keys set
        assert all(p in ["claude", "openai", "gemini"] for p in providers)

    def test_is_any_available(self):
        """Test checking if any provider is available."""
        manager = LLMManager()
        available = manager.is_any_available()
        assert isinstance(available, bool)

    def test_get_provider(self):
        """Test getting specific provider."""
        manager = LLMManager()
        # Try to get each provider type
        for name in ["claude", "openai", "gemini"]:
            provider = manager.get_provider(name)
            if provider:
                assert provider.provider_name == name

    @patch.dict(os.environ, {}, clear=True)
    def test_no_providers_available(self):
        """Test manager with no providers available."""
        manager = LLMManager()
        if not manager.is_any_available():
            with pytest.raises(RuntimeError, match="No LLM providers available"):
                manager.generate("test prompt")

    def test_preferred_provider(self):
        """Test setting preferred provider."""
        with patch.dict(os.environ, {"FL_LLM_PROVIDER": "gemini"}):
            manager = LLMManager()
            assert manager.preferred_provider == "gemini"


class TestLLMManagerGeneration:
    """Test LLM Manager generation with mocks."""

    def test_generate_with_mock_provider(self):
        """Test generation with mocked provider."""
        manager = LLMManager()

        # Create mock provider
        mock_provider = Mock(spec=LLMProvider)
        mock_provider.provider_name = "test"
        mock_provider.generate.return_value = LLMResponse(
            text="Generated code", model="test-model", provider="test"
        )

        # Add to manager
        manager.providers["test"] = mock_provider
        manager.preferred_provider = "test"

        # Generate
        response = manager.generate("test prompt")

        assert isinstance(response, LLMResponse)
        assert response.text == "Generated code"
        assert response.provider == "test"
        mock_provider.generate.assert_called_once()

    def test_fallback_on_failure(self):
        """Test fallback to another provider on failure."""
        manager = LLMManager()

        # Create mock providers
        mock_provider1 = Mock(spec=LLMProvider)
        mock_provider1.provider_name = "provider1"
        mock_provider1.generate.side_effect = Exception("API error")

        mock_provider2 = Mock(spec=LLMProvider)
        mock_provider2.provider_name = "provider2"
        mock_provider2.generate.return_value = LLMResponse(
            text="Fallback response", model="fallback-model", provider="provider2"
        )

        # Add to manager
        manager.providers = {"provider1": mock_provider1, "provider2": mock_provider2}
        manager.preferred_provider = "provider1"

        # Generate with fallback
        response = manager.generate("test prompt", fallback=True)

        assert response.text == "Fallback response"
        assert response.provider == "provider2"
        mock_provider1.generate.assert_called_once()
        mock_provider2.generate.assert_called_once()

    def test_no_fallback_on_failure(self):
        """Test no fallback when fallback=False."""
        manager = LLMManager()

        # Create mock provider that fails
        mock_provider = Mock(spec=LLMProvider)
        mock_provider.provider_name = "provider1"
        mock_provider.generate.side_effect = Exception("API error")

        # Add to manager
        manager.providers = {"provider1": mock_provider}
        manager.preferred_provider = "provider1"

        # Should raise exception
        with pytest.raises(Exception):
            manager.generate("test prompt", fallback=False)


class TestGetLLMManager:
    """Test global LLM manager."""

    def test_get_llm_manager_singleton(self):
        """Test that get_llm_manager returns same instance."""
        manager1 = get_llm_manager()
        manager2 = get_llm_manager()

        assert manager1 is manager2


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
