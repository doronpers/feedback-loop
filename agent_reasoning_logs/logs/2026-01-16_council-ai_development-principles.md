# Reasoning Log: Council AI Development Principles

**Date**: 2026-01-16 (Migrated from LLM_COGNITION_NOTES.md)  
**Repository**: council-ai  
**Agent**: Various (Historical)  
**Task Duration**: Ongoing  
**Difficulty**: 3 ⭐ (moderate - architectural insights)

---

## Context

This document captures the thinking process, design decisions, and architectural insights encountered during the development of Council AI. It serves as a reference for understanding "how" and "why" certain choices were made.

## Approach

### Principles of Interaction

1. **Systematic Problem Solving**: When faced with multiple failures (like pre-commit blocks), prioritize by "ease of fix" vs "impact." Start with low-hanging fruit (docstrings, unused imports) to clear the "noise" and then tackle complex logic or type errors.

2. **Iterative Refinement**: Don't aim for perfection in the first pass if the problem is multifaceted. Apply a batch of fixes, re-run the validation, and narrow down the remaining issues.

3. **Proactive Maintenance**: If a script is becoming unwieldy or non-standard, refactor it early to prevent technical debt.

## Key Decisions

- **Decision 1**: Use "ease of fix" prioritization for multi-failure scenarios
  - *Rationale*: Clearing noise first makes complex issues easier to identify and resolve

- **Decision 2**: Iterative refinement over one-shot perfection
  - *Rationale*: Complex problems reveal themselves through iteration; early attempts inform later solutions

## Challenges & Solutions

| Challenge                                    | Solution                                                        | Outcome                        |
| -------------------------------------------- | --------------------------------------------------------------- | ------------------------------ |
| `detect-secrets` extremely slow              | Added `exclude` patterns for `.mypy_cache`, `.venv`, etc.       | Pre-commit hook restored       |
| SQLAlchemy vs Mypy type issues               | Use `class Base(DeclarativeBase)` (SQLAlchemy 2.0 style)        | Better type inference          |
| Async iterators in abstract methods          | Change `async def` to regular `def` returning `AsyncIterator`   | Correct type matching          |
| `replace_file_content` syntax errors         | Re-read file around error line to verify indentation/quotes     | Reduced replacement errors     |
| YAML multi-document issues in K8s files      | Add `--allow-multiple-documents` flag to `check-yaml` hook      | CI passes for K8s manifests    |

## Lessons Learned

- **Syntax Errors in Replacements**: When using `replace_file_content` on large f-strings, it's easy to accidentally miss a closing quote or introduce a mismatch if the target content isn't perfectly matched. **Action**: Re-read the file around the error line to ensure indentation and string termination are intact.

- **YAML Multi-document**: K8s files often have multiple documents. Standard `check-yaml` hooks need the `--allow-multiple-documents` flag to avoid failing on these files.

- **Meta-Thinking**: When the user asks for "thinking notes," interpret this as a desire for a "Developer Journal" or "Design Doc." Aim to provide context that isn't always obvious from the code diffs alone.

## Hippocratic Check

> "First, do no harm" — Before committing, verify:

- [x] No breaking changes introduced
- [x] Backward compatibility maintained
- [x] Error handling preserved or improved
- [x] Tests pass (if applicable)
- [x] Security not compromised

## Notes for Future Reference

This was the original "LLM Cognition Notes" document that served as the inspiration for the centralized reasoning log system. Future agents should use the template at `templates/reasoning_entry.md` for new entries.

## What Would Have Helped

N/A - This is a historical document migration.

---

Migrated to feedback-loop reasoning log system: 2026-01-16
