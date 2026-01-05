#!/bin/bash
# Quick setup for existing repositories
# Usage: cd your-repo && curl -sSL https://raw.githubusercontent.com/doronpers/feedback-loop/main/quickstart.sh | bash

set -e

echo "🔄 Feedback Loop - Repository Setup"
echo "===================================="
echo ""

# Check if feedback-loop is installed
if ! command -v feedback-loop &> /dev/null; then
    echo "Error: feedback-loop not installed globally"
    echo "Install with: pip install feedback-loop"
    echo "Or run: pip install -e /path/to/feedback-loop"
    exit 1
fi

# Check if we're in a git repo
if [ ! -d ".git" ]; then
    echo "Error: Not in a git repository"
    echo "Run this script from the root of your git repository"
    exit 1
fi

echo "Setting up feedback-loop for this repository..."
echo ""

# Copy conftest if not exists
if [ ! -f "conftest.py" ]; then
    echo -n "Installing pytest plugin (conftest.py)... "
    python3 << 'EOF'
import sys
from pathlib import Path

# Find feedback-loop installation
import metrics
feedback_loop_path = Path(metrics.__file__).parent.parent

conftest_src = feedback_loop_path / "conftest.py"
conftest_dst = Path("conftest.py")

if conftest_src.exists():
    conftest_dst.write_text(conftest_src.read_text())
    print("✓")
else:
    print("✗ Source not found")
    sys.exit(1)
EOF
else
    echo "⚠  conftest.py already exists, skipping"
fi

# Install git hook
if [ ! -f ".git/hooks/pre-commit" ] || ! grep -q "feedback loop" ".git/hooks/pre-commit" 2>/dev/null; then
    echo -n "Installing git pre-commit hook... "
    python3 << 'EOF'
import sys
from pathlib import Path

# Find feedback-loop installation
import metrics
feedback_loop_path = Path(metrics.__file__).parent.parent

hook_src = feedback_loop_path / "hooks" / "pre-commit"
hook_dst = Path(".git/hooks/pre-commit")

if hook_src.exists():
    hook_dst.write_text(hook_src.read_text())
    hook_dst.chmod(0o755)
    print("✓")
else:
    print("✗ Source not found")
    sys.exit(1)
EOF
else
    echo "⚠  Pre-commit hook already exists"
fi

# Setup GitHub Actions if .github directory exists
if [ -d ".github" ]; then
    if [ ! -f ".github/workflows/feedback-loop.yml" ]; then
        echo -n "Installing GitHub Actions workflow... "
        mkdir -p .github/workflows
        python3 << 'EOF'
import sys
from pathlib import Path

# Find feedback-loop installation
import metrics
feedback_loop_path = Path(metrics.__file__).parent.parent

workflow_src = feedback_loop_path / ".github" / "workflows" / "feedback-loop.yml"
workflow_dst = Path(".github/workflows/feedback-loop.yml")

if workflow_src.exists():
    workflow_dst.parent.mkdir(parents=True, exist_ok=True)
    workflow_dst.write_text(workflow_src.read_text())
    print("✓")
else:
    print("✗ Source not found")
    sys.exit(1)
EOF
    else
        echo "⚠  GitHub workflow already exists"
    fi
fi

# Create pytest.ini if it doesn't exist
if [ ! -f "pytest.ini" ] && [ ! -f "pyproject.toml" ]; then
    echo -n "Creating pytest.ini with auto-metrics... "
    cat > pytest.ini << 'EOF'
[pytest]
addopts = --enable-metrics -v
testpaths = tests
EOF
    echo "✓"
fi

echo ""
echo "✓ Setup complete!"
echo ""
echo "Next steps:"
echo "  1. Run tests: pytest"
echo "  2. Review metrics: feedback-loop analyze"
echo "  3. Generate code: feedback-loop generate 'your prompt'"
echo ""
echo "The system is now integrated into your workflow!"
echo ""
