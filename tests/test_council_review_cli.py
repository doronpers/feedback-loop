"""Tests for Council AI reviewer CLI integration."""

import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from metrics.integrate import _handle_council_review


def test_handle_council_review_from_file(tmp_path):
    """Test council review command with file input."""
    test_file = tmp_path / "test_code.py"
    test_file.write_text("def hello():\n    print('world')\n")

    with patch("metrics.integrate.CouncilCodeReviewer") as mock_reviewer_class:
        mock_reviewer = MagicMock()
        mock_reviewer.review_code.return_value = {
            "review": "Good code",
            "responses": [],
            "source": "council_http",
        }
        mock_reviewer_class.return_value = mock_reviewer

        _handle_council_review(
            file_path=str(test_file),
            context=None,
            api_key=None,
            http_base_url=None,
            provider=None,
            prefer_local=False,
        )

        mock_reviewer.review_code.assert_called_once()
        call_args = mock_reviewer.review_code.call_args
        assert "def hello():" in call_args[0][0]
        assert call_args[1]["context"] is None


def test_handle_council_review_from_stdin(monkeypatch):
    """Test council review command with stdin input."""
    test_code = "print('test')"

    with patch("metrics.integrate.CouncilCodeReviewer") as mock_reviewer_class:
        mock_reviewer = MagicMock()
        mock_reviewer.review_code.return_value = {
            "review": "Review result",
            "responses": [],
            "source": "council_http",
        }
        mock_reviewer_class.return_value = mock_reviewer

        monkeypatch.setattr("sys.stdin", MagicMock(read=lambda: test_code))

        _handle_council_review(
            file_path=None,
            context="Test context",
            api_key="test-key",
            http_base_url="http://test",
            provider="openai",
            prefer_local=True,
        )

        mock_reviewer.review_code.assert_called_once()
        call_args = mock_reviewer.review_code.call_args
        assert call_args[0][0] == test_code
        assert call_args[1]["context"] == "Test context"
        assert call_args[1]["api_key"] == "test-key"


def test_handle_council_review_with_error(capsys, tmp_path):
    """Test council review command error handling."""
    test_file = tmp_path / "test_code.py"
    test_file.write_text("bad code")

    with patch("metrics.integrate.CouncilCodeReviewer") as mock_reviewer_class:
        mock_reviewer = MagicMock()
        mock_reviewer.review_code.return_value = {
            "error": "Review failed",
            "responses": [],
        }
        mock_reviewer_class.return_value = mock_reviewer

        _handle_council_review(
            file_path=str(test_file),
            context=None,
            api_key=None,
            http_base_url=None,
            provider=None,
            prefer_local=False,
        )

        captured = capsys.readouterr()
        assert "Error:" in captured.out
        assert "Review failed" in captured.out


def test_handle_council_review_success_output(capsys, tmp_path):
    """Test council review command successful output."""
    test_file = tmp_path / "test_code.py"
    test_file.write_text("def test(): pass")

    with patch("metrics.integrate.CouncilCodeReviewer") as mock_reviewer_class:
        mock_reviewer = MagicMock()
        mock_reviewer.review_code.return_value = {
            "review": "Excellent code quality",
            "responses": [{"content": "Persona 1 review"}],
            "source": "council_local",
        }
        mock_reviewer_class.return_value = mock_reviewer

        _handle_council_review(
            file_path=str(test_file),
            context=None,
            api_key=None,
            http_base_url=None,
            provider=None,
            prefer_local=False,
        )

        captured = capsys.readouterr()
        assert "Excellent code quality" in captured.out
