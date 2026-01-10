# Feedback Loop Improvements

This document describes the major improvements implemented to transform the feedback-loop system from a theoretical framework into a fully functional continuous improvement tool.

## Overview

Three major improvements have been implemented:

1. **Automated Metrics Collection** - Pytest plugin and CI/CD integration
2. **Real AI Integration** - LLM-powered code generation with pattern context
3. **Continuous Feedback** - GitHub Actions workflow for automated analysis

## 1. Automated Metrics Collection

### Pytest Plugin (`conftest.py`)

Automatically collects test failure metrics without manual intervention.

**Features:**
- Auto-detects pattern violations from test failures
- Extracts code snippets and error information
- Supports pattern detection heuristics
- Saves metrics to JSON file

**Usage:**
```bash
# Enable automatic metrics collection
pytest tests/ --enable-metrics

# Save metrics to specific file
pytest tests/ --metrics-output=metrics_ci.json
```

**How it works:**
- Hooks into pytest's test execution
- Captures failures in real-time
- Detects patterns like:
  - `numpy_json_serialization` - NumPy type errors
  - `bounds_checking` - Index out of range errors
  - `specific_exceptions` - Bare except issues
  - `logger_debug` - Print vs logger issues

### Git Pre-Commit Hook (`hooks/pre-commit`)

Analyzes staged changes before allowing commits.

**Installation:**
```bash
cp hooks/pre-commit .git/hooks/pre-commit
chmod +x .git/hooks/pre-commit
```

**Features:**
- Scans staged Python files for pattern violations
- Shows warnings with file/line numbers
- Provides suggestions for fixes
- Non-blocking (warnings only)

**Example output:**
```
🔄 Running feedback loop pattern analysis...

⚠️  Found 2 potential pattern violations:

  examples/bad_patterns.py:42
    Pattern: bounds_checking
    Issue: List access without bounds checking
    Suggestion: Check length: if items: first = items[0]

💡 Tip: These are warnings. Review the suggestions above.
   To bypass this check: git commit --no-verify
```

### Code Generation Logging

The metrics system now tracks code generation events.

**New method in `MetricsCollector`:**
```python
collector.log_code_generation(
    prompt="Create a function to process JSON",
    patterns_applied=["numpy_json_serialization"],
    confidence=0.85,
    success=True,
    code_length=150
)
```

This creates a feedback loop where the system learns from its own code generation success/failure rates.

## 2. Real AI Integration

### LLM-Powered Code Generation

Replaced hardcoded templates with actual Anthropic Claude API integration.

**Key improvements:**
- Uses Claude Sonnet 4.5 for intelligent code generation
- Enriches prompts with pattern context from metrics
- Includes pattern examples and effectiveness scores
- Falls back to templates if API unavailable

**Environment setup:**
```bash
export ANTHROPIC_API_KEY=your_api_key_here
```

**Usage:**
```bash
python -m metrics.integrate generate "Create a function to process NumPy arrays and return JSON"
```

**How it works:**

1. **Pattern Matching**: Analyzes prompt for relevant patterns
2. **Context Enrichment**: Builds enriched prompt with:
   - Required patterns and their effectiveness scores
   - Good examples from pattern library
   - Metrics context (high-frequency issues)
3. **LLM Generation**: Calls Claude API with enriched prompt
4. **Validation**: Validates generated code for syntax and common issues
5. **Feedback Logging**: Logs generation results back to metrics

**Example enriched prompt:**
```
Create a function to process NumPy arrays and return JSON

## Required Patterns
Apply the following validated patterns to your code:

### Pattern: numpy_json_serialization
**Effectiveness:** 85.0%
**Description:** Convert NumPy types before JSON serialization
**Example:**
```python
result = {"mean": float(np.mean(data))}
return json.dumps(result)
```

## Instructions
Generate production-ready Python code that:
1. Implements the requested functionality
2. Applies all required patterns
3. Includes proper error handling
4. Has clear comments explaining pattern usage
5. Is syntactically correct and ready to run
```

### Code Validation

All generated code is automatically validated.

**Validation checks:**
- Syntax validation using AST parsing
- Detection of `print()` statements (should use logger)
- Detection of bare `except:` clauses
- Detection of TODO/FIXME comments

**Validation output:**
```
Validation Results:
  Syntax Valid: ✓
  Warnings: 1
    - Code contains print() statements - consider using logger.debug()
  Overall: ✗ Issues Found
```

## 3. Continuous Feedback via GitHub Actions

### Workflow (`.github/workflows/feedback-loop.yml`)

Automatically runs on every push and pull request.

**Workflow steps:**

1. **Run tests with metrics collection**
   ```bash
   pytest tests/ -v --metrics-output=metrics_ci.json --enable-metrics
   ```

2. **Analyze git diff for pattern violations**
   ```bash
   python -m metrics.integrate analyze-commit \
     --base=${{ github.event.pull_request.base.sha }} \
     --head=${{ github.sha }}
   ```

3. **Analyze metrics and update patterns**
   ```bash
   python -m metrics.integrate analyze \
     --metrics-file=metrics_ci.json \
     --patterns-file=patterns.json
   ```

4. **Generate and post report as PR comment**
   - Automatic comment on PR with pattern violations
   - Updates existing comment if already present
   - Includes suggestions and file/line references

5. **Upload artifacts**
   - Metrics data (30 day retention)
   - Pattern library (90 day retention)

**Example PR comment:**
```markdown
## 🔄 Feedback Loop Analysis

## Pattern Violations Detected

- **bounds_checking**: List access without bounds checking
  - File: `examples/new_feature.py`
  - Suggestion: Check length: if items: first = items[0]

- **numpy_json_serialization**: NumPy types may not be JSON serializable
  - File: `api/endpoints.py`
  - Suggestion: Convert NumPy types: float(np_value)

## Metrics Analysis Report

✓ High Frequency Patterns: 3
  - numpy_json_serialization: 5 occurrences
  - bounds_checking: 3 occurrences
```

## 4. Bidirectional Pattern Sync

### Sync from patterns.json to AI_PATTERNS.md

The pattern library now maintains bidirectional sync.

**New method in `PatternManager`:**
```python
pattern_manager.sync_to_markdown("AI_PATTERNS.md")
```

**CLI command:**
```bash
python -m metrics.integrate sync-to-markdown
```

**What it does:**
- Reads all patterns from `patterns.json`
- Generates markdown sections with:
  - Pattern name and ID
  - Frequency and effectiveness metrics
  - Bad and good examples
  - Description
- Preserves non-pattern content in AI_PATTERNS.md
- Sorts patterns by occurrence frequency

**Generated markdown example:**
```markdown
### 1. Numpy Json Serialization

**Pattern:** `numpy_json_serialization`

**Metrics:** Frequency: 12 | Effectiveness: 85.0%

**Problems:**
Convert NumPy types before JSON serialization to avoid TypeError

❌ Bad Pattern:
```python
result = {"mean": np.mean(data)}
return json.dumps(result)  # TypeError!
```

✅ Good Pattern:
```python
result = {"mean": float(np.mean(data))}
return json.dumps(result)  # Works!
```
```

## 5. New CLI Commands

### `analyze-commit`

Analyzes git commit diff for pattern violations.

```bash
python -m metrics.integrate analyze-commit \
  --base=abc123 \
  --head=def456 \
  --output=commit_analysis.json
```

**Output:**
```json
{
  "base_sha": "abc123",
  "head_sha": "def456",
  "files_changed": 5,
  "violations": [
    {
      "file": "api/endpoints.py",
      "line": 42,
      "pattern": "numpy_json_serialization",
      "description": "NumPy types may not be JSON serializable",
      "suggestion": "Convert NumPy types: float(np_value)"
    }
  ],
  "timestamp": "2026-01-05T10:30:00"
}
```

### `sync-to-markdown`

Syncs patterns from patterns.json to AI_PATTERNS.md.

```bash
python -m metrics.integrate sync-to-markdown \
  --patterns-file=patterns.json \
  --markdown-file=AI_PATTERNS.md
```

## How the Feedback Loop Now Works

### Before (Broken Loop)

```
Metrics → patterns.json → (dead end)
                           ↓
                    AI_PATTERNS.md (static)
                           ↓
                    Code generation (hardcoded templates)
                           ↓
                    No feedback
```

### After (Functional Loop)

```
1. Test failures → Auto-logged via pytest plugin
                          ↓
2. Metrics collected → patterns.json
                          ↓
3. Analyze patterns → Update frequencies & effectiveness
                          ↓
4. Sync to markdown → AI_PATTERNS.md updated
                          ↓
5. Code generation → LLM uses pattern context
                          ↓
6. Validation → Results logged back to metrics
                          ↓
7. CI/CD → Automatic analysis on every PR
                          ↓
   (Loop back to 1)
```

## Complete Usage Example

### Step 1: Set up API key

```bash
export ANTHROPIC_API_KEY=your_api_key_here
```

### Step 2: Run tests with metrics collection

```bash
pytest tests/ --metrics-output=metrics.json --enable-metrics
```

### Step 3: Analyze metrics

```bash
python -m metrics.integrate analyze --metrics-file=metrics.json
```

Output:
```
✓ High Frequency Patterns: 3
  - numpy_json_serialization: 5 occurrences
  - bounds_checking: 3 occurrences
  - logger_debug: 2 occurrences

✓ Updating pattern library...
  Pattern library saved to patterns.json
```

### Step 4: Sync patterns to documentation

```bash
python -m metrics.integrate sync-to-markdown
```

Output:
```
✓ Patterns synced to AI_PATTERNS.md
```

### Step 5: Generate code with pattern awareness

```bash
python -m metrics.integrate generate "Create a function to process NumPy arrays and output JSON"
```

Output:
```
============================================================
GENERATED CODE:
============================================================
import json
import logging
import numpy as np

logger = logging.getLogger(__name__)

def process_numpy_arrays(data_array):
    """Process NumPy array and return JSON-serializable result.

    Applies pattern: numpy_json_serialization
    """
    # PATTERN: numpy_json_serialization - Convert before JSON serialization
    if not isinstance(data_array, np.ndarray):
        logger.debug("Input is not a NumPy array")
        return None

    result = {
        "mean": float(np.mean(data_array)),
        "std": float(np.std(data_array)),
        "max": float(np.max(data_array)),
        "min": float(np.min(data_array))
    }

    return json.dumps(result)

============================================================
REPORT:
============================================================
=== Pattern-Aware Code Generation Report ===

Confidence Score: 100.00%
Generation Mode: LLM

Context Detected:
  ✓ numpy
  ✓ json

Patterns Applied: 1
  - numpy_json_serialization (severity: medium, confidence: 100.00%)

Patterns Suggested: 0

Validation Results:
  Syntax Valid: ✓
  Overall: ✓ Valid

=== End Report ===

✓ Code saved to generated_code.py
✓ Metadata saved to generated_code.py.meta.json
```

### Step 6: CI/CD automatically analyzes PRs

When you create a PR:
1. GitHub Actions runs tests
2. Collects metrics
3. Analyzes commit diff
4. Posts report as PR comment

## Files Modified/Created

### New Files
- `conftest.py` - Pytest plugin for auto-metrics
- `hooks/pre-commit` - Git pre-commit hook
- `.github/workflows/feedback-loop.yml` - CI/CD workflow
- `FEEDBACK_LOOP_IMPROVEMENTS.md` - This documentation

### Modified Files
- `metrics/collector.py` - Added `log_code_generation()` method
- `metrics/pattern_manager.py` - Added `sync_to_markdown()` method
- `metrics/code_generator.py` - Rewritten to use real LLM, added validation
- `metrics/integrate.py` - Added new commands: `analyze-commit`, `sync-to-markdown`

## Impact

### Before
- Manual metrics logging required
- Hardcoded code generation templates
- No CI/CD integration
- Static documentation
- No actual feedback loop

### After
- ✅ Automatic metrics collection from tests
- ✅ Real AI code generation with pattern context
- ✅ CI/CD automatically analyzes every PR
- ✅ Documentation auto-updates from metrics
- ✅ Complete, functional feedback loop

## Next Steps

### For developers using this system:

1. **Install the pre-commit hook:**
   ```bash
   cp hooks/pre-commit .git/hooks/pre-commit
   chmod +x .git/hooks/pre-commit
   ```

2. **Set up your API key:**
   ```bash
   export ANTHROPIC_API_KEY=your_key
   # Add to ~/.bashrc or ~/.zshrc for persistence
   ```

3. **Run tests with metrics:**
   ```bash
   pytest tests/ --enable-metrics
   ```

4. **Review generated patterns:**
   ```bash
   python -m metrics.integrate analyze
   python -m metrics.integrate sync-to-markdown
   git diff AI_PATTERNS.md  # See what changed
   ```

### For teams adopting this:

1. Configure GitHub repository secrets with `ANTHROPIC_API_KEY`
2. Enable GitHub Actions in repository settings
3. Merge the workflow file to your main branch
4. Create a test PR to see the system in action

## Troubleshooting

### "ANTHROPIC_API_KEY not found"
Set the environment variable:
```bash
export ANTHROPIC_API_KEY=sk-ant-...
```

### Pytest plugin not working
Ensure `conftest.py` is in the repository root:
```bash
ls -la conftest.py
```

### Pre-commit hook not running
Make it executable:
```bash
chmod +x .git/hooks/pre-commit
```

### GitHub Actions failing
Check workflow logs in GitHub Actions tab. Common issues:
- API key not configured in secrets
- Python dependencies not installed

## Conclusion

These improvements transform the feedback-loop from documentation into a working system. The loop is now truly continuous:

1. Tests auto-collect metrics
2. Metrics update patterns
3. Patterns sync to documentation
4. Documentation informs code generation
5. Code generation logs results
6. CI/CD provides continuous feedback

**The feedback loop is now closed and functional.**
