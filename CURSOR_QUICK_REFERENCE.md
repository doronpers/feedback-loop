# Cursor Quick Reference Card

**feedback-loop + Cursor IDE** - Essential commands and workflows

## 🚀 Quick Setup

```bash
cd feedback-loop
./cursor-setup.sh
# Open in Cursor - done!
```

## 🎯 Cursor Composer Prompts

### Pattern-Aware Generation
```
@Codebase Generate a function to process NumPy arrays and return JSON
```

### Refactoring with Patterns
```
@Codebase Refactor this function to follow feedback-loop patterns,
especially for error handling and type safety
```

### Testing
```
@Codebase Generate pytest tests for this function that validate 
all feedback-loop patterns are correctly applied
```

## ⌨️ Cursor Keyboard Shortcuts

| Action | Shortcut | What it does |
|--------|----------|--------------|
| **Composer** | `Cmd/Ctrl + I` | Open inline AI assistant |
| **Chat** | `Cmd/Ctrl + L` | Open chat panel |
| **Quick Actions** | `Cmd/Ctrl + K` | Quick AI commands |
| **Run Task** | `Cmd/Ctrl + Shift + P` → Tasks | Run feedback-loop tools |
| **Quick Fix** | `Cmd/Ctrl + .` | Apply pattern suggestions (LSP) |

## 🛠️ Available Tasks

Access via: `Cmd/Ctrl + Shift + P` → "Tasks: Run Task"

- **Chat Assistant** - Interactive pattern help
- **Dashboard** - View metrics and patterns
- **Setup Wizard** - Configure feedback-loop
- **Doctor** - Diagnose issues
- **Run Tests with Metrics** - Test with pattern collection
- **Analyze Patterns** - Update pattern library

## 🎨 The 9 Patterns (Cheat Sheet)

### 1. NumPy Type Conversion
```python
# ✅ ALWAYS convert before JSON
result = {"mean": float(np.mean(data))}
```

### 2. Bounds Checking
```python
# ✅ Check before accessing
first = items[0] if items else None
```

### 3. Specific Exceptions
```python
# ✅ Never use bare except:
try:
    data = json.loads(text)
except json.JSONDecodeError as e:
    logger.debug(f"Invalid JSON: {e}")
    return None
```

### 4. Structured Logging
```python
# ✅ Use logger, not print
logger.debug(f"Processing {filename}")
```

### 5. Metadata-Based Logic
```python
# ✅ Use explicit metadata
priority = metadata.get("priority_level", "normal")
```

### 6. Temp File Handling
```python
# ✅ Always cleanup
fd, path = tempfile.mkstemp()
try:
    with os.fdopen(fd, 'wb') as f:
        f.write(data)
finally:
    os.unlink(path)
```

### 7. Large File Processing
```python
# ✅ Process in chunks
while chunk := f.read(1024 * 1024):
    process(chunk)
```

### 8. FastAPI Streaming
```python
# ✅ Stream to disk
while chunk := await file.read(1024 * 1024):
    tmp_file.write(chunk)
```

### 9. NaN/Inf Handling
```python
# ✅ Check and handle
def safe_float(val):
    return None if np.isnan(val) or np.isinf(val) else float(val)
```

## 💡 Cursor Best Practices

### 1. Use @Codebase Reference
Always include `@Codebase` to give Cursor access to patterns:
```
@Codebase [your request]
```

### 2. Mention Patterns Explicitly
For critical code, mention specific patterns:
```
Apply the NumPy type conversion and bounds checking patterns to...
```

### 3. Request Tests
Always generate tests with your code:
```
@Codebase Generate a safe file handler with tests
```

### 4. Review AI Output
Even with patterns, always:
- ✅ Check edge cases
- ✅ Verify error handling
- ✅ Run tests
- ✅ Review type hints

## 🔍 Common Workflows

### Workflow 1: New Feature
1. Ask Cursor with `@Codebase` for initial code
2. Run tests: `pytest --enable-metrics`
3. Review with `./bin/fl-chat`
4. Iterate based on feedback

### Workflow 2: Fix Bug
1. Identify pattern violation
2. Ask Cursor: `@Codebase Fix this using feedback-loop patterns`
3. Verify fix with tests
4. Update pattern if needed

### Workflow 3: Code Review
1. Open file in Cursor
2. Run: `Cmd/Ctrl + Shift + P` → "Feedback Loop: Doctor"
3. Fix issues highlighted
4. Request Cursor AI for suggestions

### Workflow 4: Learning
1. Run: `python demo.py` to see patterns
2. Ask Cursor: `@Codebase Explain the NumPy type conversion pattern`
3. Generate examples with Cursor
4. Test and verify

## 🐛 Quick Troubleshooting

### Cursor not using patterns?
```bash
# Verify .cursorrules exists
ls -la .cursorrules

# Reload Cursor
Cmd/Ctrl + Shift + P → "Developer: Reload Window"

# Always use @Codebase in prompts
```

### Language server not working?
```bash
# Check installation
pip list | grep pygls

# Verify settings
cat .vscode/settings.json

# View logs
Cmd/Ctrl + Shift + P → "Output: Show Output Channels" → "Feedback Loop"
```

### Tasks not appearing?
```bash
# Verify tasks.json exists
ls -la .vscode/tasks.json

# Reload window
Cmd/Ctrl + Shift + P → "Developer: Reload Window"
```

## 📚 Quick Links

| Resource | Location |
|----------|----------|
| **Full Guide** | `CURSOR_INTEGRATION.md` |
| **Pattern Details** | `documentation/QUICK_REFERENCE.md` |
| **Getting Started** | `documentation/GETTING_STARTED.md` |
| **Examples** | `examples/` directory |
| **Tests** | `tests/` directory |

## 🎓 Pro Tips

1. **Use Composer for new code** - `Cmd/Ctrl + I`
2. **Use Chat for questions** - `Cmd/Ctrl + L`
3. **Run tasks frequently** - Test early and often
4. **Keep patterns updated** - `feedback-loop analyze` regularly
5. **Learn from failures** - Review test output carefully

## 🚨 Remember

- ✅ **ALWAYS** use `@Codebase` in Cursor prompts
- ✅ **ALWAYS** apply patterns to NumPy code
- ✅ **ALWAYS** check bounds before array access
- ✅ **ALWAYS** use specific exceptions
- ✅ **NEVER** use bare `except:`
- ✅ **NEVER** use `print()` in production code

---

**Need more help?** 
- Run: `./bin/fl-chat` for interactive assistance
- Read: `CURSOR_INTEGRATION.md` for detailed guide
- Visit: [GitHub Issues](https://github.com/doronpers/feedback-loop/issues)

**Happy coding with Cursor! 🎯**
