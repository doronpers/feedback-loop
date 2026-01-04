# feedback-loop

Reusable and improvable AI-assisted development patterns with automated metrics collection and pattern-aware code generation.

## Overview

This repository demonstrates best practices for robust, maintainable Python code and provides a comprehensive feedback loop framework for continuous improvement. It includes:

- **Core Patterns**: 9 essential best practices for Python development
- **Metrics System**: Automated collection and analysis of code quality metrics
- **Pattern-Aware Generation**: AI code generation using learned patterns
- **FastAPI Patterns**: Specialized patterns for handling massive files (up to 800MB)
- **Complete Testing**: 99 tests ensuring all patterns work correctly

## Core Patterns

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

### Installation

```bash
# Clone the repository
git clone https://github.com/doronpers/feedback-loop.git
cd feedback-loop

# Install dependencies
pip install -r requirements.txt
```

### Running Examples

```bash
# View core patterns demo
python demo.py

# View FastAPI patterns demo
python demo_fastapi.py

# View metrics system demo (interactive)
python demo_metrics.py

# Run FastAPI server
python examples/fastapi_audio_example.py
# Then visit http://localhost:8000/docs for API documentation
```

### Running Tests

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ -v --cov=. --cov-report=html

# Run specific test file
pytest tests/test_good_patterns.py -v
```

## Documentation

### Core Documentation
- **[AI_PATTERNS.md](AI_PATTERNS.md)** - Comprehensive guide with examples, tests, and the feedback loop process
- **[FASTAPI_IMPLEMENTATION.md](FASTAPI_IMPLEMENTATION.md)** - FastAPI patterns for large file handling
- **[METRICS_INTEGRATION.md](METRICS_INTEGRATION.md)** - Metrics collection and pattern-aware code generation
- **[RESULTS.md](RESULTS.md)** - Implementation results and verification checklist

### Code Examples
- **[examples/good_patterns.py](examples/good_patterns.py)** - Best practices to follow
- **[examples/bad_patterns.py](examples/bad_patterns.py)** - Antipatterns to avoid
- **[examples/fastapi_audio_patterns.py](examples/fastapi_audio_patterns.py)** - Production-ready FastAPI patterns
- **[examples/fastapi_audio_example.py](examples/fastapi_audio_example.py)** - Complete FastAPI application

### Tests
- **[tests/test_good_patterns.py](tests/test_good_patterns.py)** - Core patterns test suite (38 tests)
- **[tests/test_fastapi_audio_patterns.py](tests/test_fastapi_audio_patterns.py)** - FastAPI patterns tests (25 tests)
- **[tests/test_metrics.py](tests/test_metrics.py)** - Metrics system tests (36 tests)

## Metrics System

The repository includes an advanced metrics collection and analysis system that learns from your development patterns:

### Features

- **Automated Metrics Collection**: Track bugs, test failures, code review issues, performance metrics, and deployment issues
- **Pattern Analysis**: Identify high-frequency patterns and trends over time
- **Pattern-Aware Code Generation**: Generate code that applies learned patterns automatically
- **Pattern Library Management**: Maintain and evolve a library of best practices

### Using the Metrics System

```bash
# Collect metrics (from logs, bug trackers, etc.)
python -m metrics.integrate collect

# Analyze collected metrics
python -m metrics.integrate analyze

# Generate code with pattern awareness
python -m metrics.integrate generate "Create a function to process JSON data"

# Generate reports
python -m metrics.integrate report --period weekly
```

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

This continuous improvement cycle ensures that:
1. Common mistakes are documented as patterns
2. Patterns are tested and validated
3. AI assistants learn from past issues
4. Code quality improves over time

See [AI_PATTERNS.md](AI_PATTERNS.md) for detailed documentation.

## Project Structure

```
feedback-loop/
├── examples/           # Code examples and patterns
│   ├── good_patterns.py
│   ├── bad_patterns.py
│   ├── fastapi_audio_patterns.py
│   └── fastapi_audio_example.py
├── metrics/            # Metrics collection and analysis system
│   ├── collector.py    # Metrics data collection
│   ├── analyzer.py     # Pattern analysis and trends
│   ├── pattern_manager.py  # Pattern library management
│   ├── code_generator.py   # Pattern-aware code generation
│   └── integrate.py    # CLI interface
├── tests/              # Comprehensive test suite (99 tests)
│   ├── test_good_patterns.py
│   ├── test_fastapi_audio_patterns.py
│   └── test_metrics.py
├── demo.py             # Core patterns demonstration
├── demo_fastapi.py     # FastAPI patterns demonstration
├── demo_metrics.py     # Metrics system demonstration
└── AI_PATTERNS.md      # Comprehensive pattern documentation
```

## Requirements

- Python 3.8+
- See [requirements.txt](requirements.txt) for dependencies

## Contributing

Contributions are welcome! When adding new patterns:

1. Document the pattern in `AI_PATTERNS.md`
2. Add bad example in `examples/bad_patterns.py`
3. Add good example in `examples/good_patterns.py`
4. Write tests in `tests/test_good_patterns.py`
5. Update this README if needed

## License

MIT License - see LICENSE file for details.
