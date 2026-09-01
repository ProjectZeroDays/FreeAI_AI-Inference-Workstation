---
name: verify-gate
description: "Runs project compile, test, and lint commands between implementation and quality review. Gates simplify-and-harden behind machine verification. If checks fail, routes back to implementation with diagnostics for a fix loop. If checks pass, signals ready for the quality pass. Use after any implementation work completes and before simplify-and-harden. Essential for the inner loop's verify step."
---

# Verify Gate

Machine verification gate between implementation and quality review. Runs the project's compile, test, and lint commands. If any fail, enters a fix loop. If all pass, unblocks simplify-and-harden.

## When to Use

- After any implementation work completes, before signaling "done"
- Before running simplify-and-harden
- Any time you want a machine-verified green signal

## Pipeline Position

```
[implementation] → verify-gate → simplify-and-harden → self-improvement
                   ↻ fix loop — on failure, hands diagnostics to self-healing
```

## Step 1: Discover Project Commands

Read the project's configuration to find verification commands. Check these sources in order:

1. **Project instruction files** (CLAUDE.md, AGENTS.md, .github/copilot-instructions.md) — look for a `## Verification` or `## Test Commands` section
2. **package.json** — `scripts.test`, `scripts.lint`, `scripts.typecheck`, `scripts.build`
3. **Makefile** / **Justfile** — `test`, `lint`, `check`, `build` targets
4. **Cargo.toml** — `cargo build`, `cargo test`, `cargo clippy`
5. **pyproject.toml** — `pytest`, `mypy`, `ruff`
6. **go.mod** — `go build ./...`, `go test ./...`, `go vet ./...`

If no commands are discoverable, ask the user once and suggest they add a `## Verification` section to their project instruction files.

## Step 2: Run Verification

Run discovered commands in this order. Stop at the first failure category.

### Phase 1: Compile / Type Check
Run the build or type-check command. These catch structural errors before wasting time on tests.

```
Exit 0 → proceed to Phase 2
Exit non-zero → enter fix loop with compiler output
```

### Phase 2: Tests
Run the test command. Scope to changed files if the test runner supports it.

```
Exit 0 → proceed to Phase 3
Exit non-zero → enter fix loop with test output
```

### Phase 3: Lint (optional, skippable with --skip-lint)
Run the lint command. Lint failures are lower severity but still worth catching.

```
Exit 0 → all phases green, gate passes
Exit non-zero → enter fix loop with lint output
```

## Step 3: Fix Loop

When a phase fails:

1. **Read the output.** Parse the error output for actionable diagnostics — file paths, line numbers, error messages.
2. **Scope the fix.** Only fix what the verification caught. Do not refactor, improve, or touch unrelated code.
3. **Apply the fix.** Make the minimal change to resolve the failure.
4. **Re-run the failed phase.** Not all phases — just the one that failed.
5. **If it passes**, continue to the next phase.
6. **If it fails again**, increment the attempt counter.

### Fix Loop Limits

- **Default max attempts:** 3 per phase (configurable via `--fix-limit N`)
- **If limit reached:** Stop. Report what failed, what was tried, and the remaining error output. Do not guess further — signal to the user that manual intervention is needed.
- **Total budget:** The fix loop should not exceed 20% of the original implementation effort.

## Step 4: Gate Signal

When all phases pass:

```markdown
## Verify Gate: PASSED

- Build: passed
- Tests: passed (N tests, M suites)
- Lint: passed (or skipped)

Ready for simplify-and-harden.
```

When the fix loop is exhausted:

```markdown
## Verify Gate: BLOCKED

- Build: passed
- Tests: FAILED (attempt 3/3)
  - [file:line] error description
  - [file:line] error description
- Lint: not reached

Fix loop exhausted. Manual intervention needed before quality review.
```

## Integration with Other Skills

### skill-pipeline
verify-gate should run at every pipeline depth except Trivial.

### simplify-and-harden
verify-gate gates simplify-and-harden. Only activates after green gate.

### self-healing
On any failure during the verify run, hand the diagnostics to `self-healing` (don't just retry the same command). Self-healing runs the diagnose → patch → verify loop, files a `HEAL-` entry to `.learnings/HEALS.md`, and returns control. Verify-gate then re-runs the checks.

## What This Skill Does NOT Do

- Does not review code quality (that's simplify-and-harden)
- Does not check security (that's harden-auditor)
- Does not verify spec compliance (that's spec-auditor)
- Does not modify test files or add new tests
