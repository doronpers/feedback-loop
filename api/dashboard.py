"""
Dashboard API Module

Provides REST API endpoints for the feedback-loop analytics dashboard.
Serves data for charts, metrics, and insights visualization.
"""

import json
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel

from metrics.analyzer import MetricsAnalyzer
from metrics.insights_engine import InsightsEngine

# Create router
router = APIRouter(prefix="/dashboard", tags=["dashboard"])


# Pydantic models for API responses
class DashboardSummary(BaseModel):
    """Dashboard summary data model."""

    total_bugs: int
    total_test_failures: int
    total_code_reviews: int
    total_deployment_issues: int
    pattern_effectiveness_score: float
    top_patterns: List[Dict[str, Any]]
    recent_activity: List[Dict[str, Any]]


class ChartData(BaseModel):
    """Chart data model."""

    labels: List[str]
    datasets: List[Dict[str, Any]]


class InsightsResponse(BaseModel):
    """Insights response model."""

    insights: List[Dict[str, Any]]
    recommendations: List[Dict[str, Any]]
    trends: List[Dict[str, Any]]


# Global instances (in production, these would be injected)
_insights_engine = None
_metrics_analyzer = None


def get_insights_engine() -> InsightsEngine:
    """Get or create insights engine instance."""
    global _insights_engine
    if _insights_engine is None:
        _insights_engine = InsightsEngine()
    return _insights_engine


def get_metrics_analyzer(metrics_file: str = "data/metrics_data.json") -> Optional[MetricsAnalyzer]:
    """Get or create metrics analyzer instance."""
    global _metrics_analyzer
    if _metrics_analyzer is None and Path(metrics_file).exists():
        try:
            with open(metrics_file, "r") as f:
                metrics_data = json.load(f)
            _metrics_analyzer = MetricsAnalyzer(metrics_data)
        except Exception:
            return None
    return _metrics_analyzer


@router.get("/", response_class=HTMLResponse)
async def dashboard_home():
    """Serve the main dashboard HTML page."""
    # #region agent log
    import json

    log_path = "/Volumes/Treehorn/Gits/sono-platform/.cursor/debug.log"
    try:
        with open(log_path, "a") as f:
            f.write(
                json.dumps(
                    {
                        "sessionId": "debug-session",
                        "runId": "run1",
                        "hypothesisId": "H5",
                        "location": "dashboard.py:79",
                        "message": "dashboard_home route called",
                        "data": {"route": "/dashboard/"},
                        "timestamp": int(__import__("time").time() * 1000),
                    }
                )
                + "\n"
            )
    except Exception:
        pass
    # #endregion

    template_path = Path(__file__).parent / "templates" / "dashboard.html"

    # #region agent log
    try:
        with open(log_path, "a") as f:
            f.write(
                json.dumps(
                    {
                        "sessionId": "debug-session",
                        "runId": "run1",
                        "hypothesisId": "H5",
                        "location": "dashboard.py:87",
                        "message": "Template path check",
                        "data": {
                            "template_path": str(template_path),
                            "exists": template_path.exists(),
                            "parent": str(Path(__file__).parent),
                        },
                        "timestamp": int(__import__("time").time() * 1000),
                    }
                )
                + "\n"
            )
    except Exception:
        pass
    # #endregion

    if not template_path.exists():
        # #region agent log
        try:
            with open(log_path, "a") as f:
                f.write(
                    json.dumps(
                        {
                            "sessionId": "debug-session",
                            "runId": "run1",
                            "hypothesisId": "H5",
                            "location": "dashboard.py:92",
                            "message": "Template not found",
                            "data": {"template_path": str(template_path)},
                            "timestamp": int(__import__("time").time() * 1000),
                        }
                    )
                    + "\n"
                )
        except Exception:
            pass
        # #endregion
        raise HTTPException(status_code=404, detail="Dashboard template not found")

    with open(template_path, "r", encoding="utf-8") as f:
        html_content = f.read()

    # #region agent log
    try:
        with open(log_path, "a") as f:
            f.write(
                json.dumps(
                    {
                        "sessionId": "debug-session",
                        "runId": "run1",
                        "hypothesisId": "H5",
                        "location": "dashboard.py:100",
                        "message": "Template loaded successfully",
                        "data": {"content_length": len(html_content)},
                        "timestamp": int(__import__("time").time() * 1000),
                    }
                )
                + "\n"
            )
    except Exception:
        pass
    # #endregion

    return HTMLResponse(content=html_content)


@router.get("/summary")
async def get_dashboard_summary(metrics_file: str = "data/metrics_data.json") -> DashboardSummary:
    """Get dashboard summary data."""
    analyzer = get_metrics_analyzer(metrics_file)

    if not analyzer:
        # Return empty summary if no metrics available
        return DashboardSummary(
            total_bugs=0,
            total_test_failures=0,
            total_code_reviews=0,
            total_deployment_issues=0,
            pattern_effectiveness_score=0.0,
            top_patterns=[],
            recent_activity=[],
        )

    # Get summary data
    summary = analyzer.get_summary()

    # Get top patterns
    high_freq = analyzer.get_high_frequency_patterns(threshold=1)[:5]

    # Calculate pattern effectiveness
    effectiveness = analyzer.calculate_effectiveness()
    avg_effectiveness = 0.0
    if effectiveness:
        scores = [metrics["score"] for metrics in effectiveness.values()]
        avg_effectiveness = sum(scores) / len(scores) if scores else 0.0

    # Get recent activity (mock data for now)
    recent_activity = [
        {
            "type": "pattern_applied",
            "description": "NumPy serialization pattern applied",
            "timestamp": datetime.now().isoformat(),
            "severity": "high",
        },
        {
            "type": "test_failure",
            "description": "Bounds checking test failed",
            "timestamp": (datetime.now() - timedelta(hours=2)).isoformat(),
            "severity": "medium",
        },
    ]

    return DashboardSummary(
        total_bugs=summary["bugs"],
        total_test_failures=summary["test_failures"],
        total_code_reviews=summary["code_reviews"],
        total_deployment_issues=summary["deployment_issues"],
        pattern_effectiveness_score=avg_effectiveness,
        top_patterns=high_freq,
        recent_activity=recent_activity,
    )


@router.get("/charts/patterns-over-time")
async def get_patterns_over_time_chart(
    days: int = Query(30, description="Number of days to look back")
) -> ChartData:
    """Get patterns over time chart data."""
    analyzer = get_metrics_analyzer()

    if not analyzer:
        return ChartData(labels=[], datasets=[])

    # Generate mock time series data (in production, this would analyze real timestamps)
    labels = []
    data = []

    for i in range(days, 0, -1):
        date = datetime.now() - timedelta(days=i)
        labels.append(date.strftime("%Y-%m-%d"))

        # Mock data - in production, this would be calculated from real metrics
        data.append(max(0, 10 - i + (i % 3)))

    return ChartData(
        labels=labels,
        datasets=[
            {
                "label": "Pattern Violations",
                "data": data,
                "borderColor": "rgb(75, 192, 192)",
                "backgroundColor": "rgba(75, 192, 192, 0.2)",
                "tension": 0.1,
            }
        ],
    )


@router.get("/charts/severity-distribution")
async def get_severity_distribution_chart() -> ChartData:
    """Get severity distribution pie chart data."""
    analyzer = get_metrics_analyzer()

    if not analyzer:
        return ChartData(labels=[], datasets=[])

    # Get severity rankings
    severity_data = analyzer.get_severity_distribution()

    labels = []
    data = []
    colors = []

    severity_colors = {
        "high": "#dc3545",  # red
        "medium": "#ffc107",  # yellow
        "low": "#28a745",  # green
    }

    for severity, count in severity_data.items():
        labels.append(severity.title())
        data.append(count)
        colors.append(severity_colors.get(severity, "#6c757d"))

    return ChartData(
        labels=labels,
        datasets=[
            {"data": data, "backgroundColor": colors, "borderColor": colors, "borderWidth": 1}
        ],
    )


@router.get("/charts/pattern-effectiveness")
async def get_pattern_effectiveness_chart() -> ChartData:
    """Get pattern effectiveness bar chart data."""
    analyzer = get_metrics_analyzer()

    if not analyzer:
        return ChartData(labels=[], datasets=[])

    # Get pattern effectiveness
    effectiveness = analyzer.calculate_effectiveness()

    labels = []
    scores = []
    trends = []

    for pattern, metrics in list(effectiveness.items())[:10]:  # Top 10
        labels.append(pattern)
        scores.append(metrics["score"] * 100)  # Convert to percentage
        trends.append(metrics.get("trend", "stable"))

    return ChartData(
        labels=labels,
        datasets=[
            {
                "label": "Effectiveness Score (%)",
                "data": scores,
                "backgroundColor": "rgba(54, 162, 235, 0.8)",
                "borderColor": "rgba(54, 162, 235, 1)",
                "borderWidth": 1,
            }
        ],
    )


@router.get("/charts/adoption-reduction")
async def get_adoption_reduction_chart() -> ChartData:
    """Get pattern adoption vs bug reduction chart data."""
    analyzer = get_metrics_analyzer()

    if not analyzer:
        return ChartData(labels=[], datasets=[])

    # Mock adoption vs reduction data (in production, this would analyze real trends)
    labels = []
    adoption_data = []
    reduction_data = []

    for i in range(14, 0, -1):  # Last 14 days
        date = datetime.now() - timedelta(days=i)
        labels.append(date.strftime("%m/%d"))

        # Mock data showing patterns adopted and bugs reduced
        adoption_data.append(max(0, 20 - i + (i % 3)))
        reduction_data.append(max(0, 15 - i + (i % 2)))

    return ChartData(
        labels=labels,
        datasets=[
            {
                "label": "Patterns Adopted",
                "data": adoption_data,
                "borderColor": "rgb(75, 192, 192)",
                "backgroundColor": "rgba(75, 192, 192, 0.2)",
                "tension": 0.1,
            },
            {
                "label": "Bugs Reduced",
                "data": reduction_data,
                "borderColor": "rgb(255, 99, 132)",
                "backgroundColor": "rgba(255, 99, 132, 0.2)",
                "tension": 0.1,
            },
        ],
    )


@router.get("/charts/pattern-roi")
async def get_pattern_roi_chart() -> ChartData:
    """Get pattern ROI analysis chart data."""
    insights_engine = get_insights_engine()

    labels = []
    roi_data = []

    # Get top patterns and calculate ROI
    analyzer = get_metrics_analyzer()
    if analyzer:
        high_freq = analyzer.get_high_frequency_patterns(threshold=1)[:8]  # Top 8

        for pattern_info in high_freq:
            pattern_name = pattern_info["pattern"]
            roi = insights_engine.calculate_pattern_roi(pattern_name)

            if "roi_ratio" in roi:
                labels.append(pattern_name)
                roi_data.append(roi["roi_ratio"])

    return ChartData(
        labels=labels,
        datasets=[
            {
                "label": "ROI Ratio",
                "data": roi_data,
                "backgroundColor": [
                    "rgba(255, 99, 132, 0.8)",
                    "rgba(54, 162, 235, 0.8)",
                    "rgba(255, 205, 86, 0.8)",
                    "rgba(75, 192, 192, 0.8)",
                    "rgba(153, 102, 255, 0.8)",
                    "rgba(255, 159, 64, 0.8)",
                    "rgba(199, 199, 199, 0.8)",
                    "rgba(83, 102, 255, 0.8)",
                ],
                "borderWidth": 1,
            }
        ],
    )


@router.get("/charts/team-usage")
async def get_team_usage_chart() -> ChartData:
    """Get team pattern usage radar chart data."""
    insights_engine = get_insights_engine()
    team_data = insights_engine.get_team_comparison()

    if not team_data or not team_data.get("team_members"):
        return ChartData(labels=[], datasets=[])

    # Extract pattern usage data
    team_members = team_data["team_members"]
    labels = ["Patterns Applied", "Effectiveness Score", "Code Quality"]

    datasets = []
    colors = ["rgba(255, 99, 132, 0.8)", "rgba(54, 162, 235, 0.8)", "rgba(255, 205, 86, 0.8)"]

    for i, member in enumerate(team_members):
        if i >= 3:  # Limit to 3 team members for readability
            break

        datasets.append(
            {
                "label": member["name"],
                "data": [
                    member["patterns_applied"] / 10,  # Normalize
                    member["effectiveness"] * 10,  # Scale up
                    (member["effectiveness"] * 8) + 2,  # Mock code quality
                ],
                "borderColor": colors[i],
                "backgroundColor": colors[i].replace("0.8", "0.2"),
                "pointBackgroundColor": colors[i],
                "pointBorderColor": "#fff",
                "pointHoverBackgroundColor": "#fff",
                "pointHoverBorderColor": colors[i],
            }
        )

    return ChartData(labels=labels, datasets=datasets)


@router.get("/insights")
async def get_insights() -> InsightsResponse:
    """Get insights and recommendations."""
    insights_engine = get_insights_engine()
    analyzer = get_metrics_analyzer()

    if not analyzer:
        return InsightsResponse(insights=[], recommendations=[], trends=[])

    # Generate insights
    insights = insights_engine.generate_insights()

    # Get recommendations
    recommendations = insights_engine.get_recommendations()

    # Get trends
    trends = insights_engine.analyze_trends()

    return InsightsResponse(insights=insights, recommendations=recommendations, trends=trends)


@router.get("/export/metrics")
async def export_metrics(format: str = Query("json", description="Export format (json, csv)")):
    """Export metrics data."""
    analyzer = get_metrics_analyzer()

    if not analyzer:
        raise HTTPException(status_code=404, detail="No metrics data available")

    if format.lower() == "json":
        # Return JSON data
        return JSONResponse(content=analyzer.metrics_data)

    elif format.lower() == "csv":
        # Generate CSV (simplified)
        csv_content = "category,type,count,timestamp\n"

        for category, items in analyzer.metrics_data.items():
            for item in items:
                csv_content += f"{category},{item.get('pattern', '')},{item.get('count', 1)},{item.get('timestamp', '')}\n"

        from fastapi.responses import Response

        return Response(
            content=csv_content,
            media_type="text/csv",
            headers={"Content-Disposition": "attachment; filename=metrics.csv"},
        )

    else:
        raise HTTPException(status_code=400, detail="Unsupported export format")


# Static file serving endpoints (for development)
@router.get("/static/{file_path:path}")
async def serve_static(file_path: str):
    """Serve static files (CSS, JS) for the dashboard."""
    static_dir = Path(__file__).parent / "static"
    file_full_path = static_dir / file_path

    if not file_full_path.exists() or not file_full_path.is_file():
        raise HTTPException(status_code=404, detail="Static file not found")

    # Determine content type
    if file_path.endswith(".css"):
        media_type = "text/css"
    elif file_path.endswith(".js"):
        media_type = "application/javascript"
    else:
        media_type = "text/plain"

    with open(file_full_path, "r", encoding="utf-8") as f:
        content = f.read()

    from fastapi.responses import Response

    return Response(content=content, media_type=media_type)
