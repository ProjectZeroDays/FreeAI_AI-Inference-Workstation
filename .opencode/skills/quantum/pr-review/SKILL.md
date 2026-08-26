---
name: pr-review
description: Review pull requests for the Quantum C2 project. Use when the user asks to review PRs, check recent changes, analyze code quality, or generate changelog summaries.
trigger_keywords: review PR, pr review, code review, review changes, changelog, analyze PR, check PRs
---

## Purpose
Review pull requests merged in the last 7 days, analyze code changes for quality/security/performance, generate succinct changelog summaries, create tracking issues, and suggest improvements.

## When to Use
- When user asks to "review PRs" or "check recent changes"
- After merges to generate changelog summaries
- Before releases to audit recent changes
- When asked to "analyze code quality" of recent PRs
- For security review of merged changes

## Workflow

### Step 1: Discover Repository Context

```bash
# Extract repo owner and name from remote
REMOTE_URL=$(git remote get-url origin)
OWNER_REPO=$(echo "$REMOTE_URL" | sed -E 's|.*github\.com[:/]||; s|\.git$||')
OWNER=$(echo "$OWNER_REPO" | cut -d/ -f1)
REPO=$(echo "$OWNER_REPO" | cut -d/ -f2)

# Verify GitHub auth
gh auth status
```

### Step 2: List Recent Merged PRs (Last 7 Days)

```bash
# List merged PRs in the last 7 days
gh pr list --state merged --limit 30 --json number,title,author,mergedAt,labels,additions,deletions,changedFiles

# Alternative with curl:
curl -s -H "Authorization: token $GITHUB_TOKEN" \
  "https://api.github.com/repos/$OWNER/$REPO/pulls?state=merged&per_page=30" \
  | python3 -c "
import sys, json
from datetime import datetime, timedelta
seven_days_ago = (datetime.utcnow() - timedelta(days=7)).isoformat() + 'Z'
for pr in json.load(sys.stdin):
    if pr.get('merged_at', '') >= seven_days_ago:
        print(f\"#{pr['number']}  {pr['title']}  merged: {pr['merged_at'][:10]}\")"
```

### Step 3: Analyze Each PR

For each PR, gather full details:

```bash
# Get PR details
gh pr view <NUMBER> --json title,body,author,mergedAt,labels,additions,deletions,changedFiles,reviewDecision

# Get the diff
gh pr diff <NUMBER>

# Get files changed
gh pr changed-files <NUMBER>

# Get review comments
gh pr view <NUMBER> --comments
```

### Step 4: Code Quality Analysis

Analyze each PR's diff for:

**Correctness:**
- Logic errors, off-by-one mistakes
- Unhandled edge cases
- Broken control flow
- Incorrect type handling

**Security (Critical for Quantum C2):**
- Hardcoded secrets or credentials
- SQL/command injection vectors
- Unsafe deserialization
- Missing input validation
- Authorization bypasses
- Information leakage in logs/errors
- Cryptographic weaknesses

**Performance:**
- N+1 queries or unbounded database calls
- Memory leaks or unbounded growth
- Blocking operations in async contexts
- Inefficient algorithms

**Code Quality:**
- Adherence to project conventions (see `debug-workflow` skill)
- Naming consistency
- Duplicate code
- Missing error handling
- Comment quality

```bash
# Run targeted security checks on changed files
SECURITY_FILES=$(gh pr diff <NUMBER> | grep "^+" | grep -v "^+++" | awk '{print $1}' | tr -d ' ')
ruff check <changed_files> --select=S,E,W,F
bandit -r <changed_dirs> -ll
```

### Step 5: Generate Changelog Summary

For each PR, produce a succinct entry:

```
## Change Summary (<date>)

### #<NUMBER> - <title> (<author>)
- **Type:** bugfix | feature | refactor | docs | chore
- **Files changed:** <count>
- **Lines:** +<additions> / -<deletions>
- **Summary:** <1-2 sentence description of what changed and why>
- **Security:** clean | flagged | needs review
```

Aggregate into a grouped changelog:

```
## Changelog (Last 7 Days)

### Features
- #<N> - <title>: <one-line description>

### Bug Fixes
- #<N> - <title>: <one-line description>

### Security
- #<N> - <title>: <one-line description>

### Refactoring
- #<N> - <title>: <one-line description>

### Dependencies
- <package>: <version change>
```

### Step 6: Create Tracking Issues

When a PR reveals follow-up work, bugs, or technical debt:

```bash
# Create issue for follow-up work
gh issue create \
  --title "Follow-up: <description>" \
  --body "## Context
Related to PR #<NUMBER> (merged <date>).

## Description
<Clear description of the follow-up work needed>

## Acceptance Criteria
- [ ] <criterion 1>
- [ ] <criterion 2>

## Original PR
- #<NUMBER>" \
  --label "follow-up"
```

```bash
# Create issue for discovered bug
gh issue create \
  --title "Bug: <description>" \
  --body "## Context
Discovered during PR #<NUMBER> review.

## Description
<Bug description>

## Steps to Reproduce
1. <step>

## Expected Behavior
<expected>

## Actual Behavior
<actual>" \
  --label "bug,priority:high"
```

### Step 7: Suggest Improvements

For each PR, provide actionable improvement suggestions:

```
## Improvement Suggestions

| Priority | Suggestion | File | Line |
|----------|-----------|------|------|
| P0 | <description> | <path> | <line> |
| P1 | <description> | <path> | <line> |
| P2 | <description> | <path> | <line> |
```

Only suggest changes to code introduced by the PR, not pre-existing issues.

## Review Output Format

Present the full review as:

```
## PR Review Report

**Period:** <start date> to <end date>
**PRs Reviewed:** <count>
**Overall Status:** All Clean | Needs Attention | Issues Found

### Changelog
<generated changelog>

### Security Findings
<list any security concerns, or "No security issues detected">

### Quality Findings
<list P0/P1 findings, or "No quality issues detected">

### Tracking Issues Created
<list any follow-up issues created, or "None">

### Improvement Suggestions
<aggregate suggestions across all PRs>
```

## Notes
- Review only PRs merged in the last 7 days unless told otherwise
- Use `gh pr diff <NUMBER>` to get the actual code changes
- Prioritize security findings given the nature of Quantum C2
- Never suggest changes to pre-existing code outside the PR scope
- Reference existing skills: `debug-workflow` for common errors, `security-audit` for deep security checks
- Check `.learnings/ERRORS.md` for previously found patterns in recent changes
