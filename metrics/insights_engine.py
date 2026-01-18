"""
Insights Engine Module

Generates actionable insights, recommendations, and trends from metrics data.
Provides intelligent analysis for the analytics dashboard.
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
                        "description": f"Pattern '{best_pattern}' has {best_metrics['score']:.1%} effectiveness with {best_metrics['trend']} trend.",
                        "type": "success",
                        "impact": f"Continue applying this pattern - it's working well",
                    }
                )

                # Worst performing pattern (if score < 50%)
                worst_pattern, worst_metrics = sorted_patterns[0]
                if worst_metrics["score"] < 0.5:
                    insights.append(
                        {
                            "title": f"⚠️ Low Effectiveness: {worst_pattern}",
                            "description": f"Pattern '{worst_pattern}' only has {worst_metrics['score']:.1%} effectiveness.",
                            "type": "warning",
                            "impact": f"Review and update this pattern - it may need improvement",
                        }
                    )

        # High frequency patterns
        high_freq = self.analyzer.get_high_frequency_patterns(threshold=3)
        if high_freq:
            top_pattern = high_freq[0]
            insights.append(
                {
                    "title": f"🔄 High Frequency Pattern: {top_pattern['pattern']}",
                    "description": f"Pattern '{top_pattern['pattern']}' occurs {top_pattern['count']} times - consider automating detection.",
                    "type": "info",
                    "impact": f"High frequency suggests this is a common issue worth addressing",
                }
            )

        # Severity insights
        severity_ranking = self.analyzer.get_severity_distribution()
        if severity_ranking.get("high", 0) > severity_ranking.get("low", 0):
            insights.append(
                {
                    "title": "🚨 High Severity Issues Detected",
                    "description": f"Found {severity_ranking.get('high', 0)} high-severity issues. Focus on critical patterns first.",
                    "type": "danger",
                    "impact": "Address high-severity issues to improve code reliability",
                }
            )

        # Trend insights (mock for now)
        insights.append(
            {
                "title": "📈 Improving Trends",
                "description": "Pattern application has increased by 15% this week.",
                "type": "success",
                "impact": "Keep up the good work - patterns are being adopted",
            }
        )

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
                    "description": f"Create automated checks for this frequently occurring pattern",
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

        Returns:
            List of trend analysis dictionaries
        """
        if not self.analyzer:
            return []

        trends = []

        # Pattern adoption trends (mock data for now)
        trends.append(
            {
                "metric": "Pattern Adoption",
                "trend": "increasing",
                "change": "+15%",
                "period": "last 7 days",
                "description": "More patterns are being applied in code",
            }
        )

        trends.append(
            {
                "metric": "Error Reduction",
                "trend": "stable",
                "change": "-2%",
                "period": "last 30 days",
                "description": "Slight decrease in error rates",
            }
        )

        trends.append(
            {
                "metric": "Code Review Efficiency",
                "trend": "increasing",
                "change": "+8%",
                "period": "last 14 days",
                "description": "Faster code review turnaround time",
            }
        )

        return trends

    def calculate_pattern_roi(self, pattern_name: str) -> Dict[str, Any]:
        """Calculate return on investment for a pattern.

        Args:
            pattern_name: Name of the pattern

        Returns:
            ROI analysis dictionary
        """
        if not self.analyzer:
            return {"error": "No metrics data available"}

        # Get pattern effectiveness
        effectiveness = self.analyzer.calculate_effectiveness()
        pattern_effectiveness = effectiveness.get(pattern_name, {})

        # Mock ROI calculation
        base_cost = 10  # minutes to implement pattern
        occurrences_prevented = pattern_effectiveness.get("score", 0) * 20  # estimated
        time_saved = occurrences_prevented * 5  # minutes saved per occurrence

        roi = {
            "pattern": pattern_name,
            "implementation_cost_minutes": base_cost,
            "estimated_occurrences_prevented": occurrences_prevented,
            "estimated_time_saved_minutes": time_saved,
            "roi_ratio": time_saved / base_cost if base_cost > 0 else 0,
            "break_even_occurrences": base_cost / 5,  # minutes saved per occurrence
            "status": "profitable" if time_saved > base_cost else "not_yet",
        }

        return roi

    def get_team_comparison(self) -> Dict[str, Any]:
        """Compare pattern adoption across team members.

        Returns:
            Team comparison data
        """
        # Mock team comparison data
        return {
            "team_members": [
                {"name": "Alice", "patterns_applied": 25, "effectiveness": 0.85},
                {"name": "Bob", "patterns_applied": 18, "effectiveness": 0.92},
                {"name": "Charlie", "patterns_applied": 32, "effectiveness": 0.78},
            ],
            "team_average": 0.85,
            "top_performer": "Bob",
            "insights": [
                "Bob has highest effectiveness - share techniques with team",
                "Charlie applies most patterns but lower effectiveness - focus on quality",
                "Alice is balanced - good model for consistency",
            ],
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
