# Metrics Integration Guide

Complete guide to integrating and using the metrics collection and pattern-aware code generation system.

## 📋 Table of Contents

1. [Introduction](#introduction)
2. [System Overview](#system-overview)
3. [Getting Started](#getting-started)
4. [Collecting Metrics](#collecting-metrics)
5. [Analyzing Patterns](#analyzing-patterns)
6. [Pattern-Aware Code Generation](#pattern-aware-code-generation)
7. [Integration Workflows](#integration-workflows)
8. [Customization](#customization)
9. [Troubleshooting](#troubleshooting)
10. [FAQ](#faq)

## 1. Introduction

The Metrics Integration System provides a feedback loop for continuous code quality improvement by:

- **Learning from Mistakes**: Automatically collecting data about bugs, failures, and issues
- **Identifying Patterns**: Detecting recurring problems that should be systematized
- **Preventing Recurrence**: Applying learned patterns to new code automatically
- **Measuring Effectiveness**: Tracking how well patterns prevent issues over time

### Key Benefits

✅ **Reduced Bugs**: Prevent known issues from recurring
✅ **Consistent Quality**: Apply best practices automatically
✅ **Team Learning**: Share knowledge through pattern library
✅ **Faster Development**: Reduce time spent on common problems
✅ **Data-Driven**: Make decisions based on actual metrics

## 2. System Overview

### Components

```
┌─────────────────────────────────────────────────────────┐
│                   FEEDBACK LOOP CYCLE                    │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  1. COLLECT      →  2. ANALYZE     →  3. LEARN          │
│     Metrics          Patterns          Update Library    │
│        ↑                                    │            │
│        │                                    ↓            │
│  4. GENERATE  ←  ←  ←  ←  ←  ←  ←  ←  ←  Pattern        │
│     New Code                               Aware         │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

### Data Flow

1. **Metrics Collection**: Bugs, test failures, code reviews, performance issues
2. **Pattern Analysis**: Frequency analysis, trend detection, effectiveness scoring
3. **Pattern Management**: Update library, add new patterns, archive unused
4. **Code Generation**: Context-aware code with automatic pattern application

## 3. Getting Started

### Installation

See [README.md](../README.md) for installation instructions.

Quick start for metrics system:

```bash
python demo_metrics.py
```

### Initial Setup

1. **Initialize Pattern Library**:

```python
from metrics.pattern_manager import PatternManager

manager = PatternManager("data/patterns.json")
manager.load_from_ai_patterns_md("documentation/AI_PATTERNS_GUIDE.md")
manager.save_patterns()
```

1. **Set Up Metrics Collection**:

```python
from metrics.collector import MetricsCollector

collector = MetricsCollector()
# Start collecting metrics (see section 4)
```

1. **Run First Analysis**:

```bash
python -m metrics.integrate collect
python -m metrics.integrate analyze
python -m metrics.integrate report --format text  # or --format markdown
```

## 4. Collecting Metrics

### 4.1 Bug Tracking

Track bugs that occur in development or production:

```python
from metrics.collector import MetricsCollector

collector = MetricsCollector()

# Log a bug
collector.log_bug(
    pattern="numpy_json_serialization",
    error="TypeError: Object of type float64 is not JSON serializable",
    code='result = {"score": np.mean(data)}',
    file_path="api/endpoints.py",
    line=42,
    stack_trace="Traceback (most recent call last)..."  # Optional
)
```

**When to log bugs:**

- Exception handlers catch known issues
- CI/CD detects failures
- Production error monitoring alerts
- Manual bug reports filed

### 4.2 Test Failure Tracking

Track test failures to identify patterns:

```python
collector.log_test_failure(
    test_name="test_numpy_serialization",
    failure_reason="JSON serialization failed for NumPy types",
    pattern_violated="numpy_json_serialization",
    code_snippet='assert json.dumps({"val": np.float64(1.0)})'
)
```

**Integration points:**

- pytest hooks
- unittest tearDown methods
- CI/CD test runners
- Pre-commit test runs

### 4.3 Code Review Issues

Track findings from code reviews:

```python
collector.log_code_review_issue(
    issue_type="Missing exception handling",
    pattern="specific_exceptions",
    severity="high",  # low|medium|high|critical
    file_path="core/parser.py",
    line=67,
    suggestion="Use specific exceptions instead of bare except"
)
```

**Sources:**

- Manual code reviews
- Automated linting tools
- Static analysis results
- Pull request comments

### 4.4 Performance Metrics

Track performance issues:

```python
# Memory errors
collector.log_performance_metric(
    metric_type="memory_error",
    details={
        "error": "MemoryError loading 900MB file",
        "file_size": 900 * 1024 * 1024,
        "context": "Audio file processing"
    }
)

# Execution times
collector.log_performance_metric(
    metric_type="execution_time",
    details={
        "function": "process_large_file",
        "avg_time_ms": 5420,
        "max_time_ms": 8900,
        "sample_size": 50
    }
)
```

### 4.5 Deployment Issues

Track deployment problems:

```python
collector.log_deployment_issue(
    issue_type="File upload limit exceeded",
    pattern="large_file_processing",
    environment="production",
    root_cause="nginx client_max_body_size not configured",
    resolution_time_minutes=45
)
```

### 4.6 Saving and Loading Metrics

```python
# Export to JSON
json_str = collector.export_json()
with open("metrics_data.json", "w") as f:
    f.write(json_str)

# Load from JSON
with open("metrics_data.json", "r") as f:
    json_str = f.read()
collector.load_from_json(json_str)

# Get summary
summary = collector.get_summary()
print(f"Total metrics collected: {summary['total']}")
```

## 5. Analyzing Patterns

### 5.1 High-Frequency Pattern Detection

Identify patterns that occur frequently:

```python
from metrics.analyzer import MetricsAnalyzer

analyzer = MetricsAnalyzer(collector.export_dict())

# Find patterns occurring at least 3 times
high_freq = analyzer.get_high_frequency_patterns(threshold=3)

for pattern in high_freq:
    print(f"{pattern['pattern']}: {pattern['count']} occurrences")
```

### 5.2 New Pattern Detection

Detect patterns not yet in your library:

```python
# Get known patterns from library
known_patterns = manager.get_pattern_names()

# Detect new patterns
new_patterns = analyzer.detect_new_patterns(known_patterns)

for pattern in new_patterns:
    print(f"New: {pattern['pattern']} ({pattern['count']} occurrences)")
    print(f"Details: {pattern['details'][:2]}")  # First 2 occurrences
```

### 5.3 Effectiveness Analysis

Measure how well patterns prevent issues:

```python
# Calculate effectiveness over last 30 days
effectiveness = analyzer.calculate_effectiveness(time_window_days=30)

for pattern, metrics in effectiveness.items():
    print(f"{pattern}:")
    print(f"  Score: {metrics['score']:.1%}")
    print(f"  Trend: {metrics['trend']}")
    print(f"  Total occurrences: {metrics['total_occurrences']}")
```

**Effectiveness Trends:**

- `improving`: Occurrences decreasing over time (pattern is working)
- `stable`: Occurrences steady (pattern maintains quality)
- `worsening`: Occurrences increasing (pattern needs review)
- `insufficient_data`: Not enough data points to determine trend

### 5.4 Severity Ranking

Rank patterns by severity and frequency:

```python
ranked = analyzer.rank_patterns_by_severity()

print("Top 10 patterns by severity:")
for item in ranked[:10]:
    print(f"{item['severity'].upper():10} | {item['pattern']:30} | Count: {item['count']}")
```

### 5.5 Comprehensive Reports

Generate full analysis reports:

```python
report = analyzer.generate_report()

print(f"Summary:")
print(f"  Bugs: {report['summary']['total_bugs']}")
print(f"  Test Failures: {report['summary']['total_test_failures']}")
print(f"  Code Reviews: {report['summary']['total_code_reviews']}")

# Save report
with open("analysis_report.json", "w") as f:
    json.dump(report, f, indent=2)
```

## 6. Pattern-Aware Code Generation

### 6.1 Basic Code Generation

Generate code with automatic pattern application:

```python
from metrics.code_generator import PatternAwareGenerator

generator = PatternAwareGenerator(
    pattern_library=manager.get_all_patterns(),
    pattern_library_version="1.0.0"
)

result = generator.generate(
    prompt="Create function to process NumPy array and return JSON"
)

print(result.code)
print(result.report)
```

### 6.2 Context-Aware Generation

Use metrics context to prioritize patterns:

```python
# Get context from analyzer
metrics_context = analyzer.get_context()

result = generator.generate(
    prompt="Create FastAPI endpoint for audio file upload",
    metrics_context=metrics_context,
    apply_patterns=True,
    min_confidence=0.8
)

print(f"Confidence: {result.confidence:.1%}")
print(f"Patterns applied: {len(result.patterns_applied)}")
print(f"Patterns suggested: {len(result.patterns_suggested)}")
```

### 6.3 Generation Result Structure

```python
result = generator.generate("...")

# Generated code with pattern annotations
print(result.code)

# Applied patterns
for match in result.patterns_applied:
    print(f"Applied: {match['pattern']['name']}")
    print(f"  Confidence: {match['confidence']:.1%}")
    print(f"  Severity: {match['severity']}")

# Suggested patterns (not auto-applied)
for match in result.patterns_suggested:
    print(f"Suggested: {match['pattern']['name']}")

# Metadata
print(result.metadata)
# {
#     "prompt": "...",
#     "pattern_library_version": "1.0.0",
#     "timestamp": "2024-01-04T12:00:00",
#     "confidence": 0.87,
#     "context_indicators": {"numpy": True, "json": True}
# }

# Human-readable report
print(result.report)
```

### 6.4 Pattern Application Rules

Patterns are applied based on severity:

| Severity | Auto-Applied? | Threshold |
|----------|---------------|-----------|
| Critical | Always | N/A |
| High | Yes (default) | min_confidence |
| Medium | Yes (with notice) | min_confidence |
| Low | Suggested only | N/A |

### 6.5 Customizing Generation

```python
# Don't apply patterns automatically
result = generator.generate(
    prompt="...",
    apply_patterns=False  # Only suggest, don't apply
)

# Higher confidence threshold
result = generator.generate(
    prompt="...",
    min_confidence=0.95  # Only apply patterns with 95%+ confidence
)

# Without metrics context
result = generator.generate(
    prompt="...",
    metrics_context=None  # Don't use historical data
)
```

## 7. Integration Workflows

### 7.1 CI/CD Integration

#### GitHub Actions Example

```yaml
name: Metrics Collection
on: [push, pull_request]

jobs:
  collect-metrics:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Install dependencies
        run: pip install -r requirements.txt

      - name: Run tests and collect failures
        run: |
          pytest tests/ --json-report --json-report-file=test_results.json || true

      - name: Parse test results and log metrics
        run: python scripts/parse_test_results.py

      - name: Analyze patterns
        run: python -m metrics.integrate analyze

      - name: Upload metrics
        uses: actions/upload-artifact@v2
        with:
          name: metrics
          path: |
            metrics_data.json
            patterns.json
```

### 7.2 Pre-commit Hook

```bash
#!/bin/bash
# .git/hooks/pre-commit

# Analyze recent patterns before commit
python -m metrics.integrate analyze --no-update

# Generate pattern report
python -m metrics.integrate report > /tmp/pattern_report.txt

# Show top issues
echo "Top patterns to watch:"
grep "CRITICAL\|HIGH" /tmp/pattern_report.txt | head -5
```

### 7.3 Development Workflow

```python
# In your development script/notebook
from metrics.collector import MetricsCollector
from metrics.code_generator import PatternAwareGenerator

# Initialize
collector = MetricsCollector()
generator = PatternAwareGenerator(...)

# During development
try:
    result = some_function()
except Exception as e:
    # Log the error
    collector.log_bug(
        pattern="unknown",
        error=str(e),
        code=inspect.getsource(some_function),
        file_path=__file__,
        line=inspect.currentframe().f_lineno
    )
    raise

# Generate new code with pattern awareness
result = generator.generate("Create data processing function")
```

### 7.4 Production Monitoring

```python
# In your application error handler
import logging
from metrics.collector import MetricsCollector

collector = MetricsCollector()

def error_handler(error, context):
    """Log production errors to metrics system."""

    # Classify error type
    pattern = classify_error(error)

    # Log to metrics
    collector.log_bug(
        pattern=pattern,
        error=str(error),
        code=context.get("code_snippet", ""),
        file_path=context.get("file", ""),
        line=context.get("line", 0),
        stack_trace=context.get("traceback", "")
    )

    # Send to monitoring service
    logging.error(f"Error: {error}", extra=context)

    # Save metrics periodically
    if should_save_metrics():
        with open("metrics_data.json", "w") as f:
            f.write(collector.export_json())
```

## 8. Customization

### 8.1 Custom Patterns

Add custom patterns to your library:

```python
custom_pattern = {
    "pattern_id": str(uuid.uuid4()),
    "name": "custom_validation",
    "description": "Always validate user input before processing",
    "bad_example": "def process(data): return data.upper()",
    "good_example": "def process(data): return data.upper() if data else ''",
    "test_coverage": "def test_process(): assert process('') == ''",
    "occurrence_frequency": 0,
    "last_occurrence": None,
    "severity": "high",
    "effectiveness_score": 0.5
}

manager.patterns.append(custom_pattern)
manager.save_patterns()
```

### 8.2 Custom Metrics

Extend the collector for domain-specific metrics:

```python
class CustomMetricsCollector(MetricsCollector):
    """Extended collector with custom metric types."""

    def log_api_error(self, endpoint, status_code, error):
        """Log API-specific errors."""
        self.log_bug(
            pattern="api_error",
            error=f"{status_code}: {error}",
            code=f"Endpoint: {endpoint}",
            file_path="api/routes.py",
            line=0
        )

    def log_database_slow_query(self, query, execution_time_ms):
        """Log slow database queries."""
        self.log_performance_metric(
            metric_type="slow_query",
            details={
                "query": query,
                "execution_time_ms": execution_time_ms,
                "threshold_ms": 1000
            }
        )
```

### 8.3 Custom Analysis

Create custom analyzers for specific needs:

```python
class CustomAnalyzer(MetricsAnalyzer):
    """Extended analyzer with custom analysis methods."""

    def get_api_error_rate(self):
        """Calculate API error rate."""
        api_errors = [
            bug for bug in self.metrics_data.get("bugs", [])
            if bug.get("pattern") == "api_error"
        ]
        return len(api_errors)

    def get_slowest_queries(self, top_n=10):
        """Get slowest database queries."""
        queries = [
            metric for metric in self.metrics_data.get("performance_metrics", [])
            if metric.get("metric_type") == "slow_query"
        ]
        queries.sort(
            key=lambda x: x["details"].get("execution_time_ms", 0),
            reverse=True
        )
        return queries[:top_n]
```

### 8.4 Custom Code Templates

Customize code generation templates:

```python
class CustomGenerator(PatternAwareGenerator):
    """Extended generator with custom templates."""

    def _generate_api_endpoint(self, prompt):
        """Generate FastAPI endpoint with custom structure."""
        return [
            "@router.post('/endpoint')",
            "async def endpoint(request: Request):",
            "    # Pattern: input_validation",
            "    if not request:",
            "        raise HTTPException(400, 'Invalid request')",
            "    ",
            "    # Pattern: logger_debug",
            "    logger.debug(f'Processing request: {request}')",
            "    ",
            "    # Implementation",
            "    result = process(request)",
            "    return result"
        ]
```

## 9. Troubleshooting

### 9.1 Common Issues

**Issue: Pattern library not loading from the patterns guide**

Solution:

```python
# Check file exists
import os
assert os.path.exists("documentation/AI_PATTERNS_GUIDE.md"), "File not found"

# Load with error handling
try:
    manager.load_from_ai_patterns_md("documentation/AI_PATTERNS_GUIDE.md")
except Exception as e:
    print(f"Error loading patterns: {e}")
    # Use default patterns or manual creation
```

**Issue: Low coverage in pattern detection**

Solution:

- Lower the threshold: `get_high_frequency_patterns(threshold=1)`
- Collect more metrics over time
- Check that pattern names match between metrics and library

**Issue: Generated code doesn't include expected patterns**

Solution:

```python
# Check context indicators
indicators = generator._analyze_prompt(prompt)
print(f"Detected context: {indicators}")

# Check pattern matching
matched = generator._match_patterns(indicators, metrics_context)
print(f"Matched patterns: {[m['pattern']['name'] for m in matched]}")

# Lower confidence threshold
result = generator.generate(prompt, min_confidence=0.5)
```

### 9.2 Debugging

Enable debug logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)

# Now all operations will log debug information
collector.log_bug(...)  # Shows: "Logged bug for pattern: ..."
```

Check metrics data structure:

```python
import json
data = collector.export_dict()
print(json.dumps(data, indent=2))
```

Verify pattern library:

```python
patterns = manager.get_all_patterns()
print(f"Total patterns: {len(patterns)}")
for p in patterns:
    print(f"  - {p['name']}: freq={p.get('occurrence_frequency', 0)}")
```

## 10. FAQ

**Q: How often should I analyze metrics?**
A: Weekly for active projects, monthly for stable projects. More frequent analysis helps catch emerging patterns early.

**Q: What's a good confidence threshold?**
A: Start with 0.8 (80%). Lower if you want more aggressive pattern application, raise if you get too many false positives.

**Q: How many patterns should I have?**
A: Start with 5-10 core patterns. Add 1-2 per month based on detected issues. Archive patterns not used in 90 days.

**Q: Can I use this with languages other than Python?**
A: The system is Python-based, but metrics collection can work with any language. Code generation currently targets Python.

**Q: How do I share patterns across teams?**
A: Store `patterns.json` in a shared repository. Teams pull latest patterns before generation.

**Q: What if a pattern is applied incorrectly?**
A: Review the `patterns_suggested` list and manually apply. Add feedback to improve pattern matching rules.

**Q: How do I integrate with our existing monitoring?**
A: Export metrics to JSON and send to your monitoring service. See section 7.4 for examples.

**Q: Can I use this in production?**
A: Yes! The metrics collector is lightweight. Code generation is best used in development. See production monitoring section.

**Q: How do I contribute new patterns?**
A: Update `documentation/AI_PATTERNS_GUIDE.md` and keep examples/tests in sync. See `CONTRIBUTING.md`.

**Q: What's the performance impact?**
A: Metrics collection: <1ms per operation. Analysis: ~100ms for 1000 entries. Generation: ~500ms per request.

---

## Need Help?

- 📖 See [metrics/README.md](../metrics/README.md) for API documentation
- 🎮 Run `python demo_metrics.py` for interactive demonstration
- 🐛 Check [GitHub Issues](https://github.com/doronpers/feedback-loop/issues) for known problems
- 💬 Ask questions in discussions

## Contributing

Contributions welcome! Please:

1. Add tests for new features
2. Update documentation
3. Follow existing code patterns
4. Submit pull requests with clear descriptions

---

**Happy coding with pattern awareness! 🎯**
