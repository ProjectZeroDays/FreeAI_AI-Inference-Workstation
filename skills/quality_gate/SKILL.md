---
name: quality_gate
description: Automated code quality gates: lint, typecheck, test coverage, security scan before merge. Use when the user asks about CI quality gates, pre-merge checks, linting, type checking, test coverage requirements, or security scanning.
---

# Quality Gate

## Gate Definition

A quality gate is a set of automated checks that must pass before code is merged. Each gate returns **PASS** or **FAIL** with a score.

## Lint Gate

```bash
# ESLint (JavaScript/TypeScript)
npx eslint src/ --max-warnings=0
# Exit non-zero on any warning

# Ruff (Python)
ruff check src/
ruff check --select I src/  # sort imports

# Pylint
pylint src/ --fail-under=8.0

# Rust
cargo clippy -- -D warnings

# Go
golangci-lint run
```

### Lint Configuration

```json
// .eslintrc.json
{
  "rules": {
    "no-console": "error",
    "no-unused-vars": "error",
    "@typescript-eslint/no-explicit-any": "error"
  }
}
```

## Type Check Gate

```bash
# TypeScript
npx tsc --noEmit

# Pyright
pyright src/

# MyPy
mypy src/ --strict

# Rust
cargo check
```

## Test Coverage Gate

```bash
# Python
pytest --cov=src --cov-fail-under=80 --cov-report=term-missing

# JavaScript/TypeScript
npx vitest run --coverage --coverage.thresholds.uncoveredLines=80

# Go
go test ./... -coverprofile=coverage.out
go tool cover -func=coverage.out | grep "total:" \
  | awk '{if ($3+0 < 80) exit 1}'
```

### Coverage Thresholds

| Metric | Minimum |
|--------|---------|
| Line coverage | 80% |
| Branch coverage | 70% |
| Function coverage | 85% |

## Security Scan Gate

```bash
# Dependency scanning
npm audit --audit-level=high
pip-audit
go list -m all | xargs -I{} go install golang.org/x/vuln/cmd/govulncheck@latest
govulncheck ./...

# SAST
semgrep --config=auto src/
 Bandit
bandit -r src/ -ll

# Container
trivy image myapp:latest
```

## Pre-Merge Checklist

```yaml
# .github/workflows/quality-gate.yml
name: Quality Gate
on: [pull_request]
jobs:
  gate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Lint
        run: ruff check . && eslint src/
      - name: Type Check
        run: mypy src/ && npx tsc --noEmit
      - name: Tests
        run: pytest --cov=src --cov-fail-under=80
      - name: Security Scan
        run: semgrep --config=auto . && npm audit --audit-level=high
```

## Gate Results Format

```
## Quality Gate: FAILED

| Gate | Status | Details |
|------|--------|---------|
| Lint | PASS | 0 violations |
| Type Check | FAIL | 3 errors in auth.ts |
| Coverage | PASS | 84.2% lines |
| Security | PASS | No vulnerabilities |

## Action Required
Fix type errors before merge:
- auth.ts:45 — Object is possibly 'undefined'
- auth.ts:112 — Argument of type 'string | null' is not assignable
- auth.ts:203 — Property 'id' does not exist on type 'User'
```

## Escalation Rules

| Condition | Action |
|-----------|--------|
| Lint count > 10 | Block merge, require team review |
| Type errors > 5 | Block merge, require author fix |
| Coverage drop > 5% | Warn, require justification |
| High/critical vuln | Block merge immediately |
| All gates pass | Auto-approve for merge |
