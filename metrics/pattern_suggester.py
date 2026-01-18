"""
Pattern Suggester Module

Suggests relevant patterns for a given task based on task description and context.
Combines task context (from Planning with Files) with historical pattern knowledge
(from feedback-loop).

This module extends the Planning with Files workflow by adding pattern-aware suggestions.
"""

import logging
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class PatternSuggester:
    """Suggests patterns based on task descriptions and context."""

    def __init__(self, pattern_manager):
        """Initialize the pattern suggester.

        Args:
            pattern_manager: PatternManager instance to query patterns
        """
        self.pattern_manager = pattern_manager

    def suggest_patterns_for_task(
        self, task_description: str, metrics_context: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """Analyze task description and suggest relevant patterns.

        Args:
            task_description: Description of the task/goal
            metrics_context: Optional metrics context from analyzer (for frequency data)

        Returns:
            List of suggested patterns with confidence scores, sorted by relevance
        """
        task_lower = task_description.lower()

        # Get all available patterns
        all_patterns = self.pattern_manager.get_all_patterns()

        # Score each pattern based on task description
        scored_patterns = []
        for pattern in all_patterns:
            score = self._calculate_relevance_score(pattern, task_lower, metrics_context)
            if score > 0:
                scored_patterns.append(
                    {
                        "pattern": pattern,
                        "name": pattern.get("name", ""),
                        "confidence": score,
                        "description": pattern.get("description", ""),
                        "severity": pattern.get("severity", "medium"),
                    }
                )

        # Sort by confidence (descending)
        scored_patterns.sort(key=lambda x: x["confidence"], reverse=True)

        logger.debug(f"Suggested {len(scored_patterns)} patterns for task")
        return scored_patterns

    def generate_pattern_section(self, patterns: List[Dict[str, Any]]) -> str:
        """Generate markdown section for task_plan.md with suggested patterns.

        Args:
            patterns: List of pattern suggestions (from suggest_patterns_for_task)

        Returns:
            Markdown string with "Patterns to Apply" section
        """
        if not patterns:
            return ""

        lines = ["## Patterns to Apply", ""]

        for pattern_info in patterns:
            pattern_name = pattern_info["name"]
            confidence = pattern_info["confidence"]
            severity = pattern_info.get("severity", "medium")

            # Format: - [ ] pattern_name (confidence: 0.85, from feedback-loop)
            confidence_pct = f"{confidence:.0%}"
            line = f"- [ ] {pattern_name} " f"(confidence: {confidence_pct}, from feedback-loop)"

            # Add severity indicator for high/critical patterns
            if severity in ["high", "critical"]:
                line += f" [{severity.upper()}]"

            lines.append(line)

        lines.append("")
        return "\n".join(lines)

    def _calculate_relevance_score(
        self,
        pattern: Dict[str, Any],
        task_description: str,
        metrics_context: Optional[Dict[str, Any]] = None,
    ) -> float:
        """Calculate how relevant a pattern is to the task description.

        Args:
            pattern: Pattern dictionary from pattern manager
            task_description: Lowercase task description
            metrics_context: Optional metrics context

        Returns:
            Relevance score between 0.0 and 1.0
        """
        pattern_name = pattern.get("name", "").lower()
        pattern_desc = pattern.get("description", "").lower()

        score = 0.0

        # Keyword matching rules
        keyword_rules = {
            "numpy_json_serialization": ["numpy", "json", "serialize", "array", "api"],
            "bounds_checking": ["list", "array", "index", "first", "last", "access"],
            "specific_exceptions": ["exception", "error", "try", "catch", "handle"],
            "logger_debug": ["log", "debug", "print", "logging"],
            "metadata_categorization": ["categorize", "classify", "metadata", "type"],
            "temp_file_handling": ["temp", "file", "temporary", "cleanup"],
            "large_file_processing": ["large", "file", "upload", "stream", "memory"],
            "fastapi": ["fastapi", "endpoint", "api", "route", "upload"],
        }

        # Check pattern-specific keywords
        keywords = keyword_rules.get(pattern_name, [])
        matches = sum(1 for keyword in keywords if keyword in task_description)
        if keywords:
            score = matches / len(keywords)

        # Boost score if pattern name appears in description
        if pattern_name.replace("_", " ") in task_description:
            score = min(1.0, score + 0.3)

        # Boost score if pattern description keywords match
        pattern_keywords = pattern_desc.split()[:5]  # First 5 words
        desc_matches = sum(1 for kw in pattern_keywords if len(kw) > 3 and kw in task_description)
        if pattern_keywords:
            score = min(1.0, score + (desc_matches / len(pattern_keywords)) * 0.2)

        # Boost from metrics context (high frequency patterns)
        if metrics_context:
            high_freq = metrics_context.get("high_frequency_patterns", [])
            critical = metrics_context.get("critical_patterns", [])

            if pattern_name in critical:
                score = min(1.0, score + 0.3)
            elif pattern_name in high_freq:
                score = min(1.0, score + 0.2)

        # Apply severity boost
        severity = pattern.get("severity", "medium")
        if severity == "critical":
            score = min(1.0, score + 0.1)
        elif severity == "high":
            score = min(1.0, score + 0.05)

        return score
