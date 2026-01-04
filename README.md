# feedback-loop
Reusable and improvable AI-assisted development patterns

## Overview

This repository demonstrates best practices for robust, maintainable Python code and provides a feedback loop framework for continuous improvement. Includes specialized patterns for FastAPI backends with massive audio-processing constraints (up to 800MB files).

## Key Patterns

1. **NumPy Type Conversion** - Convert NumPy types before JSON serialization
2. **Bounds Checking** - Validate list access before indexing
3. **Specific Exceptions** - Use targeted exception handling, not bare `except:`
4. **Structured Logging** - Use `logger.debug()` instead of `print()`
5. **Metadata-Based Logic** - Prefer metadata over string matching
6. **Temp File Handling** - Proper cleanup with try/finally blocks
7. **Large File Processing** - Chunked reading for 800MB files
8. **FastAPI Streaming Uploads** - Stream files to disk without loading into memory
9. **NumPy NaN/Inf Handling** - Explicit handling of edge cases in audio processing

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Run tests
pytest tests/ -v

# View examples
python demo.py

# Run FastAPI example (requires uvicorn)
python examples/fastapi_audio_example.py
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
