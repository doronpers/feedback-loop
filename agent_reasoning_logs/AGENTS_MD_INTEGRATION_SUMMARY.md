# AGENTS.md Integration Summary

**Date**: 2026-01-20
**Task**: Review AGENTS.md files and update .cursorrules to ensure agents read and follow them

## AGENTS.md Files Found

1. **sono-platform/modes/sonotheia/documentation/governance/AGENTS.md**
   - Comprehensive 248-line guide with workflows, guardrails, patterns
   - Key content: Sensor development, patent compliance, configuration management, PR checklist

2. **sono-platform/modes/xlayer/.github/agents/AGENTS.md**
   - Code quality verification guidelines
   - Key content: NumPy types, bounds checking, exceptions, logging, iteration loop

3. **sono-eval/AGENTS.md**
   - Repository guidelines and common pitfalls
   - Key content: Project structure, linting protocols, script permissions, testing guidelines

4. **Website-Sonotheia-v251120/AGENTS.md**
   - File organization standards and development guidelines
   - Key content: Root directory rules, documentation organization, sensor development, API structure

## Updates Made

### ✅ sono-platform/modes/sonotheia/.cursorrules

**Added**:

- Reference to `documentation/governance/AGENTS.md` as required reading
- Key guardrails from AGENTS.md:
  - Patent compliance requirements
  - Sensor categories (prosecution vs defense)
  - Configuration management (`backend/config/settings.yaml`)
  - Audio format requirements
  - Error handling patterns
  - Performance constraints
- Reasoning log requirement

### ✅ sono-platform/modes/xlayer/.cursorrules

**Added**:

- Reference to `.github/agents/AGENTS.md` as required reading
- Code quality verification checklist:
  - NumPy type conversion
  - Bounds checking
  - Specific exceptions
  - Logging practices
  - Metadata-based categorization
- Iteration loop process
- Reasoning log requirement

### ✅ sono-eval/.cursorrules

**Added**:

- Reference to `AGENTS.md` as required reading (alongside AGENT_KNOWLEDGE_BASE.md)
- Linting protocols section with common issues:
  - E402 (sys.path hacks)
  - F401 (unused imports)
  - F541 (f-string placeholders)
  - E501 (line length)
  - Test file import handling
- Script permissions requirement
- Make commands reference

### ✅ Website-Sonotheia-v251120/.cursorrules

**Added**:

- Reference to `AGENTS.md` as required reading
- File organization standards as Quick Rule #5:
  - Root directory minimalism
  - Documentation subdirectories (reviews/, implementation/, planning/)
  - Scripts and tools organization

## Key Improvements

1. **Explicit References**: All .cursorrules now explicitly require reading AGENTS.md
2. **Key Content Extracted**: Critical guardrails and patterns included directly in .cursorrules
3. **Actionable Rules**: Converted AGENTS.md guidance into numbered Quick Rules
4. **Consistency**: All repos now follow similar pattern for referencing AGENTS.md

## Pattern Established

For repos with AGENTS.md files, .cursorrules now includes:

```markdown
## CRITICAL: Read Before ANY Task

Before starting any task, you MUST read and follow:
1. `AGENT_KNOWLEDGE_BASE.md` in the repository root
2. `AGENTS.md` in the repository root (or path to AGENTS.md)

[Key content from AGENTS.md extracted into Quick Rules or dedicated sections]
```

## Files Updated

- ✅ `sono-platform/modes/sonotheia/.cursorrules`
- ✅ `sono-platform/modes/xlayer/.cursorrules`
- ✅ `sono-eval/.cursorrules`
- ✅ `Website-Sonotheia-v251120/.cursorrules`

## Verification

To verify agents are following AGENTS.md:

1. Check that .cursorrules explicitly references AGENTS.md
2. Verify key guardrails from AGENTS.md are included in .cursorrules
3. Monitor agent behavior to ensure AGENTS.md patterns are followed

---

**Status**: ✅ Complete - All repos with AGENTS.md files now have updated .cursorrules that reference and incorporate key content
