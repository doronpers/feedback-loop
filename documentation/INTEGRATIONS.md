# Integrations

This page summarizes how to connect feedback-loop with common developer workflows.

## GitHub Actions (CI)

- See **Continuous Feedback via GitHub Actions** in `IMPLEMENTATION_DETAILS.md` for the full workflow and PR comment behavior.
- See the **GitHub Actions Example** in `METRICS_GUIDE.md` for a copy-paste workflow recipe.

## Pre-commit hook (local Git)

- Use the **Pre-commit Hook** example in `docs/METRICS_GUIDE.md` to analyze patterns before each commit.

## Desktop launchers

- Quick-start GUI launchers are documented in `DESKTOP_LAUNCHERS.md`.

## VS Code / Cursor (LSP)

### Quick Start

feedback-loop integrates seamlessly with both VS Code and Cursor through:
1. **`.cursorrules` file** - Automatically teaches Cursor AI about feedback-loop patterns
2. **Language Server Protocol (LSP)** - Real-time pattern detection and quick fixes
3. **VS Code Tasks** - Quick access to all feedback-loop tools
4. **Settings Integration** - Pre-configured for optimal experience

### For Cursor Users

Cursor is VS Code-based with enhanced AI capabilities. See the **[Cursor Integration Guide](../CURSOR_INTEGRATION.md)** for:
- Complete setup instructions
- Cursor Composer integration
- Pattern-aware code generation
- Interactive workflows
- Troubleshooting

**Quick setup:**
```bash
cd feedback-loop
pip install -e .
# Cursor automatically reads .cursorrules file
# Use Cmd/Ctrl + Shift + P → "Tasks: Run Task" to access tools
```

### For VS Code Users

The VS Code extension POC and language server setup are described in `../vscode-extension/README.md`.

**Features:**
- Real-time diagnostics
- Quick fixes for pattern violations  
- Hover documentation
- Task integration
