---
name: project-context-injector
description: "Automatically reads project files (README, AGENTS.md, MEMORY.md, .learnings/, recent git history) and injects relevant context into the agent's working memory. Use at session start or when the user says 'remember what I was working on' or 'what's the project context'."
---

# Project Context Injector

Scans the current project for context files and recent work, then surfaces the most relevant information to help the agent understand what was being done and what to continue.

## When to Use

- Session start (before doing any work)
- User asks: "what am I working on?", "what was I doing last?", "give me context", "what's the project structure"
- Before starting a complex task where prior context matters
- When the user says "resume where we left off"

## What It Scans (in priority order)

1. `AGENTS.md` — agent workflow and project facts
2. `MEMORY.md` or `memory/MEMORY.md` — long-term memory
3. `.learnings/LEARNINGS.md` — recent corrections and insights
4. `.learnings/ERRORS.md` — recent errors and fixes
5. `README.md` — project overview
6. `SESSION-STATE.md` — active working memory (WAL)
7. `memory/YYYY-MM-DD.md` — daily logs (most recent 3)
8. `git log --oneline -20` — recent commits
9. `git diff --name-only HEAD~5` — recently changed files
10. `docs/plans/` — active implementation plans
11. Any `SESSION-*.md` or `SUMMARY-*.md` in the project root

## Output

Produce a structured context briefing:

```
## Project Context
**Project**: [name from README or git remote]
**Branch**: [current git branch]
**Last Commit**: [hash + message + date]

### Active Work
[From SESSION-STATE.md or recent daily logs]

### Recent Changes
[Files modified in last 5 commits]

### Key Decisions
[From MEMORY.md or LEARNINGS.md]

### Open Items
[TODOs, pending learnings, unresolved errors]

### Files to Know
[Core files: entry points, configs, key modules]
```

## Rules

- Read files in order of relevance; stop when you have enough context.
- Do NOT read node_modules, .git, build artifacts, or binary files.
- Keep the summary under 500 words unless the project is very large.
- If no context files exist, create a minimal `SESSION-STATE.md` and note it.
- Never log secrets, tokens, or full source files in the summary.
