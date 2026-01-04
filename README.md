# feedback-loop
Reusable and improvable AI-assisted development patterns

## Overview

This repository demonstrates best practices for robust, maintainable Python code and provides a feedback loop framework for continuous improvement.

## Key Patterns

1. **NumPy Type Conversion** - Convert NumPy types before JSON serialization
2. **Bounds Checking** - Validate list access before indexing
3. **Specific Exceptions** - Use targeted exception handling, not bare `except:`
4. **Structured Logging** - Use `logger.debug()` instead of `print()`
5. **Metadata-Based Logic** - Prefer metadata over string matching

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Run tests
pytest tests/ -v

# View examples
python -c "from examples.good_patterns import *"
```

## Documentation

- **[AI_PATTERNS.md](AI_PATTERNS.md)** - Comprehensive guide with examples, tests, and the feedback loop process
- **[examples/bad_patterns.py](examples/bad_patterns.py)** - Antipatterns to avoid
- **[examples/good_patterns.py](examples/good_patterns.py)** - Best practices to follow
- **[tests/test_good_patterns.py](tests/test_good_patterns.py)** - Comprehensive test suite

## The Feedback Loop

```
PLAN → BUILD → REVIEW → ITERATE
                  ↓
           Retrospective
                  ↓
        Update AI_PATTERNS.md
                  ↓
       Better prompts next time
```

See [AI_PATTERNS.md](AI_PATTERNS.md) for detailed documentation.

## License

MIT License - see LICENSE file for details.
