---
name: scan-and-debug
description: Scan, test, and debug the application — runs the project's own static analysis (lint/typecheck/security) AND test suite, mirrors CI locally, isolates failures, and walks a debugging playbook (print vs debugger vs repro). Read-only-probe; fixes go through the `coder` subagent. Use when the user says "scan for errors", "run all tests", "what's failing in CI", "debug this", "reproduce this bug", "Test why", "run lint and tests", "audit code".
---

# Scan and debug — find and reproduce errors

This skill runs the project's own automated checks **and** its tests, mirrors what
CI does (so failures reproduce locally), then walks a debugging playbook once a
real failure is found. It does NOT fix things — fixes go through the `coder`
subagent. This skill pairs with the community `systematic-debugging` and
`debug-pro` skills (load those for hard repros).

## 0. What "scan" means here

Three things, run in order: static analysis §1, tests §2, debug playbook §3.
Each phase is independent; a green §1 with a red §2 is a normal and useful
state — don't bail early.

## 1. Static analysis (cheap; run first)

Auto-detected per stack; do not assume — read the manifest:

| stack       | lint                                   | types                          | security                            |
|-------------|----------------------------------------|--------------------------------|-------------------------------------|
| TS/JS       | `eslint .`, `tsc --noEmit`             | `tsc --noEmit`                 | `npm audit --omit=dev`, `pnpm audit` |
| Python      | `ruff check .`, `flake8`               | `pyright` or `mypy --strict`   | `pip-audit`, `bandit -r src/`       |
| Rust        | `cargo clippy --all-targets -- -D warnings` | `cargo check`             | `cargo audit`                       |
| Go          | `golangci-lint run`                    | `go vet ./...`                 | `govulncheck ./...`                 |
| .NET        | `dotnet format --verify-no-changes`    | `dotnet build -c Release`      | `dotnet list package --vulnerable`  |

Report format (one block):
```
STATIC ANALYSIS:
  lint:    <pass | fail: top-3 issues with file:line>
  types:   <pass | fail: M errors / N warnings>
  audit:   <clean | N high+critical, list them>
```

If a tool isn't installed, print the install command and skip cleanly — don't
fail the whole pass.

## 2. Tests (run after static; mirror CI)

Find the canonical test command by reading, in order:
1. `.github/workflows/*.yml` (or equivalent CI file) — the **source of truth**.
2. `package.json#scripts.test`, `pyproject.toml [tool.pytest.ini_options]`,
   `Cargo.toml [[test]]`, `Makefile test:`.
3. Common defaults: Node's built-in runner, `pytest`, `cargo test`, `go test ./...`.

Run with **the same flags CI uses** (filter, env vars, coverage threshold). If you
mock-locally and CI then catches bugs you didn't, you've wasted a cycle.

### Coverage
Run with coverage if the tool supports it cheaply:
- Node: `node --test --experimental-strip-types --experimental-test-coverage "src/**/*.test.ts"`
- Python: `pytest --cov=src --cov-report=term-missing`
- Rust: `cargo tarpaulin` (or `cargo llvm-cov`)
- Go: `go test -coverprofile=coverage.out ./... && go tool cover -func=coverage.out`

Report the **delta** vs last commit if there's a baseline; absolute percentage
alone is noise.

### Watch mode (only when asked)
If the user asks for "watch": prefer the runner's native watch (`pytest-watch`,
`cargo watch`, `gotestsum -watch`). Don't roll your own loop.

### Failure isolation
For each failing test:
1. Capture the assertion + the printed `expected` vs `actual`.
2. Recapture the same test alone (not the suite). Does it still fail in
   isolation? If not → order dependency or shared state. File as "test-isolation
   bug", not a code bug.
3. Read only the files in the failing test's stack trace. Don't open the whole
   tree.
4. Print the F.I.R.S.T. classification (Fast / Isolated / Repeatable /
   Self-validating / Timely); flag any non-F.I.R.S.T. test you saw.

Report format:
```
TESTS:
  command: npm test
  result:  184 passed / 7 failed / 2 skipped
  failing:
    - src/foo.test.ts > "withRetry backs off…" · expected [50,100,200] got [50,101,200]
    - src/bar.test.ts > "TokenBucket refills" · AssertionError: 60.0 != 60
  coverage: 78.4% (-1.2% vs main; threshold 75%) — bar.ts L40-L48 uncovered
  CI-mirror: matches `.github/workflows/test.yml` step "Run tests"
```

## 3. Debug playbook (only when §2 produced a real failure)

Don't go here prophylactically. Only when a real bug surfaced.

### A. State your hypothesis in one sentence
"I think X happens because Y." If you can't form one, the bug is research, not
debug — hand off to the `research` subagent or load the community
`systematic-debugging` skill.

### B. Pick the simplest tool that reproduces
1. **Repro script first.** Two-liner that triggers the bug. If you can't write
   one, that itself is the clue (you don't actually know the trigger).
2. **Print, not debugger, *when*:**
   - the bug is in production logging (add a `console.log` you can ship with),
   - the failing code runs in a worker/async,
   - it's faster to re-read a log line than step through.
3. **Debugger, not print, *when*:**
   - state diverges from the spec mid-flight,
   - the bug is data-dependent (you need to inspect what the failing function
     actually received).
4. Pick the right debugger:
   - Node: `--inspect` + chrome://inspect, or `node --inspect-brk` for the
     entrypoint.
   - Python: `pdb` REPL, or `debugpy` for remote DAP.
   - Rust: `rust-gdb`/`lldb`, or `rr record`/`rr replay` for nondeterministic.
   - Go: `dlv` (`dlv test ./pkg/tests -test.run '^TestFailing$'`).

### C. Bisect
For "this used to work":
```
git bisect start
git bisect bad HEAD
git bisect good <last-known-green-sha>
# run the failing test at each step; `git bisect (good|bad)` until pinned
```
Prefer the failing test as the bisect oracle. If no test exists, write one
fix-first (TDD-red).

### D. Hypothesis tests (write a failing test, then fix until green)
1. Write a test that asserts the FIX, not the bug — it should fail now.
2. Change the smallest possible code.
3. Re-run the test plus the full suite (catch regressions).
4. If still red, refine the hypothesis (back to §A). Limit yourself to **3
   hypothesis-fix iterations**; if you haven't found it, escalate — hand the
   bug to the `coder` with bisect log + repro script + failing-test path.

### E. Real-world gotchas (don't ignore)
- Async but-not-awaited silently swallowing errors — print the rejection.
- Snapshot test "drift" — many snapshot failures aren't bugs, just updated
  expected output. Update with `--update-snapshots` and **manually review the
  diff**, never blindly accept.
- Time-dependent bug — freeze the clock (`vi.useFakeTimers()`, `freezegun`,
  `tokio::time::pause()`).
- Locale/ordering bug — sort before asserting in tests that compare lists.
- Concurrency bug — suggests you forgot a mutex. Try single-thread first to
  prove it's a race; if the bug vanishes you've localized it.

## 4. Output format (always, even when green)

```
SCAN: <project> @ <ref>
STATIC ANALYSIS:
  lint:    ...
  types:   ...
  audit:   ...
TESTS:
  command: ...
  result:  ...
  coverage: ... (delta vs main)
ISSUES FOUND:
  [1] static · src/foo.ts:42 · unused 'x' import · remove
  [2] test  · src/bar.test.ts:55 · order-dependent · add setup/teardown
  [3] test  · src/baz.test.ts:88 · snapshot drift (manually diff'd; safe to update)
HYPOTHESIS (only if a code bug was found):
  "TokenBucket.snapshot returns 6.0000009 because real clock elapsed between
   tryConsume and snapshot on a warm machine; tests should use fakeClock."
NEXT:
  reply `fix [n]` to dispatch a `coder` task that fixes issue [n] with a
  regression test. Each fix is one isolated commit.
```

## 5. Hard limits

- Never fix the bug under this skill. Hand off to `coder` with bisect log +
  repro script + failing-test path. This skill diagnoses.
- Never run tests in a way that mutates the user's working tree in a way that
  can't be undone (`--update-snapshots`, `--fix`, `cargo fmt`). If you must
  mutate for diagnosis, do it on a throwaway branch and `git stash` before
  returning to the user's tree.
- Never `git bisect` from a dirty working tree — `git stash` first or use a
  separate worktree (`git worktree add`).
- Never disable a test to make the suite green. Flag the broken test and stop.
- Don't auto-update snapshots; always require explicit `update-snapshots [test
  name]` confirmation from the user and print the diff before applying.