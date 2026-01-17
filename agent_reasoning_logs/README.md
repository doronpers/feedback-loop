# Agent Reasoning Logs

This folder contains reasoning logs from coding agents working across all repositories in the workspace.

## Purpose

- **Document decision-making processes** during coding tasks
- **Preserve architectural insights** and lessons learned
- **Create a searchable knowledge base** of problem-solving approaches
- **Track agent reasoning** for quality improvement and debugging
- **Feed into feedback-loop pattern library** for continuous improvement

## Hippocratic Principle: "First, Do No Harm"

> *"To do good or to do no harm"* — Hippocratic tradition

All agents should verify their work follows this principle before committing changes.

## Integration with Feedback-Loop

This reasoning log system is part of the [feedback-loop](https://github.com/doronpers/feedback-loop) repository because:

- It aligns with the mission of capturing patterns and learnings
- Logs can feed into the pattern library for AI improvement
- Analytics dashboards can visualize agent performance trends

## Folder Structure

```text
agent_reasoning_logs/
├── README.md                        # This file
├── AGENT_REASONING_INSTRUCTIONS.md  # Portable instructions for other repos
├── logs/                            # Individual log entries
│   └── YYYY-MM-DD_repo_task.md      # Log file naming convention
└── templates/                       # Log templates
    └── reasoning_entry.md           # Standard entry template
```

## Log Format

Each entry should follow the template in `templates/reasoning_entry.md`

## File Naming Convention

`YYYY-MM-DD_<repo>_<brief-task-description>.md`

**Examples**:

- `2026-01-16_council-ai_documentation-consolidation.md`
- `2026-01-17_sono-eval_api-refactor.md`
- `2026-01-18_feedback-loop_bug-fix.md`

## When to Create a Log Entry

- ✅ Complex problem-solving tasks
- ✅ Architectural decisions
- ✅ Bug fixes with non-obvious solutions
- ✅ Refactoring work
- ✅ Any task with valuable lessons learned
- ❌ Simple formatting or typo fixes
- ❌ Routine dependency updates

## For Agents

After completing significant tasks in any repository, create a reasoning log entry here. This helps:

1. Future agents understand past decisions
2. Users track agent reasoning quality
3. Build institutional knowledge across projects
4. Improve the feedback-loop pattern library

---

Last Updated: 2026-01-16
