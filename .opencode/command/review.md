---
description: Run a defect-first code review on a change (uncommitted, base-branch diff, or commit range). Returns actionable findings only.
agent: reviewer
model: anthropic/claude-sonnet-4-5-20250929
subtask: true
---

Load the `code-review` skill and review the change specified by `$ARGUMENTS`.

`$ARGUMENTS` may be one of:
- (empty)              → review `git diff` + `git diff --staged` + untracked files on the current branch.
- `--pr`               → review `origin/main...HEAD` (the open PR's base-branch diff).
- `<sha1>..<sha2>`     → review that commit range.
- `<sha>`              → review that single commit.

Run the pre-flight automated checks (§1 of the skill) before the manual pass.
Return the report format from §4. No edits; you are read-only.