# feedback-loop

![Python](https://img.shields.io/badge/python-3.8+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Tests](https://img.shields.io/badge/tests-183%20collected-success.svg)
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

- **[Getting Started](documentation/GETTING_STARTED.md)**
- **[Quick Reference](documentation/QUICK_REFERENCE.md)**
- **[AI Patterns Guide](documentation/AI_PATTERNS_GUIDE.md)**
- **[Metrics Guide](documentation/METRICS_GUIDE.md)**
- **[Memory Integration](documentation/MEMORY_INTEGRATION.md)** ⭐ NEW - Semantic pattern learning with MemU
- **[Superset Analytics Integration](documentation/SUPERSET_INTEGRATION.md)** ⭐ NEW
- **[LLM Integration Guide](documentation/LLM_GUIDE.md)**
- **[Cloud Sync](documentation/CLOUD_SYNC.md)**
- **[API Reference](metrics/README.md)**
- **[Contributing](CONTRIBUTING.md)**
- **[Security](documentation/Status/SECURITY.md)**
- **[Results](documentation/Status/RESULTS.md)**

## Memory-Enhanced Patterns (Optional)

feedback-loop now supports intelligent pattern memory via [MemU](https://github.com/NevaMind-AI/memU), enabling:

✨ **Semantic Search**: Query patterns by concept, not just name  
🧠 **Self-Evolving**: Patterns improve based on usage over time  
🔗 **Cross-Project**: Share learnings across all your codebases  
💡 **Smart Recommendations**: Get context-aware pattern suggestions  

### Quick Setup

```bash
# 1. Install MemU
pip install memu-py

# 2. Enable memory (optional)
export FEEDBACK_LOOP_MEMORY_ENABLED=true
export OPENAI_API_KEY=sk-...  # For embeddings

# 3. Sync patterns to memory
feedback-loop memory sync

# 4. Query semantically
feedback-loop memory query "How do I handle JSON serialization with NumPy?"

# 5. Get recommendations
feedback-loop memory recommend --context "Building FastAPI file upload endpoint"
```

**Note:** Memory integration is **opt-in** and backward compatible. All existing functionality works without MemU.

See **[Memory Integration Guide](documentation/MEMORY_INTEGRATION.md)** for detailed documentation.

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

Use **[Quick Reference](documentation/QUICK_REFERENCE.md)** for the full catalog and examples.

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

See **[Superset Integration Guide](documentation/SUPERSET_INTEGRATION.md)** for setup instructions.

## Project status

See **[documentation/Status/RESULTS.md](documentation/Status/RESULTS.md)** for test coverage and verification details.

## Agent Instructions
This repository follows [Agent Behavioral Standards](documentation/governance/AGENT_BEHAVIORAL_STANDARDS.md). All AI agents MUST read these before performing any tasks.
