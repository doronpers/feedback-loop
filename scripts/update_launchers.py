#!/usr/bin/env python3
"""
Auto-update script for desktop launchers.

This script regenerates the desktop launcher scripts (Mac .command and Windows .bat)
based on the current bin/ scripts and demo files available in the repository.

Usage:
    python scripts/update_launchers.py [--check-only]

Options:
    --check-only    Only check if updates are needed, don't modify files
"""

import argparse
import os
import sys
from pathlib import Path
from typing import List, Dict, Tuple


def find_tools() -> List[Dict[str, str]]:
    """Find all available tools in bin/ directory."""
    tools = []
    bin_dir = Path("bin")
    
    if not bin_dir.exists():
        return tools
    
    for script in sorted(bin_dir.glob("fl-*")):
        if script.is_file() and os.access(script, os.X_OK):
            # Read first few lines to get description
            try:
                with open(script, 'r') as f:
                    lines = f.readlines()
                    description = "Tool"
                    for idx, line in enumerate(lines[:10]):
                        if '"""' in line or "'''" in line:
                            # Found docstring, try to extract description
                            for next_line in lines[idx+1:idx+5]:
                                if next_line.strip() and not next_line.strip().startswith('"""'):
                                    description = next_line.strip()
                                    break
                            break
                    
                    tools.append({
                        "name": script.stem.replace("fl-", "").replace("-", " ").title(),
                        "script": str(script),
                        "description": description
                    })
            except Exception as e:
                print(f"Warning: Could not read {script}: {e}", file=sys.stderr)
    
    return tools


def find_demos() -> List[str]:
    """Find all demo scripts."""
    demos = []
    for demo in sorted(Path(".").glob("demo*.py")):
        if demo.is_file():
            demos.append(str(demo))
    return demos


def generate_mac_launcher(tools: List[Dict[str, str]], demos: List[str]) -> str:
    """Generate Mac launcher script content."""
    
    # Build menu items
    menu_items = []
    case_items = []
    
    # Map of known tools to their emoji and description
    tool_map = {
        "Chat": ("💬", "Interactive AI-powered chat for coding help"),
        "Setup": ("⚙️", "Configure feedback-loop for your project"),
        "Dashboard": ("📊", "View metrics and pattern insights"),
        "Doctor": ("🩺", "Diagnose and fix common issues"),
    }
    
    item_num = 1
    for tool in tools:
        tool_key = tool["name"].split()[0]  # Get first word
        emoji, desc = tool_map.get(tool_key, ("🔧", tool.get("description", "Tool")))
        
        menu_items.append(f'    echo "  {item_num}) {emoji} {tool["name"]:<15} - {desc}"')
        
        case_items.append(f"""        {item_num})
            echo "🚀 Launching {tool['name']}..."
            echo "════════════════════════════════════════════════════════════════════"
            echo ""
            python3 {tool['script']}
            STATUS=$?
            echo ""
            echo "════════════════════════════════════════════════════════════════════"
            if [ $STATUS -eq 0 ]; then
                echo "✓ {tool['name']} exited successfully"
            else
                echo "⚠️  {tool['name']} exited with code: $STATUS"
            fi
            echo ""
            echo "Press any key to return to menu..."
            read -n 1 -s
            echo ""
            ;;""")
        item_num += 1
    
    # Add demo if available
    if demos:
        menu_items.append(f'    echo "  {item_num}) 🎬 Demo              - See patterns in action"')
        case_items.append(f"""        {item_num})
            echo "🚀 Running Demo..."
            echo "════════════════════════════════════════════════════════════════════"
            echo ""
            python3 {demos[0]}
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
            ;;""")
        item_num += 1
    
    # Add docs and exit
    menu_items.append(f'    echo "  {item_num}) 📚 Open Documentation"')
    docs_num = item_num
    item_num += 1
    menu_items.append(f'    echo "  {item_num}) 🚪 Exit"')
    exit_num = item_num
    
    case_items.append(f"""        {docs_num})
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
            ;;""")
    
    case_items.append(f"""        {exit_num})
            echo "👋 Goodbye!"
            echo ""
            exit 0
            ;;""")
    
    case_items.append(f"""        *)
            echo "❌ Invalid choice. Please enter a number between 1 and {exit_num}."
            echo ""
            echo "Press any key to continue..."
            read -n 1 -s
            echo ""
            ;;""")
    
    menu_text = "\n".join(menu_items)
    case_text = "\n".join(case_items)
    
    return f'''#!/bin/bash
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
        python3 -m pip install -e . || {{
            echo ""
            echo "❌ Installation failed"
            echo "Press any key to exit..."
            read -n 1 -s
            exit 1
        }}
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
{menu_text}
    echo ""
    echo -n "Enter your choice (1-{exit_num}): "
    read -r choice
    echo ""

    case $choice in
{case_text}
    esac
done
'''


def generate_windows_launcher(tools: List[Dict[str, str]], demos: List[str]) -> str:
    """Generate Windows batch file content."""
    
    # Build menu items
    menu_items = []
    goto_checks = []
    sections = []
    
    # Map of known tools to their emoji and description
    tool_map = {
        "Chat": ("💬", "Interactive AI-powered chat for coding help"),
        "Setup": ("⚙️", "Configure feedback-loop for your project"),
        "Dashboard": ("📊", "View metrics and pattern insights"),
        "Doctor": ("🩺", "Diagnose and fix common issues"),
    }
    
    item_num = 1
    for tool in tools:
        tool_key = tool["name"].split()[0]
        emoji, desc = tool_map.get(tool_key, ("🔧", tool.get("description", "Tool")))
        label = tool_key.upper()
        
        menu_items.append(f'echo   {item_num}) {emoji} {tool["name"]:<15} - {desc}')
        goto_checks.append(f'if "%CHOICE%"=="{item_num}" goto {label}')
        
        script_path = tool['script'].replace('/', '\\')
        sections.append(f''':{label}
echo 🚀 Launching {tool['name']}...
echo ════════════════════════════════════════════════════════════════════
echo.
python {script_path}
set STATUS=%ERRORLEVEL%
echo.
echo ════════════════════════════════════════════════════════════════════
if %STATUS%==0 (
    echo ✓ {tool['name']} exited successfully
) else (
    echo ⚠️  {tool['name']} exited with code: %STATUS%
)
echo.
echo Press any key to return to menu...
pause >nul
echo.
goto START''')
        item_num += 1
    
    # Add demo
    if demos:
        menu_items.append(f'echo   {item_num}) 🎬 Demo              - See patterns in action')
        goto_checks.append(f'if "%CHOICE%"=="{item_num}" goto DEMO')
        sections.append(f''':DEMO
echo 🚀 Running Demo...
echo ════════════════════════════════════════════════════════════════════
echo.
python {demos[0]}
set STATUS=%ERRORLEVEL%
echo.
echo ════════════════════════════════════════════════════════════════════
if %STATUS%==0 (
    echo ✓ Demo completed successfully
) else (
    echo ⚠️  Demo exited with code: %STATUS%
)
echo.
echo Press any key to return to menu...
pause >nul
echo.
goto START''')
        item_num += 1
    
    # Add docs and exit
    menu_items.append(f'echo   {item_num}) 📚 Open Documentation')
    goto_checks.append(f'if "%CHOICE%"=="{item_num}" goto DOCS')
    docs_num = item_num
    item_num += 1
    
    menu_items.append(f'echo   {item_num}) 🚪 Exit')
    goto_checks.append(f'if "%CHOICE%"=="{item_num}" goto EXIT')
    exit_num = item_num
    
    sections.append(f''':DOCS
echo 📚 Opening documentation...
start https://github.com/doronpers/feedback-loop
echo.
echo Press any key to return to menu...
pause >nul
echo.
goto START''')
    
    menu_text = "\n".join(menu_items)
    goto_text = "\n".join(goto_checks)
    sections_text = "\n\n".join(sections)
    
    return f'''@echo off
REM ###########################################################################
REM Feedback Loop - Windows Desktop Launcher
REM ###########################################################################
REM This script can be double-clicked from Windows Explorer to launch feedback-loop
REM Usage: Double-click this file from your desktop or any folder
REM AUTO-GENERATED - Run scripts/update_launchers.py to regenerate
REM ###########################################################################

SETLOCAL EnableDelayedExpansion

REM Change to the directory where this script is located
cd /d "%~dp0"

REM Set console properties for better display
title Feedback Loop Launcher
color 0A

:START
cls
echo.
echo ╔════════════════════════════════════════════════════════════════════╗
echo ║                    Feedback Loop Launcher                         ║
echo ╚════════════════════════════════════════════════════════════════════╝
echo.
echo 📍 Current directory: %CD%
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Error: Python is not installed or not in PATH
    echo.
    echo Please install Python 3.8 or later:
    echo   • Download from: https://www.python.org/downloads/
    echo   • Make sure to check "Add Python to PATH" during installation
    echo.
    echo Press any key to exit...
    pause >nul
    exit /b 1
)

REM Display Python version
for /f "tokens=*" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo ✓ Found: !PYTHON_VERSION!
echo.

REM Check if feedback-loop is installed
python -c "import metrics" >nul 2>&1
if errorlevel 1 (
    echo ⚠️  Feedback Loop not installed in current environment
    echo.
    set /p RESPONSE="Would you like to install it now? (y/n): "
    if /i "!RESPONSE!"=="y" (
        echo.
        echo Installing feedback-loop...
        python -m pip install -e .
        if errorlevel 1 (
            echo.
            echo ❌ Installation failed
            echo Press any key to exit...
            pause >nul
            exit /b 1
        )
        echo.
        echo ✓ Installation complete!
        echo.
    ) else (
        echo.
        echo Cannot proceed without installation
        echo Press any key to exit...
        pause >nul
        exit /b 1
    )
)

:MENU
echo ════════════════════════════════════════════════════════════════════
echo Please select a tool to launch:
echo ════════════════════════════════════════════════════════════════════
echo.
{menu_text}
echo.
set /p CHOICE="Enter your choice (1-{exit_num}): "
echo.

{goto_text}
goto INVALID

{sections_text}

:INVALID
echo ❌ Invalid choice. Please enter a number between 1 and {exit_num}.
echo.
echo Press any key to continue...
pause >nul
echo.
goto START

:EXIT
echo.
echo 👋 Goodbye!
echo.
timeout /t 2 /nobreak >nul
exit /b 0
'''


def main():
    parser = argparse.ArgumentParser(description="Update desktop launcher scripts")
    parser.add_argument("--check-only", action="store_true",
                        help="Only check if updates are needed")
    args = parser.parse_args()
    
    # Find tools and demos
    tools = find_tools()
    demos = find_demos()
    
    print(f"Found {len(tools)} tools and {len(demos)} demos")
    for tool in tools:
        print(f"  - {tool['name']}: {tool['script']}")
    
    if not tools:
        print("Warning: No tools found in bin/ directory", file=sys.stderr)
        return 1
    
    # Generate launchers
    mac_content = generate_mac_launcher(tools, demos)
    win_content = generate_windows_launcher(tools, demos)
    
    # Check if updates are needed
    mac_file = Path("launch-feedback-loop.command")
    win_file = Path("launch-feedback-loop.bat")
    
    needs_update = False
    
    if not mac_file.exists() or mac_file.read_text() != mac_content:
        print("Mac launcher needs update")
        needs_update = True
    
    if not win_file.exists() or win_file.read_text() != win_content:
        print("Windows launcher needs update")
        needs_update = True
    
    if not needs_update:
        print("✓ Launchers are up to date")
        return 0
    
    if args.check_only:
        print("Updates needed (use without --check-only to apply)")
        return 1
    
    # Write updated files
    print("Updating launchers...")
    
    mac_file.write_text(mac_content)
    mac_file.chmod(0o755)
    print(f"✓ Updated {mac_file}")
    
    win_file.write_text(win_content)
    print(f"✓ Updated {win_file}")
    
    print("✓ Launcher scripts updated successfully")
    return 0


if __name__ == "__main__":
    sys.exit(main())
