"""
Metrics Analyzer Module

Analyzes collected metrics to identify patterns, trends, and effectiveness.
"""

import logging
from collections import Counter
from datetime import datetime, timedelta
from typing import Any, Dict, List, Tuple

logger = logging.getLogger(__name__)


class MetricsAnalyzer:
    """Analyzes metrics to identify patterns and trends."""

    def __init__(self, metrics_data: Dict[str, List[Dict[str, Any]]]):
        """Initialize the metrics analyzer.

        Args:
            metrics_data: Dictionary of metrics data from MetricsCollector
        """
        self.metrics_data = metrics_data

    def get_high_frequency_patterns(self, threshold: int = 2) -> List[Dict[str, Any]]:
        """Identify patterns that occur frequently.

        Args:
            threshold: Minimum occurrence count to be considered high frequency

        Returns:
            List of high frequency patterns with counts
        """
        pattern_counts: Counter = Counter()

        # Count from bugs
        for bug in self.metrics_data.get("bugs", []):
            pattern = bug.get("pattern")
            count = bug.get("count", 1)
            if pattern:
                pattern_counts[pattern] += count

        # Count from test failures
        for failure in self.metrics_data.get("test_failures", []):
            pattern = failure.get("pattern_violated")
            count = failure.get("count", 1)
            if pattern:
                pattern_counts[pattern] += count

        # Count from code reviews
        for review in self.metrics_data.get("code_reviews", []):
            pattern = review.get("pattern")
            if pattern:
                pattern_counts[pattern] += 1

        # Count from deployment issues
        for deployment in self.metrics_data.get("deployment_issues", []):
            pattern = deployment.get("pattern")
            if pattern:
                pattern_counts[pattern] += 1

        # Filter by threshold
        high_freq = [
            {"pattern": pattern, "count": count}
            for pattern, count in pattern_counts.items()
            if count >= threshold
        ]

        # Sort by count descending
        high_freq.sort(key=lambda x: x["count"], reverse=True)

        logger.debug(f"Found {len(high_freq)} high frequency patterns")
        return high_freq

    def detect_new_patterns(self, known_patterns: List[str]) -> List[Dict[str, Any]]:
        """Detect patterns not in the known pattern library.

        Args:
            known_patterns: List of known pattern names

        Returns:
            List of new patterns with details
        """
        all_patterns: Counter = Counter()
        new_pattern_details: Dict[str, List[Dict[str, Any]]] = {}

        # Collect all patterns from metrics
        for bug in self.metrics_data.get("bugs", []):
            pattern = bug.get("pattern")
            if pattern:
                all_patterns[pattern] += bug.get("count", 1)
                if pattern not in new_pattern_details:
                    new_pattern_details[pattern] = []
                new_pattern_details[pattern].append(
                    {
                        "type": "bug",
                        "error": bug.get("error"),
                        "code": bug.get("code"),
                        "file_path": bug.get("file_path"),
                    }
                )

        for failure in self.metrics_data.get("test_failures", []):
            pattern = failure.get("pattern_violated")
            if pattern:
                all_patterns[pattern] += failure.get("count", 1)
                if pattern not in new_pattern_details:
                    new_pattern_details[pattern] = []
                new_pattern_details[pattern].append(
                    {
                        "type": "test_failure",
                        "test_name": failure.get("test_name"),
                        "reason": failure.get("failure_reason"),
                    }
                )

        for review in self.metrics_data.get("code_reviews", []):
            pattern = review.get("pattern")
            if pattern:
                all_patterns[pattern] += 1
                if pattern not in new_pattern_details:
                    new_pattern_details[pattern] = []
                new_pattern_details[pattern].append(
                    {
                        "type": "code_review",
                        "issue_type": review.get("issue_type"),
                        "severity": review.get("severity"),
                    }
                )

        # Filter for new patterns
        new_patterns = []
        for pattern, count in all_patterns.items():
            if pattern not in known_patterns:
                new_patterns.append(
                    {
                        "pattern": pattern,
                        "count": count,
                        "details": new_pattern_details.get(pattern, []),
                    }
                )

        # Sort by count descending
        new_patterns.sort(key=lambda x: x["count"], reverse=True)

        logger.debug(f"Detected {len(new_patterns)} new patterns")
        return new_patterns

    def calculate_effectiveness(self, time_window_days: int = 30) -> Dict[str, Dict[str, Any]]:
        """Calculate pattern effectiveness over time.

        Effectiveness is measured by reduction in occurrences over time.

        Args:
            time_window_days: Number of days to analyze

        Returns:
            Dictionary mapping pattern names to effectiveness scores
        """
        cutoff_date = datetime.now() - timedelta(days=time_window_days)
        pattern_timeline: Dict[str, List[datetime]] = {}

        # Collect timestamps for each pattern
        for bug in self.metrics_data.get("bugs", []):
            pattern = bug.get("pattern")
            timestamp_str = bug.get("timestamp")
            if pattern and timestamp_str:
                try:
                    timestamp = datetime.fromisoformat(timestamp_str)
                    if timestamp >= cutoff_date:
                        if pattern not in pattern_timeline:
                            pattern_timeline[pattern] = []
                        pattern_timeline[pattern].append(timestamp)
                except ValueError:
                    continue

        for failure in self.metrics_data.get("test_failures", []):
            pattern = failure.get("pattern_violated")
            timestamp_str = failure.get("timestamp")
            if pattern and timestamp_str:
                try:
                    timestamp = datetime.fromisoformat(timestamp_str)
                    if timestamp >= cutoff_date:
                        if pattern not in pattern_timeline:
                            pattern_timeline[pattern] = []
                        pattern_timeline[pattern].append(timestamp)
                except ValueError:
                    continue

        # Calculate effectiveness scores
        effectiveness = {}
        for pattern, timestamps in pattern_timeline.items():
            if len(timestamps) < 2:
                # Not enough data to calculate trend
                effectiveness[pattern] = {
                    "score": 0.5,
                    "trend": "insufficient_data",
                    "total_occurrences": len(timestamps),
                }
                continue

            # Sort timestamps
            timestamps.sort()

            # Split into first and second half
            mid = len(timestamps) // 2
            first_half = timestamps[:mid]
            second_half = timestamps[mid:]

            # Calculate rate of occurrences (per day)
            # Use max(1, days) to ensure we never divide by zero
            first_days = max(1, (timestamps[mid - 1] - timestamps[0]).days)
            second_days = max(1, (timestamps[-1] - timestamps[mid]).days)

            first_rate = len(first_half) / first_days
            second_rate = len(second_half) / second_days

            # Calculate effectiveness score (0-1)
            # Higher score = fewer occurrences in second half (pattern is working)
            if first_rate == 0:
                score = 0.5
                trend = "stable"
            else:
                reduction_ratio = (first_rate - second_rate) / first_rate
                score = max(0.0, min(1.0, (reduction_ratio + 1) / 2))

                if reduction_ratio > 0.2:
                    trend = "improving"
                elif reduction_ratio < -0.2:
                    trend = "worsening"
                else:
                    trend = "stable"

            effectiveness[pattern] = {
                "score": float(score),
                "trend": trend,
                "total_occurrences": len(timestamps),
                "first_half_rate": float(first_rate),
                "second_half_rate": float(second_rate),
            }

        logger.debug(f"Calculated effectiveness for {len(effectiveness)} patterns")
        return effectiveness

    def rank_patterns_by_severity(self) -> List[Dict[str, Any]]:
        """Rank patterns by severity and frequency.

        Returns:
            List of patterns ranked by severity (critical > high > medium > low)
            and frequency within each severity level
        """
        pattern_severity: Dict[str, Tuple[str, int]] = {}

        severity_weights = {"critical": 4, "high": 3, "medium": 2, "low": 1}

        # Collect severity information from code reviews
        for review in self.metrics_data.get("code_reviews", []):
            pattern = review.get("pattern")
            severity = review.get("severity", "medium")

            if pattern:
                if pattern not in pattern_severity:
                    pattern_severity[pattern] = (severity, 0)

                # Update to highest severity seen
                current_severity, count = pattern_severity[pattern]
                if severity_weights.get(severity, 0) > severity_weights.get(current_severity, 0):
                    pattern_severity[pattern] = (severity, count + 1)
                else:
                    pattern_severity[pattern] = (current_severity, count + 1)

        # Add bugs with default severity
        for bug in self.metrics_data.get("bugs", []):
            pattern = bug.get("pattern")
            if pattern and pattern not in pattern_severity:
                pattern_severity[pattern] = ("medium", bug.get("count", 1))
            elif pattern:
                severity, count = pattern_severity[pattern]
                pattern_severity[pattern] = (severity, count + bug.get("count", 1))

        # Convert to list and sort
        ranked = [
            {
                "pattern": pattern,
                "severity": severity,
                "count": count,
                "severity_weight": severity_weights.get(severity, 2),
            }
            for pattern, (severity, count) in pattern_severity.items()
        ]

        # Sort by severity weight (descending) then count (descending)
        ranked.sort(key=lambda x: (x["severity_weight"], x["count"]), reverse=True)

        logger.debug(f"Ranked {len(ranked)} patterns by severity")
        return ranked

    def get_summary(self) -> Dict[str, Any]:
        """Get summary statistics of metrics data.

        Returns:
            Dictionary containing summary counts
        """
        return {
            "total": sum(
                [
                    len(self.metrics_data.get("bugs", [])),
                    len(self.metrics_data.get("test_failures", [])),
                    len(self.metrics_data.get("code_reviews", [])),
                    len(self.metrics_data.get("performance_metrics", [])),
                    len(self.metrics_data.get("deployment_issues", [])),
                ]
            ),
            "bugs": len(self.metrics_data.get("bugs", [])),
            "test_failures": len(self.metrics_data.get("test_failures", [])),
            "code_reviews": len(self.metrics_data.get("code_reviews", [])),
            "performance_metrics": len(self.metrics_data.get("performance_metrics", [])),
            "deployment_issues": len(self.metrics_data.get("deployment_issues", [])),
        }

    def generate_report(self) -> Dict[str, Any]:
        """Generate a comprehensive analysis report.

        Returns:
            Dictionary containing analysis results
        """
        report = {
            "summary": self.get_summary(),
            "high_frequency_patterns": self.get_high_frequency_patterns(),
            "ranked_patterns": self.rank_patterns_by_severity(),
            "generated_at": datetime.now().isoformat(),
        }

        logger.debug("Generated analysis report")
        return report

    def get_context(self) -> Dict[str, Any]:
        """Get analysis context for code generation.

        Returns:
            Dictionary with relevant context for code generation
        """
        high_freq = self.get_high_frequency_patterns(threshold=1)
        ranked = self.rank_patterns_by_severity()

        # Get most critical patterns
        critical_patterns = [p["pattern"] for p in ranked if p["severity"] in ["critical", "high"]][
            :5
        ]

        return {
            "high_frequency_patterns": [p["pattern"] for p in high_freq[:10]],
            "critical_patterns": critical_patterns,
            "pattern_counts": {p["pattern"]: p["count"] for p in high_freq},
        }

    def get_severity_distribution(self) -> Dict[str, int]:
        """Get distribution of issue severities.

        Returns:
            Dictionary mapping severity levels to counts
        """
        severity_counts = {"high": 0, "medium": 0, "low": 0}

        # Count from code reviews
        for review in self.metrics_data.get("code_reviews", []):
            severity = review.get("severity", "medium")
            if severity in severity_counts:
                severity_counts[severity] += 1

        # Count from bugs (assume medium severity if not specified)
        bug_count = len(self.metrics_data.get("bugs", []))
        severity_counts["medium"] += bug_count

        # Count from test failures (assume medium severity)
        test_failure_count = len(self.metrics_data.get("test_failures", []))
        severity_counts["medium"] += test_failure_count

        return severity_counts
