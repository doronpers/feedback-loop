#!/bin/bash
# Automated installation script for feedback-loop system
# Usage: curl -sSL https://raw.githubusercontent.com/doronpers/feedback-loop/main/install.sh | bash

set -e

echo "🔄 Feedback Loop - Automated Installation"
echo "=========================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check Python version
echo -n "Checking Python version... "
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}✗${NC}"
    echo "Error: Python 3 is not installed. Please install Python 3.8 or higher."
    exit 1
fi

PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
REQUIRED_VERSION="3.8"

if [ "$(printf '%s\n' "$REQUIRED_VERSION" "$PYTHON_VERSION" | sort -V | head -n1)" != "$REQUIRED_VERSION" ]; then
    echo -e "${RED}✗${NC}"
    echo "Error: Python $PYTHON_VERSION found, but $REQUIRED_VERSION or higher is required."
    exit 1
fi
echo -e "${GREEN}✓${NC} Python $PYTHON_VERSION"

# Install package
echo -n "Installing feedback-loop package... "
pip install -e . > /tmp/feedback-loop-install.log 2>&1
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓${NC}"
else
    echo -e "${RED}✗${NC}"
    echo "Installation failed. Check /tmp/feedback-loop-install.log for details."
    exit 1
fi

# Check for API key
echo ""
echo "Checking for Anthropic API key..."
if [ -z "$ANTHROPIC_API_KEY" ]; then
    echo -e "${YELLOW}⚠${NC}  ANTHROPIC_API_KEY not set"
    echo ""
    echo "To enable LLM-powered code generation, set your API key:"
    echo "  export ANTHROPIC_API_KEY='sk-ant-your-key-here'"
    echo ""
    echo "Add this to ~/.bashrc or ~/.zshrc for persistence:"
    echo "  echo 'export ANTHROPIC_API_KEY=\"sk-ant-your-key-here\"' >> ~/.bashrc"
    echo ""
else
    echo -e "${GREEN}✓${NC} API key found"
fi

# Create shell configuration
echo ""
echo "Setting up shell integration..."

SHELL_CONFIG=""
if [ -n "$BASH_VERSION" ]; then
    SHELL_CONFIG="$HOME/.bashrc"
elif [ -n "$ZSH_VERSION" ]; then
    SHELL_CONFIG="$HOME/.zshrc"
fi

if [ -n "$SHELL_CONFIG" ]; then
    if ! grep -q "# Feedback Loop aliases" "$SHELL_CONFIG"; then
        cat >> "$SHELL_CONFIG" << 'EOF'

# Feedback Loop aliases
alias fl-analyze='feedback-loop analyze'
alias fl-generate='feedback-loop generate'
alias fl-sync='feedback-loop sync-to-markdown'
alias fl-report='feedback-loop report'

# Quick code generation function
flg() {
    feedback-loop generate "$*" --output generated.py && cat generated.py
}
EOF
        echo -e "${GREEN}✓${NC} Added aliases to $SHELL_CONFIG"
        echo ""
        echo "Reload your shell to use aliases:"
        echo "  source $SHELL_CONFIG"
    else
        echo -e "${YELLOW}⚠${NC}  Aliases already exist in $SHELL_CONFIG"
    fi
fi

echo ""
echo -e "${GREEN}✓ Installation complete!${NC}"
echo ""
echo "Quick Start:"
echo "  1. Set API key: export ANTHROPIC_API_KEY='your-key'"
echo "  2. Run tests: pytest --enable-metrics"
echo "  3. Analyze: fl-analyze"
echo "  4. Generate: fl-generate 'your prompt here'"
echo ""
echo "For help: feedback-loop --help"
echo ""
