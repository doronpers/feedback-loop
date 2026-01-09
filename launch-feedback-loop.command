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

# Clear the screen for a clean start
clear

echo "╔════════════════════════════════════════════════════════════════════╗"
echo "║                    Feedback Loop Launcher                         ║"
echo "╚════════════════════════════════════════════════════════════════════╝"
echo ""
echo "📍 Current directory: $(pwd)"
echo ""

# Check if Python 3 is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Error: Python 3 is not installed or not in PATH"
    echo ""
    echo "Please install Python 3.8 or later:"
    echo "  • Download from: https://www.python.org/downloads/"
    echo "  • Or use Homebrew: brew install python3"
    echo ""
    echo "Press any key to exit..."
    read -n 1 -s
    exit 1
fi

# Display Python version
PYTHON_VERSION=$(python3 --version 2>&1)
echo "✓ Found: $PYTHON_VERSION"
echo ""

# Check if feedback-loop is installed
if ! python3 -c "import metrics" &> /dev/null; then
    echo "⚠️  Feedback Loop not installed in current environment"
    echo ""
    echo "Would you like to install it now? (y/n)"
    read -r response
    if [[ "$response" =~ ^[Yy]$ ]]; then
        echo ""
        echo "Installing feedback-loop..."
        python3 -m pip install -e . || {
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
    echo "  5) 🎬 Demo              - See patterns in action"
    echo "  6) 📚 Open Documentation"
    echo "  7) 🚪 Exit"
    echo ""
    echo -n "Enter your choice (1-7): "
    read -r choice
    echo ""

    case $choice in
        1)
            echo "🚀 Launching Chat..."
            echo "════════════════════════════════════════════════════════════════════"
            echo ""
            python3 bin/fl-chat
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
            python3 bin/fl-dashboard
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
            python3 bin/fl-doctor
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
            python3 bin/fl-setup
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
            echo "🚀 Running Demo..."
            echo "════════════════════════════════════════════════════════════════════"
            echo ""
            python3 demo.py
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
        6)
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
        7)
            echo "👋 Goodbye!"
            echo ""
            exit 0
            ;;
        *)
            echo "❌ Invalid choice. Please enter a number between 1 and 7."
            echo ""
            echo "Press any key to continue..."
            read -n 1 -s
            echo ""
            ;;
    esac
done
