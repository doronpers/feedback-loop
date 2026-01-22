# Troubleshooting Guide

**Quick answer to common issues.** If your problem isn't here, run `fl-doctor` for diagnostics.

---

## 🚀 Quick Start Issues

### Dashboard won't open (port 8000 already in use)

**Problem:** `fl-start` fails with "Port 8000 already in use"

**Why it happens:**

- Another service (web server, previous feedback-loop instance) is using port 8000–8003
- Common on development machines with multiple projects

**Quick fix:**

1. Let feedback-loop auto-detect an available port:

   ```bash
   python3 bin/fl-start
   ```

   The tool will automatically try ports 8000, 8001, 8002, 8003 and use the first available one.

2. Or, manually free port 8000:

   ```bash
   # Find what's using port 8000
   lsof -i :8000

   # Kill it if it's a previous feedback-loop instance
   kill -9 <PID>
   ```

3. Check in a new terminal:

   ```bash
   python3 bin/fl-start
   ```

**Still stuck?** Run diagnostics:

```bash
python3 bin/fl-doctor
```

---

### Installation fails (missing dependencies)

**Problem:** `pip install -e .` fails with "ModuleNotFoundError" or "No module named..."

**Why it happens:**

- Python version too old (need 3.13+)
- Virtual environment not active
- Partial installation (interrupted pip)

**Quick fix:**

1. **Check Python version:**

   ```bash
   python3 --version
   # Should be 3.13 or higher

   # If older, use python3.13 explicitly:
   python3.13 -m pip install -e .
   ```

2. **Activate virtual environment:**

   ```bash
   # Create if doesn't exist
   python3 -m venv venv

   # Activate
   source venv/bin/activate  # macOS/Linux
   venv\Scripts\activate      # Windows

   # Try install again
   pip install -e .
   ```

3. **Clean and reinstall:**

   ```bash
   # Remove old installation
   pip uninstall feedback-loop -y

   # Clear pip cache
   pip cache purge

   # Reinstall
   pip install -e .
   ```

**Still stuck?** Check auto-bootstrap:

```bash
python3 bin/fl-bootstrap
```

---

### Auto-setup script fails

**Problem:** `python3 bin/fl-start` or `python3 bin/fl-bootstrap` crashes

**Why it happens:**

- Missing system dependencies (git, Python)
- Permission issues
- Incomplete previous attempt

**Quick fix:**

1. **Verify prerequisites:**

   ```bash
   # Check Python
   python3 --version

   # Check Git
   git --version

   # Check if in a Git repository
   git status
   ```

2. **Run diagnostics:**

   ```bash
   python3 bin/fl-doctor
   ```

   This will check all prerequisites and tell you exactly what's missing.

3. **Manual bootstrap:**

   ```bash
   # Install dependencies explicitly
   pip install -r requirements.txt

   # Then try demo
   python3 demo.py
   ```

---

## 🤖 LLM & AI Assistant Issues

### Chat assistant says "No LLM providers available"

**Problem:** `fl-chat` refuses to start without an API key

**Why it happens:**

- No LLM provider is configured (missing environment variable)
- Or, all API keys are invalid/expired

**Quick fix:**

1. **Check which LLM providers you have:**

   ```bash
   python3 bin/fl-doctor
   ```

   Look for the "LLM Providers" section.

2. **Set an API key:**

   ```bash
   # For Anthropic Claude (recommended)
   export ANTHROPIC_API_KEY='sk-ant-...'

   # For OpenAI
   export OPENAI_API_KEY='sk-...'

   # For Google Gemini
   export GEMINI_API_KEY='...'
   ```

3. **Verify it works:**

   ```bash
   python3 bin/fl-chat
   ```

4. **Make it permanent:**
   Add to `.env` file (already in `.gitignore`):

   ```bash
   # .env (at project root)
   ANTHROPIC_API_KEY=sk-ant-...
   OPENAI_API_KEY=sk-...
   GEMINI_API_KEY=...
   ```

**Want to test without an API key?** Use mock mode (offline demos):

```bash
python3 bin/fl-chat --mock-llm
```

---

### Chat assistant is very slow or times out

**Problem:** `fl-chat` takes 30+ seconds to respond or gives timeout error

**Why it happens:**

- Network latency to LLM service
- LLM provider is overloaded or down
- Poor internet connection

**Quick fix:**

1. **Check your internet:**

   ```bash
   ping api.openai.com  # or api.anthropic.com
   ```

2. **Try a different provider:**
   If using OpenAI, switch to Anthropic (often faster):

   ```bash
   export ANTHROPIC_API_KEY='sk-ant-...'
   python3 bin/fl-chat
   ```

3. **Check LLM provider status:**
   - Anthropic: <https://status.anthropic.com>
   - OpenAI: <https://status.openai.com>
   - Google: <https://status.cloud.google.com>

4. **Use mock mode for local testing:**

   ```bash
   python3 bin/fl-chat --mock-llm
   ```

---

### Code generation produces poor results

**Problem:** `fl-apply` or `fl-generate` gives unhelpful suggestions

**Why it happens:**

- Patterns haven't been learned yet (no metrics collected)
- LLM provider has low-quality responses
- Context not clear enough

**Quick fix:**

1. **Collect patterns first:**

   ```bash
   # Run tests to generate metrics
   pytest --enable-metrics tests/

   # Analyze patterns
   python3 -m metrics.integrate analyze
   ```

2. **Check which patterns are available:**

   ```bash
   python3 bin/fl-explore
   ```

3. **Try with explicit pattern:**

   ```bash
   feedback-loop generate "Create NumPy serialization function" --pattern numpy_json_serialization
   ```

4. **Review the pattern library:**
   Check `documentation/AI_PATTERNS_GUIDE.md` or run:

   ```bash
   python3 bin/fl-chat
   # Then ask: "Show me the NumPy pattern"
   ```

---

## 📊 Dashboard & Analytics Issues

### Dashboard shows "no data" or empty charts

**Problem:** Analytics dashboard opens but shows no metrics

**Why it happens:**

- No metrics have been collected yet
- Metrics file is empty or corrupted
- Dashboard is looking at wrong data file

**Quick fix:**

1. **Collect some metrics:**

   ```bash
   pytest --enable-metrics tests/
   ```

2. **Check metrics file exists:**

   ```bash
   ls -lh data/metrics_data.json
   # Should show a file with size > 100 bytes
   ```

3. **Verify metrics are valid:**

   ```bash
   python3 -c "import json; json.load(open('data/metrics_data.json'))"
   # Should exit silently (no error)
   ```

4. **Refresh dashboard:**
   - Reload in browser (Cmd+R or Ctrl+R)
   - Or restart dashboard: `python3 bin/fl-dashboard`

---

### Superset integration not working

**Problem:** Superset shows error when connecting to database

**Why it happens:**

- Metrics haven't been exported to database
- Database credentials incorrect
- SQLite file not in expected location

**Quick fix:**

1. **Export metrics to database:**

   ```bash
   # First, collect metrics
   pytest --enable-metrics

   # Then export
   python3 superset_dashboards/scripts/export_to_db.py --input data/metrics_data.json
   ```

2. **Check database file:**

   ```bash
   ls -lh data/metrics.db
   # Should show a file with size > 10KB
   ```

3. **In Superset, add database connection:**
   - Go to Data → Databases → + Database
   - Select SQLite
   - SQLAlchemy URI: `sqlite:////full/path/to/feedback-loop/data/metrics.db`
   - Test Connection

**See detailed Superset guide:** [SUPERSET_INTEGRATION.md](SUPERSET_INTEGRATION.md)

---

## 🔧 Development & Testing Issues

### Tests fail with "ModuleNotFoundError"

**Problem:** `pytest` fails to find modules

**Why it happens:**

- Not in project root directory
- Virtual environment not activated
- Missing `__init__.py` files

**Quick fix:**

1. **Verify you're in project root:**

   ```bash
   pwd
   # Should end with /feedback-loop

   ls pyproject.toml
   # Should exist
   ```

2. **Activate virtual environment:**

   ```bash
   source venv/bin/activate  # macOS/Linux
   venv\Scripts\activate      # Windows
   ```

3. **Run tests from project root:**

   ```bash
   pytest tests/ -v
   ```

---

### Metrics collection is not working

**Problem:** `pytest --enable-metrics` doesn't create `data/metrics_data.json`

**Why it happens:**

- Metrics directory doesn't exist
- Permission denied writing to `data/`
- Pytest plugin not loaded

**Quick fix:**

1. **Create data directory:**

   ```bash
   mkdir -p data
   chmod 755 data
   ```

2. **Verify metrics plugin is installed:**

   ```bash
   pytest --co -q | grep metrics
   # Should show metrics fixtures
   ```

3. **Run a test explicitly:**

   ```bash
   pytest tests/test_good_patterns.py -v --enable-metrics -s
   ```

4. **Check if file was created:**

   ```bash
   ls -lh data/metrics_data.json
   ```

---

## 🔍 Diagnostics & Debug Mode

### Get detailed diagnostic information

**Run the diagnostics tool:**

```bash
python3 bin/fl-doctor
```

This will check:

- Python version
- Git repository status
- Virtual environment
- Installed dependencies
- LLM providers and API keys
- Database connectivity
- Metrics files
- Patterns library

**Output will tell you:**

- What's working ✅
- What's missing ⚠️
- What's broken ❌
- Suggested fixes for each issue

---

### Enable debug logging

**For detailed troubleshooting:**

```bash
# Enable debug mode
export DEBUG=1
export LOG_LEVEL=DEBUG

# Run tool with verbose output
python3 bin/fl-chat -v
python3 bin/fl-start -v
pytest tests/ -v -s --log-cli-level=DEBUG
```

---

### Collect logs for bug reports

**Before reporting an issue:**

1. **Run diagnostics:**

   ```bash
   python3 bin/fl-doctor > diagnostics.txt 2>&1
   ```

2. **Collect error logs:**

   ```bash
   # If dashboard crashed
   cat ~/Library/Logs/feedback-loop.log  # macOS
   cat ~/.local/share/feedback-loop/logs/error.log  # Linux

   # Or run with debug
   DEBUG=1 python3 bin/fl-start 2>&1 | tee debug.log
   ```

3. **Include in bug report:**
   - `diagnostics.txt` output
   - Error message (full traceback)
   - What you were trying to do
   - Expected vs actual behavior

---

## 💡 Common Questions

### Can I use feedback-loop without internet?

**Yes!** Use mock mode for local development:

```bash
python3 bin/fl-chat --mock-llm
python3 bin/fl-start --mock-llm
```

All LLM features will use deterministic mock responses, perfect for demos and CI.

---

### Can I run multiple feedback-loop instances?

**Yes, but:**

- Each should use a different dashboard port (auto-selected by `fl-start`)
- If sharing metrics: use separate `data/` directories or a centralized database
- Recommended: use one instance per team with shared database

---

### How do I reset everything and start fresh?

```bash
# Reset metrics and patterns
rm -rf data/metrics_data.json data/patterns.json

# Reset database
rm -f data/metrics.db

# Clear cache
rm -rf .pytest_cache __pycache__

# Reinstall
pip install -e . --force-reinstall

# Start fresh
python3 bin/fl-start
```

---

### How do I migrate from file-based metrics to database?

```bash
# If using database backend
python3 superset_dashboards/scripts/export_to_db.py \
  --input data/metrics_data.json \
  --output data/metrics.db

# Verify
sqlite3 data/metrics.db "SELECT COUNT(*) FROM metrics_bugs;"
```

---

## 🆘 Still stuck?

1. **Check documentation:**
   - [GETTING_STARTED.md](GETTING_STARTED.md) - Installation
   - [AI_PATTERNS_GUIDE.md](AI_PATTERNS_GUIDE.md) - Patterns
   - [METRICS_GUIDE.md](METRICS_GUIDE.md) - Metrics

2. **Run diagnostics:**

   ```bash
   python3 bin/fl-doctor
   ```

3. **Chat with AI assistant:**

   ```bash
   python3 bin/fl-chat
   # Ask: "I'm getting error X when doing Y"
   ```

4. **Report issue on GitHub:**
   - Include diagnostics output
   - Include error logs (see "Collect logs" above)
   - Include steps to reproduce
   - <https://github.com/doronpers/feedback-loop/issues>

---

**Last updated:** January 2026
**Feedback Loop Version:** 1.0.0+
