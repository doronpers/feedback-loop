# Planning with Files Integration Guide

This guide explains how to use the integration between **Planning with Files** and **feedback-loop** to combine current task state with historical pattern knowledge.

## Overview

The integration connects two context engineering systems:

- **Planning with Files**: Manages current task state via markdown files (task_plan.md, notes.md)
- **Feedback-Loop**: Provides historical pattern knowledge and metrics

This enables bidirectional knowledge flow: task plans reference patterns, and feedback-loop learns from plan files.

## Attribution

This integration incorporates concepts and patterns from the **Planning with Files** project:

- **Original work**: [Planning with Files](https://github.com/OthmanAdi/planning-with-files)
- **Author**: Ahmad Othman Ammar Adi (OthmanAdi)
- **License**: MIT License
- **Description**: Claude Code skill implementing Manus-style persistent markdown planning

### Key Concepts Used

- Persistent markdown files for task state management (task_plan.md, notes.md)
- The 3-file pattern (task_plan.md, notes.md, deliverables)
- Context engineering principles for AI-assisted development
- Filesystem as memory approach

## Quick Start

### 1. Create a Task Plan

Create a `task_plan.md` file with your task goal:

```markdown
# Task Plan

## Goal
Fix JSON serialization bug in API endpoint

## Phases
- [ ] Phase 1: Research
- [ ] Phase 2: Implementation
- [ ] Phase 3: Testing
```

### 2. Get Pattern Suggestions

Run the pattern suggester to get relevant patterns:

```bash
python -m metrics.integrate suggest-patterns --task-plan task_plan.md
```

This will analyze your task and add a "Patterns to Apply" section:

```markdown
## Patterns to Apply
- [ ] numpy_json_serialization (confidence: 85%, from feedback-loop)
- [ ] bounds_checking (confidence: 72%, from feedback-loop)
```

### 3. Extract Patterns for Metrics

Log the planned patterns to metrics:

```bash
python -m metrics.integrate extract-plan-patterns --plan task_plan.md
```

This records which patterns you planned to use, making them analyzable alongside actual code generation.

### 4. Generate Code with Task Context

Generate code that uses both your task context and pattern library:

```bash
python -m metrics.integrate generate-with-plan \
  --prompt "Create function to serialize NumPy array to JSON" \
  --plan task_plan.md
```

The generated code will:
- Include your task goal in the context
- Prioritize patterns referenced in your plan
- Apply learned patterns from the pattern library

## Workflows

### Workflow 1: Creating a Task Plan with Pattern Suggestions

1. Create `task_plan.md` with your goal
2. Run: `python -m metrics.integrate suggest-patterns --task-plan task_plan.md`
3. Review suggested patterns and check off as you apply them
4. Patterns are automatically added to your plan file

### Workflow 2: Code Generation with Task Context

1. Create or update `task_plan.md` with goal and referenced patterns
2. Run: `python -m metrics.integrate generate-with-plan --prompt "Your prompt" --plan task_plan.md`
3. Generated code includes:
   - Task goal context
   - Current phase information
   - Prioritized patterns from your plan

### Workflow 3: Learning from Plan Files

1. Periodically run: `python -m metrics.integrate extract-plan-patterns --plan task_plan.md`
2. Patterns from plans are logged to metrics
3. Analyzer can identify: "numpy_json_serialization is commonly used for JSON processing tasks"

## API Usage

### Programmatic Pattern Suggestions

```python
from metrics.pattern_manager import PatternManager
from metrics.pattern_suggester import PatternSuggester

manager = PatternManager("patterns.json")
suggester = PatternSuggester(manager)

suggestions = suggester.suggest_patterns_for_task(
    "Serialize NumPy arrays to JSON"
)

for suggestion in suggestions:
    print(f"{suggestion['name']}: {suggestion['confidence']:.1%}")
```

### Extract Task Context

```python
from metrics.plan_parser import PlanParser

parser = PlanParser()
context = parser.extract_task_context("task_plan.md")

print(f"Goal: {context['goal']}")
print(f"Current Phase: {context['current_phase']}")
```

### Generate Code with Task Context

```python
from metrics.code_generator import PatternAwareGenerator
from metrics.pattern_manager import PatternManager

manager = PatternManager("patterns.json")
generator = PatternAwareGenerator(manager.get_all_patterns())

result = generator.generate_with_task_context(
    prompt="Create function to process data",
    task_plan_path="task_plan.md"
)

print(result.code)
```

### Log Patterns from Plan

```python
from metrics.collector import MetricsCollector

collector = MetricsCollector()
patterns = collector.log_from_plan_file("task_plan.md")

print(f"Extracted {len(patterns)} patterns: {patterns}")
```

## Plan File Format

### Required Sections

```markdown
# Task Plan

## Goal
Your task goal here

## Phases
- [ ] Phase 1: Description
- [x] Phase 2: Description (CURRENT)
- [ ] Phase 3: Description

## Patterns to Apply
- [ ] pattern_name (from feedback-loop)
- [x] another_pattern (from feedback-loop) ✓ Applied
```

### Pattern Reference Format

Patterns in the "Patterns to Apply" section can be formatted as:

- `- [ ] pattern_name` - Unchecked (not yet applied)
- `- [x] pattern_name` - Checked (applied)
- `- [ ] pattern_name (from feedback-loop)` - With source annotation
- `- [ ] pattern_name (confidence: 0.85, from feedback-loop)` - With confidence

The parser extracts pattern names and ignores trailing annotations.

## Integration Points

### Pattern References in task_plan.md

The system extracts patterns from checklists in the "Patterns to Apply" section:

```markdown
## Patterns to Apply
- [x] numpy_json_serialization (from feedback-loop) ✓ Applied
- [ ] bounds_checking (from feedback-loop)
- [ ] specific_exceptions (from feedback-loop, confidence: 0.65)
```

### Task Context in Code Generation

When generating code with task context, the system enriches the prompt:

```
Task Goal: Fix JSON serialization bug in API endpoint
Current Phase: Implementation
Referenced Patterns: numpy_json_serialization, bounds_checking

User Prompt: Create function to serialize NumPy array to JSON
```

### Metrics Tracking

Patterns from plan files are stored in the `code_generation` metrics category:

```json
{
  "code_generation": [
    {
      "prompt": "plan:task_plan.md",
      "patterns_applied": ["numpy_json_serialization", "bounds_checking"],
      "confidence": 1.0,
      "success": true,
      "metadata": {
        "source": "plan_file",
        "section_heading": "Patterns to Apply",
        "plan_path": "/absolute/path/to/task_plan.md"
      }
    }
  ]
}
```

## Safety Features

The integration includes security features:

- **Path traversal protection**: Rejects paths containing `..`
- **Allowed plan roots**: Configurable via `MetricsCollector.ALLOWED_PLAN_ROOTS`
- **File existence validation**: Checks files exist before processing

## Examples

### Example 1: JSON Serialization Task

**task_plan.md**:
```markdown
# Task Plan

## Goal
Fix JSON serialization errors in API endpoints

## Patterns to Apply
- [ ] numpy_json_serialization (from feedback-loop)
- [ ] bounds_checking (from feedback-loop)
```

**Command**:
```bash
python -m metrics.integrate extract-plan-patterns --plan task_plan.md
python -m metrics.integrate generate-with-plan \
  --prompt "Create endpoint to return NumPy array as JSON" \
  --plan task_plan.md
```

### Example 2: Large File Processing

**task_plan.md**:
```markdown
# Task Plan

## Goal
Handle large file uploads without memory issues

## Patterns to Apply
- [ ] large_file_processing (from feedback-loop)
- [ ] temp_file_handling (from feedback-loop)
```

**Command**:
```bash
python -m metrics.integrate suggest-patterns --task-plan task_plan.md
# Reviews suggestions, then:
python -m metrics.integrate generate-with-plan \
  --prompt "Create FastAPI endpoint for large file upload" \
  --plan task_plan.md
```

## Troubleshooting

### No patterns suggested

- Check that your task description includes relevant keywords
- Ensure pattern library is loaded: `python -m metrics.integrate analyze`
- Try a more specific task description

### Plan file not found

- Verify the file path is correct
- Check that file is within allowed roots (current directory or /tmp)
- Ensure file exists and is readable

### Patterns not extracted

- Verify "Patterns to Apply" section exists in plan file
- Check section heading matches exactly (case-insensitive)
- Ensure patterns are in checklist format: `- [ ] pattern_name`

## References

1. **Planning with Files** - OthmanAdi (2024). 
   [planning-with-files](https://github.com/OthmanAdi/planning-with-files). 
   MIT License. Claude Code skill implementing Manus-style persistent markdown planning.

2. **Manus AI** - Context engineering patterns that inspired Planning with Files.
   Meta acquired Manus for $2B in December 2024.

3. **Feedback-Loop** - This project. Reusable and improvable AI-assisted development patterns.

## Next Steps

- See [METRICS_INTEGRATION.md](METRICS_INTEGRATION.md) for metrics system details
- See [README.md](README.md) for overall project documentation
- See [AI_PATTERNS.md](AI_PATTERNS.md) for pattern catalog
