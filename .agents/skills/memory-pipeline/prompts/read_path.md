# Memory System — Agent Prompt Integration

## When to Use Memory

Before solving ambiguous or project-dependent work, check if relevant memories exist.
Memory helps you avoid repeating mistakes and reuse proven solutions.

## How to Access Memory

1. **Quick check**: Read `memory_summary.md` for a high-level overview
2. **Deep dive**: Read `MEMORY.md` for organized knowledge
3. **Specific topic**: Search `rollout_summaries/` for related conversations
4. **Procedures**: Check `skills/` for reusable workflows

## Decision Boundary

| Situation | Action |
|-----------|--------|
| Repeating a past task | Check memory first |
| User mentions "remember" / "saved" | Reference memory |
| Solving a new problem | Skip memory, solve fresh |
| Uncertain if memory helps | Check summary, skip if <2 min read |

## Citation Requirements

When you reference memory in your response, cite it:

```xml
<mem-citation>
<entries>
MEMORY.md:100-105|note=[what you recalled]
rollout_summaries/2026-06-20-a1b2.md:5-8|note=[specific detail]
</entries>
<rollout_ids>
<conversation-id>
</rollout_ids>
</mem-citation>
```

## Saving New Memories

After completing a task, consider if anything should be saved:

1. If you solved a non-trivial problem → save the solution
2. If the user stated a preference → save it
3. If you learned an environment fact → save it
4. If the task was trivial/one-off → skip

To save, write to `extensions/ad_hoc/notes/YYYY-MM-DDTHH-MM-SS-<slug>.md`
