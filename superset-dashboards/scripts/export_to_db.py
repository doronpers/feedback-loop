#!/usr/bin/env python
"""
Export feedback-loop metrics to a database for Superset visualization.

This script reads metrics from JSON files and exports them to a SQL database
(SQLite or PostgreSQL) where they can be queried by Apache Superset.

Usage:
    # Export to SQLite (default)
    python export_to_db.py --format sqlite
    
    # Export to PostgreSQL
    python export_to_db.py --format postgresql --db-uri "postgresql://user:pass@localhost/db"
    
    # Export specific metrics file
    python export_to_db.py --input metrics_data.json --format sqlite
"""

import argparse
import json
import logging
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError

# Add database directory to path for imports
database_dir = Path(__file__).parent.parent / 'database'
sys.path.insert(0, str(database_dir))

from models import (
    Base,
    MetricsBug,
    MetricsTestFailure,
    MetricsCodeReview,
    MetricsPerformance,
    MetricsDeployment,
    MetricsCodeGeneration,
    PatternEffectiveness,
    MetricsSummary
)

logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s: %(message)s'
)
logger = logging.getLogger(__name__)


class MetricsExporter:
    """Export metrics data to SQL database."""
    
    def __init__(self, db_uri: str):
        """Initialize exporter with database URI.
        
        Args:
            db_uri: SQLAlchemy database URI
        """
        self.db_uri = db_uri
        self.engine = create_engine(db_uri, echo=False)
        self.Session = sessionmaker(bind=self.engine)
    
    def create_tables(self):
        """Create all tables if they don't exist."""
        logger.info("Creating database tables...")
        Base.metadata.create_all(self.engine)
        logger.info("✓ Tables created successfully")
    
    def load_metrics_file(self, file_path: str) -> Dict[str, List[Dict[str, Any]]]:
        """Load metrics from JSON file.
        
        Args:
            file_path: Path to metrics JSON file
            
        Returns:
            Dictionary of metrics data
        """
        logger.info(f"Loading metrics from {file_path}...")
        with open(file_path, 'r') as f:
            data = json.load(f)
        
        # Validate structure
        expected_keys = [
            'bugs', 'test_failures', 'code_reviews',
            'performance_metrics', 'deployment_issues', 'code_generation'
        ]
        
        for key in expected_keys:
            if key not in data:
                data[key] = []
        
        return data
    
    def export_bugs(self, bugs: List[Dict[str, Any]], session) -> int:
        """Export bug metrics to database.
        
        Args:
            bugs: List of bug entries
            session: SQLAlchemy session
            
        Returns:
            Number of records exported
        """
        count = 0
        for bug in bugs:
            try:
                bug_record = MetricsBug(
                    pattern=bug.get('pattern', 'unknown'),
                    error=bug.get('error', ''),
                    code=bug.get('code'),
                    file_path=bug.get('file_path'),
                    line=bug.get('line'),
                    stack_trace=bug.get('stack_trace'),
                    count=bug.get('count', 1),
                    timestamp=self._parse_timestamp(bug.get('timestamp'))
                )
                session.add(bug_record)
                count += 1
            except Exception as e:
                logger.warning(f"Failed to export bug: {e}")
        
        return count
    
    def export_test_failures(self, failures: List[Dict[str, Any]], session) -> int:
        """Export test failure metrics to database."""
        count = 0
        for failure in failures:
            try:
                failure_record = MetricsTestFailure(
                    test_name=failure.get('test_name', 'unknown'),
                    failure_reason=failure.get('failure_reason', ''),
                    pattern_violated=failure.get('pattern_violated'),
                    code_snippet=failure.get('code_snippet'),
                    timestamp=self._parse_timestamp(failure.get('timestamp'))
                )
                session.add(failure_record)
                count += 1
            except Exception as e:
                logger.warning(f"Failed to export test failure: {e}")
        
        return count
    
    def export_code_reviews(self, reviews: List[Dict[str, Any]], session) -> int:
        """Export code review metrics to database."""
        count = 0
        for review in reviews:
            try:
                review_record = MetricsCodeReview(
                    issue_type=review.get('issue_type', 'unknown'),
                    pattern=review.get('pattern', 'unknown'),
                    severity=review.get('severity', 'medium'),
                    file_path=review.get('file_path'),
                    line=review.get('line'),
                    suggestion=review.get('suggestion'),
                    timestamp=self._parse_timestamp(review.get('timestamp'))
                )
                session.add(review_record)
                count += 1
            except Exception as e:
                logger.warning(f"Failed to export code review: {e}")
        
        return count
    
    def export_performance(self, metrics: List[Dict[str, Any]], session) -> int:
        """Export performance metrics to database."""
        count = 0
        for metric in metrics:
            try:
                details = metric.get('details', {})
                
                perf_record = MetricsPerformance(
                    metric_type=metric.get('metric_type', 'unknown'),
                    details=details,
                    timestamp=self._parse_timestamp(metric.get('timestamp')),
                    function_name=details.get('function'),
                    execution_time_ms=details.get('avg_time_ms') or details.get('max_time_ms'),
                    memory_usage_bytes=details.get('memory_usage'),
                    file_size_bytes=details.get('file_size')
                )
                session.add(perf_record)
                count += 1
            except Exception as e:
                logger.warning(f"Failed to export performance metric: {e}")
        
        return count
    
    def export_deployment(self, issues: List[Dict[str, Any]], session) -> int:
        """Export deployment issue metrics to database."""
        count = 0
        for issue in issues:
            try:
                deploy_record = MetricsDeployment(
                    issue_type=issue.get('issue_type', 'unknown'),
                    pattern=issue.get('pattern'),
                    environment=issue.get('environment', 'production'),
                    root_cause=issue.get('root_cause'),
                    resolution_time_minutes=issue.get('resolution_time_minutes'),
                    timestamp=self._parse_timestamp(issue.get('timestamp'))
                )
                session.add(deploy_record)
                count += 1
            except Exception as e:
                logger.warning(f"Failed to export deployment issue: {e}")
        
        return count
    
    def export_code_generation(self, generations: List[Dict[str, Any]], session) -> int:
        """Export code generation metrics to database."""
        count = 0
        for gen in generations:
            try:
                patterns = gen.get('patterns_applied', [])
                
                gen_record = MetricsCodeGeneration(
                    prompt=gen.get('prompt', ''),
                    patterns_applied=patterns,
                    confidence=gen.get('confidence', 0.0),
                    success=gen.get('success', False),
                    code_length=gen.get('code_length'),
                    compilation_error=gen.get('compilation_error'),
                    generation_metadata=gen.get('metadata', {}),  # Store input metadata in generation_metadata field
                    timestamp=self._parse_timestamp(gen.get('timestamp')),
                    patterns_count=len(patterns)
                )
                session.add(gen_record)
                count += 1
            except Exception as e:
                logger.warning(f"Failed to export code generation: {e}")
        
        return count
    
    def export_all(self, metrics_data: Dict[str, List[Dict[str, Any]]]):
        """Export all metrics to database.
        
        Args:
            metrics_data: Complete metrics data dictionary
        """
        session = self.Session()
        
        try:
            logger.info("Exporting metrics to database...")
            
            # Export each category
            bugs_count = self.export_bugs(metrics_data.get('bugs', []), session)
            logger.info(f"  ✓ Exported {bugs_count} bug records")
            
            failures_count = self.export_test_failures(
                metrics_data.get('test_failures', []), session
            )
            logger.info(f"  ✓ Exported {failures_count} test failure records")
            
            reviews_count = self.export_code_reviews(
                metrics_data.get('code_reviews', []), session
            )
            logger.info(f"  ✓ Exported {reviews_count} code review records")
            
            perf_count = self.export_performance(
                metrics_data.get('performance_metrics', []), session
            )
            logger.info(f"  ✓ Exported {perf_count} performance records")
            
            deploy_count = self.export_deployment(
                metrics_data.get('deployment_issues', []), session
            )
            logger.info(f"  ✓ Exported {deploy_count} deployment records")
            
            gen_count = self.export_code_generation(
                metrics_data.get('code_generation', []), session
            )
            logger.info(f"  ✓ Exported {gen_count} code generation records")
            
            # Commit all changes
            session.commit()
            
            total = (bugs_count + failures_count + reviews_count + 
                    perf_count + deploy_count + gen_count)
            logger.info(f"\n✓ Successfully exported {total} total records")
            
        except SQLAlchemyError as e:
            session.rollback()
            logger.error(f"Database error: {e}")
            raise
        finally:
            session.close()
    
    @staticmethod
    def _parse_timestamp(timestamp_str: Optional[str]) -> datetime:
        """Parse timestamp string to datetime object.
        
        Args:
            timestamp_str: ISO format timestamp string (supports Z or +HH:MM timezone)
            
        Returns:
            datetime object
        """
        if not timestamp_str:
            return datetime.utcnow()
        
        try:
            # Handle ISO format with 'Z' suffix (UTC)
            if timestamp_str.endswith('Z'):
                timestamp_str = timestamp_str.replace('Z', '+00:00')
            
            # Parse ISO format timestamp
            return datetime.fromisoformat(timestamp_str)
        except (ValueError, AttributeError):
            # If parsing fails, return current time
            logger.warning(f"Failed to parse timestamp: {timestamp_str}, using current time")
            return datetime.utcnow()


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Export feedback-loop metrics to database for Superset'
    )
    parser.add_argument(
        '--input',
        default='metrics_data.json',
        help='Input metrics JSON file (default: metrics_data.json)'
    )
    parser.add_argument(
        '--format',
        choices=['sqlite', 'postgresql'],
        default='sqlite',
        help='Database format (default: sqlite)'
    )
    parser.add_argument(
        '--db-uri',
        help='Database URI (overrides --format)'
    )
    parser.add_argument(
        '--db-path',
        default='metrics.db',
        help='SQLite database path (default: metrics.db)'
    )
    
    args = parser.parse_args()
    
    # Determine database URI
    if args.db_uri:
        db_uri = args.db_uri
    elif args.format == 'sqlite':
        db_path = Path(args.db_path).absolute()
        db_uri = f'sqlite:///{db_path}'
        logger.info(f"Using SQLite database: {db_path}")
    else:
        logger.error("PostgreSQL requires --db-uri argument")
        return 1
    
    # Check if input file exists
    if not Path(args.input).exists():
        logger.error(f"Metrics file not found: {args.input}")
        logger.info("Run 'pytest --enable-metrics' to collect metrics first")
        return 1
    
    try:
        # Initialize exporter
        exporter = MetricsExporter(db_uri)
        
        # Create tables
        exporter.create_tables()
        
        # Load and export metrics
        metrics_data = exporter.load_metrics_file(args.input)
        exporter.export_all(metrics_data)
        
        logger.info("\n" + "="*60)
        logger.info("Export complete! Next steps:")
        logger.info("1. Configure database connection in Superset")
        logger.info(f"   SQLAlchemy URI: {db_uri}")
        logger.info("2. Import dashboard configurations:")
        logger.info("   python superset-dashboards/scripts/import_dashboards.py")
        logger.info("="*60)
        
        return 0
        
    except Exception as e:
        logger.error(f"Export failed: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())
