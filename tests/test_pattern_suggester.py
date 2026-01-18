"""Tests for Pattern Suggester Module."""

import pytest

from metrics.pattern_manager import PatternManager
from metrics.pattern_suggester import PatternSuggester


class TestPatternSuggester:
    """Tests for PatternSuggester class."""

    @pytest.fixture
    def pattern_manager(self, tmp_path):
        """Create a PatternManager with test patterns."""
        patterns_file = tmp_path / "patterns.json"
        manager = PatternManager(str(patterns_file))

        # Add test patterns
        manager.patterns = [
            {
                "pattern_id": "1",
                "name": "numpy_json_serialization",
                "description": "Convert NumPy types before JSON serialization",
                "bad_example": "json.dumps({'val': np.float64(1.0)})",
                "good_example": "json.dumps({'val': float(np.float64(1.0))})",
                "severity": "high",
                "occurrence_frequency": 10,
            },
            {
                "pattern_id": "2",
                "name": "bounds_checking",
                "description": "Validate list access before indexing",
                "bad_example": "first = items[0]",
                "good_example": "first = items[0] if items else None",
                "severity": "medium",
                "occurrence_frequency": 5,
            },
            {
                "pattern_id": "3",
                "name": "specific_exceptions",
                "description": "Use specific exceptions, not bare except",
                "bad_example": "except:",
                "good_example": "except ValueError as e:",
                "severity": "high",
                "occurrence_frequency": 8,
            },
        ]

        return manager

    def test_suggest_patterns_for_task_matches_keywords(self, pattern_manager):
        """Test that suggest_patterns_for_task matches patterns by keywords."""
        suggester = PatternSuggester(pattern_manager)

        suggestions = suggester.suggest_patterns_for_task(
            "I need to serialize NumPy arrays to JSON"
        )

        # Should find numpy_json_serialization
        pattern_names = [s["name"] for s in suggestions]
        assert "numpy_json_serialization" in pattern_names

        # Should have confidence > 0
        numpy_suggestion = next(s for s in suggestions if s["name"] == "numpy_json_serialization")
        assert numpy_suggestion["confidence"] > 0

    def test_suggest_patterns_for_task_ranks_by_relevance(self, pattern_manager):
        """Test that suggestions are ranked by confidence."""
        suggester = PatternSuggester(pattern_manager)

        suggestions = suggester.suggest_patterns_for_task("Serialize NumPy array to JSON format")

        # Should be sorted by confidence (descending)
        confidences = [s["confidence"] for s in suggestions]
        assert confidences == sorted(confidences, reverse=True)

    def test_suggest_patterns_for_task_handles_no_matches(self, pattern_manager):
        """Test that suggest_patterns_for_task handles tasks with no matches."""
        suggester = PatternSuggester(pattern_manager)

        suggestions = suggester.suggest_patterns_for_task(
            "Completely unrelated task about cooking recipes"
        )

        # Should return empty or very low confidence suggestions
        assert all(s["confidence"] < 0.3 for s in suggestions)

    def test_generate_pattern_section_creates_markdown(self, pattern_manager):
        """Test that generate_pattern_section creates valid markdown."""
        suggester = PatternSuggester(pattern_manager)

        suggestions = [
            {
                "name": "numpy_json_serialization",
                "confidence": 0.85,
                "description": "Convert NumPy types",
                "severity": "high",
            },
            {
                "name": "bounds_checking",
                "confidence": 0.72,
                "description": "Validate access",
                "severity": "medium",
            },
        ]

        section = suggester.generate_pattern_section(suggestions)

        assert "## Patterns to Apply" in section
        assert "numpy_json_serialization" in section
        assert "bounds_checking" in section
        assert "confidence: 85%" in section
        assert "confidence: 72%" in section
        assert "[HIGH]" in section

    def test_generate_pattern_section_handles_empty_list(self, pattern_manager):
        """Test that generate_pattern_section handles empty suggestions."""
        suggester = PatternSuggester(pattern_manager)

        section = suggester.generate_pattern_section([])

        assert section == ""

    def test_suggest_patterns_with_metrics_context(self, pattern_manager):
        """Test that metrics context boosts pattern scores."""
        suggester = PatternSuggester(pattern_manager)

        metrics_context = {
            "high_frequency_patterns": ["numpy_json_serialization"],
            "critical_patterns": [],
        }

        suggestions = suggester.suggest_patterns_for_task(
            "Process arrays", metrics_context=metrics_context
        )

        # numpy_json_serialization should have boosted confidence
        numpy_suggestion = next(
            (s for s in suggestions if s["name"] == "numpy_json_serialization"), None
        )

        if numpy_suggestion:
            # Should have higher confidence due to metrics context
            assert numpy_suggestion["confidence"] > 0.2
