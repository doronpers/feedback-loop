# Reasoning Log Requirement - Update Summary

**Date**: 2026-01-20
**Task**: Update all `.cursorrules` files to include prominent reasoning log requirement

## Files Updated

### ✅ Completed Updates

1. **sono-eval/.cursorrules**
   - Added as Quick Rule #6
   - File path: `feedback-loop/agent_reasoning_logs/logs/YYYY-MM-DD_sono-eval_task.md`

2. **council-ai/.cursorrules**
   - Added as Quick Rule #5 (moved from Core Principles)
   - File path: `feedback-loop/agent_reasoning_logs/logs/YYYY-MM-DD_council-ai_task.md`

3. **sono-platform/.cursorrules**
   - Added as Quick Rule #6
   - File path: `feedback-loop/agent_reasoning_logs/logs/YYYY-MM-DD_sono-platform_task.md`

4. **council-ai-personal/.cursorrules**
   - Added as Quick Rule #5
   - Updated Core Principles to reference Quick Rule #5
   - File path: `feedback-loop/agent_reasoning_logs/logs/YYYY-MM-DD_council-ai-personal_task.md`

5. **sonotheia-examples/.cursorrules**
   - Added as Quick Rule #5
   - File path: `feedback-loop/agent_reasoning_logs/logs/YYYY-MM-DD_sonotheia-examples_task.md`

6. **Website-Sonotheia-v251120/.cursorrules**
   - Added as Quick Rule #5
   - File path: `feedback-loop/agent_reasoning_logs/logs/YYYY-MM-DD_Website-Sonotheia-v251120_task.md`

7. **spatial-selecta/.cursorrules**
   - Added as Quick Rule #5
   - File path: `feedback-loop/agent_reasoning_logs/logs/YYYY-MM-DD_spatial-selecta_task.md`

8. **drrweb/.cursorrules**
   - Added as Quick Rule #5
   - File path: `feedback-loop/agent_reasoning_logs/logs/YYYY-MM-DD_drrweb_task.md`

9. **feedback-loop/.cursorrules**
   - Added new "Reasoning Logs" section before "Final Notes"
   - File path: `agent_reasoning_logs/logs/YYYY-MM-DD_feedback-loop_task.md` (relative path since it's in the same repo)

## Standard Format Added

All repos now include this format in their Quick Rules section:

```markdown
5. **Reasoning Logs**: After significant tasks (complex, architectural, refactoring, non-obvious bug fixes), create log entry at `feedback-loop/agent_reasoning_logs/logs/YYYY-MM-DD_<repo-name>_task.md` (see template: `feedback-loop/agent_reasoning_logs/templates/reasoning_entry.md`)
```

## Key Improvements

1. **Prominence**: Moved from "Core Principles" (bottom) to "Quick Rules" (top)
2. **Specificity**: Includes exact file path and template location
3. **Actionability**: Uses action verb ("create log entry") not passive language
4. **Context**: Explains when to create logs with examples
5. **Consistency**: Same format across all repos

## Files Not Updated

The following `.cursorrules` files are minimal/agent-specific and don't follow the standard format:

- `sono-platform/modes/sonotheia/.cursorrules` - Minimal agent instructions
- `sono-platform/modes/xlayer/.cursorrules` - Minimal agent instructions

These can be updated later if needed, but they reference `AGENT_KNOWLEDGE_BASE.md` which should contain the requirement.

## Next Steps

1. ✅ All major repos updated
2. ⏳ Monitor reasoning log creation rate
3. ⏳ Consider adding to `AGENT_KNOWLEDGE_BASE.md` files (move section higher)
4. ⏳ Add to pre-task workflows where they exist
5. ⏳ Create quick reference card for agents

## Verification

To verify an update, check that:

- Reasoning log requirement appears in "Quick Rules" section
- File path includes correct repo name
- Template path is included
- Context about when to create logs is provided

---

**Status**: ✅ Complete - All major repos updated with prominent reasoning log requirement
