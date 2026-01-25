# Agent Reasoning Log Discoverability Improvements

## Summary

This document outlines improvements made to increase the likelihood that coding agents will find and follow the reasoning log requirement.

## Changes Made

### 1. ✅ Updated `.cursorrules` Files

**Updated Repos:**
- `sono-eval/.cursorrules` - Added reasoning log as Quick Rule #6
- `council-ai/.cursorrules` - Moved reasoning log to Quick Rule #5 (more prominent)

**Change Pattern:**
- Moved from "Core Principles" (bottom) to "Quick Rules" (top)
- Added explicit file path and template location
- Made it a numbered rule with action verb

### 2. ✅ Created Task Completion Checklist

**File**: `TASK_COMPLETION_CHECKLIST.md`

Provides:
- Clear criteria for when to create logs
- Step-by-step instructions
- Quick command examples
- File naming conventions

### 3. ✅ Created Improvement Plan

**File**: `IMPROVEMENT_PLAN.md`

Documents:
- Current state analysis
- Improvement strategy
- Implementation priorities
- Success metrics

## Recommendations for Maximum Discoverability

### High Priority (Do Now)

1. **Update All `.cursorrules` Files**
   ```bash
   # Add to Quick Rules section in each repo:
   5. **Reasoning Logs**: After significant tasks (complex, architectural, refactoring, non-obvious bug fixes), create log entry at `feedback-loop/agent_reasoning_logs/logs/YYYY-MM-DD_<repo>_task.md`
   ```

2. **Add to Pre-Task Workflows**
   - If `.agent/workflows/pre-task.md` exists, add reminder
   - Example: "For significant tasks, remember to create reasoning log"

3. **Add to AGENT_KNOWLEDGE_BASE.md**
   - Move reasoning log section higher (currently section 8)
   - Add to "Before Starting" checklist
   - Include in "Task Completion" section

### Medium Priority (Do Soon)

4. **Create Agent Reminder System**
   - Add reminder when agent completes complex task
   - Trigger on keywords: "architectural", "refactor", "complex", "bug fix"

5. **Add to Code Review Templates**
   - Include reasoning log check in PR templates
   - Ask: "Was a reasoning log created for this change?"

6. **Create Quick Reference Card**
   - One-page cheat sheet for agents
   - Include: when to log, where to log, template location

### Low Priority (Nice to Have)

7. **Automated Reminders**
   - Pre-commit hook that checks for reasoning log
   - CI check for significant changes

8. **Agent Dashboard**
   - Visual dashboard showing reasoning log coverage
   - Track which repos/tasks have logs

## Template for Updating Other Repos

Add this to each repo's `.cursorrules` in the "Quick Rules" section:

```markdown
5. **Reasoning Logs**: After significant tasks (complex, architectural, refactoring, non-obvious bug fixes), create log entry at `feedback-loop/agent_reasoning_logs/logs/YYYY-MM-DD_<repo-name>_task.md` (see template: `feedback-loop/agent_reasoning_logs/templates/reasoning_entry.md`)
```

## Key Success Factors

1. **Prominence**: Move from "Core Principles" to "Quick Rules" (top of file)
2. **Specificity**: Include exact file path and template location
3. **Actionability**: Use action verb ("create log entry") not passive ("log decisions")
4. **Context**: Explain when to create logs (with examples)
5. **Reminders**: Add to task completion checklists

## Testing the Improvements

To verify agents are finding the requirement:

1. **Monitor Log Creation**: Check `agent_reasoning_logs/logs/` for new entries
2. **Ask Agents Directly**: "Did you create a reasoning log for this task?"
3. **Review Task Completions**: Check if agents mention reasoning logs in completion messages

## Next Steps

1. [ ] Update remaining `.cursorrules` files (sono-platform, feedback-loop, etc.)
2. [ ] Update `AGENT_KNOWLEDGE_BASE.md` files to move reasoning log section higher
3. [ ] Add to pre-task workflows where they exist
4. [ ] Create quick reference card
5. [ ] Monitor log creation rate over next 2 weeks

---

Last Updated: 2026-01-20
Created by: Claude (Cursor)
