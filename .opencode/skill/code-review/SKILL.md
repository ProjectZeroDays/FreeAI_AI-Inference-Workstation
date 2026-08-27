---
name: code-review
description: Defect-first code review of a change (uncommitted, base-branch diff, or one or more commits). Pairs with the `reviewer` subagent. Use when the user says "review this PR", "find bugs in this diff", "code review", "audit these commits", "look over my changes", "review for security". Returns actionable findings only — no nitpicks.
---

# Code review — defect-first

This is the playbook the `reviewer` subagent loads. The reviewer runs **read-only**
and returns findings to the coordinator; it never edits. If the `reviewer`
subagent is unavailable, the coordinator can run this skill itself, but only with
read tools.

## 0. Scope the change

Decide what's under review:
- A PR: `git diff origin/main...HEAD` (or the PR's base ref).
- Uncommitted work: `git diff` + `git diff --staged` + untracked files (`git status --porcelain`).
- A commit range: `git diff <sha1>...<sha2>`.

Refuse nothing broader than the diff unless the user asked for whole-file review.
Out-of-scope findings (style in untouched code) get noted at the end as
"NOT REVIEWED" — don't waste lines nitpicking them.

## 1. Pre-flight: run the project's own automated checks first

Don't eyeball what a tool can catch. Run (in this order, stop at first red so you
don't drown in cascade errors):

| stack        | lint                  | types                | security                         |
|--------------|-----------------------|----------------------|----------------------------------|
| TS/JS        | `eslint`, `tsc -p .`  | `tsc --noEmit`       | `npm audit --omit=dev`           |
| Python       | `ruff check .`        | `pyright`/`mypy`     | `pip-audit`                      |
| Rust         | `cargo clippy`        | `cargo check`        | `cargo audit`                    |
| Go           | `golangci-lint run`   | `go vet ./...`       | `govulncheck ./...`              |

Auto-detected findings go into your report **once**, summarized — they were the
cheap part. The rest of the review is the manual pass.

## 2. Manual pass — categories in priority order

Scan the diff file-by-file. Look only for what's *actionable*. Skip anything that
"could be nicer."

### A. Correctness (find first)
- Wrong/null-path: what happens to every variable when an upstream `?.` returns
  `undefined`? When the API returns empty? When `length === 0`?
- Off-by-one, reversed comparison, swapped arguments, `<` vs `<=`.
- Async without await; promise not returned; race between two fetches.
- Numeric: integer overflow, float equality, timezone-naive datetime comparison.
- Branches the diff added but didn't test.

### B. Security (find second; cite file:line)
- Injection: SQL (string-built query), command (`child_process` + user input),
  template (unescaped user input rendered), LDAP/XPath.
- Authn/authz: route added without an authz check the rest of the codebase has.
- Secrets: keys/tokens written to code, logs, error messages, or URLs.
- Mass assignment: bind straight from request body to a privileged model.
- CSRF, open redirects, SSRF (user-controlled URL fetched server-side), path
  traversal (`../` joined into a path).
- Unsafe deserialization (pickle, yaml.load, eval, Function ctor, child_process).
- Timing leaks (early-return on bad password vs. missing user).

### C. Reliability (only if material)
- I/O with no retry (DB call, HTTP) — but no retry storms either.
- Swallowed errors: `catch {}` / `except: pass` that hides real failures.
- Resource leaks: file/stream/socket not closed, missing `with`/`using`.
- Non-idempotent writes when a retry can replay them.

### D. Maintainability (only if it harms readability or correctness)
- A 200-line method that mixes 3 concerns.
- Two new helpers with the same name in different modules of the same package.
- A misleading name (function called `isReady` that has side effects).

**Skip nitpicks.** "Consider adding a comment", "could be a one-liner", "I
prefer early returns" — none of these ship.

## 3. Severity rubric

- **blocker** — wrong behavior, security hole, data loss. Must change before merge.
- **high** — likely bug or realistic reliability issue; should change before merge.
- **medium** — real issue, deferrable; should change before next release.
- **low** — cosmetic but worth fixing (missing `const`, dead branch). Optional.

If you can't decide between two levels, pick the **lower** — over-alarming
teaches users to ignore the report.

## 4. Output format (exact, no preamble)

```
CHANGE: <one line: scope of the diff>
VERDICT: request-changes | approve-with-comments | APPROVED

AUTO-CHECKS:
  lint:   <pass|fail: N issues>
  types:  <pass|fail: M errors>
  audit:  <clean|N high/critical>

FINDINGS:
[<n>] blocker · src/foo.ts:42 · SQL built by concatenation · use parameterized query ($1, $2)
[<n>] high   · src/bar.py:88 · except: pass hides ConnectionError · log + re-raise
[<n>] medium · src/baz.go:15 · missing context.WithTimeout on HTTP call · wrap with 5s timeout
[<n>] low    · src/qux.ts:3  · unused import 'lodash' · remove

NOT REVIEWED:
  - test fixtures (out of scope)
  - generated/ code

SUMMARY: <2-3 lines for the user, leading with the merge decision>
```

If there are zero actionable findings, return **exactly**:

```
VERDICT: APPROVED
No actionable findings.
```

## 5. Hard rules

- Cite `file:line` for every finding. No "in the handler somewhere."
- One concrete fix per finding. No "you should refactor this."
- Don't run anything destructive (`rm`, `git reset --hard`, `--force`).
- Don't fix things — that's the `coder`'s job. You flag.
- If you found the same bug pattern three times, file one finding listing all
  three locations rather than three identical findings.