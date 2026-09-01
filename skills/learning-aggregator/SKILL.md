---
name: learning-aggregator
description: "[Beta] Cross-session analysis of accumulated .learnings/ files. Reads all entries, groups by pattern_key, computes recurrence across sessions, and outputs ranked promotion candidates. This is the outer loop's inspect step — it turns raw learning data into actionable gap reports. Use on a regular cadence (weekly, before major tasks, or at session start for critical projects). Can be invoked manually or scheduled."
---

# Learning Aggregator

Reads accumulated `.learnings/` files across all sessions, finds patterns, and produces a ranked list of promotion candidates. This is the outer loop's **inspect** step.

## When to Use

- **Weekly cadence** — scheduled or manual review
- **Before major tasks** — check for known patterns
- **After a burst of sessions** — consolidate findings
- **When Recurrence-Count reaches >= 3** — verify with full context

## What It Produces

A **gap report** — ranked patterns that have crossed (or are approaching) the promotion threshold.

## Step 1: Read All Learning Files

| File | Contains |
|------|----------|
| `LEARNINGS.md` | Corrections, knowledge gaps, best practices |
| `ERRORS.md` | Command failures, API errors |
| `FEATURE_REQUESTS.md` | Missing capabilities |
| `HEALS.md` | Verified runtime recoveries |

## Step 2: Group and Aggregate

Group entries by `Pattern-Key`. For each group:
1. Sum recurrences across all entries
2. Count distinct tasks
3. Compute time window
4. Collect all related files
5. Take highest priority
6. Collect evidence

## Step 3: Rank and Classify

### Promotion Threshold
An entry is **promotion-ready** when:
- `Recurrence-Count >= 3`
- Seen in `>= 2 distinct tasks`
- Within a `30-day window`

### Approaching Threshold
- `Recurrence-Count >= 2` OR
- `Priority: high/critical` with any recurrence

### Gap Types
| Gap Type | Signal | Fix Target |
|----------|--------|------------|
| Knowledge gap | Agent didn't know X | Update CLAUDE.md, AGENTS.md |
| Tool gap | Agent improvised | Add MCP tool/script |
| Skill gap | Same pattern failing | Create/update skill |
| Ambiguity | Conflicting interpretations | Tighten instructions |
| Reasoning failure | Had knowledge but reasoned wrong | Add decision rules |

## Step 4: Produce Gap Report

```markdown
## Learning Aggregator: Gap Report

**Scan date:** YYYY-MM-DD
**Entries scanned:** N
**Patterns found:** N
**Promotion-ready:** N

### Promotion-Ready Patterns
#### 1. [Pattern-Key] — [Summary]
- **Recurrence:** N times across M tasks
- **Priority:** high
- **Gap type:** knowledge gap
- **Recommended action:** Add rule to CLAUDE.md/AGENTS.md
```

## Step 5: Handoff

The gap report feeds into:
1. **harness-updater** — applies promotions to project files
2. **eval-creator** — creates permanent test cases
3. **Human review** — for ambiguity/reasoning failures

## What This Skill Does NOT Do

- Does not modify `.learnings/` files (read-only)
- Does not apply promotions (that's harness-updater)
- Does not create evals (that's eval-creator)
- Does not fix code or run tests
