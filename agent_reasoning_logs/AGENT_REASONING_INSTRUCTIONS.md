# Agent Reasoning Log Instructions

This document provides portable instructions for adding reasoning log requirements to any repository's agent knowledge base.

## Quick Setup for New Repositories

Add the following sections to your repository's agent instruction files (`AGENT_KNOWLEDGE_BASE.md`, `.cursorrules`, `GEMINI.md`, etc.):

---

## Section 1: Hippocratic Principle

```markdown
## Hippocratic Principle: "First, Do No Harm"

> *"To do good or to do no harm"* — Hippocratic tradition

Before making ANY change, verify it follows this principle:

1. **Avoid Deleterious Changes**: Do not introduce changes that harm functionality, security, or maintainability.
2. **Preserve Working Systems**: If code works correctly, changes must maintain or improve its behavior.
3. **Minimize Side Effects**: Consider downstream impacts before modifying shared code.
4. **Document Breaking Changes**: If a breaking change is unavoidable, document it clearly with migration paths.
5. **Err on the Side of Caution**: When uncertain, ask for clarification rather than making assumptions.

**Checklist before committing**:
- [ ] Does this change preserve existing functionality?
- [ ] Are there any unintended side effects?
- [ ] Have I tested affected code paths?
- [ ] Is backward compatibility maintained (or documented if not)?
```

---

## Section 2: Reasoning Log Requirement

```markdown
## Reasoning Logs

After completing significant tasks, document your reasoning in the feedback-loop repository.

**Location**: `feedback-loop/agent_reasoning_logs/logs/`

**When to Log**:
- Complex problem-solving tasks
- Architectural decisions
- Bug fixes with non-obvious solutions
- Refactoring work
- Any task with valuable lessons learned

**Template**: Use `feedback-loop/agent_reasoning_logs/templates/reasoning_entry.md`

**File Naming**: `YYYY-MM-DD_<repo-name>_<brief-task>.md`

**Example**: `2026-01-16_council-ai_documentation-consolidation.md`
```

---

## Minimal Version (for `.cursorrules` or `GEMINI.md`)

```markdown
## Core Principles

1. **Hippocratic**: "First, do no harm" — preserve functionality, avoid breaking changes
2. **Document Reasoning**: Log significant decisions to `feedback-loop/agent_reasoning_logs/logs/`
```

---

## Notes

- The `agent_reasoning_logs/` folder lives in the **feedback-loop** repository
- Logs become part of the feedback-loop pattern library ecosystem
- Use the template at `templates/reasoning_entry.md` for consistent formatting

---

Last Updated: 2026-01-16
