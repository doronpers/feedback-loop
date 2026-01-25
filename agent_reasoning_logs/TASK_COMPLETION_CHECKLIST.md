# Task Completion Checklist for Agents

Before reporting a task as complete, verify the following:

## Code Quality
- [ ] Code formatted (`black`, `ruff`, etc.)
- [ ] Linting passes
- [ ] Tests pass (if applicable)
- [ ] No breaking changes introduced (or documented if unavoidable)

## Reasoning Log (Required for Significant Tasks)

**When to create a reasoning log:**
- ✅ Complex problem-solving tasks
- ✅ Architectural decisions
- ✅ Bug fixes with non-obvious solutions
- ✅ Refactoring work
- ✅ Any task with valuable lessons learned
- ❌ Simple formatting or typo fixes
- ❌ Routine dependency updates

**If your task qualifies, create a log entry:**

- [ ] **Location**: `feedback-loop/agent_reasoning_logs/logs/YYYY-MM-DD_<repo-name>_<brief-task>.md`
- [ ] **Template**: Use `feedback-loop/agent_reasoning_logs/templates/reasoning_entry.md`
- [ ] **Include**: Context, approach, key decisions, challenges, lessons learned, Hippocratic check

**Quick Command:**
```bash
# Navigate to feedback-loop repo
cd /path/to/feedback-loop

# Copy template
cp agent_reasoning_logs/templates/reasoning_entry.md \
   agent_reasoning_logs/logs/$(date +%Y-%m-%d)_<repo>_<task>.md

# Edit the file with your reasoning
```

## Example File Names
- `2026-01-20_sono-eval_automatic-port-detection.md`
- `2026-01-20_council-ai_documentation-consolidation.md`
- `2026-01-20_feedback-loop_bug-fix.md`

---

**Remember**: Reasoning logs help future agents understand past decisions and build institutional knowledge.
