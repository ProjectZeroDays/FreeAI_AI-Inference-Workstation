---
description: Run the repo-maintenance bot (lint, typecheck, format, tests, deps audit, optional safe PR) on the current repo.
agent: maintainer
model: anthropic/claude-sonnet-4-5-20250929
subtask: true
---

Run a full maintenance pass on the current repository per the `repo-maintenance`
skill. Use the small model for Phase 0/2 and the default model for Phases 1/3.

$ARGUMENTS

If `$ARGUMENTS` includes:
- `--pr`        → open the one safe automated PR described in Phase 3.
- `--triage`    → also run Phase 4 (stale issue/PR triage).
- `--deps-only` → skip lint/typecheck/tests; only run the dependency audit.

Always return the standard Phase 5 report at the end. Do not commit or push
anything unless `--pr` was passed.