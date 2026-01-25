# Desktop Launcher Scripts

This directory contains launcher scripts that can be double-clicked from your desktop to easily run Feedback Loop tools.

## 🤖 Automatic Updates

The launcher scripts are **automatically maintained** through:

1. **GitHub Actions Workflow**: Whenever changes are made to bin scripts, demos, or requirements, the launchers are automatically checked and updated if needed
2. **Manual Update Script**: Run `python scripts/update_launchers.py` to manually regenerate the launchers
3. **Auto-detection**: The update script automatically discovers all tools in `bin/` and demo scripts

This ensures the launchers always include the latest tools without manual editing!

## 📁 Available Launchers

### For Mac (macOS)

**File:** `launch-feedback-loop.command`

### For Windows (PC)

**File:** `launch-feedback-loop.bat`

## 🚀 How to Use

### On Mac

1. **Copy to Desktop (Optional)**

   ```bash
   cp launch-feedback-loop.command ~/Desktop/
   ```

2. **Double-click** the `.command` file from Finder
   - The file should open in Terminal and display a menu
   - If you get a security warning, right-click → "Open" → "Open anyway"

3. **Select a tool** from the interactive menu:
   - Chat Assistant - Interactive AI-powered coding help
   - Setup Wizard - Configure feedback-loop for your project
   - Dashboard - View metrics and patterns
   - Doctor - Diagnose and fix issues
   - Demo - See patterns in action

### On Windows (PC)

1. **Copy to Desktop (Optional)**
   - Right-click `launch-feedback-loop.bat` → "Copy"
   - Right-click on Desktop → "Paste"

2. **Double-click** the `.bat` file from Explorer
   - A command window will open with a menu

3. **Select a tool** from the interactive menu (same options as Mac)

## 📋 Requirements

Both launchers will:

- ✅ Check if Python 3.13+ is installed
- ✅ Offer to install feedback-loop if not already installed
- ✅ Display the current directory
- ✅ Keep the window open after each tool finishes
- ✅ Allow you to run multiple tools without reopening

### Python Installation

If Python is not installed:

**Mac:**

```bash
# Using Homebrew
brew install python3

# Or download from
https://www.python.org/downloads/
```

**Windows:**

- Download from: <https://www.python.org/downloads/>
- ⚠️ **Important:** Check "Add Python to PATH" during installation

## 🎯 Quick Start

After copying to your desktop:

**Mac:** Double-click `launch-feedback-loop.command`
**Windows:** Double-click `launch-feedback-loop.bat`

The launcher will:

1. Check your Python installation
2. Verify feedback-loop is installed (or offer to install it)
3. Present an interactive menu
4. Launch your selected tool
5. Return to the menu when done

## 🔧 Troubleshooting

### "Permission denied" on Mac

```bash
chmod +x launch-feedback-loop.command
```

### "Python not found" error

- Make sure Python 3.13+ is installed
- Verify it's in your PATH:
  - Mac: `python3 --version`
  - Windows: `python --version`

### "Cannot open" security warning on Mac

- Right-click the file → "Open"
- Click "Open" in the security dialog
- Future launches will work with double-click

### Scripts don't launch tools correctly

- Make sure you're running the script from the feedback-loop directory
- Or ensure feedback-loop is installed globally: `pip install -e .`

## 📚 What Each Tool Does

| Tool | Description |
|------|-------------|
| **Chat Assistant** | Interactive AI chat for coding questions and pattern guidance |
| **Setup Wizard** | Guided setup for integrating feedback-loop into your project |
| **Dashboard** | Visual display of collected metrics and learned patterns |
| **Doctor** | Diagnostic tool to check your environment and fix common issues |
| **Demo** | Demonstration of good coding patterns in action |

## 💡 Tips

- **Keep the launcher scripts in the feedback-loop directory** - They reference files relative to their location
- **Create shortcuts** instead of moving the files to maintain the correct paths
- **Add to dock/taskbar** for even faster access
- The launchers work from any location if feedback-loop is installed globally
- **Launchers auto-update** - When new tools are added, run `python scripts/update_launchers.py` or wait for the automated workflow

## 🔄 Maintaining the Launchers

The launcher scripts are auto-generated from `/scripts/update_launchers.py`. When you add new tools:

```bash
# Check if launchers need updating
python scripts/update_launchers.py --check-only

# Update launchers
python scripts/update_launchers.py
```

The GitHub Actions workflow (`.github/workflows/update-launchers.yml`) automatically runs this script when:

- New scripts are added to `bin/`
- Demo files change
- Requirements or setup files change

## 📖 More Information

For detailed documentation, visit:
<https://github.com/doronpers/feedback-loop>

Or select option 6 from the launcher menu to open the documentation in your browser.
