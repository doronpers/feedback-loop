#!/bin/bash
###############################################################################
# Cursor Quick Setup Script for feedback-loop
###############################################################################
# This script helps Cursor users quickly set up and verify feedback-loop
# Usage: ./cursor-setup.sh
###############################################################################

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo ""
echo "╔════════════════════════════════════════════════════════════════════╗"
echo "║           Feedback Loop - Cursor Integration Setup                ║"
echo "╚════════════════════════════════════════════════════════════════════╝"
echo ""

# Check if we're in the right directory
if [ ! -f "setup.py" ] || [ ! -f ".cursorrules" ]; then
    echo -e "${RED}❌ Error: Please run this script from the feedback-loop repository root${NC}"
    exit 1
fi

echo -e "${BLUE}📍 Working directory: $(pwd)${NC}"
echo ""

# Step 1: Check Python
echo -e "${BLUE}[1/6] Checking Python installation...${NC}"
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version)
    echo -e "${GREEN}✅ Found: $PYTHON_VERSION${NC}"
else
    echo -e "${RED}❌ Python 3 not found. Please install Python 3.8+${NC}"
    exit 1
fi

# Step 2: Check pip
echo ""
echo -e "${BLUE}[2/6] Checking pip installation...${NC}"
if command -v pip3 &> /dev/null || command -v pip &> /dev/null; then
    echo -e "${GREEN}✅ pip is installed${NC}"
else
    echo -e "${RED}❌ pip not found${NC}"
    exit 1
fi

# Step 3: Install feedback-loop
echo ""
echo -e "${BLUE}[3/6] Installing feedback-loop...${NC}"
if pip3 install -e . &> /dev/null || pip install -e . &> /dev/null; then
    echo -e "${GREEN}✅ feedback-loop installed successfully${NC}"
else
    echo -e "${YELLOW}⚠️  Installation may have encountered issues. Continuing...${NC}"
fi

# Step 4: Verify .cursorrules
echo ""
echo -e "${BLUE}[4/6] Verifying Cursor configuration...${NC}"
if [ -f ".cursorrules" ]; then
    echo -e "${GREEN}✅ .cursorrules file found${NC}"
    echo -e "   Cursor will automatically use feedback-loop patterns"
else
    echo -e "${RED}❌ .cursorrules file not found${NC}"
    exit 1
fi

# Step 5: Verify VS Code/Cursor settings
echo ""
echo -e "${BLUE}[5/6] Checking VS Code/Cursor settings...${NC}"
if [ -f ".vscode/settings.json" ]; then
    echo -e "${GREEN}✅ .vscode/settings.json configured${NC}"
else
    echo -e "${YELLOW}⚠️  .vscode/settings.json not found (optional)${NC}"
fi

if [ -f ".vscode/tasks.json" ]; then
    echo -e "${GREEN}✅ .vscode/tasks.json configured${NC}"
else
    echo -e "${YELLOW}⚠️  .vscode/tasks.json not found (optional)${NC}"
fi

# Step 6: Run quick tests
echo ""
echo -e "${BLUE}[6/6] Running quick verification...${NC}"
if python3 -c "import metrics; print('Import successful')" &> /dev/null; then
    echo -e "${GREEN}✅ Python modules import correctly${NC}"
else
    echo -e "${YELLOW}⚠️  Module import issues detected${NC}"
fi

# Summary
echo ""
echo "╔════════════════════════════════════════════════════════════════════╗"
echo "║                      Setup Complete! 🎉                            ║"
echo "╚════════════════════════════════════════════════════════════════════╝"
echo ""
echo -e "${GREEN}Next steps:${NC}"
echo ""
echo "1. ${BLUE}Open this repository in Cursor${NC}"
echo "   Cursor will automatically read .cursorrules"
echo ""
echo "2. ${BLUE}Try Cursor's AI with pattern awareness:${NC}"
echo "   Use Cmd/Ctrl + K and ask:"
echo "   '@Codebase Generate a function to process NumPy arrays to JSON'"
echo ""
echo "3. ${BLUE}Access feedback-loop tools via Tasks:${NC}"
echo "   Press Cmd/Ctrl + Shift + P → 'Tasks: Run Task' → Select a tool"
echo ""
echo "4. ${BLUE}Run the demo:${NC}"
echo "   python demo.py"
echo ""
echo "5. ${BLUE}Read the full guide:${NC}"
echo "   cat CURSOR_INTEGRATION.md"
echo ""
echo -e "${YELLOW}💡 Pro tip:${NC} Use '@Codebase' in Cursor prompts to include pattern context"
echo ""
echo -e "${BLUE}📚 Resources:${NC}"
echo "   • Cursor Integration: CURSOR_INTEGRATION.md"
echo "   • Getting Started: documentation/GETTING_STARTED.md"
echo "   • Quick Reference: documentation/QUICK_REFERENCE.md"
echo ""
echo -e "${GREEN}Happy coding with feedback-loop! 🚀${NC}"
echo ""
