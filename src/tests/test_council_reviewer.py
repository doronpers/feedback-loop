"""Tests for Council AI reviewer integration."""

import sys
from unittest.mock import MagicMock

from metrics.code_reviewer import CouncilCodeReviewer


def test_council_review_http_fallback(monkeypatch):
    """Ensure HTTP fallback returns synthesis response."""

    class FakeResponse:
        ok = True

        def json(self):
            return {
                "synthesis": "Review result",
                "responses": [{"content": "Persona review"}],
                "mode": "synthesis",
            }

    class FakeRequests:
        @staticmethod
        def post(*_args, **_kwargs):
            return FakeResponse()

    monkeypatch.setitem(sys.modules, "requests", FakeRequests)

    reviewer = CouncilCodeReviewer(prefer_local=False, http_base_url="http://example")
    result = reviewer.review_code("print('hi')")

    assert result["review"] == "Review result"
    assert result["mode"] == "synthesis"
    assert result["source"] == "council_http"


def test_council_review_empty_code():
    """Test that empty code returns error."""
    reviewer = CouncilCodeReviewer(prefer_local=False)
    result = reviewer.review_code("")
    assert "error" in result
    assert "No code provided" in result["error"]


def test_council_review_whitespace_only():
    """Test that whitespace-only code returns error."""
    reviewer = CouncilCodeReviewer(prefer_local=False)
    result = reviewer.review_code("   \n\t  ")
    assert "error" in result
    assert "No code provided" in result["error"]


def test_council_review_local_preference(monkeypatch):
    """Test that local import is attempted when prefer_local=True."""

    class FakeCouncil:
        @staticmethod
        def for_domain(*_args, **_kwargs):
            council = MagicMock()
            result = MagicMock()
            result.synthesis = "Local review"
            result.responses = []
            result.mode = "synthesis"
            council.consult.return_value = result
            return council

    monkeypatch.setitem(sys.modules, "council_ai", MagicMock(Council=FakeCouncil))

    reviewer = CouncilCodeReviewer(prefer_local=True)
    result = reviewer.review_code("print('test')")

    assert result["review"] == "Local review"
    assert result["source"] == "council_local"


def test_council_review_local_import_error(monkeypatch):
    """Test fallback to HTTP when local import fails."""

    class FakeResponse:
        ok = True

        def json(self):
            return {"synthesis": "HTTP fallback", "responses": [], "mode": "synthesis"}

    class FakeRequests:
        @staticmethod
        def post(*_args, **_kwargs):
            return FakeResponse()

    # Remove council_ai from modules if present, and prevent import
    if "council_ai" in sys.modules:
        monkeypatch.delitem(sys.modules, "council_ai", raising=False)

    def raise_import_error(name, *args, **kwargs):
        if name == "council_ai":
            raise ImportError("No module named 'council_ai'")
        return __import__(name, *args, **kwargs)

    monkeypatch.setattr("builtins.__import__", raise_import_error)
    monkeypatch.setitem(sys.modules, "requests", FakeRequests)

    reviewer = CouncilCodeReviewer(prefer_local=True)
    result = reviewer.review_code("print('test')")

    assert result["review"] == "HTTP fallback"
    assert result["source"] == "council_http"


def test_council_review_http_timeout(monkeypatch):
    """Test HTTP timeout handling."""

    class FakeTimeoutError(Exception):
        """Fake timeout exception."""

    class FakeRequests:
        class Exceptions:
            Timeout = FakeTimeoutError

        @staticmethod
        def post(*_args, **_kwargs):
            raise FakeTimeoutError("Request timed out")

    monkeypatch.setitem(sys.modules, "requests", FakeRequests)

    reviewer = CouncilCodeReviewer(prefer_local=False, timeout_seconds=5)
    result = reviewer.review_code("print('test')")

    assert "error" in result
    assert "timeout" in result["error"].lower()


def test_council_review_http_connection_error(monkeypatch):
    """Test HTTP connection error handling."""

    class FakeConnectionError(Exception):
        """Fake connection error exception."""

    class FakeRequests:
        class Exceptions:
            ConnectionError = FakeConnectionError

        @staticmethod
        def post(*_args, **_kwargs):
            raise FakeConnectionError("Connection refused")

    monkeypatch.setitem(sys.modules, "requests", FakeRequests)

    reviewer = CouncilCodeReviewer(prefer_local=False)
    result = reviewer.review_code("print('test')")

    assert "error" in result
    assert "connection" in result["error"].lower()


def test_council_review_http_error_response(monkeypatch):
    """Test HTTP error response handling."""

    class FakeResponse:
        ok = False
        status_code = 500
        text = "Internal Server Error"

    class FakeRequests:
        @staticmethod
        def post(*_args, **_kwargs):
            return FakeResponse()

    monkeypatch.setitem(sys.modules, "requests", FakeRequests)

    reviewer = CouncilCodeReviewer(prefer_local=False)
    result = reviewer.review_code("print('test')")

    assert "error" in result
    assert "500" in result["error"]


def test_council_review_prompt_building():
    """Test that prompt includes pattern context."""
    reviewer = CouncilCodeReviewer(prefer_local=False)
    prompt = reviewer._build_review_prompt("def test(): pass", context="Test context")

    assert "def test(): pass" in prompt
    assert "Test context" in prompt
    assert "multi-perspective code reviewer" in prompt.lower()


def test_council_review_with_context(monkeypatch):
    """Test review with additional context."""
    reviewer = CouncilCodeReviewer(prefer_local=False)

    class FakeResponse:
        ok = True

        def json(self):
            return {"synthesis": "Review with context", "responses": [], "mode": "synthesis"}

    class FakeRequests:
        @staticmethod
        def post(*_args, **_kwargs):
            return FakeResponse()

    monkeypatch.setitem(sys.modules, "requests", FakeRequests)
    result = reviewer.review_code("print('hi')", context="This is a test function")
    assert result["review"] == "Review with context"


def test_council_review_requests_import_error(monkeypatch):
    """Test handling when requests library is not available."""

    # Simulate ImportError for requests
    def raise_import_error(name, *args, **kwargs):
        if name == "requests":
            raise ImportError("No module named 'requests'")
        return __import__(name, *args, **kwargs)

    monkeypatch.setattr("builtins.__import__", raise_import_error)

    reviewer = CouncilCodeReviewer(prefer_local=False)
    result = reviewer.review_code("print('test')")

    assert "error" in result
    assert "requests" in result["error"].lower()
