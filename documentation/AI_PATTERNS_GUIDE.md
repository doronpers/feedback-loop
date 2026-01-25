# AI Patterns Guide

**Living Pattern Library Philosophy** - This guide explains how feedback-loop transforms failures into reusable patterns, creating a self-evolving knowledge base that improves AI code generation and team collaboration.

> **Consistency Note:** This guide aligns with `.cursorrules` to ensure the "living pattern library" philosophy is consistent across IDE integration and documentation. See **[.cursorrules](../.cursorrules)** for Cursor-specific pattern application rules.

## What is a pattern?

A pattern is a reusable fix captured from test failures and recurring reviews. Each pattern includes:

- **Problem** — what goes wrong in real code.
- **Solution** — a reliable fix.
- **Examples** — good vs. bad implementations.
- **Context** — where it should be applied.

## The 6-stage workflow

1. **Observe** — tests fail and produce metrics.
2. **Identify** — recurring failures are grouped.
3. **Codify** — a pattern is documented.
4. **Apply** — AI-assisted generation uses the pattern.
5. **Verify** — tests confirm the fix.
6. **Share** — patterns become shared knowledge for the team.

## Pattern categories (quick scan)

- **Serialization & Type Safety** — NumPy conversion, NaN/Inf validation.
- **Defensive Programming** — bounds checks, specific exceptions.
- **Production Readiness** — logging, temp file hygiene, streaming.
- **API Development** — FastAPI streaming uploads.
- **Business Logic** — metadata-driven routing and rules.

Use the **[Quick Reference](QUICK_REFERENCE.md)** for concrete good/bad examples and commands.

## When to use patterns

Use patterns whenever you see:

- Repeated review comments.
- Failure clusters in metrics.
- Bug classes that reappear across sprints.
- AI-generated code missing edge-case handling.

## Working with patterns

### Adding or refining a pattern

1. Capture a real failure (test, bug report, or incident).
2. Describe the failure and the fix.
3. Add a good and bad example in `examples/`.
4. Update the pattern metadata and docs.
5. Re-run tests and metrics analysis.

For contribution steps, see **[CONTRIBUTING.md](../CONTRIBUTING.md)**.

### Applying patterns in generation

- Use the CLI to generate code with pattern awareness:

```bash
feedback-loop generate "Create a safe file handler"
```

- To bias toward the patterns you actually see failing in your project, run analysis first:

```bash
pytest --enable-metrics
feedback-loop analyze
```

### Applying patterns in review

- Use pattern checks for PRs that touch known risk areas.
- Enforce only the minimum set needed to avoid friction.

## Metrics-driven iteration

The system is designed to keep the pattern library current. If patterns stop preventing failures, it means:

- The pattern is too generic.
- The fix is missing an edge case.
- The project’s context has shifted.

When that happens, revise the pattern and re-run tests.

## Integration with Cursor IDE

The `.cursorrules` file ensures Cursor IDE automatically applies these patterns during code generation. The patterns are the same across both the CLI and IDE integration, creating a consistent developer experience.

**Key principles (from .cursorrules):**

- Patterns exist because they've prevented real bugs in production
- Apply them consistently, and the feedback loop continues learning
- When in doubt, check existing code in `/examples/` or `/tests/` for pattern application examples
- For new patterns, follow the workflow: observe, identify, codify, apply, verify, share

## Where to go next

- **[Quick Reference](QUICK_REFERENCE.md)** — the full pattern list with examples.
- **[Metrics Guide](METRICS_GUIDE.md)** — collection and analysis workflows.
- **[Cursor Integration](../CURSOR_INTEGRATION.md)** — IDE setup with pattern-aware AI.
- **[Full guide archive](archive/AI_PATTERNS_GUIDE_FULL.md)** — deep dives and extended examples.
