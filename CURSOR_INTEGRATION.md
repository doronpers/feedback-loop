# Cursor Integration Guide

**feedback-loop** integrates seamlessly with Cursor, the AI-powered code editor. This guide shows you how to set up and use feedback-loop within Cursor for enhanced AI-assisted development.

## 🚀 Quick Start

### Prerequisites

- [Cursor IDE](https://cursor.sh/) installed
- Python 3.8+ installed
- feedback-loop repository cloned

### 1. Install feedback-loop

```bash
cd feedback-loop
pip install -e .
```

### 2. Configure Cursor

Cursor will automatically detect the `.cursorrules` file in the repository root, which includes feedback-loop patterns and best practices.

### 3. Enable the Language Server (Optional)

For real-time pattern detection and diagnostics:

1. Open Cursor settings (Cmd/Ctrl + ,)
2. Add the following to your settings:

```json
{
  "feedback-loop.enable": true,
  "feedback-loop.serverPath": "${workspaceFolder}/bin/feedback_loop_lsp.py"
}
```

3. Reload Cursor (Cmd/Ctrl + Shift + P → "Reload Window")

## 🎯 Features

### 1. Pattern-Aware AI Suggestions

When you ask Cursor's AI for help, it will:
- ✅ Apply learned patterns from your codebase
- ✅ Avoid common pitfalls (NumPy types, NaN handling, etc.)
- ✅ Generate code that matches your project's standards
- ✅ Suggest improvements based on test failures

### 2. Real-Time Pattern Detection (with LSP)

The language server provides:
- ⚠️ Warnings for code that violates patterns
- 💡 Quick fixes for common issues
- 🔍 Inline documentation for patterns
- 📊 Pattern usage statistics

### 3. Interactive Chat Assistant

Use the feedback-loop chat assistant alongside Cursor:

```bash
# In a terminal within Cursor
./bin/fl-chat
```

Or add as a Cursor task (see Tasks section below).

### 4. Dashboard Integration

View metrics and patterns without leaving Cursor:

```bash
# In Cursor's terminal
./bin/fl-dashboard
```

## 🔧 Configuration

### Cursor Rules File

The repository includes a `.cursorrules` file that teaches Cursor about feedback-loop patterns. This file is automatically detected by Cursor and applied to all AI interactions.

**Location:** `.cursorrules` (repository root)

**What it includes:**
- All 9 core patterns
- Common pitfalls to avoid
- Best practices for AI-generated code
- Testing standards

### VS Code/Cursor Settings

Create or update `.vscode/settings.json` (Cursor uses the same format):

```json
{
  // Enable feedback-loop language server
  "feedback-loop.enable": true,
  "feedback-loop.serverPath": "${workspaceFolder}/bin/feedback_loop_lsp.py",
  
  // LLM integration
  "feedback-loop.llmProvider": "claude",
  "feedback-loop.enableLLM": true,
  
  // Analysis settings
  "feedback-loop.analysisDelay": 500,
  
  // Python settings for consistency
  "python.linting.enabled": true,
  "python.linting.flake8Enabled": true,
  "python.formatting.provider": "black",
  "python.formatting.blackArgs": ["--line-length", "88"],
  
  // Test discovery
  "python.testing.pytestEnabled": true,
  "python.testing.unittestEnabled": false,
  "python.testing.pytestArgs": ["tests/"]
}
```

### Cursor Tasks

Add these tasks to `.vscode/tasks.json` for quick access:

```json
{
  "version": "2.0.0",
  "tasks": [
    {
      "label": "Feedback Loop: Chat Assistant",
      "type": "shell",
      "command": "${workspaceFolder}/bin/fl-chat",
      "presentation": {
        "reveal": "always",
        "panel": "dedicated"
      },
      "problemMatcher": []
    },
    {
      "label": "Feedback Loop: Dashboard",
      "type": "shell",
      "command": "${workspaceFolder}/bin/fl-dashboard",
      "presentation": {
        "reveal": "always",
        "panel": "dedicated"
      },
      "problemMatcher": []
    },
    {
      "label": "Feedback Loop: Setup Wizard",
      "type": "shell",
      "command": "${workspaceFolder}/bin/fl-setup",
      "presentation": {
        "reveal": "always",
        "panel": "dedicated"
      },
      "problemMatcher": []
    },
    {
      "label": "Feedback Loop: Run Tests with Metrics",
      "type": "shell",
      "command": "pytest --enable-metrics -v",
      "presentation": {
        "reveal": "always",
        "panel": "shared"
      },
      "problemMatcher": []
    },
    {
      "label": "Feedback Loop: Analyze Patterns",
      "type": "shell",
      "command": "feedback-loop analyze",
      "presentation": {
        "reveal": "always",
        "panel": "shared"
      },
      "problemMatcher": []
    }
  ]
}
```

**Access tasks in Cursor:** Cmd/Ctrl + Shift + P → "Tasks: Run Task" → Select task

## 💡 Workflows

### Workflow 1: Pattern-Aware Code Generation

1. **Ask Cursor's AI for code:**
   ```
   @Codebase Generate a function to process NumPy arrays and return JSON
   ```

2. **Cursor will:**
   - Reference `.cursorrules` patterns
   - Apply NumPy type conversion (`.tolist()`)
   - Add proper error handling
   - Include validation

3. **Verify with tests:**
   ```bash
   pytest tests/ -k numpy
   ```

### Workflow 2: Learning from Test Failures

1. **Run tests with metrics:**
   ```bash
   pytest --enable-metrics
   ```

2. **Analyze patterns:**
   ```bash
   feedback-loop analyze
   ```

3. **Ask Cursor to fix:**
   ```
   @Codebase The test is failing with TypeError on NumPy serialization. Fix using patterns.
   ```

4. **Cursor will apply learned patterns automatically**

### Workflow 3: Code Review with Patterns

1. **Make changes in Cursor**

2. **Run pattern-aware review:**
   ```bash
   feedback-loop review --file path/to/file.py
   ```

3. **Cursor highlights issues inline (with LSP)**

4. **Apply quick fixes:** Click lightbulb icon or Cmd/Ctrl + .

### Workflow 4: Interactive Pattern Learning

1. **Open chat assistant:**
   ```bash
   ./bin/fl-chat
   ```

2. **Ask questions:**
   - "How do I handle large file uploads?"
   - "What's the pattern for NumPy JSON serialization?"
   - "Show me examples of proper bounds checking"

3. **Get code examples with explanations**

4. **Apply to your code in Cursor**

## 🎨 Cursor Composer Integration

Use Cursor Composer (Cmd/Ctrl + I) with feedback-loop context:

### Example Prompts

**With pattern context:**
```
@Codebase Using the feedback-loop patterns, create a FastAPI endpoint 
that accepts file uploads up to 800MB and processes them asynchronously
```

**For refactoring:**
```
@Codebase Refactor this function to follow feedback-loop patterns,
especially for error handling and type safety
```

**For testing:**
```
@Codebase Generate pytest tests for this function that validate 
all feedback-loop patterns are correctly applied
```

## 🔍 Using the Language Server

### Features

Once configured, the language server provides:

1. **Diagnostics**
   - Red underlines for pattern violations
   - Yellow warnings for potential issues
   - Blue hints for improvements

2. **Quick Fixes**
   - Click the lightbulb icon
   - Or press Cmd/Ctrl + .
   - Select "Apply feedback-loop pattern"

3. **Hover Documentation**
   - Hover over flagged code
   - See pattern explanation
   - View correct examples

### Supported Patterns

The LSP currently detects:
- ✅ Bare `except:` clauses
- ✅ Missing bounds checks on lists
- ✅ Print statements in production code
- ✅ NumPy type issues
- ✅ Missing validation
- ✅ Improper error handling

## 📊 Dashboard in Cursor

View the feedback-loop dashboard without leaving Cursor:

1. **Open terminal in Cursor** (Ctrl + `)

2. **Run dashboard:**
   ```bash
   ./bin/fl-dashboard
   ```

3. **See:**
   - Pattern usage statistics
   - Test failure trends
   - Code quality metrics
   - AI suggestion accuracy

## 🚨 Troubleshooting

### Language Server Not Starting

1. **Check Python path:**
   ```bash
   which python3
   python3 --version
   ```

2. **Install pygls:**
   ```bash
   pip install pygls
   ```

3. **Check settings:**
   - Open Cursor settings
   - Search "feedback-loop"
   - Verify paths are correct

4. **View logs:**
   - Cmd/Ctrl + Shift + P
   - "Output: Show Output Channels"
   - Select "Feedback Loop Language Server"

### Cursor Not Reading .cursorrules

1. **Verify file exists:**
   ```bash
   ls -la .cursorrules
   ```

2. **Reload window:**
   - Cmd/Ctrl + Shift + P
   - "Developer: Reload Window"

3. **Check file encoding:**
   - Should be UTF-8
   - No BOM (byte order mark)

### AI Not Applying Patterns

1. **Use @Codebase reference:**
   ```
   @Codebase [your question]
   ```

2. **Mention patterns explicitly:**
   ```
   Using feedback-loop patterns, [your request]
   ```

3. **Reference specific patterns:**
   ```
   Apply the NumPy type conversion pattern to [code]
   ```

### Tasks Not Appearing

1. **Create tasks.json:**
   - See Configuration → Cursor Tasks above

2. **Reload window**

3. **Check task syntax:**
   - Validate JSON with: `python -m json.tool .vscode/tasks.json`

## 🎓 Best Practices

### 1. Always Reference the Codebase

Use `@Codebase` in Cursor prompts to ensure patterns are included:

```
@Codebase Generate a file handler using feedback-loop patterns
```

### 2. Run Tests with Metrics

Enable metrics collection to improve pattern learning:

```bash
pytest --enable-metrics
```

### 3. Review Generated Code

Even with patterns, always review AI-generated code:
- Check for edge cases
- Verify error handling
- Run tests
- Use `./bin/fl-doctor` for diagnostics

### 4. Keep Patterns Updated

Regularly analyze and update patterns:

```bash
feedback-loop analyze
feedback-loop update-patterns
```

### 5. Use Cursor Tasks

Set up tasks for frequent operations:
- Chat assistant
- Dashboard
- Test runs
- Pattern analysis

## 🔗 Integration with Other Tools

### Pre-commit Hooks

Combine with Git pre-commit hooks:

```yaml
# .pre-commit-config.yaml
- repo: local
  hooks:
    - id: feedback-loop-check
      name: Feedback Loop Pattern Check
      entry: feedback-loop
      args: [check, --file]
      language: system
      types: [python]
```

### CI/CD

Use in GitHub Actions:

```yaml
- name: Run tests with metrics
  run: |
    pip install -e .
    pytest --enable-metrics
    
- name: Analyze patterns
  run: feedback-loop analyze
```

### VS Code Extension

The same extension works in Cursor:

1. Package the extension (from `vscode-extension/`)
2. Install in Cursor: Extensions → Install from VSIX
3. Configure as shown above

## 📚 Additional Resources

- **[Getting Started](documentation/GETTING_STARTED.md)** - feedback-loop basics
- **[AI Patterns Guide](documentation/AI_PATTERNS_GUIDE.md)** - Complete pattern catalog
- **[VS Code Extension](vscode-extension/README.md)** - Extension documentation
- **[Desktop Launchers](DESKTOP_LAUNCHERS.md)** - Alternative launch methods
- **[Quick Reference](documentation/QUICK_REFERENCE.md)** - Pattern cheat sheet

## 🤝 Contributing

Found a way to improve Cursor integration? 

1. Fork the repository
2. Create a feature branch
3. Submit a pull request

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## 📝 License

MIT License - See [LICENSE](LICENSE) file for details.

---

**Questions or issues?** Open an issue on [GitHub](https://github.com/doronpers/feedback-loop/issues)
