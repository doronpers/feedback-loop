"""
Metrics Collector Module

Collects usage metrics including bugs, test failures, code review issues,
performance metrics, and deployment issues.
"""

import json
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class MetricsCollector:
    """Collects and stores various types of usage metrics."""
    
    # Expected metric categories
    METRIC_CATEGORIES = ["bugs", "test_failures", "code_reviews", 
                        "performance_metrics", "deployment_issues"]
    
    def __init__(self):
        """Initialize the metrics collector."""
        self.data: Dict[str, List[Dict[str, Any]]] = {
            category: [] for category in self.METRIC_CATEGORIES
        }
    
    def log_bug(
        self,
        pattern: str,
        error: str,
        code: str,
        file_path: str,
        line: int,
        stack_trace: Optional[str] = None
    ) -> None:
        """Log a bug occurrence.
        
        Args:
            pattern: Pattern type (e.g., "numpy_json_serialization")
            error: Error message
            code: Code snippet where bug occurred
            file_path: File path where bug occurred
            line: Line number where bug occurred
            stack_trace: Optional stack trace
        """
        bug_entry = {
            "pattern": pattern,
            "error": error,
            "code": code,
            "file_path": file_path,
            "line": line,
            "stack_trace": stack_trace,
            "timestamp": datetime.now().isoformat(),
            "count": 1
        }
        
        # Check if this bug already exists and increment count
        existing = self._find_similar_bug(bug_entry)
        if existing:
            existing["count"] += 1
            existing["timestamp"] = bug_entry["timestamp"]
        else:
            self.data["bugs"].append(bug_entry)
        
        logger.debug(f"Logged bug for pattern: {pattern}")
    
    def _find_similar_bug(self, bug: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Find a similar bug entry to merge counts.
        
        Args:
            bug: Bug entry to find similar match for
            
        Returns:
            Existing bug entry or None
        """
        for existing_bug in self.data["bugs"]:
            if (existing_bug["pattern"] == bug["pattern"] and
                existing_bug["error"] == bug["error"] and
                existing_bug["file_path"] == bug["file_path"]):
                return existing_bug
        return None
    
    def log_test_failure(
        self,
        test_name: str,
        failure_reason: str,
        pattern_violated: Optional[str] = None,
        code_snippet: Optional[str] = None
    ) -> None:
        """Log a test failure.
        
        Args:
            test_name: Name of the failed test
            failure_reason: Reason for failure
            pattern_violated: Pattern that was violated (if applicable)
            code_snippet: Code snippet related to failure
        """
        failure_entry = {
            "test_name": test_name,
            "failure_reason": failure_reason,
            "pattern_violated": pattern_violated,
            "code_snippet": code_snippet,
            "timestamp": datetime.now().isoformat(),
            "count": 1
        }
        
        # Check for existing failure
        existing = self._find_similar_test_failure(failure_entry)
        if existing:
            existing["count"] += 1
            existing["timestamp"] = failure_entry["timestamp"]
        else:
            self.data["test_failures"].append(failure_entry)
        
        logger.debug(f"Logged test failure: {test_name}")
    
    def _find_similar_test_failure(self, failure: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Find a similar test failure entry.
        
        Args:
            failure: Test failure entry to find similar match for
            
        Returns:
            Existing test failure entry or None
        """
        for existing_failure in self.data["test_failures"]:
            if (existing_failure["test_name"] == failure["test_name"] and
                existing_failure["failure_reason"] == failure["failure_reason"]):
                return existing_failure
        return None
    
    def log_code_review_issue(
        self,
        issue_type: str,
        pattern: str,
        severity: str,
        file_path: str,
        line: Optional[int] = None,
        suggestion: Optional[str] = None
    ) -> None:
        """Log a code review issue.
        
        Args:
            issue_type: Type of issue found
            pattern: Pattern related to the issue
            severity: Severity level (low/medium/high/critical)
            file_path: File where issue was found
            line: Optional line number
            suggestion: Optional suggestion for fixing
        """
        if severity not in ["low", "medium", "high", "critical"]:
            logger.debug(f"Invalid severity level: {severity}, defaulting to medium")
            severity = "medium"
        
        review_entry = {
            "issue_type": issue_type,
            "pattern": pattern,
            "severity": severity,
            "file_path": file_path,
            "line": line,
            "suggestion": suggestion,
            "timestamp": datetime.now().isoformat()
        }
        
        self.data["code_reviews"].append(review_entry)
        logger.debug(f"Logged code review issue: {issue_type}")
    
    def log_performance_metric(
        self,
        metric_type: str,
        details: Dict[str, Any]
    ) -> None:
        """Log a performance metric.
        
        Args:
            metric_type: Type of metric (e.g., "memory_error", "execution_time")
            details: Details about the metric (varies by type)
        """
        metric_entry = {
            "metric_type": metric_type,
            "details": details,
            "timestamp": datetime.now().isoformat()
        }
        
        self.data["performance_metrics"].append(metric_entry)
        logger.debug(f"Logged performance metric: {metric_type}")
    
    def log_deployment_issue(
        self,
        issue_type: str,
        pattern: str,
        environment: str,
        root_cause: Optional[str] = None,
        resolution_time_minutes: Optional[int] = None
    ) -> None:
        """Log a deployment issue.
        
        Args:
            issue_type: Type of deployment issue
            pattern: Pattern related to the issue
            environment: Deployment environment
            root_cause: Root cause of the issue
            resolution_time_minutes: Time to resolve in minutes
        """
        deployment_entry = {
            "issue_type": issue_type,
            "pattern": pattern,
            "environment": environment,
            "root_cause": root_cause,
            "resolution_time_minutes": resolution_time_minutes,
            "timestamp": datetime.now().isoformat()
        }
        
        self.data["deployment_issues"].append(deployment_entry)
        logger.debug(f"Logged deployment issue: {issue_type}")
    
    def export_json(self) -> str:
        """Export all collected metrics as JSON.
        
        Returns:
            JSON string of all metrics
        """
        return json.dumps(self.data, indent=2)
    
    def export_dict(self) -> Dict[str, List[Dict[str, Any]]]:
        """Export all collected metrics as dictionary.
        
        Returns:
            Dictionary of all metrics
        """
        return self.data.copy()
    
    def get_summary(self) -> Dict[str, int]:
        """Get a summary count of all metrics.
        
        Returns:
            Dictionary with counts of each metric type
        """
        return {
            "bugs": len(self.data["bugs"]),
            "test_failures": len(self.data["test_failures"]),
            "code_reviews": len(self.data["code_reviews"]),
            "performance_metrics": len(self.data["performance_metrics"]),
            "deployment_issues": len(self.data["deployment_issues"]),
            "total": sum(len(v) for v in self.data.values())
        }
    
    def clear(self) -> None:
        """Clear all collected metrics."""
        self.data = {category: [] for category in self.METRIC_CATEGORIES}
        logger.debug("Cleared all metrics")
    
    def load_from_json(self, json_str: str) -> None:
        """Load metrics from JSON string.
        
        Args:
            json_str: JSON string containing metrics data
        """
        try:
            loaded_data = json.loads(json_str)
            self.data = loaded_data
            logger.debug("Loaded metrics from JSON")
        except json.JSONDecodeError as e:
            logger.debug(f"Failed to load metrics from JSON: {e}")
            raise
