"""
Comprehensive tests for the metrics collection and pattern-aware code generation system.
"""

import json
import os
import tempfile
from datetime import datetime, timedelta
from pathlib import Path

import pytest

from metrics.analyzer import MetricsAnalyzer
from metrics.code_generator import PatternAwareGenerator
from metrics.collector import MetricsCollector
from metrics.integrate import MetricsIntegration
from metrics.pattern_manager import PatternManager


class TestMetricsCollector:
    """Tests for MetricsCollector."""

    def test_init(self):
        """Test collector initialization."""
        collector = MetricsCollector()
        assert collector.data["bugs"] == []
        assert collector.data["test_failures"] == []
        assert collector.data["code_reviews"] == []
        assert collector.data["performance_metrics"] == []
        assert collector.data["deployment_issues"] == []

    def test_log_bug(self):
        """Test logging a bug."""
        collector = MetricsCollector()
        collector.log_bug(
            pattern="test_pattern",
            error="Test error",
            code="test code",
            file_path="/test/path.py",
            line=42,
        )

        assert len(collector.data["bugs"]) == 1
        bug = collector.data["bugs"][0]
        assert bug["pattern"] == "test_pattern"
        assert bug["error"] == "Test error"
        assert bug["line"] == 42
        assert bug["count"] == 1
        assert "timestamp" in bug

    def test_log_bug_duplicate_increments_count(self):
        """Test that duplicate bugs increment count."""
        collector = MetricsCollector()
        collector.log_bug(
            pattern="test_pattern",
            error="Same error",
            code="test code",
            file_path="/test/path.py",
            line=42,
        )
        collector.log_bug(
            pattern="test_pattern",
            error="Same error",
            code="test code",
            file_path="/test/path.py",
            line=42,
        )

        assert len(collector.data["bugs"]) == 1
        assert collector.data["bugs"][0]["count"] == 2

    def test_log_test_failure(self):
        """Test logging a test failure."""
        collector = MetricsCollector()
        collector.log_test_failure(
            test_name="test_something",
            failure_reason="Expected X but got Y",
            pattern_violated="some_pattern",
        )

        assert len(collector.data["test_failures"]) == 1
        failure = collector.data["test_failures"][0]
        assert failure["test_name"] == "test_something"
        assert failure["pattern_violated"] == "some_pattern"
        assert failure["count"] == 1

    def test_log_code_review_issue(self):
        """Test logging a code review issue."""
        collector = MetricsCollector()
        collector.log_code_review_issue(
            issue_type="Missing validation",
            pattern="input_validation",
            severity="high",
            file_path="/test/file.py",
            line=10,
        )

        assert len(collector.data["code_reviews"]) == 1
        review = collector.data["code_reviews"][0]
        assert review["severity"] == "high"
        assert review["pattern"] == "input_validation"

    def test_log_code_review_invalid_severity(self):
        """Test code review with invalid severity defaults to medium."""
        collector = MetricsCollector()
        collector.log_code_review_issue(
            issue_type="Test", pattern="test", severity="invalid", file_path="/test.py"
        )

        assert collector.data["code_reviews"][0]["severity"] == "medium"

    def test_log_performance_metric(self):
        """Test logging a performance metric."""
        collector = MetricsCollector()
        collector.log_performance_metric(
            metric_type="memory_error", details={"size": 1000, "context": "test"}
        )

        assert len(collector.data["performance_metrics"]) == 1
        metric = collector.data["performance_metrics"][0]
        assert metric["metric_type"] == "memory_error"
        assert metric["details"]["size"] == 1000

    def test_log_deployment_issue(self):
        """Test logging a deployment issue."""
        collector = MetricsCollector()
        collector.log_deployment_issue(
            issue_type="Config error",
            pattern="configuration",
            environment="production",
            resolution_time_minutes=30,
        )

        assert len(collector.data["deployment_issues"]) == 1
        issue = collector.data["deployment_issues"][0]
        assert issue["environment"] == "production"
        assert issue["resolution_time_minutes"] == 30

    def test_export_json(self):
        """Test exporting to JSON."""
        collector = MetricsCollector()
        collector.log_bug("test", "error", "code", "/path.py", 1)

        json_str = collector.export_json()
        data = json.loads(json_str)

        assert "bugs" in data
        assert len(data["bugs"]) == 1

    def test_export_dict(self):
        """Test exporting to dict."""
        collector = MetricsCollector()
        collector.log_bug("test", "error", "code", "/path.py", 1)

        data = collector.export_dict()
        assert isinstance(data, dict)
        assert len(data["bugs"]) == 1

    def test_get_summary(self):
        """Test getting summary counts."""
        collector = MetricsCollector()
        collector.log_bug("test", "error", "code", "/path.py", 1)
        collector.log_test_failure("test", "reason")

        summary = collector.get_summary()
        assert summary["bugs"] == 1
        assert summary["test_failures"] == 1
        assert summary["total"] == 2

    def test_clear(self):
        """Test clearing all metrics."""
        collector = MetricsCollector()
        collector.log_bug("test", "error", "code", "/path.py", 1)
        collector.clear()

        assert len(collector.data["bugs"]) == 0
        summary = collector.get_summary()
        assert summary["total"] == 0

    def test_load_from_json(self):
        """Test loading from JSON."""
        collector = MetricsCollector()
        test_data = {
            "bugs": [{"pattern": "test", "count": 5}],
            "test_failures": [],
            "code_reviews": [],
            "performance_metrics": [],
            "deployment_issues": [],
        }
        json_str = json.dumps(test_data)

        collector.load_from_json(json_str)
        assert len(collector.data["bugs"]) == 1
        assert collector.data["bugs"][0]["count"] == 5

    def test_log_test_failure_duplicate_increments_count(self):
        """Test that duplicate test failures increment count."""
        collector = MetricsCollector()
        collector.log_test_failure(
            test_name="test_something",
            failure_reason="Expected X but got Y",
            pattern_violated="some_pattern",
        )
        collector.log_test_failure(
            test_name="test_something",
            failure_reason="Expected X but got Y",
            pattern_violated="some_pattern",
        )

        assert len(collector.data["test_failures"]) == 1
        assert collector.data["test_failures"][0]["count"] == 2

    def test_load_from_invalid_json(self):
        """Test loading from invalid JSON raises error."""
        collector = MetricsCollector()
        invalid_json = "not valid json {"

        with pytest.raises(json.JSONDecodeError):
            collector.load_from_json(invalid_json)

    def test_load_from_json_missing_categories_defaults_to_empty(self):
        """Test missing categories are defaulted to empty lists."""
        collector = MetricsCollector()

        json_str = json.dumps(
            {"bugs": [{"pattern": "p", "count": 1}], "test_failures": []}
        )

        collector.load_from_json(json_str)

        assert collector.data["bugs"][0]["pattern"] == "p"
        for category in MetricsCollector.METRIC_CATEGORIES:
            assert category in collector.data
        assert collector.data["code_generation"] == []

    def test_load_from_json_invalid_category_type_restores_previous_state(self):
        """Test invalid category types raise error and revert data."""
        collector = MetricsCollector()
        collector.log_bug("test", "error", "code", "/path.py", 1)
        previous_data = collector.export_dict()

        invalid_json = json.dumps(
            {
                "bugs": "not-a-list",
                "test_failures": [],
                "code_reviews": [],
                "performance_metrics": [],
                "deployment_issues": [],
            }
        )

        with pytest.raises(ValueError, match=r"bugs.*str"):
            collector.load_from_json(invalid_json)

        assert (
            collector.data == previous_data
        ), "Data should be restored after load failure"

    def test_log_from_plan_file_extracts_patterns_and_logs_generation(self, tmp_path):
        """Ensure plan file patterns are parsed and recorded in code generation metrics."""
        plan_file = tmp_path / "task_plan.md"
        plan_file.write_text(
            """
            # Task Plan
            ## Patterns to Apply
            - [ ] numpy_json_serialization (from feedback-loop)
            - [x] bounds_checking
            ## Notes
            - [ ] ignore_me_section
            """
        )

        collector = MetricsCollector()
        patterns = collector.log_from_plan_file(str(plan_file))

        assert patterns == ["numpy_json_serialization", "bounds_checking"]
        assert collector.data["code_generation"][-1]["patterns_applied"] == patterns
        metadata = collector.data["code_generation"][-1]["metadata"]
        assert metadata["source"] == "plan_file"
        assert metadata["plan_path"] == str(plan_file.resolve())


class TestMetricsAnalyzer:
    """Tests for MetricsAnalyzer."""

    def test_init(self):
        """Test analyzer initialization."""
        data = {
            "bugs": [],
            "test_failures": [],
            "code_reviews": [],
            "performance_metrics": [],
            "deployment_issues": [],
        }
        analyzer = MetricsAnalyzer(data)
        assert analyzer.metrics_data == data

    def test_get_high_frequency_patterns(self):
        """Test identifying high frequency patterns."""
        data = {
            "bugs": [
                {"pattern": "pattern1", "count": 5},
                {"pattern": "pattern2", "count": 2},
            ],
            "test_failures": [{"pattern_violated": "pattern1", "count": 3}],
            "code_reviews": [],
            "performance_metrics": [],
            "deployment_issues": [],
        }

        analyzer = MetricsAnalyzer(data)
        high_freq = analyzer.get_high_frequency_patterns(threshold=2)

        assert len(high_freq) == 2
        assert high_freq[0]["pattern"] == "pattern1"
        assert high_freq[0]["count"] == 8  # 5 + 3
        assert high_freq[1]["pattern"] == "pattern2"
        assert high_freq[1]["count"] == 2

    def test_detect_new_patterns(self):
        """Test detecting new patterns."""
        data = {
            "bugs": [
                {"pattern": "new_pattern", "error": "test", "code": "test", "count": 3}
            ],
            "test_failures": [{"pattern_violated": "known_pattern", "count": 1}],
            "code_reviews": [],
            "performance_metrics": [],
            "deployment_issues": [],
        }

        analyzer = MetricsAnalyzer(data)
        known_patterns = ["known_pattern"]
        new_patterns = analyzer.detect_new_patterns(known_patterns)

        assert len(new_patterns) == 1
        assert new_patterns[0]["pattern"] == "new_pattern"
        assert new_patterns[0]["count"] == 3

    def test_calculate_effectiveness_insufficient_data(self):
        """Test effectiveness calculation with insufficient data."""
        data = {
            "bugs": [
                {
                    "pattern": "pattern1",
                    "timestamp": datetime.now().isoformat(),
                    "count": 1,
                }
            ],
            "test_failures": [],
            "code_reviews": [],
            "performance_metrics": [],
            "deployment_issues": [],
        }

        analyzer = MetricsAnalyzer(data)
        effectiveness = analyzer.calculate_effectiveness()

        assert "pattern1" in effectiveness
        assert effectiveness["pattern1"]["trend"] == "insufficient_data"

    def test_rank_patterns_by_severity(self):
        """Test ranking patterns by severity."""
        data = {
            "bugs": [
                {"pattern": "pattern1", "count": 5},
                {"pattern": "pattern2", "count": 3},
            ],
            "test_failures": [],
            "code_reviews": [
                {"pattern": "pattern1", "severity": "critical"},
                {"pattern": "pattern2", "severity": "low"},
            ],
            "performance_metrics": [],
            "deployment_issues": [],
        }

        analyzer = MetricsAnalyzer(data)
        ranked = analyzer.rank_patterns_by_severity()

        assert len(ranked) == 2
        # pattern1 should be first (critical > low)
        assert ranked[0]["pattern"] == "pattern1"
        assert ranked[0]["severity"] == "critical"

    def test_generate_report(self):
        """Test report generation."""
        data = {
            "bugs": [{"pattern": "test", "count": 1}],
            "test_failures": [],
            "code_reviews": [],
            "performance_metrics": [],
            "deployment_issues": [],
        }

        analyzer = MetricsAnalyzer(data)
        report = analyzer.generate_report()

        assert "summary" in report
        assert "high_frequency_patterns" in report
        assert "ranked_patterns" in report
        assert report["summary"]["total_bugs"] == 1

    def test_generate_report_text_format(self, tmp_path, capsys):
        """Ensure report command outputs text format by default."""
        metrics_path = tmp_path / "metrics.json"
        data = {
            "bugs": [{"pattern": "pattern1", "count": 2}],
            "test_failures": [{"pattern_violated": "pattern2", "count": 1}],
            "code_reviews": [],
            "performance_metrics": [],
            "deployment_issues": [],
        }
        metrics_path.write_text(json.dumps(data))

        integration = MetricsIntegration(metrics_file=str(metrics_path))
        integration.generate_report(period="week", format="text")

        output = capsys.readouterr().out
        assert "METRICS ANALYSIS REPORT - WEEK" in output
        assert "Total Bugs: 1" in output
        assert "HIGH FREQUENCY PATTERNS" in output

    def test_generate_report_markdown_format(self, tmp_path, capsys):
        """Ensure report command can output markdown format."""
        metrics_path = tmp_path / "metrics.json"
        data = {
            "bugs": [{"pattern": "pattern1", "count": 3}],
            "test_failures": [{"pattern_violated": "pattern2", "count": 2}],
            "code_reviews": [{"pattern": "pattern3", "severity": "high"}],
            "performance_metrics": [],
            "deployment_issues": [],
        }
        metrics_path.write_text(json.dumps(data))

        integration = MetricsIntegration(metrics_file=str(metrics_path))
        integration.generate_report(period="month", format="markdown")

        output = capsys.readouterr().out
        assert "# Metrics Analysis Report — Month" in output
        assert "## Summary" in output
        assert "- `pattern1`" in output
        assert "## Patterns Ranked by Severity" in output

    def test_get_context(self):
        """Test getting context for code generation."""
        data = {
            "bugs": [{"pattern": "pattern1", "count": 5}],
            "test_failures": [],
            "code_reviews": [{"pattern": "pattern1", "severity": "high"}],
            "performance_metrics": [],
            "deployment_issues": [],
        }

        analyzer = MetricsAnalyzer(data)
        context = analyzer.get_context()

        assert "high_frequency_patterns" in context
        assert "critical_patterns" in context
        assert "pattern_counts" in context


class TestPatternManager:
    """Tests for PatternManager."""

    def test_init_new_file(self, tmp_path):
        """Test initialization with new file."""
        pattern_file = tmp_path / "patterns.json"
        manager = PatternManager(str(pattern_file))

        assert manager.patterns == []
        assert manager.changelog == []

    def test_save_and_load_patterns(self, tmp_path):
        """Test saving and loading patterns."""
        pattern_file = tmp_path / "patterns.json"
        manager = PatternManager(str(pattern_file))

        # Add a pattern
        manager.patterns.append({"name": "test_pattern", "occurrence_frequency": 5})

        # Save
        manager.save_patterns()
        assert pattern_file.exists()

        # Load in new instance
        manager2 = PatternManager(str(pattern_file))
        assert len(manager2.patterns) == 1
        assert manager2.patterns[0]["name"] == "test_pattern"

    def test_update_frequencies(self, tmp_path):
        """Test updating pattern frequencies."""
        pattern_file = tmp_path / "patterns.json"
        manager = PatternManager(str(pattern_file))

        # Add initial pattern
        manager.patterns.append({"name": "pattern1", "occurrence_frequency": 0})

        # Update frequency
        frequency_data = [{"pattern": "pattern1", "count": 5}]
        manager.update_frequencies(frequency_data)

        assert manager.patterns[0]["occurrence_frequency"] == 5
        assert "last_occurrence" in manager.patterns[0]

    def test_add_new_patterns(self, tmp_path):
        """Test adding new patterns."""
        pattern_file = tmp_path / "patterns.json"
        manager = PatternManager(str(pattern_file))

        new_patterns = [
            {
                "pattern": "new_pattern",
                "count": 3,
                "details": [{"type": "bug", "error": "Test error"}],
            }
        ]

        manager.add_new_patterns(new_patterns)

        assert len(manager.patterns) == 1
        assert manager.patterns[0]["name"] == "new_pattern"
        assert manager.patterns[0]["occurrence_frequency"] == 3

    def test_add_duplicate_pattern_skipped(self, tmp_path):
        """Test that duplicate patterns are skipped."""
        pattern_file = tmp_path / "patterns.json"
        manager = PatternManager(str(pattern_file))

        manager.patterns.append({"name": "existing"})

        new_patterns = [{"pattern": "existing", "count": 1, "details": []}]
        manager.add_new_patterns(new_patterns)

        assert len(manager.patterns) == 1  # No duplicate added

    def test_archive_unused_patterns(self, tmp_path):
        """Test archiving unused patterns."""
        pattern_file = tmp_path / "patterns.json"
        manager = PatternManager(str(pattern_file))

        # Add pattern with old timestamp
        old_date = (datetime.now() - timedelta(days=100)).isoformat()
        manager.patterns.append({"name": "old_pattern", "last_occurrence": old_date})

        # Add pattern with recent timestamp
        recent_date = datetime.now().isoformat()
        manager.patterns.append(
            {"name": "recent_pattern", "last_occurrence": recent_date}
        )

        # Archive patterns older than 90 days
        archived = manager.archive_unused_patterns(days=90)

        assert len(archived) == 1
        assert "old_pattern" in archived
        assert len(manager.patterns) == 1
        assert manager.patterns[0]["name"] == "recent_pattern"

    def test_get_pattern_names(self, tmp_path):
        """Test getting pattern names."""
        pattern_file = tmp_path / "patterns.json"
        manager = PatternManager(str(pattern_file))

        manager.patterns.extend([{"name": "pattern1"}, {"name": "pattern2"}])

        names = manager.get_pattern_names()
        assert names == ["pattern1", "pattern2"]

    def test_get_pattern_by_name(self, tmp_path):
        """Test getting pattern by name."""
        pattern_file = tmp_path / "patterns.json"
        manager = PatternManager(str(pattern_file))

        manager.patterns.append({"name": "test", "data": "value"})

        pattern = manager.get_pattern_by_name("test")
        assert pattern is not None
        assert pattern["data"] == "value"

        missing = manager.get_pattern_by_name("nonexistent")
        assert missing is None


class TestPatternAwareGenerator:
    """Tests for PatternAwareGenerator."""

    def test_init(self):
        """Test generator initialization."""
        patterns = [{"name": "test_pattern"}]
        generator = PatternAwareGenerator(patterns)

        assert generator.pattern_library == patterns
        assert generator.pattern_library_version == "1.0.0"

    def test_analyze_prompt_numpy(self):
        """Test prompt analysis for NumPy context."""
        generator = PatternAwareGenerator([])

        indicators = generator._analyze_prompt("Process numpy array and return JSON")

        assert indicators["numpy"] is True
        assert indicators["json"] is True

    def test_analyze_prompt_list(self):
        """Test prompt analysis for list access context."""
        generator = PatternAwareGenerator([])

        indicators = generator._analyze_prompt("Get first item from list")

        assert indicators["list_access"] is True

    def test_match_patterns(self):
        """Test pattern matching based on context."""
        patterns = [
            {
                "name": "numpy_json_serialization",
                "severity": "high",
                "description": "Test",
            }
        ]
        generator = PatternAwareGenerator(patterns)

        context_indicators = {"numpy": True, "json": True}
        matched = generator._match_patterns(context_indicators, None)

        assert len(matched) == 1
        assert matched[0]["pattern"]["name"] == "numpy_json_serialization"
        assert matched[0]["confidence"] > 0

    def test_prioritize_patterns_by_severity(self):
        """Test pattern prioritization by severity."""
        patterns = [
            {"name": "pattern1", "severity": "critical"},
            {"name": "pattern2", "severity": "low"},
        ]
        generator = PatternAwareGenerator(patterns)

        matched = [
            {"pattern": patterns[0], "confidence": 0.9, "severity": "critical"},
            {"pattern": patterns[1], "confidence": 0.9, "severity": "low"},
        ]

        to_apply, to_suggest = generator._prioritize_patterns(matched, True, 0.8)

        assert len(to_apply) == 1  # Only critical applied
        assert to_apply[0]["pattern"]["name"] == "pattern1"
        assert len(to_suggest) == 1

    def test_generate_code(self):
        """Test code generation."""
        patterns = [
            {
                "name": "numpy_json_serialization",
                "severity": "high",
                "description": "Convert NumPy types",
            }
        ]
        generator = PatternAwareGenerator(patterns)

        result = generator.generate(
            prompt="Process NumPy array and return JSON",
            apply_patterns=True,
            min_confidence=0.5,
        )

        assert result.code is not None
        assert len(result.code) > 0
        assert "numpy" in result.code.lower() or "json" in result.code.lower()
        assert result.metadata is not None
        assert result.report is not None
        assert 0 <= result.confidence <= 1

    def test_generate_imports_numpy(self):
        """Test import generation for NumPy pattern."""
        patterns = [{"name": "numpy_json_serialization"}]
        generator = PatternAwareGenerator(patterns)

        matched = [{"pattern": patterns[0]}]
        imports = generator._generate_imports(matched)

        assert "import json" in imports
        assert "import numpy as np" in imports

    def test_calculate_confidence(self):
        """Test confidence calculation."""
        generator = PatternAwareGenerator([])

        matched = [{"confidence": 0.9}, {"confidence": 0.8}, {"confidence": 0.7}]

        confidence = generator._calculate_confidence(matched)

        assert 0 < confidence <= 1
        assert confidence == pytest.approx((0.9 + 0.8 + 0.7) / 3)


class TestIntegration:
    """Integration tests for the complete workflow."""

    def test_end_to_end_workflow(self, tmp_path):
        """Test complete workflow from collection to generation."""
        # Step 1: Collect metrics
        collector = MetricsCollector()
        collector.log_bug(
            pattern="numpy_json_serialization",
            error="TypeError",
            code="test",
            file_path="/test.py",
            line=1,
        )
        collector.log_bug(
            pattern="numpy_json_serialization",
            error="TypeError",
            code="test",
            file_path="/test.py",
            line=1,
        )

        # Step 2: Analyze metrics
        metrics_data = collector.export_dict()
        analyzer = MetricsAnalyzer(metrics_data)
        high_freq = analyzer.get_high_frequency_patterns()

        assert len(high_freq) >= 1
        assert high_freq[0]["pattern"] == "numpy_json_serialization"
        assert high_freq[0]["count"] == 2

        # Step 3: Manage patterns
        pattern_file = tmp_path / "patterns.json"
        manager = PatternManager(str(pattern_file))
        manager.patterns.append(
            {
                "name": "numpy_json_serialization",
                "description": "Test",
                "severity": "high",
                "occurrence_frequency": 0,
            }
        )

        manager.update_frequencies(high_freq)
        assert manager.patterns[0]["occurrence_frequency"] == 2

        # Step 4: Generate code
        generator = PatternAwareGenerator(manager.get_all_patterns())
        result = generator.generate("Process NumPy array to JSON")

        assert result.code is not None
        assert len(result.patterns_applied) > 0

    def test_pattern_library_persistence(self, tmp_path):
        """Test that pattern library persists across sessions."""
        pattern_file = tmp_path / "patterns.json"

        # Session 1: Create and save
        manager1 = PatternManager(str(pattern_file))
        manager1.patterns.append(
            {"name": "test_pattern", "occurrence_frequency": 5, "severity": "high"}
        )
        manager1.save_patterns()

        # Session 2: Load and verify
        manager2 = PatternManager(str(pattern_file))
        assert len(manager2.patterns) == 1
        assert manager2.patterns[0]["name"] == "test_pattern"
        assert manager2.patterns[0]["occurrence_frequency"] == 5

    def test_metrics_export_and_import(self):
        """Test exporting and importing metrics."""
        # Export
        collector1 = MetricsCollector()
        collector1.log_bug("pattern1", "error", "code", "/path.py", 1)
        json_str = collector1.export_json()

        # Import
        collector2 = MetricsCollector()
        collector2.load_from_json(json_str)

        assert len(collector2.data["bugs"]) == 1
        assert collector2.data["bugs"][0]["pattern"] == "pattern1"
