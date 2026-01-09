# Scripts Directory

Utility scripts for maintaining the feedback-loop repository.

## update_launchers.py

Auto-generates the desktop launcher scripts for Mac and Windows.

### Usage

```bash
# Check if launchers need updating (doesn't modify files)
python scripts/update_launchers.py --check-only

# Update launchers
python scripts/update_launchers.py
```

### What it does

1. **Auto-discovers tools**: Scans `bin/` directory for all `fl-*` scripts
2. **Finds demos**: Looks for `demo*.py` files
3. **Generates launchers**: Creates both `.command` (Mac) and `.bat` (Windows) files
4. **Preserves formatting**: Maintains proper syntax and executable permissions

### When to run

- After adding new tools to `bin/`
- After adding new demo scripts
- When launcher functionality needs updating
- The GitHub Actions workflow runs this automatically

### How it works

The script:
1. Scans for executable scripts in `bin/fl-*`
2. Extracts tool names and descriptions from docstrings
3. Generates interactive menu with all discovered tools
4. Creates both Mac (.command) and Windows (.bat) versions
5. Sets proper file permissions (executable for Mac)

## Automation

These scripts are integrated with GitHub Actions:

- **`.github/workflows/update-launchers.yml`**: Automatically checks and updates launchers when relevant files change
- Creates a PR with updates when needed
- Validates syntax and functionality
- Only triggers on changes to bin/, demos, or requirements
