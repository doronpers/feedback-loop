# Quick Start Guide

Get up and running with feedback-loop in 2 minutes!

## Installation (Choose One)

### Option 1: Automated Install (Recommended)
```bash
# Clone and install
git clone https://github.com/doronpers/feedback-loop.git
cd feedback-loop
./install.sh
```

### Option 2: pip Install
```bash
# From source
pip install -e /path/to/feedback-loop

# Or from PyPI (when published)
pip install feedback-loop
```

### Option 3: Use Makefile
```bash
cd feedback-loop
make install
```

## Setup Your API Key

```bash
# Set for current session
export ANTHROPIC_API_KEY='sk-ant-your-key-here'

# Make it permanent (choose your shell)
echo 'export ANTHROPIC_API_KEY="sk-ant-your-key-here"' >> ~/.bashrc  # Bash
echo 'export ANTHROPIC_API_KEY="sk-ant-your-key-here"' >> ~/.zshrc   # Zsh

# Reload your shell
source ~/.bashrc  # or source ~/.zshrc
```

## Add to Your Repository

```bash
# Go to your project
cd your-project

# Quick setup (copies all needed files)
/path/to/feedback-loop/quickstart.sh

# Or manually
cp /path/to/feedback-loop/conftest.py ./
cp /path/to/feedback-loop/hooks/pre-commit .git/hooks/
chmod +x .git/hooks/pre-commit
```

## Daily Usage

### 1. Run Tests (Metrics Auto-Collected)
```bash
pytest --enable-metrics
```

### 2. Review What You Learned
```bash
feedback-loop analyze
# or
make analyze
```

### 3. Generate Code
```bash
feedback-loop generate "Create a function to process JSON data"
# or
make generate PROMPT="Create a function to process JSON data"
```

### 4. Check System Health
```bash
feedback-loop doctor
# or
make doctor
```

### 5. View Dashboard
```bash
make dashboard
```

## Common Commands

### Using `feedback-loop` command:
```bash
feedback-loop --help          # Show all commands
feedback-loop analyze         # Analyze metrics
feedback-loop generate "..."  # Generate code
feedback-loop sync-to-markdown # Update docs
feedback-loop report          # View report
```

### Using `make` (easier):
```bash
make help       # Show all commands
make test       # Run tests with metrics
make analyze    # Analyze patterns
make dashboard  # Interactive view
make doctor     # Health check
make sync       # Update docs
```

### Using aliases (after install.sh):
```bash
fl-analyze      # Analyze metrics
fl-generate     # Generate code
fl-sync         # Sync docs
flg "prompt"    # Quick generate
```

## Example Workflow

```bash
# 1. Write some code
vim my_feature.py

# 2. Run tests (auto-collects metrics)
pytest --enable-metrics

# 3. See what patterns emerged
make dashboard

# 4. Update documentation
make sync

# 5. Commit (hook runs automatically)
git commit -am "Add new feature"

# That's it! CI/CD will analyze on push
```

## Troubleshooting

### "command not found: feedback-loop"
```bash
# Reinstall
cd feedback-loop && pip install -e .
```

### "ANTHROPIC_API_KEY not found"
```bash
# Check if set
echo $ANTHROPIC_API_KEY

# Set it
export ANTHROPIC_API_KEY='your-key'
```

### "No metrics collected"
```bash
# Run tests with metrics enabled
pytest --enable-metrics

# Or add to pytest.ini
echo "[pytest]
addopts = --enable-metrics" > pytest.ini
```

### "Check system health"
```bash
make doctor
# or
./bin/fl-doctor
```

## What Gets Installed

```
your-repo/
├── conftest.py                 # Pytest plugin (auto-collects metrics)
├── .git/hooks/pre-commit       # Git hook (analyzes before commit)
├── .github/workflows/
│   └── feedback-loop.yml       # CI/CD workflow
├── pytest.ini                  # Pytest config (optional)
├── metrics_data.json           # Collected metrics (auto-generated)
└── patterns.json               # Learned patterns (auto-generated)
```

## Next Steps

1. **Read the patterns**: `cat AI_PATTERNS.md`
2. **Try code generation**: `make generate PROMPT="your task"`
3. **Check the dashboard**: `make dashboard`
4. **Review the full docs**: `cat FEEDBACK_LOOP_IMPROVEMENTS.md`

## One-Liner Setup

```bash
# For new repos
curl -sSL https://raw.githubusercontent.com/doronpers/feedback-loop/main/quickstart.sh | bash

# For feedback-loop itself
curl -sSL https://raw.githubusercontent.com/doronpers/feedback-loop/main/install.sh | bash
```

## Need Help?

```bash
make help              # Show all commands
feedback-loop --help   # Show CLI help
make doctor            # Diagnose issues
```

---

**That's it! You're ready to go.** The system will now:
- ✅ Auto-collect metrics from tests
- ✅ Learn patterns from failures
- ✅ Analyze commits before push
- ✅ Generate better code over time
- ✅ Provide continuous feedback
