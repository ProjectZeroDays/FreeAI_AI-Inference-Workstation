---
description: Deep read-only audit of the repo — duplicates, dead files, stale docs, misconfig, orphaned deps. Proposed cleanup; no deletions without confirmation.
agent: build
model: anthropic/claude-sonnet-4-5-20250929
subtask: true
---

Load the `project-audit` skill and run a deep audit on the current repo's root
folder and all non-excluded files.

`$ARGUMENTS`:
- (empty)              → full audit (Phases 0–6) on the working tree.
- `--duplicates`       → only Phase 2 (exact + near duplicates).
- `--dead`             → only Phase 3 (dead/unreferenced files).
- `--configs`          → only Phase 4 (misconfig parse checks).
- `--deps`             → only Phase 5 (orphaned dependencies).
- `--docs`             → defer to the `docs-sync` skill instead.

Produce the §7 report and STOP. Do not delete or `rm` anything. If the user
replies `apply [n]` for a P1/P2 finding afterwards, prepare the edit/deletion as
a draft PR for human review — never force-push, never `git rm` without the user's
explicit consent, and never delete a file below HIGH confidence.