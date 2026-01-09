@echo off
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
echo   1) 💬 Chat       - Interactive AI-powered chat for coding help
echo   2) 📊 Dashboard  - View metrics and pattern insights
echo   3) 🩺 Doctor     - Diagnose and fix common issues
echo   4) ⚙️ Setup      - Configure feedback-loop for your project
echo   5) 🔧 Synthesize - Interactive Code Synthesizer
echo   6) 🎬 Demo              - See patterns in action
echo   7) 📊 Superset Setup   - Set up analytics dashboards
echo   8) 📚 Open Documentation
echo   9) 🚪 Exit
echo.
set /p CHOICE="Enter your choice (1-9): "
echo.

if "%CHOICE%"=="1" goto CHAT
if "%CHOICE%"=="2" goto DASHBOARD
if "%CHOICE%"=="3" goto DOCTOR
if "%CHOICE%"=="4" goto SETUP
if "%CHOICE%"=="5" goto SYNTHESIZE
if "%CHOICE%"=="6" goto DEMO
if "%CHOICE%"=="7" goto SUPERSET
if "%CHOICE%"=="8" goto DOCS
if "%CHOICE%"=="9" goto EXIT
goto INVALID

:CHAT
echo 🚀 Launching Chat...
echo ════════════════════════════════════════════════════════════════════
echo.
python bin\fl-chat
set STATUS=%ERRORLEVEL%
echo.
echo ════════════════════════════════════════════════════════════════════
if %STATUS%==0 (
    echo ✓ Chat exited successfully
) else (
    echo ⚠️  Chat exited with code: %STATUS%
)
echo.
echo Press any key to return to menu...
pause >nul
echo.
goto START

:DASHBOARD
echo 🚀 Launching Dashboard...
echo ════════════════════════════════════════════════════════════════════
echo.
python bin\fl-dashboard
set STATUS=%ERRORLEVEL%
echo.
echo ════════════════════════════════════════════════════════════════════
if %STATUS%==0 (
    echo ✓ Dashboard exited successfully
) else (
    echo ⚠️  Dashboard exited with code: %STATUS%
)
echo.
echo Press any key to return to menu...
pause >nul
echo.
goto START

:DOCTOR
echo 🚀 Launching Doctor...
echo ════════════════════════════════════════════════════════════════════
echo.
python bin\fl-doctor
set STATUS=%ERRORLEVEL%
echo.
echo ════════════════════════════════════════════════════════════════════
if %STATUS%==0 (
    echo ✓ Doctor exited successfully
) else (
    echo ⚠️  Doctor exited with code: %STATUS%
)
echo.
echo Press any key to return to menu...
pause >nul
echo.
goto START

:SETUP
echo 🚀 Launching Setup...
echo ════════════════════════════════════════════════════════════════════
echo.
python bin\fl-setup
set STATUS=%ERRORLEVEL%
echo.
echo ════════════════════════════════════════════════════════════════════
if %STATUS%==0 (
    echo ✓ Setup exited successfully
) else (
    echo ⚠️  Setup exited with code: %STATUS%
)
echo.
echo Press any key to return to menu...
pause >nul
echo.
goto START

:SYNTHESIZE
echo 🚀 Launching Synthesize...
echo ════════════════════════════════════════════════════════════════════
echo.
python bin\fl-synthesize
set STATUS=%ERRORLEVEL%
echo.
echo ════════════════════════════════════════════════════════════════════
if %STATUS%==0 (
    echo ✓ Synthesize exited successfully
) else (
    echo ⚠️  Synthesize exited with code: %STATUS%
)
echo.
echo Press any key to return to menu...
pause >nul
echo.
goto START

:DEMO
echo 🚀 Running Demo...
echo ════════════════════════════════════════════════════════════════════
echo.
python demo.py
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
goto START

:SUPERSET
echo 🚀 Launching Superset Quickstart...
echo ════════════════════════════════════════════════════════════════════
echo.
python superset-dashboards\quickstart_superset.py
set STATUS=%ERRORLEVEL%
echo.
echo ════════════════════════════════════════════════════════════════════
if %STATUS%==0 (
    echo ✓ Superset setup completed successfully
) else (
    echo ⚠️  Superset setup exited with code: %STATUS%
)
echo.
echo Press any key to return to menu...
pause >nul
echo.
goto START

:DOCS
echo 📚 Opening documentation...
start https://github.com/doronpers/feedback-loop
echo.
echo Press any key to return to menu...
pause >nul
echo.
goto START

:INVALID
echo ❌ Invalid choice. Please enter a number between 1 and 9.
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
