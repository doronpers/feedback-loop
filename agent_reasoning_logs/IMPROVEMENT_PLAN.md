# Improving Agent Reasoning Log Discoverability

## Current State

The reasoning log requirement is:
- ✅ Mentioned in `.cursorrules` (line 38 in council-ai: "Document Reasoning: Log significant decisions...")
- ✅ Detailed in `AGENT_KNOWLEDGE_BASE.md` (section 8)
- ❌ Not consistently across all repos
- ❌ Not in task completion checklists
- ❌ Not in pre-task workflows
- ❌ Easy to miss (buried in "Core Principles" section)

## Improvement Strategy

### 1. **Make it Prominent in `.cursorrules`**
   - Move to "Quick Rules" section (top of file)
   - Add as a numbered rule with action verb
   - Include in task completion checklist

### 2. **Add to Task Completion Checklist**
   - Create explicit checklist item
   - Add reminder before "task complete" messages

### 3. **Integrate into Pre-Task Workflows**
   - Add to `.agent/workflows/pre-task.md` if it exists
   - Create reminder for significant tasks

### 4. **Add Contextual Triggers**
   - When agent completes complex task → reminder
   - When agent makes architectural decision → reminder
   - When agent refactors code → reminder

### 5. **Create Standard Template Snippet**
   - Quick copy-paste template for agents
   - Include file path and naming convention

## Implementation Priority

1. **High Priority**: Update `.cursorrules` in all repos
2. **High Priority**: Add to task completion reminders
3. **Medium Priority**: Create pre-task workflow integration
4. **Low Priority**: Add contextual triggers (requires more complex logic)

## Template for `.cursorrules` Update

```markdown
## Quick Rules

1. **Format**: Use `black` (line-length 100) and `ruff`
2. **Style**: `snake_case` for functions, `PascalCase` for classes
3. **Tests**: All new features require pytest tests
4. **Security**: NEVER log API keys or commit `.env` files
5. **Reasoning Logs**: After significant tasks, create log entry at `feedback-loop/agent_reasoning_logs/logs/YYYY-MM-DD_repo_task.md`
6. **Personas**: Don't modify built-in personas without approval
```

## Template for Task Completion Checklist

```markdown
## Before Reporting Task Complete

- [ ] Code formatted and linted
- [ ] Tests pass (if applicable)
- [ ] No breaking changes introduced
- [ ] **Reasoning log created** (if task was: complex, architectural, refactoring, or bug fix with non-obvious solution)
  - Location: `feedback-loop/agent_reasoning_logs/logs/`
  - Template: `feedback-loop/agent_reasoning_logs/templates/reasoning_entry.md`
```

## Success Metrics

- [ ] All repos have reasoning log requirement in `.cursorrules`
- [ ] Task completion checklists include reasoning log reminder
- [ ] Pre-task workflows mention reasoning logs for significant tasks
- [ ] Increase in reasoning log entries created

---

Last Updated: 2026-01-20
