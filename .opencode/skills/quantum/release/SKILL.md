---
name: release
description: Full release workflow for Quantum C2. Use when the user types [RELEASE] or asks to create a release, bump version, or tag and push a release.
trigger_keywords: release, RELEASE, create release, bump version, tag release, release workflow
---

# Quantum C2
**Opencode Skill — Release Workflow**

## Description

Use when the user types `[RELEASE]` or asks to create a release. This skill orchestrates the full release lifecycle: version bumping, building, testing, asset creation, tagging, GitHub release, and release note generation.

## Trigger Keywords

- `[RELEASE]`
- "create a release"
- "bump version"
- "prepare release"
- "run release workflow"
- "tag and push release"

---

## Prerequisites

Before running this skill, verify:
1. All changes are committed and pushed to the target branch
2. All CI/CD checks pass
3. Release notes are approved (if pre-written)
4. No merge conflicts exist
5. GitHub CLI (`gh`) is authenticated and configured

---

## Workflow

### Step 1: Determine New Version

Read current version from all relevant files:

```bash
# Read current versions
cat package.json | grep '"version"'
cat frontend/package.json | grep '"version"'
grep -m1 "^version" backend/setup.py 2>/dev/null || echo "No setup.py version"
grep "^__version__" backend/app/__init__.py 2>/dev/null || echo "No __init__.py version"
```

Determine the new version using semantic versioning:
- `patch` (X.X.x): Bug fixes, minor improvements
- `minor` (X.x.0): New features, backward-compatible changes
- `major` (x.0.0): Breaking changes, major architectural shifts

Confirm the version bump with the user before proceeding.

### Step 2: Bump Version in All Files

Update version in all required locations:

```bash
# 1. Root package.json
jq '.version = "X.X.X"' package.json > package.json.tmp && mv package.json.tmp package.json

# 2. Frontend package.json
jq '.version = "X.X.X"' frontend/package.json > frontend/package.json.tmp && mv frontend/package.json.tmp frontend/package.json

# 3. Backend .env (update version comment or env var)
sed -i '' 's/Quantum C2 v[0-9.]\+/Quantum C2 vX.X.X/' backend/.env
sed -i '' 's/Quantum C2 v[0-9.]\+/Quantum C2 vX.X.X/' .env

# 4. Backend __init__.py (if applicable)
sed -i '' 's/__version__ = "[0-9.]\+"/__version__ = "X.X.X"/' backend/app/__init__.py 2>/dev/null

# 5. setup.py (if applicable)
sed -i '' 's/version="[0-9.]\+"/version="X.X.X"/' backend/setup.py 2>/dev/null

# 6. docs/CHANGELOG.md — Add new version header at top
```

### Step 3: Update CHANGELOG.md

Generate release notes from git log since last tag:

```bash
# Get commits since last tag
git log $(git describe --tags --abbrev=0 HEAD^^ 2>/dev/null || git rev-list --max-parents=0 HEAD)..HEAD --pretty=format:"%s" | head -100
```

Append to `docs/CHANGELOG.md` at the top (before the `## [X.X.X]` header):

```markdown
## [X.X.X] - YYYY-MM-DD

### Added
- [List new features]

### Changed
- [List changes]

### Fixed
- [List bug fixes]

### Security
- [List security fixes]
```

Use conventional commit prefixes:
- `feat:` → Added
- `fix:` → Fixed
- `chore:` → Changed
- `refactor:` → Changed
- `security:` → Security
- `docs:` → Documentation

### Step 4: Build Frontend

```bash
cd frontend
npm ci --frozen-lockfile
npm run build
```

Verify build output:
```bash
ls -la dist/
echo "Frontend build successful — $(du -sh dist/ | cut -f1)"
```

### Step 5: Run Backend Tests

```bash
cd ../backend
python -m pytest tests/ -q --tb=short
```

Check test results:
- All tests passing: Continue to next step
- Some tests failing: Fix critical failures before releasing
- Test coverage < 80%: Warn user (but don't block release)

### Step 6: Test Coverage Audit and Improvement

Review recently merged changes and fill in missing tests wherever coverage is thin and the business impact is non-trivial.

**Review merged PRs from the last 7 days:**
```bash
# List merged PRs in the last 7 days
gh pr list --state merged --search "merged:>=$(date -d '7 days ago' +%Y-%m-%d)" --json number,title,mergedAt --jq '.[] | "\(.number)\t\(.title)\t\(.mergedAt)"'
```

**Focus on:**
- Newly introduced code paths that lack any tests
- Bug fixes where only the production code was touched
- Boundary conditions, parsing, concurrency, authorization, and input validation
- Common helpers and critical pathways whose failure would have wide-reaching effects

**Skip:**
- Low-value snapshot assertions that reveal little
- Coverage for purely visual or stylistic changes
- Behavior-preserving refactors, unless they leave important behavior unverified

**Identify untested paths:**
```bash
# Generate coverage report for recent changes
cd backend
python -m pytest tests/ --cov=app --cov-report=term-missing -q
# Review missing-coverage lines reported
```

**Write tests for gaps:**
- Add test files under `tests/` mirroring the module structure
- Use `pytest` fixtures for setup and shared state
- Include edge cases, error paths, and boundary conditions
- Run `pytest` to confirm all new tests pass before proceeding

**Create an issue summarizing the audit:**
```bash
gh issue create \
  --title "Test Coverage Audit — $(date +%Y-%m-%d)" \
  --label "testing,release" \
  --body "$(cat <<'EOF'
## Test Coverage Audit

### Scope
- Reviewed merged PRs from the last 7 days
- Focused on: new code paths, bug fixes, boundary conditions, authorization, input validation

### Findings
- [List uncovered code paths and gaps identified]

### Tests Added
- [List new test files / cases added in this release]

### Remaining Gaps
- [List areas still needing test coverage]

### Recommendations
- [Suggested follow-up testing work]
EOF
)"
```

### Step 7: Run Security Scans

```bash
# Ruff linter
ruff check app/

# Bandit security scan
bandit -r app/ -ll -x tests/

#npm audit for frontend dependencies
cd ../frontend
npm audit --production
```

Fix any critical security findings before proceeding.

### Step 8: Create Release Assets

Build platform-specific distribution packages:

```bash
# Create build directory
mkdir -p dist/releases

# Backend tarball (Linux)
tar -czvf dist/releases/quantum-c2-linux-amd64-X.X.X.tar.gz \
    --exclude='*.pyc' --exclude='__pycache__' --exclude='venv' \
    --exclude='node_modules' --exclude='.git' \
    backend/ docs/ configs/ requirements.txt

# Backend Windows zip
cd ..
powershell -Command "Compress-Archive -Path 'backend\app','backend\main.py','backend\requirements.txt','docs\','configs\','package.json' -DestinationPath 'dist\releases\quantum-c2-windows-amd64-X.X.X.zip' -Force"

# Frontend build (if standalone)
cd frontend
npm run build
cp -r dist/* ../dist/releases/quantum-c2-frontend-X.X.X/

# Create checksums
cd dist/releases
for f in *; do
    sha256sum "$f" > "${f}.sha256"
done
```

Asset inventory:
| Asset | Platform | Purpose |
|-------|----------|---------|
| `quantum-c2-linux-amd64-X.X.X.tar.gz` | Linux x64 | Production deployment |
| `quantum-c2-windows-amd64-X.X.X.zip` | Windows x64 | Windows deployment |
| `quantum-c2-macos-arm64-X.X.X.tar.gz` | macOS ARM64 | macOS deployment |
| `quantum-c2-frontend-X.X.X/` | All | Frontend build |
| `SHA256SUMS` | All | Integrity verification |

### Step 9: Push to GitHub

```bash
# Commit all changes
git add -A
git commit -m "release: bump version to X.X.X"

# Push to remote
git push origin main

# Create and push tag
git tag -a "vX.X.X" -m "Release vX.X.X

$(cat docs/CHANGELOG.md | sed -n '/## \[X.X.X\]/,/^## \[/p' | head -20)"
git push origin "vX.X.X"
```

### Step 10: Create GitHub Release

Use GitHub CLI to create the release with all assets:

```bash
# Generate release body from CHANGELOG
RELEASE_BODY=$(sed -n '/## \[X.X.X\]/,/^## \[/p' docs/CHANGELOG.md | head -30)

# Create release via GitHub CLI
gh release create "vX.X.X" \
    --title "Release vX.X.X" \
    --notes "$RELEASE_BODY" \
    --draft=false \
    dist/releases/quantum-c2-linux-amd64-X.X.X.tar.gz \
    dist/releases/quantum-c2-linux-amd64-X.X.X.tar.gz.sha256 \
    dist/releases/quantum-c2-windows-amd64-X.X.X.zip \
    dist/releases/quantum-c2-windows-amd64-X.X.X.zip.sha256 \
    dist/releases/SHA256SUMS

# If gh CLI fails, create via GitHub API
curl -X POST "https://api.github.com/repos/ProjectZeroDays/Quantum/releases" \
    -H "Authorization: token $GH_TOKEN" \
    -H "Content-Type: application/json" \
    -d '{
        "tag_name": "vX.X.X",
        "target_commitish": "main",
        "name": "Release vX.X.X",
        "body": "'"$RELEASE_BODY"'",
        "draft": false,
        "prerelease": false
    }'
```

### Step 11: Post-Release Verification

```bash
# Verify release exists
gh release view "vX.X.X"

# Verify tag on remote
git fetch origin vX.X.X
git log --oneline -1 vX.X.X

# Check CI/CD triggered
gh run list --branch main --limit 5
```

### Step 12: Update Documentation

Update the following files with the new version:
- `README.md` — Update version badge and stats
- `docs/getting-started/FEATURES.md` — Update any version-specific notes
- `docs/production/readiness-report.md` — Update readiness status
- `docs/reports/app-report.md` — Update metrics

### Step 13: Notify Stakeholders

Generate and distribute release notification:

```bash
echo "
Release vX.X.X has been published!

GitHub: https://github.com/ProjectZeroDays/Quantum/releases/tag/vX.X.X
Downloads:
  - Linux: dist/releases/quantum-c2-linux-amd64-X.X.X.tar.gz
  - Windows: dist/releases/quantum-c2-windows-amd64-X.X.X.zip

Changelog:
$(sed -n '/## \[X.X.X\]/,/^## \[/p' docs/CHANGELOG.md | head -20)
"
```

---

## Release Checklist

Before executing the release workflow, confirm:

- [ ] All code changes are committed and pushed
- [ ] CI/CD pipeline passes (all checks green)
- [ ] Tests pass locally (100% passing)
- [ ] Test coverage audit completed — gaps filled where business impact is non-trivial
- [ ] No critical security vulnerabilities (bandit, ruff clean)
- [ ] CHANGELOG.md updated with release notes
- [ ] Version bumped in all required files
- [ ] Frontend build succeeds
- [ ] Release assets created for all platforms
- [ ] GitHub tag and release created
- [ ] Assets uploaded to GitHub release
- [ ] Post-release documentation updated
- [ ] Stakeholders notified

---

## Release Commands Reference

```bash
# Create new patch release
[RELEASE] --patch

# Create new minor release
[RELEASE] --minor

# Create new major release
[RELEASE] --major

# Dry run (verify without pushing)
[RELEASE] --dry-run

# Skip tests
[RELEASE] --skip-tests

# Skip security scans
[RELEASE] --skip-security

# Skip test coverage audit
[RELEASE] --skip-coverage-audit
```

---

## Output Format

After release completion, provide:

```
[RELEASE] Complete

Version: X.X.X
Tag: vX.X.X
Release URL: https://github.com/ProjectZeroDays/Quantum/releases/tag/vX.X.X
Assets:
  - quantum-c2-linux-amd64-X.X.X.tar.gz (SHA256 verified)
  - quantum-c2-windows-amd64-X.X.X.zip (SHA256 verified)
  - SHA256SUMS
Tests: {N} passed, {M} failed
Security Scan: Clean
Frontend Build: Success
Changelog: Updated
Documentation: Updated

Next Steps:
  - Monitor CI/CD pipeline
  - Watch for user reports
  - Prepare hotfix if needed
```

---

## Constraints

- NEVER release without all tests passing
- NEVER skip security scans in production releases
- ALWAYS create a tag before creating the GitHub release
- ALWAYS generate SHA256 checksums for all release assets
- NEVER commit secrets or credentials to release assets
- ALWAYS verify the release URL after creation
- MAINTAIN backward compatibility unless explicitly breaking

---

## Success Criteria

- [ ] Version bumped in all files
- [ ] Frontend build successful
- [ ] All backend tests passing
- [ ] Test coverage audit completed and issue created
- [ ] Security scans clean
- [ ] Release assets created for all platforms
- [ ] GitHub tag created
- [ ] GitHub release created with all assets
- [ ] CHANGELOG.md updated
- [ ] Documentation updated
- [ ] Stakeholders notified

---

*Skill Version: 1.1*
*Last Updated: 2026-08-17*
