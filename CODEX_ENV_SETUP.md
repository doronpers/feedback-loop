# Codex Environment Setup for feedback-loop

Complete configuration guide for setting up a Codex development environment for `feedback-loop`.

## Quick Configuration

### 1. Name & Description
- **Name**: `feedback-loop / dev + tests`
- **Description**: `Full feedback-loop dev env with dependencies, pytest, linting, FastAPI, and API access.`

### 2. Container Image & Workspace
- **Container image**: `universal`
- **Workspace directory**: `/workspace/feedback-loop` (default)

### 3. Setup Script & Caching
- **Setup script (Manual)**: `/workspace/feedback-loop/scripts/codex-setup.sh`
- **Container Caching**: `On`
- **Maintenance script**: `pip install -e ".[dev]"`

### 4. Environment Variables
```
FEEDBACK_LOOP_ENV=codex
FEEDBACK_LOOP_LOG_LEVEL=INFO
PYTHONUNBUFFERED=1
PYTHONUTF8=1
```

### 5. Secrets (API Keys)
- `OPENAI_API_KEY` - For OpenAI models
- `ANTHROPIC_API_KEY` - For Anthropic models
- `GEMINI_API_KEY` - For Google Gemini models

### 6. Agent Internet Access
- **Agent internet access**: `On`
- **Domain allowlist**: Start with `Common dependencies`, then add:
  - `api.openai.com`
  - `api.anthropic.com`
  - `generativelanguage.googleapis.com`
  - `pypi.org`
  - `files.pythonhosted.org`
  - `github.com`
  - `raw.githubusercontent.com`
- **Allowed HTTP Methods**: `All methods`

## Special Considerations

### Python 3.13 Requirement
- feedback-loop requires Python 3.13+
- Codex universal image should provide this

### Database Testing
- Many roadmap items involve database work (PostgreSQL)
- Consider using SQLite for testing or mock database connections
