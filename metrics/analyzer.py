"""
Metrics Analyzer Module

Analyzes collected metrics to identify patterns, trends, and effectiveness.

This module implements statistical analysis methods for pattern effectiveness:
- Exponential smoothing for trend analysis
- Mann-Whitney U test for statistical significance
- Bootstrap confidence intervals
- Moving averages to reduce noise

All algorithms use standard statistical methods (non-proprietary).
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
        """Calculate pattern effectiveness over time with statistical rigor.

        Uses enhanced statistical methods including:
        - Exponential smoothing for trend analysis
        - Mann-Whitney U test for significance testing
        - Bootstrap confidence intervals
        - Moving averages to reduce noise

        Effectiveness is measured by reduction in occurrences over time.

        Args:
            time_window_days: Number of days to analyze

        Returns:
            Dictionary mapping pattern names to effectiveness scores with statistical metrics
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

        # Calculate effectiveness scores with enhanced statistical methods
        effectiveness = {}
        for pattern, timestamps in pattern_timeline.items():
            if len(timestamps) < 2:
                # Not enough data to calculate trend
                effectiveness[pattern] = {
                    "score": 0.5,
                    "trend": "insufficient_data",
                    "total_occurrences": len(timestamps),
                    "confidence_interval": (0.0, 1.0),
                    "statistical_significance": False,
                    "method": "insufficient_data",
                }
                continue

            # Sort timestamps
            timestamps.sort()

            # Use enhanced statistical analysis
            stats_result = self._calculate_effectiveness_statistics(timestamps)

            effectiveness[pattern] = {
                "score": float(stats_result["score"]),
                "trend": stats_result["trend"],
                "total_occurrences": len(timestamps),
                "first_half_rate": float(stats_result["first_half_rate"]),
                "second_half_rate": float(stats_result["second_half_rate"]),
                "confidence_interval": stats_result["confidence_interval"],
                "statistical_significance": stats_result["statistical_significance"],
                "p_value": stats_result.get("p_value"),
                "method": stats_result["method"],
                "smoothed_trend": stats_result.get("smoothed_trend"),
            }

        logger.debug(f"Calculated effectiveness for {len(effectiveness)} patterns")
        return effectiveness

    def _calculate_effectiveness_statistics(self, timestamps: List[datetime]) -> Dict[str, Any]:
        """Calculate effectiveness using enhanced statistical methods.

        Args:
            timestamps: Sorted list of timestamps for pattern occurrences

        Returns:
            Dictionary with effectiveness metrics and statistical measures
        """
        # Minimum sample size for statistical analysis
        MIN_SAMPLE_SIZE = 4

        if len(timestamps) < MIN_SAMPLE_SIZE:
            # Fall back to simple split-half for small samples
            return self._simple_split_half_analysis(timestamps)

        # Method 1: Exponential smoothing with moving averages
        smoothed_result = self._exponential_smoothing_analysis(timestamps)

        # Method 2: Statistical significance testing (Mann-Whitney U test)
        significance_result = self._mann_whitney_test(timestamps)

        # Method 3: Bootstrap confidence intervals
        confidence_interval = self._bootstrap_confidence_interval(timestamps)

        # Combine results
        score = smoothed_result["score"]
        trend = smoothed_result["trend"]

        # Adjust score based on statistical significance
        if significance_result["significant"]:
            # Boost confidence if statistically significant
            if trend == "improving":
                score = min(1.0, score * 1.1)
            elif trend == "worsening":
                score = max(0.0, score * 0.9)

        return {
            "score": max(0.0, min(1.0, score)),
            "trend": trend,
            "first_half_rate": smoothed_result["first_half_rate"],
            "second_half_rate": smoothed_result["second_half_rate"],
            "confidence_interval": confidence_interval,
            "statistical_significance": significance_result["significant"],
            "p_value": significance_result.get("p_value"),
            "method": "enhanced_statistical",
            "smoothed_trend": smoothed_result.get("smoothed_trend"),
        }

    def _simple_split_half_analysis(self, timestamps: List[datetime]) -> Dict[str, Any]:
        """Simple split-half analysis for small sample sizes.

        Args:
            timestamps: Sorted list of timestamps

        Returns:
            Basic effectiveness metrics
        """
        mid = len(timestamps) // 2
        first_half = timestamps[:mid]
        second_half = timestamps[mid:]

        first_days = max(1, (timestamps[mid - 1] - timestamps[0]).days)
        second_days = max(1, (timestamps[-1] - timestamps[mid]).days)

        first_rate = len(first_half) / first_days
        second_rate = len(second_half) / second_days

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

        return {
            "score": score,
            "trend": trend,
            "first_half_rate": first_rate,
            "second_half_rate": second_rate,
            "method": "simple_split_half",
        }

    def _exponential_smoothing_analysis(self, timestamps: List[datetime]) -> Dict[str, Any]:
        """Analyze trends using exponential smoothing and moving averages.

        Args:
            timestamps: Sorted list of timestamps

        Returns:
            Effectiveness metrics with smoothed trends
        """
        # Convert timestamps to daily counts
        daily_counts = self._timestamps_to_daily_counts(timestamps)

        if len(daily_counts) < 2:
            return self._simple_split_half_analysis(timestamps)

        # Apply exponential smoothing (alpha = 0.3 for moderate smoothing)
        alpha = 0.3
        smoothed = [daily_counts[0]]
        for i in range(1, len(daily_counts)):
            smoothed.append(alpha * daily_counts[i] + (1 - alpha) * smoothed[i - 1])

        # Calculate trend from smoothed data
        mid = len(smoothed) // 2
        first_half_avg = sum(smoothed[:mid]) / len(smoothed[:mid]) if mid > 0 else 0
        second_half_avg = sum(smoothed[mid:]) / len(smoothed[mid:]) if len(smoothed) > mid else 0

        # Calculate rates (per day)
        first_half_rate = first_half_avg
        second_half_rate = second_half_avg

        # Calculate effectiveness
        if first_half_rate == 0:
            score = 0.5
            trend = "stable"
        else:
            reduction_ratio = (first_half_rate - second_half_rate) / first_half_rate
            score = max(0.0, min(1.0, (reduction_ratio + 1) / 2))

            if reduction_ratio > 0.2:
                trend = "improving"
            elif reduction_ratio < -0.2:
                trend = "worsening"
            else:
                trend = "stable"

        return {
            "score": score,
            "trend": trend,
            "first_half_rate": first_half_rate,
            "second_half_rate": second_half_rate,
            "smoothed_trend": smoothed,
        }

    def _timestamps_to_daily_counts(self, timestamps: List[datetime]) -> List[float]:
        """Convert timestamps to daily occurrence counts.

        Args:
            timestamps: Sorted list of timestamps

        Returns:
            List of daily counts
        """
        if not timestamps:
            return []

        start_date = timestamps[0].date()
        end_date = timestamps[-1].date()
        days = (end_date - start_date).days + 1

        daily_counts = [0.0] * days
        for ts in timestamps:
            day_index = (ts.date() - start_date).days
            if 0 <= day_index < days:
                daily_counts[day_index] += 1.0

        return daily_counts

    def _mann_whitney_test(self, timestamps: List[datetime]) -> Dict[str, Any]:
        """Perform Mann-Whitney U test for statistical significance.

        Tests if there's a significant difference between first and second half.

        Args:
            timestamps: Sorted list of timestamps

        Returns:
            Dictionary with significance test results
        """
        if len(timestamps) < 4:
            return {"significant": False, "p_value": None}

        # Convert to numeric values (days since first occurrence)
        start_time = timestamps[0]
        numeric_values = [(ts - start_time).total_seconds() / 86400.0 for ts in timestamps]

        mid = len(numeric_values) // 2
        first_half = numeric_values[:mid]
        second_half = numeric_values[mid:]

        # Simplified Mann-Whitney U test
        # For small samples, use rank-based approach
        all_values = first_half + second_half
        ranks = sorted(range(len(all_values)), key=lambda i: all_values[i])
        rank_dict = {i: rank + 1 for rank, i in enumerate(ranks)}

        # Calculate U statistic
        n1, n2 = len(first_half), len(second_half)
        r1 = sum(rank_dict[i] for i in range(n1))
        u1 = n1 * n2 + (n1 * (n1 + 1)) / 2 - r1
        u2 = n1 * n2 - u1
        u_stat = min(u1, u2)

        # Approximate p-value for small samples (normal approximation)
        # This is a simplified version - for production, use scipy.stats.mannwhitneyu
        mean_u = n1 * n2 / 2
        var_u = n1 * n2 * (n1 + n2 + 1) / 12
        if var_u > 0:
            z_score = abs(u_stat - mean_u) / (var_u**0.5)
            # Approximate p-value (two-tailed)
            # For z > 1.96, p < 0.05; for z > 2.58, p < 0.01
            if z_score > 2.58:
                p_value = 0.01
            elif z_score > 1.96:
                p_value = 0.05
            else:
                p_value = 0.1
        else:
            p_value = 1.0

        significant = p_value < 0.05

        return {
            "significant": significant,
            "p_value": p_value,
            "u_statistic": u_stat,
        }

    def _bootstrap_confidence_interval(
        self, timestamps: List[datetime], n_bootstrap: int = 1000, confidence: float = 0.95
    ) -> Tuple[float, float]:
        """Calculate bootstrap confidence interval for effectiveness score.

        Args:
            timestamps: Sorted list of timestamps
            n_bootstrap: Number of bootstrap samples
            confidence: Confidence level (default 0.95 for 95% CI)

        Returns:
            Tuple of (lower_bound, upper_bound)
        """
        if len(timestamps) < 4:
            return (0.0, 1.0)

        import random

        # Convert to daily counts for bootstrap
        daily_counts = self._timestamps_to_daily_counts(timestamps)

        bootstrap_scores = []
        for _ in range(n_bootstrap):
            # Resample with replacement
            resampled = random.choices(daily_counts, k=len(daily_counts))
            # Calculate score from resampled data
            mid = len(resampled) // 2
            first_avg = sum(resampled[:mid]) / len(resampled[:mid]) if mid > 0 else 0
            second_avg = sum(resampled[mid:]) / len(resampled[mid:]) if len(resampled) > mid else 0

            if first_avg == 0:
                score = 0.5
            else:
                reduction = (first_avg - second_avg) / first_avg
                score = max(0.0, min(1.0, (reduction + 1) / 2))
            bootstrap_scores.append(score)

        # Calculate confidence interval
        bootstrap_scores.sort()
        alpha = 1 - confidence
        lower_idx = int(alpha / 2 * len(bootstrap_scores))
        upper_idx = int((1 - alpha / 2) * len(bootstrap_scores))

        lower_bound = bootstrap_scores[lower_idx] if lower_idx < len(bootstrap_scores) else 0.0
        upper_bound = bootstrap_scores[upper_idx - 1] if upper_idx > 0 else 1.0

        return (lower_bound, upper_bound)

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
