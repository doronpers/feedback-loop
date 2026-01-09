"""
SQLAlchemy models for feedback-loop metrics database.

These models define the database schema for storing metrics data
that can be visualized in Apache Superset dashboards.
"""

from datetime import datetime
from typing import Optional

from sqlalchemy import (
    Column, Integer, String, Float, DateTime, Text, Boolean, JSON, Index
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class MetricsBug(Base):
    """Model for bug occurrences."""
    __tablename__ = 'metrics_bugs'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    pattern = Column(String(255), nullable=False, index=True)
    error = Column(Text, nullable=False)
    code = Column(Text)
    file_path = Column(String(500))
    line = Column(Integer)
    stack_trace = Column(Text)
    count = Column(Integer, default=1)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    
    # Indexes for common queries
    __table_args__ = (
        Index('idx_bug_pattern_timestamp', 'pattern', 'timestamp'),
        Index('idx_bug_file_path', 'file_path'),
    )
    
    def __repr__(self):
        return f"<MetricsBug(pattern={self.pattern}, error={self.error[:50]}...)>"


class MetricsTestFailure(Base):
    """Model for test failure records."""
    __tablename__ = 'metrics_test_failures'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    test_name = Column(String(500), nullable=False)
    failure_reason = Column(Text, nullable=False)
    pattern_violated = Column(String(255), index=True)
    code_snippet = Column(Text)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    
    __table_args__ = (
        Index('idx_test_pattern_timestamp', 'pattern_violated', 'timestamp'),
    )
    
    def __repr__(self):
        return f"<MetricsTestFailure(test={self.test_name}, pattern={self.pattern_violated})>"


class MetricsCodeReview(Base):
    """Model for code review issues."""
    __tablename__ = 'metrics_code_reviews'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    issue_type = Column(String(255), nullable=False)
    pattern = Column(String(255), nullable=False, index=True)
    severity = Column(String(50), nullable=False, index=True)  # high, medium, low
    file_path = Column(String(500))
    line = Column(Integer)
    suggestion = Column(Text)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    
    __table_args__ = (
        Index('idx_review_pattern_severity', 'pattern', 'severity'),
        Index('idx_review_timestamp', 'timestamp'),
    )
    
    def __repr__(self):
        return f"<MetricsCodeReview(type={self.issue_type}, severity={self.severity})>"


class MetricsPerformance(Base):
    """Model for performance metrics."""
    __tablename__ = 'metrics_performance'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    metric_type = Column(String(100), nullable=False, index=True)
    details = Column(JSON)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    
    # Extracted fields for easier querying
    function_name = Column(String(255))
    execution_time_ms = Column(Float)
    memory_usage_bytes = Column(Integer)
    file_size_bytes = Column(Integer)
    
    __table_args__ = (
        Index('idx_perf_type_timestamp', 'metric_type', 'timestamp'),
    )
    
    def __repr__(self):
        return f"<MetricsPerformance(type={self.metric_type}, time={self.execution_time_ms}ms)>"


class MetricsDeployment(Base):
    """Model for deployment issues."""
    __tablename__ = 'metrics_deployment'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    issue_type = Column(String(255), nullable=False, index=True)
    pattern = Column(String(255), index=True)
    environment = Column(String(50), nullable=False)  # production, staging, dev
    root_cause = Column(Text)
    resolution_time_minutes = Column(Integer)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    
    __table_args__ = (
        Index('idx_deploy_env_timestamp', 'environment', 'timestamp'),
        Index('idx_deploy_pattern', 'pattern'),
    )
    
    def __repr__(self):
        return f"<MetricsDeployment(type={self.issue_type}, env={self.environment})>"


class MetricsCodeGeneration(Base):
    """Model for code generation events."""
    __tablename__ = 'metrics_code_generation'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    prompt = Column(Text, nullable=False)
    patterns_applied = Column(JSON)  # List of pattern names
    confidence = Column(Float, nullable=False)
    success = Column(Boolean, nullable=False, index=True)
    code_length = Column(Integer)
    compilation_error = Column(Text)
    generation_metadata = Column(JSON)  # Renamed from metadata to avoid conflict
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    
    # Computed field
    patterns_count = Column(Integer)
    
    __table_args__ = (
        Index('idx_generation_success_timestamp', 'success', 'timestamp'),
        Index('idx_generation_confidence', 'confidence'),
    )
    
    def __repr__(self):
        return f"<MetricsCodeGeneration(success={self.success}, confidence={self.confidence:.2f})>"


class PatternEffectiveness(Base):
    """Model for tracking pattern effectiveness over time."""
    __tablename__ = 'pattern_effectiveness'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    pattern_name = Column(String(255), nullable=False, index=True)
    application_count = Column(Integer, default=0)
    success_count = Column(Integer, default=0)
    failure_count = Column(Integer, default=0)
    effectiveness_score = Column(Float)  # 0.0 to 1.0
    period_start = Column(DateTime, nullable=False)
    period_end = Column(DateTime, nullable=False)
    
    __table_args__ = (
        Index('idx_pattern_eff_name_period', 'pattern_name', 'period_start'),
    )
    
    def __repr__(self):
        return f"<PatternEffectiveness(pattern={self.pattern_name}, score={self.effectiveness_score:.2f})>"


class MetricsSummary(Base):
    """Model for pre-computed summary statistics."""
    __tablename__ = 'metrics_summary'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    metric_type = Column(String(100), nullable=False)
    summary_date = Column(DateTime, nullable=False, index=True)
    
    # Summary counts
    total_count = Column(Integer, default=0)
    high_severity_count = Column(Integer, default=0)
    medium_severity_count = Column(Integer, default=0)
    low_severity_count = Column(Integer, default=0)
    
    # Pattern statistics
    top_pattern = Column(String(255))
    top_pattern_count = Column(Integer)
    
    # Trends
    trend_direction = Column(String(20))  # increasing, decreasing, stable
    week_over_week_change = Column(Float)
    
    __table_args__ = (
        Index('idx_summary_type_date', 'metric_type', 'summary_date'),
    )
    
    def __repr__(self):
        return f"<MetricsSummary(type={self.metric_type}, date={self.summary_date})>"


def get_all_models():
    """Return list of all model classes.
    
    Returns:
        List of SQLAlchemy model classes
    """
    return [
        MetricsBug,
        MetricsTestFailure,
        MetricsCodeReview,
        MetricsPerformance,
        MetricsDeployment,
        MetricsCodeGeneration,
        PatternEffectiveness,
        MetricsSummary
    ]
