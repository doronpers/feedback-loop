# feedback-loop

![Python](https://img.shields.io/badge/python-3.8+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Tests](https://img.shields.io/badge/tests-119%20passing-success.svg)
![Coverage](https://img.shields.io/badge/coverage-91%25-brightgreen.svg)

**A practical framework for AI-assisted development with continuous learning from your code.**

## What is This?

feedback-loop helps you write better code by:
1. **Learning** from bugs and patterns in your development
2. **Applying** best practices automatically through AI code generation
3. **Improving** continuously through automated metrics collection

## Quick Start

```bash
# Clone and install
git clone https://github.com/doronpers/feedback-loop.git
cd feedback-loop
pip install -r requirements.txt

# See it in action
python demo.py                  # Core patterns demo
python demo_metrics.py          # Interactive metrics system
```

## For New Users

**Start here:** Read [docs/GETTING_STARTED.md](docs/GETTING_STARTED.md) for a 5-minute introduction.

**Then explore:**
- 9 essential code patterns that prevent common bugs
- Automated metrics collection from your test failures
- AI code generation that learns from your mistakes

## Core Patterns

This repository includes 9 battle-tested patterns for Python development:

1. **NumPy Type Conversion** - Avoid JSON serialization errors
2. **Bounds Checking** - Prevent index out of range crashes  
3. **Specific Exceptions** - Better error handling
4. **Structured Logging** - Production-ready logging
5. **Metadata-Based Logic** - Maintainable business logic
6. **Temp File Handling** - No file leaks
7. **Large File Processing** - Handle 800MB+ files
8. **FastAPI Streaming** - Memory-safe file uploads
9. **NumPy NaN/Inf Handling** - Edge case safety

💡 **Tip**: These patterns use audio processing as examples, but apply to any domain with similar challenges.

## Documentation

### 📘 Start Here
- **[Getting Started](docs/GETTING_STARTED.md)** - 5-minute introduction for new users
- **[Quick Reference](docs/QUICK_REFERENCE.md)** - Common patterns and commands at a glance

### 📖 Learn the Patterns
- **[AI Patterns Guide](docs/AI_PATTERNS_GUIDE.md)** - Complete guide to all 9 patterns with workflow
- **[Code Examples](examples/)** - Working examples of good and bad patterns

### 🔧 Use the Tools
- **[Metrics System](docs/METRICS_GUIDE.md)** - Automated metrics collection and pattern learning
- **[API Reference](metrics/README.md)** - Detailed API documentation

### 📊 Reference
- **[Results & Testing](RESULTS.md)** - Implementation verification (119 tests, 91% coverage)
- **[Changelog](CHANGELOG.md)** - Version history

## Running Tests

```bash
pytest tests/ -v                    # All tests
pytest tests/ --cov=. --cov-report=html    # With coverage
```

## The Feedback Loop

```
Code → Tests → Metrics → Analysis → Patterns → AI Generation → Better Code
  ↑                                                                  ↓
  └──────────────────────── Continuous Learning ────────────────────┘
```

**How it works:**
1. Tests collect metrics automatically
2. Patterns emerge from common issues
3. AI learns from pattern library
4. Better code prevents future issues

## Project Structure

```
feedback-loop/
├── docs/               # 📘 Organized documentation
├── examples/           # 💻 Code examples (good & bad patterns)
├── metrics/            # 📊 Metrics collection & AI generation
├── tests/              # ✅ 119 tests with 91% coverage
└── demo*.py            # 🎮 Interactive demonstrations
```

## Contributing

See [docs/CONTRIBUTING.md](docs/CONTRIBUTING.md) for guidelines.

## License

MIT License - see LICENSE file for details.
