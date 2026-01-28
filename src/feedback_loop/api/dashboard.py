"""
Dashboard API Module

Provides REST API endpoints for the feedback-loop analytics dashboard.
Serves data for charts, metrics, and insights visualization.
"""

import csv
import io
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import HTMLResponse, JSONResponse, Response
from pydantic import BaseModel
from sqlalchemy.orm import Session

from feedback_loop.metrics.analyzer import MetricsAnalyzer
from feedback_loop.persistence.database import get_db
from feedback_loop.persistence.models import Metric

# Shared InsightsEngine stub or import (omitted for brevity, assuming standard import or stub logic)
try:
    from shared_ai_utils import InsightsEngine
except ImportError:

    class InsightsEngine:
        def __init__(self, analyzer=None):
            self.analyzer = analyzer

        def generate_insights(self):
            return []

        def get_recommendations(self):
            return []

        def analyze_trends(self):
            return []

        def calculate_pattern_roi(self, pattern_name):
            return 0.0

        def get_team_comparison(self):
            return {"labels": [], "datasets": []}


router = APIRouter(prefix="/dashboard", tags=["dashboard"])
logger = logging.getLogger(__name__)


# Models (same as before)
class DashboardSummary(BaseModel):
    total_bugs: int
    total_test_failures: int
    total_code_reviews: int
    total_deployment_issues: int
    pattern_effectiveness_score: float
    top_patterns: List[Dict[str, Any]]
    recent_activity: List[Dict[str, Any]]


class ChartData(BaseModel):
    labels: List[str]
    datasets: List[Dict[str, Any]]


class InsightsResponse(BaseModel):
    insights: List[Dict[str, Any]]
    recommendations: List[Dict[str, Any]]
    trends: List[Dict[str, Any]]


# Global cache (optional, simplifed for now)
_insights_engine = None


def parse_date_range(date_range: str) -> Tuple[Optional[datetime], datetime]:
    end_date = datetime.utcnow()
    if date_range == "7d":
        start_date = end_date - timedelta(days=7)
    elif date_range == "30d":
        start_date = end_date - timedelta(days=30)
    elif date_range == "90d":
        start_date = end_date - timedelta(days=90)
    elif date_range == "1y":
        start_date = end_date - timedelta(days=365)
    elif date_range == "all":
        start_date = None
    else:
        start_date = end_date - timedelta(days=30)
    return start_date, end_date


def get_metrics_analyzer_from_db(db: Session) -> Optional[MetricsAnalyzer]:
    """Fetch metrics from DB and initialize analyzer."""
    # Query all metrics (optimize later with date filtering if needed)
    metrics_query = db.query(Metric).all()

    if not metrics_query:
        return MetricsAnalyzer({})

    # Reshape data for analyzer: Dict[str, List[Dict]]
    # Metric types in DB: "bugs", "test_failures", etc. (from type column)
    # The 'data' column contains the dictionary.
    # OR if type is "user_metrics", the 'data' might be {"bugs": [...], "test_failures": [...]}
    # Let's handle both cases.

    analyzable_data = {}

    for m in metrics_query:
        if m.type == "user_metrics":
            # Nested structure
            if isinstance(m.data, dict):
                for k, v in m.data.items():
                    if isinstance(v, list):
                        if k not in analyzable_data:
                            analyzable_data[k] = []
                        analyzable_data[k].extend(v)
        else:
            # Single type
            t = m.type
            if t not in analyzable_data:
                analyzable_data[t] = []
            if isinstance(m.data, dict):
                analyzable_data[t].append(m.data)
            elif isinstance(m.data, list):
                analyzable_data[t].extend(m.data)

    return MetricsAnalyzer(analyzable_data)


def get_insights_engine(db: Session) -> InsightsEngine:
    analyzer = get_metrics_analyzer_from_db(db)
    return InsightsEngine(analyzer=analyzer)


@router.get("/", response_class=HTMLResponse)
async def dashboard_home():
    """Serve the React dashboard application."""
    frontend_dist = Path(__file__).parent.parent.parent.parent / "frontend" / "dist"
    index_path = frontend_dist / "index.html"

    if not index_path.exists():
        raise HTTPException(
            status_code=500,
            detail="Frontend build not found. Run 'cd frontend && npm run build' first.",
        )

    return HTMLResponse(content=index_path.read_text(), status_code=200)


@router.get("/summary")
async def get_dashboard_summary(
    date_range: str = Query("30d"), db: Session = Depends(get_db)
) -> DashboardSummary:
    analyzer = get_metrics_analyzer_from_db(db)

    if not analyzer or not analyzer.metrics_data:
        return DashboardSummary(
            total_bugs=0,
            total_test_failures=0,
            total_code_reviews=0,
            total_deployment_issues=0,
            pattern_effectiveness_score=0.0,
            top_patterns=[],
            recent_activity=[],
        )

    summary = analyzer.get_summary()
    high_freq = analyzer.get_high_frequency_patterns(threshold=1)[:5]
    effectiveness = analyzer.calculate_effectiveness()
    avg_effectiveness = (
        sum([m["score"] for m in effectiveness.values()]) / len(effectiveness)
        if effectiveness
        else 0.0
    )

    recent_activity = [
        {
            "type": "info",
            "description": "Database metrics loaded",
            "timestamp": datetime.now().isoformat(),
            "severity": "low",
        }
    ]

    return DashboardSummary(
        total_bugs=summary.get("bugs", 0),
        total_test_failures=summary.get("test_failures", 0),
        total_code_reviews=summary.get("code_reviews", 0),
        total_deployment_issues=summary.get("deployment_issues", 0),
        pattern_effectiveness_score=avg_effectiveness,
        top_patterns=high_freq,
        recent_activity=recent_activity,
    )


@router.get("/charts/patterns-over-time")
async def get_patterns_over_time_chart(
    date_range: str = Query("30d"), db: Session = Depends(get_db)
) -> ChartData:
    start_date, end_date = parse_date_range(date_range)
    days = (end_date - start_date).days if start_date else 365

    labels = []
    data = []
    for i in range(days, 0, -1):
        date = end_date - timedelta(days=i)
        labels.append(date.strftime("%Y-%m-%d"))
        data.append(0)  # Logic to query DB/Analyzer for counts per day would go here

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
async def get_severity_distribution_chart(
    date_range: str = Query("30d"), db: Session = Depends(get_db)
) -> ChartData:
    analyzer = get_metrics_analyzer_from_db(db)
    severity_data = analyzer.get_severity_distribution() if analyzer else {}

    labels = list(severity_data.keys())
    data = list(severity_data.values())
    colors = ["#dc3545", "#ffc107", "#28a745"]  # red, yellow, green approximations

    return ChartData(
        labels=labels, datasets=[{"data": data, "backgroundColor": colors[: len(data)]}]
    )


@router.get("/charts/pattern-effectiveness")
async def get_pattern_effectiveness_chart(
    date_range: str = Query("30d"), db: Session = Depends(get_db)
) -> ChartData:
    analyzer = get_metrics_analyzer_from_db(db)
    effectiveness = analyzer.calculate_effectiveness() if analyzer else {}

    labels = []
    scores = []
    for pattern, metrics in list(effectiveness.items())[:10]:
        labels.append(pattern)
        scores.append(metrics["score"] * 100)

    return ChartData(
        labels=labels,
        datasets=[
            {
                "label": "Effectiveness Score (%)",
                "data": scores,
                "backgroundColor": "rgba(54, 162, 235, 0.8)",
            }
        ],
    )


@router.get("/charts/adoption-reduction")
async def get_adoption_reduction_chart(
    date_range: str = Query("30d"), db: Session = Depends(get_db)
) -> ChartData:
    # Stub implementation - requires complex analysis
    return ChartData(labels=[], datasets=[])


@router.get("/charts/pattern-roi")
async def get_pattern_roi_chart(
    date_range: str = Query("30d"), db: Session = Depends(get_db)
) -> ChartData:
    insights_engine = get_insights_engine(db)  # noqa: F841
    # Stub implementation
    return ChartData(labels=[], datasets=[])


@router.get("/charts/team-usage")
async def get_team_usage_chart(
    date_range: str = Query("30d"), db: Session = Depends(get_db)
) -> ChartData:
    # Stub implementation
    return ChartData(labels=[], datasets=[])


@router.get("/insights")
async def get_insights(db: Session = Depends(get_db)) -> InsightsResponse:
    insights_engine = get_insights_engine(db)
    return InsightsResponse(
        insights=insights_engine.generate_insights(),
        recommendations=insights_engine.get_recommendations(),
        trends=insights_engine.analyze_trends(),
    )


@router.get("/export")
async def export_dashboard_data(
    format: str = Query("json"), date_range: str = Query("30d"), db: Session = Depends(get_db)
):
    analyzer = get_metrics_analyzer_from_db(db)
    if not analyzer:
        raise HTTPException(status_code=404, detail="No data")

    summary = analyzer.get_summary()
    top_patterns = analyzer.get_high_frequency_patterns(threshold=1)[:10]
    effectiveness = analyzer.calculate_effectiveness()

    export_data = {
        "summary": summary,
        "top_patterns": top_patterns,
        "effectiveness": effectiveness,
        "date_range": date_range,
        "exported_at": datetime.utcnow().isoformat(),
    }

    if format.lower() == "json":
        return JSONResponse(content=export_data)
    elif format.lower() == "csv":
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(["Metric", "Value"])
        for k, v in summary.items():
            writer.writerow([k, v])
        return Response(content=output.getvalue(), media_type="text/csv")
    else:
        raise HTTPException(status_code=400, detail="Invalid format")


@router.get("/export/metrics")
async def export_metrics_endpoint(format: str = Query("json"), db: Session = Depends(get_db)):
    analyzer = get_metrics_analyzer_from_db(db)
    if not analyzer:
        raise HTTPException(status_code=404, detail="No data")
    if format.lower() == "json":
        return JSONResponse(content=analyzer.metrics_data)
    # CSV logic omitted for brevity
    return Response(content="Not implemented", media_type="text/plain")


@router.get("/static/{file_path:path}")
async def serve_static(file_path: str):
    static_dir = Path(__file__).parent / "static"
    file_full_path = static_dir / file_path
    if not file_full_path.exists() or not file_full_path.is_file():
        raise HTTPException(status_code=404, detail="Static file not found")
    media_type = (
        "text/css"
        if file_path.endswith(".css")
        else "application/javascript"
        if file_path.endswith(".js")
        else "text/plain"
    )
    with open(file_full_path, "r", encoding="utf-8") as f:
        return Response(content=f.read(), media_type=media_type)
