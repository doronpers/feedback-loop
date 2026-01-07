# Metrics Collection & Pattern-Aware Code Generation System

A comprehensive system for collecting usage metrics, analyzing patterns, and generating code with pattern awareness to continuously improve code quality.

## 📋 Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [Components](#components)
- [CLI Usage](#cli-usage)
- [API Usage](#api-usage)
- [Examples](#examples)

## 🎯 Overview

This system provides:

- **Metrics Collection**: Track bugs, test failures, code reviews, performance issues, and deployments
- **Pattern Analysis**: Identify high-frequency patterns, detect new patterns, calculate effectiveness
- **Pattern Management**: Maintain a living pattern library with automatic updates and archiving
- **Code Generation**: Generate code with automatic pattern application based on context
- **Continuous Improvement**: Learn from past mistakes to prevent future issues

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    METRICS SYSTEM ARCHITECTURE                   │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌──────────────┐      ┌──────────────┐      ┌──────────────┐ │
│  │   Collector  │─────▶│   Analyzer   │─────▶│   Pattern    │ │
│  │              │      │              │      │   Manager    │ │
│  └──────────────┘      └──────────────┘      └──────────────┘ │
│         │                      │                      │        │
│         │                      │                      │        │
│         ▼                      ▼                      ▼        │
│  ┌──────────────────────────────────────────────────────────┐ │
│  │                   Pattern Library (JSON)                  │ │
│  └──────────────────────────────────────────────────────────┘ │
│         │                                                      │
│         ▼                                                      │
│  ┌──────────────┐                                             │
│  │     Code     │                                             │
│  │  Generator   │                                             │
│  └──────────────┘                                             │
│         │                                                      │
│         ▼                                                      │
│  Pattern-Aware Code                                           │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

## 📦 Installation

The metrics system is included in the feedback-loop repository. Ensure dependencies are installed:

```bash
pip install -r requirements.txt
```

Dependencies:
- `numpy>=1.20.0`
- `pytest>=7.0.0`
- `pytest-cov>=4.0.0`
- `openai>=1.0.0` (optional, for AI integration)
- `anthropic>=0.7.0` (optional, for AI integration)

## 🚀 Quick Start

### 1. Run the Demo

See the complete system in action:

```bash
python demo_metrics.py
```

### 2. Collect Metrics

```python
from metrics.collector import MetricsCollector

collector = MetricsCollector()
collector.log_bug(
    pattern="numpy_json_serialization",
    error="TypeError: Object of type float64 is not JSON serializable",
    code='result = {"score": np.mean(data)}',
    file_path="api/endpoints.py",
    line=42
)
```

### 3. Analyze Metrics

```python
from metrics.analyzer import MetricsAnalyzer

analyzer = MetricsAnalyzer(collector.export_dict())
high_freq = analyzer.get_high_frequency_patterns()
print(f"High frequency patterns: {high_freq}")
```

### 4. Generate Pattern-Aware Code

```python
from metrics.pattern_manager import PatternManager
from metrics.code_generator import PatternAwareGenerator

manager = PatternManager("patterns.json")
manager.load_from_ai_patterns_md("AI_PATTERNS.md")

generator = PatternAwareGenerator(manager.get_all_patterns())
result = generator.generate("Process NumPy array and return JSON")
print(result.code)
```

## 🧩 Components

### MetricsCollector

Collects and stores usage metrics from various sources.

**Key Methods:**
- `log_bug()` - Track bug occurrences
- `log_test_failure()` - Track test failures
- `log_code_review_issue()` - Track code review findings
- `log_performance_metric()` - Track performance issues
- `log_deployment_issue()` - Track deployment problems
- `log_code_generation()` - Track code generation events with applied patterns
- `log_from_plan_file()` - Parse and log patterns from Planning-with-Files style task plans
- `export_json()` - Export metrics as JSON
- `get_summary()` - Get metrics summary

**Example:**
```python
collector = MetricsCollector()
collector.log_bug(
    pattern="bounds_checking",
    error="IndexError: list index out of range",
    code='item = items[0]',
    file_path="utils/helpers.py",
    line=15
)
```

**Planning with Files Integration:**

The `log_from_plan_file()` method bridges Planning-with-Files workflows with metrics tracking. It parses a markdown plan file containing a `## Patterns to Apply` checklist, extracts pattern names, and logs them as a code generation entry.

**Usage:**
```python
collector = MetricsCollector()

# Parse patterns from plan file and log as code generation
patterns = collector.log_from_plan_file("task_plan.md")
# Returns: ["numpy_json_serialization", "bounds_checking"]

# Optionally specify custom section heading
patterns = collector.log_from_plan_file("plan.md", section_heading="Required Patterns")
```

**What it logs:**
- Creates a `code_generation` entry with:
  - `prompt`: `"plan:<filename>"` (e.g., `"plan:task_plan.md"`)
  - `patterns_applied`: List of extracted pattern names
  - `confidence`: `1.0` (plan-based patterns are explicit)
  - `success`: `True`
  - `metadata`: Contains `source="plan_file"`, `section_heading`, and `plan_path`

**Safety Guarantees:**
- **Path Traversal Protection**: Rejects paths with `..` components (raises `ValueError`)
- **Allowed Roots Enforcement**: Files must be within allowed roots (`cwd` or `/tmp`), controlled by `ALLOWED_PLAN_ROOTS`
- **Missing File Handling**: Raises `FileNotFoundError` if plan file doesn't exist
- **Annotation Stripping**: Removes trailing parenthetical annotations like `"(from feedback-loop)"` from pattern names
- **Heading-Bound Parsing**: Extracts checklist items only between the specified heading and the next heading

**Parsing Behavior:**
- Recognizes checklist items matching `- [ ]` or `- [x]` or `- [X]`
- Extracts the first sequence of non-whitespace, non-parenthesis, non-hash tokens as the pattern name
- Stops parsing when it encounters the next `##` heading after the target section
- Uses default heading `"Patterns to Apply"` if not specified

**Example Plan File:**
```markdown
# Task: Add JSON API endpoint

## Patterns to Apply
- [ ] numpy_json_serialization (from feedback-loop)
- [x] bounds_checking (from feedback-loop)
- [ ] input_validation

## Implementation Notes
- Use FastAPI for the endpoint
```

The method will extract `["numpy_json_serialization", "bounds_checking", "input_validation"]` and ignore the "Implementation Notes" section.

### MetricsAnalyzer

Analyzes collected metrics to identify patterns and trends.

**Key Methods:**
- `get_high_frequency_patterns()` - Identify frequently occurring patterns
- `detect_new_patterns()` - Find patterns not in library
- `calculate_effectiveness()` - Measure pattern effectiveness over time
- `rank_patterns_by_severity()` - Rank by severity and frequency
- `generate_report()` - Create comprehensive analysis report
- `get_context()` - Get context for code generation

**Example:**
```python
analyzer = MetricsAnalyzer(metrics_data)
high_freq = analyzer.get_high_frequency_patterns(threshold=2)
effectiveness = analyzer.calculate_effectiveness(time_window_days=30)
```

### PatternManager

Manages the pattern library with CRUD operations.

**Key Methods:**
- `load_from_ai_patterns_md()` - Load patterns from AI_PATTERNS.md
- `update_frequencies()` - Update occurrence counts
- `add_new_patterns()` - Add newly detected patterns
- `archive_unused_patterns()` - Archive patterns not used in X days
- `save_patterns()` - Save to JSON file
- `get_pattern_by_name()` - Retrieve specific pattern

**Example:**
```python
manager = PatternManager("patterns.json")
manager.load_from_ai_patterns_md("AI_PATTERNS.md")
manager.update_frequencies(high_freq_patterns)
manager.archive_unused_patterns(days=90)
manager.save_patterns()
```

### PatternAwareGenerator

Generates code with automatic pattern application.

**Key Methods:**
- `generate()` - Generate code with pattern awareness
- `_analyze_prompt()` - Analyze prompt for context
- `_match_patterns()` - Match patterns to context
- `_prioritize_patterns()` - Prioritize by severity
- `_calculate_confidence()` - Calculate confidence score

**Example:**
```python
generator = PatternAwareGenerator(pattern_library)
result = generator.generate(
    prompt="Create FastAPI endpoint for file upload",
    metrics_context=analyzer.get_context(),
    apply_patterns=True,
    min_confidence=0.8
)

print(result.code)
print(result.report)
print(f"Confidence: {result.confidence:.2%}")
```

## 💻 CLI Usage

The system provides a command-line interface via `metrics.integrate`:

### Collect Metrics

```bash
python -m metrics.integrate collect [--metrics-file PATH]
```

### Analyze Metrics

```bash
python -m metrics.integrate analyze [--metrics-file PATH] [--patterns-file PATH] [--no-update]
```

### Generate Code

```bash
python -m metrics.integrate generate "Your prompt here" [--output FILE] [--no-apply] [--min-confidence 0.8]
```

### Generate Report

```bash
python -m metrics.integrate report [--period all|month|week] [--output FILE]
```

## 📚 API Usage

### Full Workflow Example

```python
from metrics.collector import MetricsCollector
from metrics.analyzer import MetricsAnalyzer
from metrics.pattern_manager import PatternManager
from metrics.code_generator import PatternAwareGenerator

# 1. Collect metrics
collector = MetricsCollector()
collector.log_bug(
    pattern="numpy_json_serialization",
    error="TypeError: Object of type float64 is not JSON serializable",
    code='result = {"score": np.mean(data)}',
    file_path="api/endpoints.py",
    line=42
)

# 2. Analyze metrics
analyzer = MetricsAnalyzer(collector.export_dict())
high_freq = analyzer.get_high_frequency_patterns()
new_patterns = analyzer.detect_new_patterns(["numpy_json_serialization", "bounds_checking"])

# 3. Update pattern library
manager = PatternManager("patterns.json")
manager.load_from_ai_patterns_md("AI_PATTERNS.md")
manager.update_frequencies(high_freq)
manager.add_new_patterns(new_patterns)
manager.save_patterns()

# 4. Generate code
generator = PatternAwareGenerator(manager.get_all_patterns())
result = generator.generate(
    prompt="Create function to process NumPy array and return JSON",
    metrics_context=analyzer.get_context()
)

print("Generated Code:")
print(result.code)
print("\nReport:")
print(result.report)
```

### Custom Pattern Format

Patterns in the library follow this schema:

```python
{
    "pattern_id": "uuid-string",
    "name": "pattern_name",
    "description": "What the pattern addresses",
    "bad_example": "code showing the anti-pattern",
    "good_example": "code showing the correct pattern",
    "test_coverage": "test code demonstrating the pattern",
    "occurrence_frequency": 42,
    "last_occurrence": "2024-01-04T12:00:00",
    "severity": "low|medium|high|critical",
    "effectiveness_score": 0.85
}
```

## 🎮 Examples

### Example 1: Track NumPy Serialization Issues

```python
collector = MetricsCollector()

# Log multiple occurrences
for i in range(5):
    collector.log_bug(
        pattern="numpy_json_serialization",
        error="TypeError: Object of type float64 is not JSON serializable",
        code=f'result = {{"score": np.mean(data_{i})}}',
        file_path=f"api/endpoint_{i}.py",
        line=42
    )

# Analyze
analyzer = MetricsAnalyzer(collector.export_dict())
high_freq = analyzer.get_high_frequency_patterns()
print(f"Most common pattern: {high_freq[0]['pattern']} ({high_freq[0]['count']} times)")
```

### Example 2: Generate Code for File Processing

```python
manager = PatternManager("patterns.json")
manager.load_from_ai_patterns_md("AI_PATTERNS.md")

generator = PatternAwareGenerator(manager.get_all_patterns())
result = generator.generate(
    "Create function to upload and process large audio file (up to 800MB)"
)

# Result includes:
# - Proper size validation
# - Chunked reading
# - Error handling
# - Logging
print(result.code)
```

### Example 3: Track Test Failures

```python
collector = MetricsCollector()

collector.log_test_failure(
    test_name="test_json_serialization",
    failure_reason="JSON serialization failed",
    pattern_violated="numpy_json_serialization",
    code_snippet='assert json.dumps({"val": np.float64(1.0)})'
)

collector.log_test_failure(
    test_name="test_empty_list",
    failure_reason="IndexError on empty list",
    pattern_violated="bounds_checking"
)

# Get summary
summary = collector.get_summary()
print(f"Test failures: {summary['test_failures']}")
```

## 📊 Metrics Schema

### Bug Entry
```json
{
  "pattern": "pattern_name",
  "error": "Error message",
  "code": "Code snippet",
  "file_path": "/path/to/file.py",
  "line": 42,
  "stack_trace": "Optional stack trace",
  "timestamp": "2024-01-04T12:00:00",
  "count": 3
}
```

### Test Failure Entry
```json
{
  "test_name": "test_something",
  "failure_reason": "Expected X but got Y",
  "pattern_violated": "pattern_name",
  "code_snippet": "test code",
  "timestamp": "2024-01-04T12:00:00",
  "count": 2
}
```

### Code Review Entry
```json
{
  "issue_type": "Missing validation",
  "pattern": "input_validation",
  "severity": "high|medium|low|critical",
  "file_path": "/path/to/file.py",
  "line": 10,
  "suggestion": "Add input validation",
  "timestamp": "2024-01-04T12:00:00"
}
```

## 🧪 Testing

Run tests:

```bash
# All tests
pytest tests/ -v

# Metrics tests only
pytest tests/test_metrics.py -v

# With coverage
pytest tests/test_metrics.py --cov=metrics --cov-report=term-missing
```

Current test coverage:
- **39 tests** covering all components
- **MetricsCollector**: 89% coverage
- **MetricsAnalyzer**: 72% coverage
- **PatternManager**: 59% coverage (excluding markdown parsing)
- **PatternAwareGenerator**: 82% coverage

## 🔧 Configuration

### Pattern Library Path

By default, the pattern library is stored in `patterns.json`. You can specify a custom path:

```python
manager = PatternManager("custom/path/patterns.json")
```

### Minimum Confidence Threshold

Control when patterns are automatically applied:

```python
result = generator.generate(
    prompt="...",
    min_confidence=0.9  # Only apply patterns with 90%+ confidence
)
```

### Archive Duration

Configure how long patterns must be unused before archiving:

```python
archived = manager.archive_unused_patterns(days=60)  # Archive after 60 days
```

## 📝 Best Practices

1. **Regular Collection**: Collect metrics continuously from CI/CD, production logs, and code reviews
2. **Periodic Analysis**: Run analysis weekly or monthly to track trends
3. **Pattern Review**: Manually review auto-detected patterns before adding to library
4. **Confidence Tuning**: Adjust `min_confidence` based on your team's tolerance for auto-applied patterns
5. **Documentation**: Keep pattern examples up-to-date with current codebase
6. **Archive Cleanup**: Regularly archive unused patterns to keep library focused

## 🚀 Future Enhancements

- Integration with CI/CD pipelines
- Real-time pattern suggestions in IDEs
- Machine learning for pattern detection
- Team-specific pattern libraries
- Pattern effectiveness A/B testing
- Visual dashboards for metrics

## 📄 License

Part of the feedback-loop repository. See main LICENSE file for details.
