"""
Metrics collection and pattern-aware code generation system.

This module provides functionality for:
- Collecting usage metrics (bugs, test failures, code reviews, etc.)
- Analyzing patterns and trends
- Managing a pattern library
- Generating code with pattern awareness
"""

__version__ = "1.0.0"

from metrics.analyzer import MetricsAnalyzer
from metrics.code_generator import PatternAwareGenerator
from metrics.collector import MetricsCollector
from metrics.pattern_manager import PatternManager

__all__ = [
    "MetricsCollector",
    "MetricsAnalyzer",
    "PatternManager",
    "PatternAwareGenerator",
]
