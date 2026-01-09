# Getting Started with feedback-loop

**Time to read: 5 minutes**

> 💡 **Prefer a non-linear approach?** This guide follows a step-by-step path. If you learn by exploration, experimentation, or your own unique style, check out the [Flexible Learning Paths](FLEXIBLE_LEARNING_PATHS.md) for alternative entry points.

## What You'll Learn

feedback-loop helps you write better code by learning from mistakes. This guide shows you how in 3 simple steps.

## Installation

```bash
git clone https://github.com/doronpers/feedback-loop.git
cd feedback-loop
pip install -r requirements.txt
```

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

You'll see **119 tests** covering all patterns. Every pattern has:
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

## What's Next?

### Learn the Patterns
- [Quick Reference](QUICK_REFERENCE.md) - Pattern cheat sheet
- [AI Patterns Guide](AI_PATTERNS_GUIDE.md) - Complete workflow guide

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

- **Quick questions:** See [Quick Reference](QUICK_REFERENCE.md)
- **Deep dive:** Read [AI Patterns Guide](AI_PATTERNS_GUIDE.md)
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
