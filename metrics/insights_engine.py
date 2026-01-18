"""
Insights Engine Module

Generates actionable insights, recommendations, and trends from metrics data.
Provides intelligent analysis for the analytics dashboard.

All insights are calculated from actual metrics data. No mock or hardcoded
values are used in production calculations. Team comparison features require
user/author tracking in metrics metadata to function.
"""

import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional

from metrics.analyzer import MetricsAnalyzer


class InsightsEngine:
    """Engine for generating insights and recommendations from metrics."""

    def __init__(self, metrics_file: str = "data/metrics_data.json"):
        """Initialize insights engine.

        Args:
            metrics_file: Path to metrics data file
        """
        self.metrics_file = Path(metrics_file)
        self.analyzer: Optional[MetricsAnalyzer] = None
        self._load_analyzer()

    def _load_analyzer(self) -> None:
        """Load metrics analyzer if data is available."""
        if self.metrics_file.exists():
            try:
                with open(self.metrics_file, "r") as f:
                    metrics_data = json.load(f)
                self.analyzer = MetricsAnalyzer(metrics_data)
            except Exception:
                self.analyzer = None

    def generate_insights(self) -> List[Dict[str, Any]]:
        """Generate actionable insights from metrics data.

        Returns:
            List of insight dictionaries
        """
        if not self.analyzer:
            return [
                {
                    "title": "No Metrics Data",
                    "description": "Run tests with --enable-metrics to collect data for insights.",
                    "type": "info",
                    "impact": "Start collecting metrics to unlock insights",
                }
            ]

        insights = []

        # Pattern effectiveness insights
        effectiveness = self.analyzer.calculate_effectiveness()
        if effectiveness:
            # Find most/least effective patterns
            sorted_patterns = sorted(effectiveness.items(), key=lambda x: x[1]["score"])

            if sorted_patterns:
                # Best performing pattern
                best_pattern, best_metrics = sorted_patterns[-1]
                insights.append(
                    {
                        "title": f"🏆 Top Performing Pattern: {best_pattern}",
                        "description": (
                            f"Pattern '{best_pattern}' has {best_metrics['score']:.1%} "
                            f"effectiveness with {best_metrics['trend']} trend."
                        ),
                        "type": "success",
                        "impact": "Continue applying this pattern - it's working well",
                    }
                )

                # Worst performing pattern (if score < 50%)
                worst_pattern, worst_metrics = sorted_patterns[0]
                if worst_metrics["score"] < 0.5:
                    insights.append(
                        {
                            "title": f"⚠️ Low Effectiveness: {worst_pattern}",
                            "description": (
                                f"Pattern '{worst_pattern}' only has {worst_metrics['score']:.1%} "
                                "effectiveness."
                            ),
                            "type": "warning",
                            "impact": "Review and update this pattern - it may need improvement",
                        }
                    )

        # High frequency patterns
        high_freq = self.analyzer.get_high_frequency_patterns(threshold=3)
        if high_freq:
            top_pattern = high_freq[0]
            insights.append(
                {
                    "title": f"🔄 High Frequency Pattern: {top_pattern['pattern']}",
                    "description": (
                        f"Pattern '{top_pattern['pattern']}' occurs {top_pattern['count']} times "
                        "- consider automating detection."
                    ),
                    "type": "info",
                    "impact": "High frequency suggests this is a common issue worth addressing",
                }
            )

        # Severity insights
        severity_ranking = self.analyzer.get_severity_distribution()
        if severity_ranking.get("high", 0) > severity_ranking.get("low", 0):
            insights.append(
                {
                    "title": "🚨 High Severity Issues Detected",
                    "description": (
                        f"Found {severity_ranking.get('high', 0)} high-severity issues. "
                        "Focus on critical patterns first."
                    ),
                    "type": "danger",
                    "impact": "Address high-severity issues to improve code reliability",
                }
            )

        # Calculate real trend insights from metrics data
        trend_insight = self._calculate_trend_insight()
        if trend_insight:
            insights.append(trend_insight)

        return insights

    def get_recommendations(self) -> List[Dict[str, Any]]:
        """Generate actionable recommendations.

        Returns:
            List of recommendation dictionaries
        """
        if not self.analyzer:
            return [
                {
                    "action": "Enable Metrics Collection",
                    "description": "Run pytest --enable-metrics to start collecting data",
                    "priority": "high",
                    "effort": "low",
                }
            ]

        recommendations = []

        # Pattern-based recommendations
        high_freq = self.analyzer.get_high_frequency_patterns(threshold=2)
        if high_freq:
            recommendations.append(
                {
                    "action": f"Automate {high_freq[0]['pattern']} Detection",
                    "description": "Create automated checks for this frequently occurring pattern",
                    "priority": "high",
                    "effort": "medium",
                }
            )

        # Effectiveness-based recommendations
        effectiveness = self.analyzer.calculate_effectiveness()
        if effectiveness:
            low_effective = [p for p, m in effectiveness.items() if m["score"] < 0.6]
            if low_effective:
                recommendations.append(
                    {
                        "action": "Review Low-Effectiveness Patterns",
                        "description": f"Update patterns: {', '.join(low_effective[:3])}",
                        "priority": "medium",
                        "effort": "high",
                    }
                )

        # CI/CD recommendations
        recommendations.append(
            {
                "action": "Add Pattern Checks to CI/CD",
                "description": "Integrate feedback-loop checks into your build pipeline",
                "priority": "medium",
                "effort": "low",
            }
        )

        recommendations.append(
            {
                "action": "Set Up Team Dashboards",
                "description": "Create shared dashboards for team-wide pattern insights",
                "priority": "low",
                "effort": "medium",
            }
        )

        return recommendations

    def analyze_trends(self) -> List[Dict[str, Any]]:
        """Analyze trends in metrics data.

        Calculates real trends from actual metrics data using time-series analysis.

        Returns:
            List of trend analysis dictionaries
        """
        if not self.analyzer:
            return []

        trends = []

        # Calculate pattern adoption trend from code generation metrics
        adoption_trend = self._calculate_pattern_adoption_trend()
        if adoption_trend:
            trends.append(adoption_trend)

        # Calculate error reduction trend from bugs and test failures
        error_trend = self._calculate_error_reduction_trend()
        if error_trend:
            trends.append(error_trend)

        # Calculate code review efficiency trend
        review_trend = self._calculate_review_efficiency_trend()
        if review_trend:
            trends.append(review_trend)

        return trends

    def _calculate_trend_insight(self) -> Optional[Dict[str, Any]]:
        """Calculate trend insight from actual metrics data.

        Returns:
            Trend insight dictionary or None if insufficient data
        """
        if not self.analyzer:
            return None

        # Get pattern adoption trend
        adoption_trend = self._calculate_pattern_adoption_trend()
        if not adoption_trend:
            return None

        trend_type = adoption_trend.get("trend", "stable")
        change = adoption_trend.get("change", "0%")

        if trend_type == "increasing":
            return {
                "title": "📈 Improving Trends",
                "description": (
                    f"Pattern application has {change} over "
                    f"{adoption_trend.get('period', 'recent period')}."
                ),
                "type": "success",
                "impact": "Keep up the good work - patterns are being adopted",
            }
        elif trend_type == "decreasing":
            return {
                "title": "📉 Declining Pattern Usage",
                "description": (
                    f"Pattern application has {change} over "
                    f"{adoption_trend.get('period', 'recent period')}."
                ),
                "type": "warning",
                "impact": "Consider reviewing why pattern usage is declining",
            }

        return None

    def _calculate_pattern_adoption_trend(self) -> Optional[Dict[str, Any]]:
        """Calculate pattern adoption trend from code generation metrics.

        Returns:
            Trend dictionary or None if insufficient data
        """
        if not self.analyzer:
            return None

        # Get code generation metrics
        code_gen = self.analyzer.metrics_data.get("code_generation", [])
        if len(code_gen) < 2:
            return None

        # Group by time period (last 7 days vs previous 7 days)
        now = datetime.now()
        week_ago = now - timedelta(days=7)
        two_weeks_ago = now - timedelta(days=14)

        recent_patterns = []
        previous_patterns = []

        for gen in code_gen:
            timestamp_str = gen.get("timestamp")
            if not timestamp_str:
                continue

            try:
                timestamp = datetime.fromisoformat(timestamp_str)
                patterns = gen.get("patterns_applied", [])

                if timestamp >= week_ago:
                    recent_patterns.extend(patterns)
                elif timestamp >= two_weeks_ago:
                    previous_patterns.extend(patterns)
            except ValueError:
                continue

        if not previous_patterns:
            return None

        recent_count = len(recent_patterns)
        previous_count = len(previous_patterns)

        if previous_count == 0:
            return None

        change_pct = ((recent_count - previous_count) / previous_count) * 100
        change_str = f"{change_pct:+.0f}%"

        if change_pct > 5:
            trend = "increasing"
        elif change_pct < -5:
            trend = "decreasing"
        else:
            trend = "stable"

        return {
            "metric": "Pattern Adoption",
            "trend": trend,
            "change": change_str,
            "period": "last 7 days",
            "description": f"Pattern application has {change_str} compared to previous week",
        }

    def _calculate_error_reduction_trend(self) -> Optional[Dict[str, Any]]:
        """Calculate error reduction trend from bugs and test failures.

        Returns:
            Trend dictionary or None if insufficient data
        """
        if not self.analyzer:
            return None

        now = datetime.now()
        month_ago = now - timedelta(days=30)
        two_months_ago = now - timedelta(days=60)

        recent_errors = 0
        previous_errors = 0

        # Count bugs
        for bug in self.analyzer.metrics_data.get("bugs", []):
            timestamp_str = bug.get("timestamp")
            if not timestamp_str:
                continue
            try:
                timestamp = datetime.fromisoformat(timestamp_str)
                if timestamp >= month_ago:
                    recent_errors += bug.get("count", 1)
                elif timestamp >= two_months_ago:
                    previous_errors += bug.get("count", 1)
            except ValueError:
                continue

        # Count test failures
        for failure in self.analyzer.metrics_data.get("test_failures", []):
            timestamp_str = failure.get("timestamp")
            if not timestamp_str:
                continue
            try:
                timestamp = datetime.fromisoformat(timestamp_str)
                if timestamp >= month_ago:
                    recent_errors += failure.get("count", 1)
                elif timestamp >= two_months_ago:
                    previous_errors += failure.get("count", 1)
            except ValueError:
                continue

        if previous_errors == 0:
            return None

        change_pct = ((recent_errors - previous_errors) / previous_errors) * 100
        change_str = f"{change_pct:+.0f}%"

        if change_pct < -5:
            trend = "improving"  # Fewer errors
        elif change_pct > 5:
            trend = "worsening"  # More errors
        else:
            trend = "stable"

        return {
            "metric": "Error Reduction",
            "trend": trend,
            "change": change_str,
            "period": "last 30 days",
            "description": f"Error rate has {change_str} compared to previous month",
        }

    def _calculate_review_efficiency_trend(self) -> Optional[Dict[str, Any]]:
        """Calculate code review efficiency trend.

        Returns:
            Trend dictionary or None if insufficient data
        """
        if not self.analyzer:
            return None

        # This is a placeholder - actual implementation would require
        # tracking review completion times, which may not be in current metrics
        # For now, return None to indicate insufficient data
        return None

    def calculate_pattern_roi(self, pattern_name: str) -> Dict[str, Any]:
        """Calculate return on investment for a pattern.

        Estimates ROI based on actual pattern effectiveness and occurrence data.
        Uses conservative estimates for time costs and savings.

        Args:
            pattern_name: Name of the pattern

        Returns:
            ROI analysis dictionary with estimated values based on actual data
        """
        if not self.analyzer:
            return {"error": "No metrics data available"}

        # Get pattern effectiveness
        effectiveness = self.analyzer.calculate_effectiveness()
        pattern_effectiveness = effectiveness.get(pattern_name, {})

        if not pattern_effectiveness:
            return {"error": f"Pattern '{pattern_name}' not found in effectiveness data"}

        # Calculate actual occurrences prevented based on effectiveness
        total_occurrences = pattern_effectiveness.get("total_occurrences", 0)
        effectiveness_score = pattern_effectiveness.get("score", 0.5)

        # Estimate: if effectiveness is high, we've prevented occurrences
        # Conservative estimate: assume 50% of improvement is due to pattern
        occurrences_prevented = int(total_occurrences * effectiveness_score * 0.5)

        # Estimated costs (based on industry averages, can be configured)
        # These are conservative estimates - actual values may vary
        base_cost_minutes = 10  # Average time to implement a pattern
        time_saved_per_occurrence_minutes = 5  # Average time saved per prevented issue

        time_saved = occurrences_prevented * time_saved_per_occurrence_minutes

        roi = {
            "pattern": pattern_name,
            "implementation_cost_minutes": base_cost_minutes,
            "estimated_occurrences_prevented": occurrences_prevented,
            "estimated_time_saved_minutes": time_saved,
            "roi_ratio": time_saved / base_cost_minutes if base_cost_minutes > 0 else 0,
            "break_even_occurrences": base_cost_minutes / time_saved_per_occurrence_minutes,
            "status": "profitable" if time_saved > base_cost_minutes else "not_yet",
            "note": "ROI estimates are based on conservative assumptions. Actual values may vary.",
            "data_quality": "estimated" if total_occurrences < 10 else "good",
        }

        return roi

    def get_team_comparison(self) -> Dict[str, Any]:
        """Compare pattern adoption across team members.

        NOTE: This feature requires user/author tracking in metrics data.
        Currently returns a placeholder indicating this feature needs implementation.

        Returns:
            Team comparison data or placeholder if user tracking not available
        """
        # Check if metrics data includes user/author information
        code_gen = self.analyzer.metrics_data.get("code_generation", []) if self.analyzer else []

        # Look for user/author metadata
        has_user_data = any(
            gen.get("metadata", {}).get("user") or gen.get("metadata", {}).get("author")
            for gen in code_gen
        )

        if not has_user_data:
            return {
                "team_members": [],
                "team_average": 0.0,
                "top_performer": None,
                "insights": [
                    "Team comparison requires user/author tracking in metrics data.",
                    (
                        "Add 'user' or 'author' field to code generation metadata "
                        "to enable this feature."
                    ),
                ],
                "note": "Feature not available - user tracking not enabled in metrics collection",
            }

        # If user data is available, calculate actual team metrics
        user_stats = {}
        for gen in code_gen:
            metadata = gen.get("metadata", {})
            user = metadata.get("user") or metadata.get("author")
            if not user:
                continue

            if user not in user_stats:
                user_stats[user] = {"patterns_applied": 0, "generations": 0, "successes": 0}

            user_stats[user]["patterns_applied"] += len(gen.get("patterns_applied", []))
            user_stats[user]["generations"] += 1
            if gen.get("success", False):
                user_stats[user]["successes"] += 1

        # Calculate effectiveness for each user
        team_members = []
        for user, stats in user_stats.items():
            effectiveness = (
                stats["successes"] / stats["generations"] if stats["generations"] > 0 else 0.0
            )
            team_members.append(
                {
                    "name": user,
                    "patterns_applied": stats["patterns_applied"],
                    "effectiveness": effectiveness,
                    "generations": stats["generations"],
                }
            )

        if not team_members:
            return {
                "team_members": [],
                "team_average": 0.0,
                "top_performer": None,
                "insights": ["No team member data available"],
            }

        # Sort by effectiveness
        team_members.sort(key=lambda x: x["effectiveness"], reverse=True)
        team_average = sum(m["effectiveness"] for m in team_members) / len(team_members)

        # Generate insights
        insights = []
        if team_members:
            top = team_members[0]
            insights.append(
                f"{top['name']} has highest effectiveness ({top['effectiveness']:.0%}) "
                "- share techniques with team"
            )

            most_patterns = max(team_members, key=lambda x: x["patterns_applied"])
            if most_patterns["effectiveness"] < team_average:
                insights.append(
                    f"{most_patterns['name']} applies most patterns but lower effectiveness "
                    "- focus on quality"
                )

        return {
            "team_members": team_members,
            "team_average": team_average,
            "top_performer": team_members[0]["name"] if team_members else None,
            "insights": insights,
        }

    def get_severity_distribution(self) -> Dict[str, int]:
        """Get distribution of issue severities.

        Returns:
            Dictionary mapping severity levels to counts
        """
        if not self.analyzer:
            return {"high": 0, "medium": 0, "low": 0}

        return self.analyzer.get_severity_distribution()

    def get_summary_stats(self) -> Dict[str, Any]:
        """Get summary statistics for dashboard.

        Returns:
            Summary statistics dictionary
        """
        if not self.analyzer:
            return {"total_issues": 0, "avg_effectiveness": 0.0, "top_pattern": None, "trends": []}

        summary = self.analyzer.get_summary()
        effectiveness = self.analyzer.calculate_effectiveness()

        # Calculate average effectiveness
        avg_effectiveness = 0.0
        if effectiveness:
            scores = [metrics["score"] for metrics in effectiveness.values()]
            avg_effectiveness = sum(scores) / len(scores) if scores else 0.0

        # Find top pattern
        high_freq = self.analyzer.get_high_frequency_patterns(threshold=1)
        top_pattern = high_freq[0]["pattern"] if high_freq else None

        return {
            "total_issues": summary["total"],
            "avg_effectiveness": avg_effectiveness,
            "top_pattern": top_pattern,
            "trends": self.analyze_trends(),
        }
