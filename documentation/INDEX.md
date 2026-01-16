# Documentation Index

**Table of Contents** - Non-redundant navigation to all documentation resources.

## Documentation Root Policy

**All documentation lives in the `documentation/` directory.** Internal links should use `documentation/` paths (not `docs/`). This ensures consistency and prevents broken links. When referencing documentation files:

- Use relative paths from within `documentation/`: `[QUICK_REFERENCE.md](QUICK_REFERENCE.md)`
- Use relative paths from subdirectories: `[AI_PATTERNS_GUIDE.md](../AI_PATTERNS_GUIDE.md)`
- Use relative paths from root: `[documentation/INDEX.md](documentation/INDEX.md)`

The `CONTRIBUTING.md` file is at the repository root and should be referenced as `../CONTRIBUTING.md` from within `documentation/`.

## Start here

1. **[Getting Started](GETTING_STARTED.md)** — install, run demos, understand the loop.
2. **[Quick Reference](QUICK_REFERENCE.md)** — the 9 patterns on one page.

## IDE Integration

- **[Cursor Integration Guide](../CURSOR_INTEGRATION.md)** ⭐ NEW — complete setup for Cursor IDE with pattern-aware AI.
- **[Desktop Launchers](../DESKTOP_LAUNCHERS.md)** — double-click launchers for Mac/Windows.
- **[Integrations](INTEGRATIONS.md)** — VS Code, GitHub Actions, pre-commit hooks.

## Core guides

- **[AI Patterns Guide](AI_PATTERNS_GUIDE.md)** — condensed workflows + pattern catalog.
- **[Metrics Guide](METRICS_GUIDE.md)** — collection, analysis, CI/CD.
- **[LLM Integration Guide](LLM_GUIDE.md)** — provider setup + prompts.
- **[Cloud Sync](CLOUD_SYNC.md)** — team sync + API usage.
- **[FastAPI Guide](FASTAPI_GUIDE.md)** — streaming uploads + deployment tips.
- **[Memory Integration](MEMORY_INTEGRATION.md)** ⭐ NEW — semantic pattern learning with MemU.
- **[Superset Integration](SUPERSET_INTEGRATION.md)** ⭐ NEW — analytics dashboards.

## Reference

- **[Metrics API Reference](../metrics/README.md)**
- **[Implementation Details](IMPLEMENTATION_DETAILS.md)**
- **[Results & Testing](Status/RESULTS.md)**
- **[Security](Status/SECURITY.md)**
- **[Changelog](../CHANGELOG.md)**
- **[Contributing](../CONTRIBUTING.md)**

## Archive

Historical or exploratory docs live in **[documentation/archive](archive/README.md)**.
