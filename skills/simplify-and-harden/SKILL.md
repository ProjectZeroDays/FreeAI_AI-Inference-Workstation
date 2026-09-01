---
name: simplify-and-harden
description: "Post-completion self-review for coding agents that runs simplify, harden, and micro-documentation passes on non-trivial code changes. Use when: a coding task is complete in a general agent session and you want a bounded quality and security sweep before signaling done. For CI pipeline execution, use simplify-and-harden-ci."
---

# Simplify & Harden

Post-completion self-review for coding agents. Runs simplify, harden, and micro-documentation passes on non-trivial code changes.

## When to Use

- After any implementation work completes, before signaling "done"
- When the diff contains a non-trivial code change (>=10 lines in executable files, or high-impact logic change)
- NOT for docs-only, config-only, tests-only, or generated files

## Three Passes

### Pass 1: Simplify
**Objective:** Reduce unnecessary complexity introduced during implementation.

Review checklist:
1. **Dead code** — Remove debug logs, commented-out attempts, unused imports
2. **Naming clarity** — Rename functions/variables that don't read well
3. **Control flow** — Flatten nested conditionals, use early returns
4. **API surface** — Reduce unnecessary public exposure
5. **Over-abstraction** — Flag but don't restructure unless significant
6. **Consolidation** — Merge egregious duplication

**Cosmetic fixes** applied automatically. **Refactors** require human approval.

### Pass 2: Harden
**Objective:** Close security and resilience gaps.

Review checklist:
1. **Input validation** — Validate all external inputs
2. **Error handling** — Specific catch blocks, no swallowed exceptions
3. **Injection vectors** — SQLi, XSS, command injection, path traversal
4. **Auth and authorization** — Permission checks present and correct
5. **Secrets** — No hardcoded credentials
6. **Data exposure** — No internal state in errors/logs
7. **Dependencies** — Well-maintained, properly versioned
8. **Race conditions** — Proper synchronization

**Security patches** applied automatically. **Security refactors** require human approval.

### Pass 3: Document
**Objective:** Capture non-obvious decisions.

- Add single-line comments for logic requiring >5 seconds of "why?"
- Add comments with context for workarounds
- Max 5 comments per task

## Budget

- Max additional changes: 20% of original diff
- Max execution time: 60 seconds
- If budget exceeded, stop and report what was done

## Output

Produce a structured summary:
- Files reviewed
- Simplify changes applied (cosmetic vs refactor)
- Harden findings (applied vs flagged)
- Comments added
- Learning candidates for self-improvement

## Integration

This skill pairs with:
- **verify-gate** — runs before simplify-and-harden
- **self-improvement** — feeds learning candidates
- **self-healing** — fixes verify-gate failures
