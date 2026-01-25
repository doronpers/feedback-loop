"""
Insights API Module

Provides REST API endpoints for insights, recommendations, and intelligent analysis.
"""

from typing import Any, Dict, List

from fastapi import APIRouter
from pydantic import BaseModel

from shared_ai_utils import InsightsEngine
from metrics.analyzer import MetricsAnalyzer

# Create router
router = APIRouter(prefix="/insights", tags=["insights"])

# Global insights engine instance
_insights_engine = None


def get_insights_engine() -> InsightsEngine:
    """Get or create insights engine instance."""
    global _insights_engine
    if _insights_engine is None:
        # Load local metrics analyzer to pass to shared engine
        from pathlib import Path
        metrics_file = Path("data/metrics_data.json")
        analyzer = None
        if metrics_file.exists():
            import json
            try:
                with open(metrics_file, "r") as f:
                    metrics_data = json.load(f)
                analyzer = MetricsAnalyzer(metrics_data)
            except Exception:
                pass
        _insights_engine = InsightsEngine(analyzer=analyzer)
    return _insights_engine


# Pydantic models
class InsightResponse(BaseModel):
    """Insight response model."""

    title: str
    description: str
    type: str  # "success", "warning", "danger", "info"
    impact: str


class RecommendationResponse(BaseModel):
    """Recommendation response model."""

    action: str
    description: str
    priority: str  # "high", "medium", "low"
    effort: str  # "high", "medium", "low"


class TrendResponse(BaseModel):
    """Trend response model."""

    metric: str
    trend: str  # "increasing", "decreasing", "stable"
    change: str
    period: str
    description: str


class ROIResponse(BaseModel):
    """ROI analysis response model."""

    pattern: str
    implementation_cost_minutes: float
    estimated_occurrences_prevented: float
    estimated_time_saved_minutes: float
    roi_ratio: float
    break_even_occurrences: float
    status: str


class TeamComparisonResponse(BaseModel):
    """Team comparison response model."""

    team_members: List[Dict[str, Any]]
    team_average: float
    top_performer: str
    insights: List[str]


@router.get("/insights", response_model=List[InsightResponse])
async def get_insights():
    """Get actionable insights from metrics data."""
    engine = get_insights_engine()
    insights = engine.generate_insights()
    return insights


@router.get("/recommendations", response_model=List[RecommendationResponse])
async def get_recommendations():
    """Get actionable recommendations."""
    engine = get_insights_engine()
    recommendations = engine.get_recommendations()
    return recommendations


@router.get("/trends", response_model=List[TrendResponse])
async def get_trends():
    """Get trend analysis."""
    engine = get_insights_engine()
    trends = engine.analyze_trends()
    return trends


@router.get("/roi/{pattern_name}", response_model=ROIResponse)
async def get_pattern_roi(pattern_name: str):
    """Get ROI analysis for a specific pattern."""
    engine = get_insights_engine()
    roi = engine.calculate_pattern_roi(pattern_name)
    return roi


@router.get("/team-comparison", response_model=TeamComparisonResponse)
async def get_team_comparison():
    """Get team comparison data."""
    engine = get_insights_engine()
    comparison = engine.get_team_comparison()
    return comparison


@router.get("/summary")
async def get_insights_summary():
    """Get insights summary for dashboard."""
    engine = get_insights_engine()
    summary = engine.get_summary_stats()
    return summary


@router.get("/severity-distribution")
async def get_severity_distribution():
    """Get severity distribution of issues."""
    engine = get_insights_engine()
    distribution = engine.get_severity_distribution()
    return distribution
