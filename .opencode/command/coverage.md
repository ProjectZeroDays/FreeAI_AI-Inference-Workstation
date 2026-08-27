---
description: Compare backend routes/exports with frontend callers. Lists orphan endpoints, broken calls, and signature mismatches, and proposes concrete wiring.
agent: build
model: anthropic/claude-sonnet-4-5-20250929
subtask: true
---

Load the `frontend-coverage` skill and run the audit on the current repo.

`$ARGUMENTS`:
- (empty)              → full comparison: backend surface vs frontend usage.
- `--backend <dir|file>` → restrict the backend scan to a specific entry point.
- `--frontend <dir>`   → restrict the frontend scan to a sub-tree.
- `--only orphans`     → only list `orphan-endpoint` findings.
- `--only broken`      → only list `broken-call` and `signature-mismatch`.

Produce the §5 report and STOP. Don't edit any frontend file until the user
replies `wire [n]` to specifically request the wiring for finding `[n]`. Apply
each requested wiring as an isolated commit on the current branch.