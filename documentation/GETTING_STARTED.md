# Getting Started with feedback-loop

**Time to read: 5 minutes**

> 💡 **Prefer a non-linear approach?** This guide follows a step-by-step path. If you learn by exploration, experimentation, or your own unique style, check out the [Flexible Learning Paths](FLEXIBLE_LEARNING_PATHS.md) for alternative entry points.

## What You'll Learn

feedback-loop helps you write better code by learning from mistakes. This guide shows you how in 3 simple steps.

## Installation

**Requirements:** Python 3.13+

```bash
# Clone the repository
git clone https://github.com/doronpers/feedback-loop.git
cd feedback-loop

# Recommended: Install with testing extras (includes dev dependencies)
pip install -e .[test]

# Alternative: Install from requirements.txt
# pip install -r requirements.txt
```

### Optional: Set Up API Keys

If you want to use AI features (chat assistant, code generation), create a `.env` file in the project root:

```bash
# Create .env file (already in .gitignore)
ANTHROPIC_API_KEY=your-key-here      # For Claude
OPENAI_API_KEY=your-key-here         # For GPT-4
GEMINI_API_KEY=your-key-here         # For Gemini
```

The `.env` file is automatically loaded by all feedback-loop tools. See [LLM Guide](LLM_GUIDE.md) for more details.

## Step 1: See the Patterns (2 minutes)

Run the demo to see all 9 patterns in action:

```bash
python demo.py
```

This shows you:

- ✅ Good patterns (what to do)
- ❌ Bad patterns (what to avoid)
- Real code examples for each

**Key insight:** These patterns prevent 90% of common Python bugs.

## Step 2: Run the Tests (1 minute)

See how patterns are validated:

```bash
pytest tests/ -v
```

You'll see the test suite covering core patterns. Every pattern has:

- Tests showing correct usage
- Tests catching incorrect usage
- Edge case handling

## Step 3: Try the Metrics System (2 minutes)

See how the system learns from failures:

```bash
python demo_metrics.py
```

This interactive demo shows:

1. How test failures are automatically tracked
2. How patterns emerge from common errors
3. How AI generates code using learned patterns

**Try this:** When prompted, ask it to generate code for "process NumPy array to JSON" - it will automatically apply the right patterns.

## Data Locations

By default, feedback-loop stores learning artifacts in these locations:

- **Metrics** (test runs): `data/metrics_data.json`
- **Patterns** (learned library): `data/patterns.json`
- **Pattern guide (canonical documentation)**: `documentation/AI_PATTERNS_GUIDE.md`

If you change paths via CLI flags, keep these files together so the metrics and pattern sync stay aligned.

> **Note on markdown sync defaults:** Some CLI helpers default to writing synced patterns to `docs/AI_PATTERNS_GUIDE.md` (a legacy path). If you want to sync directly into the canonical guide, run:
>
> `feedback-loop sync-to-markdown --markdown-file documentation/AI_PATTERNS_GUIDE.md`

## What's Next?

### Use in Your Project

```bash
# Copy the patterns module
cp -r examples/ your-project/

# Start collecting metrics from your tests
pytest --enable-metrics
```

### Integrate with CI/CD

See [Metrics Guide](METRICS_GUIDE.md) for GitHub Actions integration.

## Need Help?

- **Documentation:** See [Documentation Index](INDEX.md) for all guides
- **Issues:** [GitHub Issues](https://github.com/doronpers/feedback-loop/issues)

## The Big Picture

```
Your Code → Tests (auto-collect metrics) → Analysis → Pattern Library
                                                             ↓
                                                     AI learns from it
                                                             ↓
                                              Generates better code for you
```

The more you use it, the smarter it gets. **That's the feedback loop.**
