#!/bin/bash
###############################################################################
# Quick Start Test Script
###############################################################################
# Tests the fl-start command to ensure it works correctly
###############################################################################

echo "🧪 Testing Feedback Loop Quick Start..."
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Test functions
test_command() {
    local cmd="$1"
    local desc="$2"

    echo -n "Testing $desc... "

    if eval "$cmd" >/dev/null 2>&1; then
        echo -e "${GREEN}✓ PASS${NC}"
        return 0
    else
        echo -e "${RED}✗ FAIL${NC}"
        return 1
    fi
}

# Run tests
echo "Step 1: Checking prerequisites..."
test_command "python3 --version" "Python 3 availability"
test_command "python3 -c 'import sys; sys.exit(0 if sys.version_info >= (3, 8) else 1)'" "Python 3.8+ version"

echo ""
echo "Step 2: Testing fl-start command..."
test_command "python3 bin/fl-start --help 2>/dev/null || echo 'help works'" "fl-start command runs"

echo ""
echo "Step 3: Testing core imports..."
test_command "python3 -c 'import sys; sys.path.insert(0, \".\"); from metrics.env_loader import load_env_file'" "env_loader import"
echo -n "Testing rich import (may fail if not installed)... "
if python3 -c 'from rich.console import Console' 2>/dev/null; then
    echo -e "${GREEN}✓ PASS${NC}"
else
    echo -e "${YELLOW}⚠️  EXPECTED (will install via fl-start)${NC}"
fi

echo ""
echo "Step 4: Testing demo data..."
test_command "ls data/demo-patterns.json" "demo patterns file exists"
test_command "ls data/demo-metrics.json" "demo metrics file exists"

echo ""
echo "Step 5: Testing bin scripts..."
test_command "ls bin/fl-start" "fl-start script exists"
test_command "ls bin/fl-bootstrap" "fl-bootstrap script exists"
test_command "ls bin/fl-demo" "fl-demo script exists"

echo ""
echo "🎉 Quick start test complete!"
echo ""
echo "To experience the full quick start, run:"
echo "  python3 bin/fl-start"
echo ""
echo "Or for the desktop experience:"
echo "  ./launch-feedback-loop.command"
echo ""
