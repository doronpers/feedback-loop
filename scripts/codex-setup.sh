#!/usr/bin/env bash
# Codex environment setup script for feedback-loop
# This script runs automatically when Codex creates or resumes a container

set -e

echo "🔄 Feedback-Loop - Codex Environment Setup"
echo "==========================================="
echo ""

# Change to workspace directory
cd /workspace/feedback-loop || cd "$(dirname "$0")/.." || exit 1

echo "📦 Installing/upgrading pip..."
python3 -m pip install --upgrade pip --quiet

echo "📦 Installing feedback-loop with dev dependencies..."
# Install in editable mode with dev extras (includes pytest, black, flake8, mypy)
pip install -e ".[dev]" --quiet

# Install pre-commit hooks (optional - don't fail if it's not critical)
echo "🔧 Setting up pre-commit hooks..."
pre-commit install || echo "⚠️  Pre-commit install skipped (non-critical)"

# Verify installation
echo "✅ Verifying installation..."
python3 -c "import feedback_loop; print('✓ feedback-loop installed')" || echo "⚠️  Version check skipped"

# Quick sanity check - run a fast test subset (don't fail setup on test failures)
echo "🧪 Running quick sanity check..."
pytest -q -m "not slow and not integration" --co -q > /dev/null 2>&1 && echo "✓ Test discovery successful" || echo "⚠️  Test discovery check skipped"

echo ""
echo "✅ Setup complete! Environment ready for feedback-loop development and testing."
echo ""
echo "Quick commands:"
echo "  pytest                    # Run all tests"
echo "  pytest -m 'not slow'       # Run fast tests only"
echo "  black .                    # Format code"
echo "  flake8 .                   # Lint code"
echo "  mypy src/                  # Type check"
echo "  pre-commit run --all-files # Run all pre-commit hooks"
echo "  fl-chat                    # Feedback loop CLI"
echo ""
