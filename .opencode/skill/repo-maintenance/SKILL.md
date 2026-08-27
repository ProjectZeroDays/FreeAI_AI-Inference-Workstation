---
name: repo-maintenance
description: Playbook for the maintainer subagent and the /maintain command. Runs lint, typecheck, format check, tests, dependency audits, and stale issue/PR triage on the current repo, and prepares safe automated PRs. Use for "maintain this repo", "run CI locally", "check for outdated deps", "triage stale issues", "open a deps PR", "refresh CHANGELOG". Benign repo hygiene only — no offensive tooling.
---

# Repo maintenance bot playbook

You run **only** on the repo you live in. Every action is reversible (branches,
PRs, comments). You never force-push, never close without a comment, and never
push code that fails its own checks.

## Phase 0 — orient (read-only, always first)

1. Detect stack: `package.json` → Node/TS; `pyproject.toml`/`setup.py` → Python;
   `Cargo.toml` → Rust; `go.mod` → Go.
2. Find the canonical commands by reading real config, NOT by assuming:
   - lint: `package.json scripts` (`lint`, `lint:check`), `ruff.toml`/`pyproject`
     (`ruff check .`), `eslint`, `golangci-lint run`.
   - typecheck: `tsc --noEmit`, `pyright`, `mypy`, `cargo check`.
   - format check: `prettier --check .`, `ruff format --check`, `cargo fmt --check`.
   - tests: `npm test`, `pytest`, `cargo test`, `go test ./...`.
3. Find CI config (`.github/workflows/*.yml`, `.gitlab-ci.yml`, etc.) and mirror
   the commands it runs — that's the source of truth for "does CI pass".

## Phase 1 — health check

Report each as pass/fail with the failing detail:

```
HEALTH: <green|yellow|red>
- lint:    <pass | fail: <top 3 errors>>
- types:   <pass | fail: <top 3 errors>>
- format:  <pass | fail: <n files need formatting>>
- tests:   <N passed / M failed / K skipped; slowest 3 by duration>
```

- **green** = all pass.
- **yellow** = tests pass but lint/types/format fail, or tests fail but the
  failure is pre-existing (check against `main`).
- **red** = tests fail on your change, or a security audit has high-severity
  findings.

Never "fix" a failure you didn't cause without flagging it as pre-existing and
out of scope for this run.

## Phase 2 — dependency audit

Run the right tool for the stack and summarize **only the actionable**:

- Node: `npm outdated` + `npm audit --omit=dev` (production only).
- Python: `pip list --outdated` + `pip-audit` (or `safety check`).
- Rust: `cargo outdated` + `cargo audit`.
- Go: `go list -m -u all` + `govulncheck ./...`.

For each outdated package:
- **patch/minor**: safe to bump — candidate for an automated PR.
- **major**: list the breaking changes from the CHANGELOG/release notes; never
  auto-bump. Open a draft PR for human review instead.
- **vulnerable (high/critical)**: always surface first, even if "out of scope."

Cap the summary at the top 10 most important; full list goes in the PR body.

## Phase 3 — automated safe PR (optional, one per run)

Open **at most one** PR per maintenance run, and only for safe, mechanical
changes:
- bump patch/minor deps,
- apply `lint --fix` / `ruff format` / `cargo fmt`,
- refresh a generated file (CHANGELOG, lockfile).

Steps:
1. `git switch -c chore/<descriptive-name>` from an up-to-date `main`.
2. Make the change. Update the lockfile.
3. Re-run Phase 1 health check. If red, abandon the branch and report — do not
   push.
4. Re-run tests.
5. Add a CHANGELOG entry under an `Unreleased` heading.
6. Commit with a conventional message (`chore(deps): bump foo to 1.2.3`).
7. `git push -u origin <branch>` (NEVER `--force`). Open a PR via `gh pr
   create` with: what changed, why, the health-check output as proof, and a
   checklist for the reviewer. Request review, don't merge.

## Phase 4 — stale issue/PR triage (only if explicitly asked)

- Use `gh issue list --state open --sort updated` / `gh pr list`.
- Label `stale` on anything untouched >90 days **and** leave a comment
  explaining the label and when it'll close (or that it won't auto-close).
- **Never close** an issue or PR without a human in the loop. Triage = label +
  comment, not closing.

## Phase 5 — report

Standard report (this is the whole maintainer output):

```
HEALTH: <green|yellow|red>
- lint:   ...
- types:  ...
- format: ...
- tests:  ...
DEPS:     <n patch/minor outdated, m major, k vulnerable>
PR:       <url> or "none opened (reason)"
NEXT:     <single most valuable next action>
```

## Hard limits

- One PR per run. One `git push` per branch.
- No major dep bumps without listing breaking changes.
- No silent closes. No force-push. No `--no-verify`.
- If anything is ambiguous, stop and ask the coordinator/user.