# feedback-loop

![Python](https://img.shields.io/badge/python-3.8+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Tests](https://img.shields.io/badge/tests-119%20passing-success.svg)
![Coverage](https://img.shields.io/badge/coverage-91%25-brightgreen.svg)

**A practical framework for AI-assisted development with continuous learning from your code.**

feedback-loop turns test failures into reusable patterns, then uses those patterns to improve code generation, review, and onboarding.

## What it does

- **Learns from tests**: captures failures and turns them into structured metrics.
- **Builds a living pattern library**: good/bad examples + explanations.
- **Improves AI outputs**: pattern-aware code generation and review.
- **Supports teams** (optional): cloud sync and shared configuration.

## Quick start

### Installation

```bash
# Clone and install
git clone https://github.com/doronpers/feedback-loop.git
cd feedback-loop

# Core runtime
pip install -e .

# Or install with testing extras
pip install -e .[test]
```

### Desktop Launchers (Easy Mode!)

**Mac:** Double-click `launch-feedback-loop.command`  
**Windows:** Double-click `launch-feedback-loop.bat`

These launchers provide an interactive menu to run any feedback-loop tool. See [DESKTOP_LAUNCHERS.md](DESKTOP_LAUNCHERS.md) for details.

### Interactive setup

```bash
./bin/fl-setup
```

### Chat assistant

```bash
./bin/fl-chat
```

### See the patterns in action

```bash
python demo.py
python demo_metrics.py
```

## Common workflows

```bash
# Collect metrics from pytest
pytest --enable-metrics

# Analyze and update patterns
feedback-loop analyze

# Generate code with pattern awareness
feedback-loop generate "Create a safe file handler"
```

## Documentation

- **[Getting Started](docs/GETTING_STARTED.md)**
- **[Quick Reference](docs/QUICK_REFERENCE.md)**
- **[AI Patterns Guide](docs/AI_PATTERNS_GUIDE.md)**
- **[Metrics Guide](docs/METRICS_GUIDE.md)**
- **[Superset Analytics Integration](docs/SUPERSET_INTEGRATION.md)** ⭐ NEW
- **[LLM Integration Guide](docs/LLM_GUIDE.md)**
- **[Cloud Sync](docs/CLOUD_SYNC.md)**
- **[API Reference](metrics/README.md)**
- **[Contributing](docs/CONTRIBUTING.md)**

## Core patterns (short list)

The framework ships with 9 production-tested patterns, including:
- NumPy type conversion
- NaN/Inf validation
- Bounds checking
- Specific exception handling
- Structured logging
- Temp file hygiene
- Large file streaming
- FastAPI streaming uploads
- Metadata-driven logic

Use **[Quick Reference](docs/QUICK_REFERENCE.md)** for the full catalog and examples.

## Architecture (high-level)

```
┌─────────────────────────────┐
│            Tests            │
│          (pytest)           │
└──────────────┬──────────────┘
               │ failures
               ▼
┌─────────────────────────────┐
│     Metrics Collector       │
│   (collector/analyzer)      │
└──────────────┬──────────────┘
               ▼
┌─────────────────────────────┐
│     Pattern Library          │
│ (pattern_manager/generator)  │
└──────────────┬──────────────┘
               ▼
┌─────────────────────────────┐
│     AI + Code Review         │
│   (pattern-aware outputs)    │
└─────────────────────────────┘
               │
               ▼
┌─────────────────────────────┐
│   Apache Superset Dashboards│
│     (analytics/insights)     │
└─────────────────────────────┘
```

## Analytics & Visualization

feedback-loop integrates with **Apache Superset** to provide powerful analytics dashboards:

📊 **Code Quality Dashboard** - Track bugs, test failures, and code review issues  
📈 **Pattern Analysis Dashboard** - Visualize pattern frequency and effectiveness  
🚀 **Development Trends Dashboard** - Monitor AI-assisted development metrics  

See **[Superset Integration Guide](docs/SUPERSET_INTEGRATION.md)** for setup instructions.

## Project status

See **[RESULTS.md](RESULTS.md)** for test coverage and verification details.
