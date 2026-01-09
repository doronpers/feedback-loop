"""
Metrics Collector Module

Collects usage metrics including bugs, test failures, code review issues,
performance metrics, and deployment issues.
"""

import copy
import json
import logging
import re
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

# Matches checklist lines like "- [ ] pattern_name" while ignoring trailing annotations.
# Group explanation:
#   -\s*\[[ xX]\]\s*        -> leading checkbox marker
#   (?P<pattern>[^\s(#\n]+  -> first token of the pattern name (no spaces/(#))
#   (?:\s+[^\s(#\n]+)*      -> optional additional tokens separated by spaces
CHECKLIST_PATTERN = re.compile(
    r"-\s*\[[ xX]\]\s*(?P<pattern>"
    r"[^\s(#\n]+"
    r"(?:\s+[^\s(#\n]+)*"
    r")"
)


class MetricsCollector:
    """Collects and stores various types of usage metrics."""
    
    # Expected metric categories
    METRIC_CATEGORIES = ["bugs", "test_failures", "code_reviews",
                        "performance_metrics", "deployment_issues", "code_generation"]
    
    # Allowed plan file roots for path traversal protection
    # - Current working directory: normal workspace files
    # - /tmp: standard Unix temp directory
    # - /private/var: macOS redirects /tmp to /private/var/folders/... internally
    ALLOWED_PLAN_ROOTS = [
        Path.cwd().resolve(), 
        Path("/tmp").resolve(),
        Path("/private/var").resolve()
    ]
    
    def __init__(self, memory_service=None):
        """Initialize the metrics collector.
        
        Args:
            memory_service: Optional FeedbackLoopMemory instance for memory integration
        """
        self.data: Dict[str, List[Dict[str, Any]]] = {
            category: [] for category in self.METRIC_CATEGORIES
        }
        self.memory_service = memory_service
    
    @classmethod
    def get_metric_categories(cls) -> List[str]:
        """Get the list of metric categories.
        
        Returns:
            List of metric category names
        """
        return cls.METRIC_CATEGORIES.copy()
    
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

        Raises:
            ValueError: If required parameters are empty
        """
        # Validate required parameters
        if not issue_type or not issue_type.strip():
            raise ValueError("issue_type cannot be empty")
        if not pattern or not pattern.strip():
            raise ValueError("pattern cannot be empty")
        if not file_path or not file_path.strip():
            raise ValueError("file_path cannot be empty")

        # Validate severity (defensive: warn and correct instead of raising)
        valid_severities = ["low", "medium", "high", "critical"]
        if severity not in valid_severities:
            logger.warning(f"Invalid severity level: {severity}. Must be one of {valid_severities}. Defaulting to 'medium'")
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

    def log_code_generation(
        self,
        prompt: str,
        patterns_applied: List[str],
        confidence: float,
        success: bool,
        code_length: Optional[int] = None,
        compilation_error: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """Log a code generation event.

        Args:
            prompt: The prompt used for generation
            patterns_applied: List of pattern names that were applied
            confidence: Confidence score of the generation
            success: Whether the generated code was successful
            code_length: Optional length of generated code
            compilation_error: Optional compilation error if code failed
            metadata: Optional additional metadata
        """
        generation_entry = {
            "prompt": prompt[:200],  # Limit prompt length
            "patterns_applied": patterns_applied,
            "confidence": confidence,
            "success": success,
            "code_length": code_length,
            "compilation_error": compilation_error,
            "metadata": metadata or {},
            "timestamp": datetime.now().isoformat()
        }

        self.data["code_generation"].append(generation_entry)
        logger.debug(f"Logged code generation: {len(patterns_applied)} patterns applied")

    def log_from_plan_file(
        self,
        plan_file: str,
        section_heading: str = "Patterns to Apply"
    ) -> List[str]:
        """Parse a Planning-with-Files style plan and log its pattern checklist.

        This extracts pattern identifiers from a checklist section (e.g.,
        ``## Patterns to Apply``) and records them in the code generation
        metrics so pattern usage planning is tracked alongside execution.

        Args:
            plan_file: Path to the plan markdown file.
            section_heading: Heading text that marks the checklist section.

        Returns:
            List of pattern identifiers discovered in the plan file.

        Raises:
            FileNotFoundError: If the plan file does not exist.
            ValueError: If path traversal is attempted in ``plan_file``.
        """
        plan_path = Path(plan_file)
        if ".." in plan_path.parts:
            raise ValueError(f"Path traversal detected in: {plan_file}")

        plan_path = plan_path.resolve()

        if not any(self._is_within_root(plan_path, root) for root in self.ALLOWED_PLAN_ROOTS):
            raise ValueError(f"Plan file must be within allowed roots: {self.ALLOWED_PLAN_ROOTS}")

        if not plan_path.exists():
            raise FileNotFoundError(f"Plan file not found: {plan_path}")

        content = plan_path.read_text()
        patterns = self._extract_patterns_from_plan(content, section_heading)

        self.log_code_generation(
            prompt=f"plan:{plan_path.name}",
            patterns_applied=patterns,
            confidence=1.0,
            success=True,
            metadata={
                "source": "plan_file",
                "section_heading": section_heading,
                "plan_path": str(plan_path)
            }
        )

        return patterns

    @staticmethod
    def _is_within_root(path: Path, root: Path) -> bool:
        """Return True if path is contained within root."""
        try:
            path.relative_to(root)
            return True
        except ValueError:
            return False

    def _extract_patterns_from_plan(self, content: str, section_heading: str) -> List[str]:
        """Extract patterns from a Planning-with-Files style checklist section."""
        patterns: List[str] = []
        in_section = False
        found_section = False
        heading_lower = section_heading.strip().lower()

        for line in content.splitlines():
            stripped = line.strip()
            if stripped.startswith("##"):
                heading_text = stripped[2:].strip().lower()
                if heading_text == heading_lower:
                    in_section = True
                    found_section = True
                    continue

                if found_section:
                    break

                in_section = False
                continue

            if not in_section:
                continue

            match = CHECKLIST_PATTERN.match(stripped)
            if match:
                pattern_name = match.group("pattern").strip()
                # Drop trailing annotations like "(from feedback-loop)"
                pattern_name = pattern_name.split("(")[0].strip()
                if pattern_name:
                    patterns.append(pattern_name)

        return patterns

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
            "code_generation": len(self.data["code_generation"]),
            "total": sum(len(v) for v in self.data.values())
        }
    
    def clear(self) -> None:
        """Clear all collected metrics."""
        self.data = {category: [] for category in self.METRIC_CATEGORIES}
        logger.debug("Cleared all metrics")
    
    async def store_session_to_memory(self, session_id: Optional[str] = None) -> bool:
        """Store current session metrics to MemU memory.
        
        Args:
            session_id: Optional session identifier (auto-generated if not provided)
        
        Returns:
            True if stored successfully, False otherwise
        """
        if not self.memory_service:
            logger.debug("Memory service not available")
            return False
        
        try:
            from datetime import datetime
            import uuid
            
            session_data = {
                "session_id": session_id or str(uuid.uuid4()),
                "timestamp": datetime.now().isoformat(),
                "patterns_applied": self._extract_patterns_from_generation(),
                "bugs": self.data.get("bugs", []),
                "test_failures": self.data.get("test_failures", []),
                "metrics": self.get_summary()
            }
            
            result = await self.memory_service.memorize_development_session(session_data)
            if result:
                logger.debug(f"Stored session to memory: {session_data['session_id']}")
                return True
            return False
            
        except Exception as e:
            logger.error(f"Failed to store session to memory: {e}")
            return False
    
    def _extract_patterns_from_generation(self) -> List[str]:
        """Extract pattern names from code generation events.
        
        Returns:
            List of pattern names
        """
        patterns = []
        for gen in self.data.get("code_generation", []):
            patterns.extend(gen.get("patterns_applied", []))
        return list(set(patterns))  # Remove duplicates

    def load_from_json(self, json_str: str) -> None:
        """Load metrics from a JSON string and normalize their structure.
        
        This method parses the given JSON, normalizes the payload to ensure
        that all expected metric categories are present, and updates the
        internal metrics state.

        Normalization behavior:
        - Any missing or ``null`` categories are defaulted to empty lists.
        - Category values that are dictionaries are coerced to single-element
          lists containing that dictionary.
        - Category values that are tuples are coerced to lists.

        On failure during normalization, the collector's previous ``data``
        state is restored.

        Args:
            json_str: JSON string containing metrics data.

        Raises:
            json.JSONDecodeError: If ``json_str`` is not valid JSON.
            ValueError: If the parsed payload cannot be normalized into the
                expected structure.
        """
        previous_data = copy.deepcopy(self.data)
        try:
            loaded_data = json.loads(json_str)
        except json.JSONDecodeError as e:
            logger.error(f"Failed to decode metrics JSON: {e}")
            self.data = previous_data
            raise

        try:
            normalized_data = self._normalize_loaded_data(loaded_data)
        except ValueError as e:
            logger.error(f"Failed to normalize metrics payload: {e}")
            self.data = previous_data
            raise

        self.data = normalized_data
        logger.info("Loaded metrics from JSON")

    def _normalize_loaded_data(self, loaded_data: Any) -> Dict[str, List[Dict[str, Any]]]:
        """Normalize loaded JSON data to ensure expected structure.

        Args:
            loaded_data: Parsed JSON data

        Returns:
            Normalized metrics data containing all metric categories.

        Raises:
            ValueError: If the payload cannot be normalized into the expected structure.
        """
        if not isinstance(loaded_data, dict):
            raise ValueError("Metrics payload must be a JSON object containing metric categories.")

        normalized: Dict[str, List[Dict[str, Any]]] = {}
        for category in self.METRIC_CATEGORIES:
            if category not in loaded_data or loaded_data[category] is None:
                logger.debug(f"Category '{category}' missing or null in payload; defaulting to empty list")
                normalized[category] = []
                continue

            value = loaded_data[category]

            if isinstance(value, dict):
                value = [value]
            elif isinstance(value, tuple):
                value = list(value)

            if not isinstance(value, list):
                raise ValueError(
                    f"Category '{category}' must be a list of entries (got {type(value).__name__})."
                )

            if not all(isinstance(item, dict) for item in value):
                raise ValueError(f"All items in category '{category}' must be dictionaries.")

            normalized[category] = value

        return normalized
