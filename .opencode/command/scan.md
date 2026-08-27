---
description: Run static analysis + tests + (when something fails) the debug playbook. Read-only probe; fixes are dispatched to `coder` on user confirmation.
agent: build
model: openai/gpt-4o-mini
subtask: true
---

Load the `scan-and-debug` skill and run a scan on the current branch.

`$ARGUMENTS`:
- (empty)              → full pass: §1 static + §2 tests + §3 debug (only if §2 failed).
- `--static`           → only §1 (lint/types/audit).
- `--tests`            → only §2 (mirror CI test runner + coverage).
- `--watch`            → §2 tests in watch mode; stays attached.
- `--debug <test-name>` → jump straight to §3 with the named test as the
                          failing oracle (assumes you already know it's red).

Always run with a clean working tree (stash if needed; restore at end). Print
the §4 report and STOP. If `ISSUES FOUND` is non-empty, end with the §4 `NEXT:`
block inviting the user to reply `fix [n]` to dispatch a `coder` task. Don't
apply fixes from this command. Never run `--update-snapshots`, `--fix`,
`cargo fmt`, or `git bisect` from a dirty tree.