# Feedback Loop VS Code Extension (POC)

This is a proof-of-concept VS Code extension that integrates the Feedback Loop Language Server.

## Quick Start

### 1. Install Dependencies

```bash
# Install pygls for the language server
pip install pygls

# Install Node.js dependencies (if building full extension)
npm install
```

### 2. Test the Language Server

```bash
# Start the language server manually
python ../../feedback_loop_lsp.py
```

### 3. Configure VS Code

Add to your `settings.json`:

```json
{
  "feedback-loop.enable": true,
  "feedback-loop.serverPath": "/path/to/feedback_loop_lsp.py"
}
```

### 4. Try It Out

Open any Python file and you should see:
- ⚠️ Warnings for bare `except:` clauses
- 💡 Hints for `print()` statements
- 🔍 Suggestions for list access without bounds checking

## Building the Full Extension

### Setup

```bash
cd vscode-extension
npm install
```

### Package Structure

```
vscode-extension/
├── package.json          # Extension manifest
├── src/
│   └── extension.ts      # Extension entry point
├── client/
│   └── client.ts         # LSP client
└── README.md            # This file
```

### Development

```bash
# Compile TypeScript
npm run compile

# Watch for changes
npm run watch

# Run in extension development host
# Press F5 in VS Code
```

### Publishing

```bash
# Package extension
vsce package

# Publish to marketplace
vsce publish
```

## Features

### Current (POC)

- ✅ Real-time pattern detection
- ✅ Diagnostics (warnings/errors)
- ✅ Quick fixes for common issues
- ✅ Works with Python files

### Planned

- [ ] Hover documentation
- [ ] Code completion with patterns
- [ ] Chat panel integration
- [ ] Pattern explorer sidebar
- [ ] Metrics dashboard
- [ ] LLM-powered suggestions

## Configuration

Available settings:

```json
{
  // Enable/disable the extension
  "feedback-loop.enable": true,
  
  // Path to the language server
  "feedback-loop.serverPath": "python",
  
  // Server arguments
  "feedback-loop.serverArgs": ["-m", "feedback_loop_lsp"],
  
  // LLM provider (claude, openai, gemini)
  "feedback-loop.llmProvider": "claude",
  
  // Enable LLM features
  "feedback-loop.enableLLM": true,
  
  // Analysis delay (milliseconds)
  "feedback-loop.analysisDelay": 500
}
```

## Troubleshooting

### Language server not starting

1. Check Python is installed: `python --version`
2. Check pygls is installed: `pip list | grep pygls`
3. Check server path in settings
4. View output panel: "Feedback Loop Language Server"

### No diagnostics showing

1. Ensure extension is enabled
2. Check file is recognized as Python
3. Try reloading window (Cmd+R / Ctrl+R)
4. Check for errors in Output panel

### Performance issues

1. Increase analysis delay in settings
2. Disable LLM features temporarily
3. Check CPU usage
4. Report issue on GitHub

## Support

- GitHub: https://github.com/doronpers/feedback-loop
- Issues: https://github.com/doronpers/feedback-loop/issues
- Docs: https://github.com/doronpers/feedback-loop/docs

## License

MIT
