#!/bin/bash
###############################################################################
# Feedback Loop - Mac Desktop Launcher
###############################################################################
# This script can be double-clicked from macOS Finder to launch feedback-loop
# Usage: Double-click this file from your desktop or any folder
# AUTO-GENERATED - Run scripts/update_launchers.py to regenerate
###############################################################################

# Change to the directory where this script is located
cd "$(dirname "$0")" || exit 1

# Activate virtual environment if it exists
VENV_ACTIVATED=""
if [ -d ".venv" ]; then
    source .venv/bin/activate
    VENV_ACTIVATED=".venv"
elif [ -d "venv" ]; then
    source venv/bin/activate
    VENV_ACTIVATED="venv"
fi

# Clear the screen for a clean start
clear

echo "╔════════════════════════════════════════════════════════════════════╗"
echo "║                    Feedback Loop Launcher                         ║"
echo "╚════════════════════════════════════════════════════════════════════╝"
echo ""
echo "📍 Current directory: $(pwd)"
if [ -n "$VENV_ACTIVATED" ]; then
    echo "🐍 Virtual environment: $VENV_ACTIVATED"
fi
echo ""

# Determine which Python to use (prefer venv's Python if activated)
if command -v python &> /dev/null; then
    PYTHON_CMD=python
elif command -v python3 &> /dev/null; then
    PYTHON_CMD=python3
else
    echo "❌ Error: Python is not installed or not in PATH"
    echo ""
    echo "Please install Python 3.8 or later:"
    echo "  • Download from: https://www.python.org/downloads/"
    echo "  • Or use Homebrew: brew install python3"
    echo ""
    echo "Press any key to exit..."
    read -n 1 -s
    exit 1
fi

# Display Python version and location
PYTHON_VERSION=$($PYTHON_CMD --version 2>&1)
PYTHON_PATH=$(which $PYTHON_CMD)
echo "✓ Found: $PYTHON_VERSION"
echo "✓ Python path: $PYTHON_PATH"
echo ""

# Check if feedback-loop is installed
if ! $PYTHON_CMD -c "import metrics" &> /dev/null; then
    echo "⚠️  Feedback Loop not installed in current environment"
    echo ""
    echo "Would you like to install it now? (y/n)"
    read -r response
    if [[ "$response" =~ ^[Yy]$ ]]; then
        echo ""
        echo "Installing feedback-loop..."
        $PYTHON_CMD -m pip install -e . || {
            echo ""
            echo "❌ Installation failed"
            echo "Press any key to exit..."
            read -n 1 -s
            exit 1
        }
        echo ""
        echo "✓ Installation complete!"
        echo ""
    else
        echo ""
        echo "Cannot proceed without installation"
        echo "Press any key to exit..."
        read -n 1 -s
        exit 1
    fi
fi

# Main menu loop
while true; do
    echo "════════════════════════════════════════════════════════════════════"
    echo "Please select a tool to launch:"
    echo "════════════════════════════════════════════════════════════════════"
    echo ""
    echo "  1) 💬 Chat       - Interactive AI-powered chat for coding help"
    echo "  2) 📊 Dashboard  - View metrics and pattern insights"
    echo "  3) 🩺 Doctor     - Diagnose and fix common issues"
    echo "  4) ⚙️ Setup      - Configure feedback-loop for your project"
    echo "  5) 🔧 Synthesize - Interactive Code Synthesizer"
    echo "  6) 🎬 Demo              - See patterns in action"
    echo "  7) 📊 Superset Setup   - Set up analytics dashboards"
    echo "  8) 📚 Open Documentation"
    echo "  9) 🚪 Exit"
    echo ""
    echo -n "Enter your choice (1-9): "
    read -r choice
    echo ""

    case $choice in
        1)
            echo "🚀 Launching Chat..."
            echo "════════════════════════════════════════════════════════════════════"
            echo ""
            $PYTHON_CMD bin/fl-chat
            STATUS=$?
            echo ""
            echo "════════════════════════════════════════════════════════════════════"
            if [ $STATUS -eq 0 ]; then
                echo "✓ Chat exited successfully"
            else
                echo "⚠️  Chat exited with code: $STATUS"
            fi
            echo ""
            echo "Press any key to return to menu..."
            read -n 1 -s
            echo ""
            ;;
        2)
            echo "🚀 Launching Dashboard..."
            echo "════════════════════════════════════════════════════════════════════"
            echo ""
            $PYTHON_CMD bin/fl-dashboard
            STATUS=$?
            echo ""
            echo "════════════════════════════════════════════════════════════════════"
            if [ $STATUS -eq 0 ]; then
                echo "✓ Dashboard exited successfully"
            else
                echo "⚠️  Dashboard exited with code: $STATUS"
            fi
            echo ""
            echo "Press any key to return to menu..."
            read -n 1 -s
            echo ""
            ;;
        3)
            echo "🚀 Launching Doctor..."
            echo "════════════════════════════════════════════════════════════════════"
            echo ""
            $PYTHON_CMD bin/fl-doctor
            STATUS=$?
            echo ""
            echo "════════════════════════════════════════════════════════════════════"
            if [ $STATUS -eq 0 ]; then
                echo "✓ Doctor exited successfully"
            else
                echo "⚠️  Doctor exited with code: $STATUS"
            fi
            echo ""
            echo "Press any key to return to menu..."
            read -n 1 -s
            echo ""
            ;;
        4)
            echo "🚀 Launching Setup..."
            echo "════════════════════════════════════════════════════════════════════"
            echo ""
            $PYTHON_CMD bin/fl-setup
            STATUS=$?
            echo ""
            echo "════════════════════════════════════════════════════════════════════"
            if [ $STATUS -eq 0 ]; then
                echo "✓ Setup exited successfully"
            else
                echo "⚠️  Setup exited with code: $STATUS"
            fi
            echo ""
            echo "Press any key to return to menu..."
            read -n 1 -s
            echo ""
            ;;
        5)
            echo "🚀 Launching Synthesize..."
            echo "════════════════════════════════════════════════════════════════════"
            echo ""
            $PYTHON_CMD bin/fl-synthesize
            STATUS=$?
            echo ""
            echo "════════════════════════════════════════════════════════════════════"
            if [ $STATUS -eq 0 ]; then
                echo "✓ Synthesize exited successfully"
            else
                echo "⚠️  Synthesize exited with code: $STATUS"
            fi
            echo ""
            echo "Press any key to return to menu..."
            read -n 1 -s
            echo ""
            ;;
        6)
            echo "🚀 Running Demo..."
            echo "════════════════════════════════════════════════════════════════════"
            echo ""
            $PYTHON_CMD demo.py
            STATUS=$?
            echo ""
            echo "════════════════════════════════════════════════════════════════════"
            if [ $STATUS -eq 0 ]; then
                echo "✓ Demo completed successfully"
            else
                echo "⚠️  Demo exited with code: $STATUS"
            fi
            echo ""
            echo "Press any key to return to menu..."
            read -n 1 -s
            echo ""
            ;;
        7)
            echo "🚀 Launching Superset Quickstart..."
            echo "════════════════════════════════════════════════════════════════════"
            echo ""
            $PYTHON_CMD superset-dashboards/quickstart_superset.py
            STATUS=$?
            echo ""
            echo "════════════════════════════════════════════════════════════════════"
            if [ $STATUS -eq 0 ]; then
                echo "✓ Superset setup completed successfully"
            else
                echo "⚠️  Superset setup exited with code: $STATUS"
            fi
            echo ""
            echo "Press any key to return to menu..."
            read -n 1 -s
            echo ""
            ;;
        8)
            echo "📚 Opening documentation..."
            if command -v open &> /dev/null; then
                open "https://github.com/doronpers/feedback-loop"
            else
                echo "Visit: https://github.com/doronpers/feedback-loop"
            fi
            echo ""
            echo "Press any key to return to menu..."
            read -n 1 -s
            echo ""
            ;;
        9)
            echo "👋 Goodbye!"
            echo ""
            exit 0
            ;;
        *)
            echo "❌ Invalid choice. Please enter a number between 1 and 9."
            echo ""
            echo "Press any key to continue..."
            read -n 1 -s
            echo ""
            ;;
    esac
done
