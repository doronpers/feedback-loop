# Documentation Index

**Complete guide to feedback-loop documentation.**

## For New Users

Start here to learn the basics:

1. **[Getting Started](GETTING_STARTED.md)** ← Start here (5 min)
   - Installation and setup
   - First demo walkthrough
   - Understanding the feedback loop

2. **[Quick Reference](QUICK_REFERENCE.md)** ← Quick lookup (bookmark this)
   - All 9 patterns on one page
   - Common commands cheat sheet
   - When to use each pattern

## Core Guides

Deep dives into the system:

3. **[AI Patterns Guide](AI_PATTERNS_GUIDE.md)** ← Complete workflow
   - Full 6-stage development workflow
   - All 9 patterns with detailed examples
   - Multi-agent orchestration
   - Security and compliance patterns
   - Prompt engineering techniques
   - **Note**: This is comprehensive (~2700 lines). Use Quick Reference for lookups.

4. **[Metrics Guide](METRICS_GUIDE.md)** ← Automated learning
   - Metrics collection system
   - Pattern analysis and detection
   - AI code generation integration
   - CI/CD workflows
   - Customization guide

5. **[FastAPI Guide](FASTAPI_GUIDE.md)** ← Large file handling
   - Streaming file uploads (800MB+)
   - Memory-safe patterns
   - nginx configuration
   - Production deployment

## Reference

Technical details and API documentation:

6. **[Metrics API Reference](../metrics/README.md)** ← API docs
   - MetricsCollector API
   - MetricsAnalyzer API
   - PatternManager API
   - PatternAwareGenerator API

7. **[Implementation Details](IMPLEMENTATION_DETAILS.md)** ← System internals
   - Architecture decisions
   - Integration workflows
   - GitHub Actions setup
   - Advanced customization

8. **[Results & Testing](../RESULTS.md)** ← Verification
   - Test coverage report (119 tests, 91%)
   - Security scan results
   - Implementation checklist

9. **[Changelog](../CHANGELOG.md)** ← Version history
   - Release notes
   - Breaking changes
   - Feature additions

## Contributing

Want to improve the project?

10. **[Contributing Guide](CONTRIBUTING.md)** ← How to help
    - Adding new patterns
    - Improving documentation
    - Code style guidelines
    - Pull request process

## Quick Navigation

### By Task

| I want to... | Read this |
|--------------|-----------|
| Get started quickly | [Getting Started](GETTING_STARTED.md) |
| Look up a pattern | [Quick Reference](QUICK_REFERENCE.md) |
| Understand the workflow | [AI Patterns Guide](AI_PATTERNS_GUIDE.md) |
| Set up metrics collection | [Metrics Guide](METRICS_GUIDE.md) |
| Handle large file uploads | [FastAPI Guide](FASTAPI_GUIDE.md) |
| Use the API programmatically | [Metrics API](../metrics/README.md) |
| Contribute code | [Contributing](CONTRIBUTING.md) |
| See test results | [Results](../RESULTS.md) |

### By Experience Level

**Beginner** (Never used this before):
1. [Getting Started](GETTING_STARTED.md)
2. [Quick Reference](QUICK_REFERENCE.md)
3. Try the demos

**Intermediate** (Used similar tools):
1. [Quick Reference](QUICK_REFERENCE.md)
2. [Metrics Guide](METRICS_GUIDE.md)
3. [AI Patterns Guide](AI_PATTERNS_GUIDE.md) sections relevant to your task

**Advanced** (Want to customize/extend):
1. [Metrics API Reference](../metrics/README.md)
2. [Implementation Details](IMPLEMENTATION_DETAILS.md)
3. [Contributing](CONTRIBUTING.md)

## Documentation Structure

```
docs/
├── INDEX.md                    # ← You are here
├── GETTING_STARTED.md          # Quick start (5 min)
├── QUICK_REFERENCE.md          # One-page lookup
├── AI_PATTERNS_GUIDE.md        # Complete workflow guide
├── METRICS_GUIDE.md            # Metrics system guide
├── FASTAPI_GUIDE.md            # FastAPI patterns
├── CONTRIBUTING.md             # Contribution guidelines
└── IMPLEMENTATION_DETAILS.md   # Technical deep dive

Root level:
├── README.md                   # Project overview
├── RESULTS.md                  # Test results
├── CHANGELOG.md                # Version history
└── metrics/README.md           # API reference
```

## Principles

This documentation follows Dieter Rams' design principles:

- **Understandable**: Clear hierarchy and navigation
- **Minimal**: No redundancy, focused content
- **Honest**: All code examples work as shown
- **Thorough**: Complete coverage of features
- **Unobtrusive**: Find what you need quickly

## Feedback

Found an issue or have a suggestion?
- Open an issue: [GitHub Issues](https://github.com/doronpers/feedback-loop/issues)
- See broken link? Please report it!
- Want to improve docs? See [Contributing](CONTRIBUTING.md)
