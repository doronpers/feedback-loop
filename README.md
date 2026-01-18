# feedback-loop

![Python](https://img.shields.io/badge/python-3.13+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Tests](https://img.shields.io/badge/tests-183%20collected-success.svg)
![Coverage](https://img.shields.io/badge/coverage-91%25-brightgreen.svg)

**Strategic Map: AI-Assisted Development with Continuous Learning**

feedback-loop is a production-ready framework that transforms test failures into reusable patterns, creating a living pattern library that improves AI code generation, review, and team collaboration.

## What it does

- **Learns from tests**: captures failures and turns them into structured metrics.
- **Builds a living pattern library**: good/bad examples + explanations.
- **Improves AI outputs**: pattern-aware code generation and review.
- **Supports teams** (optional): cloud sync and shared configuration.

## 🚀 Quick Start (30 seconds!)

**Easiest option:** Download and run automatically!

```bash
# 🌟 One-liner install + setup + demo + dashboard
curl -fsSL https://raw.githubusercontent.com/doronpers/feedback-loop/main/install.sh | bash
```

---

**Already cloned?** Run this single command:

```bash
# ✨ Auto-setup + interactive demo + dashboard - everything you need!
fl-start
```

Both options will:
- ✅ Auto-detect your environment and install everything
- 🎭 Launch an interactive demo showing patterns in action
- 📊 Open the analytics dashboard in your browser
- 🚀 Get you productive immediately

**First time?** Just run one command and explore!

**[📖 Complete Guide](documentation/QUICKSTART.md)** - For detailed instructions and advanced usage.

## Installation

### Automated Setup (Recommended)

The bootstrap command handles everything automatically:

```bash
fl-bootstrap
```

### Manual Installation

**Requirements:** Python 3.8+

```bash
# Clone and install
git clone https://github.com/doronpers/feedback-loop.git
cd feedback-loop

# Install with dependencies
pip install -e .
```

**Alternative:** Using requirements.txt:
```bash
pip install -r requirements.txt
```

### 🎯 Cursor Integration (Recommended)

**For Cursor IDE users:** feedback-loop provides seamless AI-powered development:

```bash
# 1. Install feedback-loop (see above)
# 2. Open this repository in Cursor
# 3. Cursor automatically reads .cursorrules file
# 4. Start coding with pattern-aware AI assistance!
```

See **[Cursor Integration Guide](CURSOR_INTEGRATION.md)** for complete setup.

### Desktop Launchers (Easy Mode!)

**Mac:** Double-click `launch-feedback-loop.command`
**Windows:** Double-click `launch-feedback-loop.bat`

These launchers provide an interactive menu to run any feedback-loop tool. See [DESKTOP_LAUNCHERS.md](DESKTOP_LAUNCHERS.md) for details.

## Common workflows

```bash
# Collect metrics from pytest
pytest --enable-metrics

# Analyze and update patterns
feedback-loop analyze

# Generate code with pattern awareness
feedback-loop generate "Create a safe file handler"

# Multi-perspective review with Council AI (local import or HTTP)
feedback-loop council-review --file path/to/file.py
```

## Documentation

**Start here:** See **[documentation/INDEX.md](documentation/INDEX.md)** for a complete table of contents.

**Key guides:**
- **[Getting Started](documentation/GETTING_STARTED.md)** - Installation and first steps
- **[AI Patterns Guide](documentation/AI_PATTERNS_GUIDE.md)** - Living pattern library philosophy
- **[Cursor Integration](CURSOR_INTEGRATION.md)** - IDE setup with pattern-aware AI
- **[Memory Integration](documentation/MEMORY_INTEGRATION.md)** - Semantic pattern learning
- **[Cloud Sync](documentation/CLOUD_SYNC.md)** - Team collaboration features

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

```text
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

> **CRITICAL**: All AI agents MUST read [`AGENT_KNOWLEDGE_BASE.md`](AGENT_KNOWLEDGE_BASE.md) before performing any tasks. It contains non-negotiable Patent, Security, and Design rules.

Additional resources:

- [Agent Behavioral Standards](documentation/governance/AGENT_BEHAVIORAL_STANDARDS.md)
