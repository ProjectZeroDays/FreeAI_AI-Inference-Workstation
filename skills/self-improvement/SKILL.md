---
name: self-improvement
description: "Captures learnings, errors, corrections, and feature requests to enable continuous improvement. Use when: (1) User corrects Claude ('No, that's wrong...', 'Actually...'), (2) User requests a capability that doesn't exist, (3) Claude realizes its knowledge is outdated or incorrect, (4) A better approach is discovered for a recurring task, (5) Receiving a Handoff block from self-healing (a recurring verified heal at Recurrence-Count >= 3) to distill into a memory file or new skill. For ACTIVE runtime failures where the agent needs to apply and verify a fix mid-task, use `self-healing` instead (it files HEAL- entries with proof; self-improvement promotes accumulated patterns). Also review learnings before major tasks. For CI-only/headless learning capture, use self-improvement-ci."
---

# Self-Improvement Skill

Log learnings and errors to markdown files for continuous improvement. Coding agents can later process these into fixes, and important learnings get promoted to project memory.

**Pair with [`self-healing`](../self-healing/SKILL.md):** self-healing is the active runtime recovery primitive — it diagnoses, patches, verifies, and files `HEAL-` entries to `.learnings/HEALS.md` when something breaks mid-task. Self-improvement (this skill) is the passive accumulation and promotion layer — it logs corrections, knowledge gaps, and feature requests, and promotes recurring heal handoffs to permanent memory.

## Quick Reference

| Situation | Action |
|-----------|--------|
| Active failure mid-task — agent needs to fix it now | **Use `self-healing` instead** |
| Command/operation failed in the past | Log to `.learnings/ERRORS.md` |
| User corrects you | Log to `.learnings/LEARNINGS.md` with category `correction` |
| User wants missing feature | Log to `.learnings/FEATURE_REQUESTS.md` |
| API/external tool fails | Log to `.learnings/ERRORS.md` with integration details |
| Self-healing Handoff block meets promotion rule | Promote the Distilled Rule to `CLAUDE.md` / `AGENTS.md` / new skill |
| Knowledge was outdated | Log to `.learnings/LEARNINGS.md` with category `knowledge_gap` |
| Found better approach | Log to `.learnings/LEARNINGS.md` with category `best_practice` |

## Setup

```bash
mkdir -p .learnings
```

## Logging Format

### Learning Entry

Append to `.learnings/LEARNINGS.md`:

```markdown
## [LRN-YYYYMMDD-XXX] category

**Logged**: ISO-8601 timestamp
**Priority**: low | medium | high | critical
**Status**: pending
**Area**: frontend | backend | infra | tests | docs | config

### Summary
One-line description of what was learned

### Details
Full context: what happened, what was wrong, what's correct

### Suggested Action
Specific fix or improvement to make

### Metadata
- Source: conversation | error | user_feedback
- Related Files: path/to/file.ext
- Tags: tag1, tag2
- See Also: LRN-20250110-001 (if related)
- Pattern-Key: simplify.dead_code (optional)
- Recurrence-Count: 1
```

### Error Entry

Append to `.learnings/ERRORS.md`:

```markdown
## [ERR-YYYYMMDD-XXX] skill_or_command_name

**Logged**: ISO-8601 timestamp
**Priority**: high
**Status**: pending
**Area**: frontend | backend | infra | tests | docs | config

### Summary
Brief description of what failed

### Error
Actual error message or output

### Context
- Command/operation attempted
- Input or parameters used
- Environment details if relevant

### Suggested Fix
If identifiable, what might resolve this

### Metadata
- Reproducible: yes | no | unknown
- Related Files: path/to/file.ext
```

### Feature Request Entry

Append to `.learnings/FEATURE_REQUESTS.md`:

```markdown
## [FEAT-YYYYMMDD-XXX] capability_name

**Logged**: ISO-8601 timestamp
**Priority**: medium
**Status**: pending
**Area**: frontend | backend | infra | tests | docs | config

### Requested Capability
What the user wanted to do

### User Context
Why they needed it, what problem they're solving

### Complexity Estimate
simple | medium | complex

### Suggested Implementation
How this could be built, what it might extend

### Metadata
- Frequency: first_time | recurring
```

## ID Generation

Format: `TYPE-YYYYMMDD-XXX` where TYPE is `LRN` (learning), `ERR` (error), `FEAT` (feature).

## Promoting to Project Memory

When a learning is broadly applicable, promote it to permanent project memory.

### When to Promote
- Learning applies across multiple files/features
- Knowledge any contributor should know
- Prevents recurring mistakes
- Documents project-specific conventions

### Promotion Targets

| Target | What Belongs There |
|--------|-------------------|
| `CLAUDE.md` | Project facts, conventions, gotchas |
| `AGENTS.md` | Agent-specific workflows, tool usage patterns |
| `.github/copilot-instructions.md` | Project context for GitHub Copilot |

## Recurring Pattern Detection

If logging something similar to an existing entry:
1. **Search first**: `grep -r "keyword" .learnings/`
2. **Link entries**: Add `**See Also**: ERR-20250110-001`
3. **Bump priority** if issue keeps recurring

## Best Practices

1. **Log immediately** - context is freshest right after the issue
2. **Be specific** - future agents need to understand quickly
3. **Include reproduction steps** - especially for errors
4. **Link related files** - makes fixes easier
5. **Suggest concrete fixes** - not just "investigate"
6. **Promote aggressively** - if in doubt, add to CLAUDE.md or AGENTS.md
