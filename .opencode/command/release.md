---
description: Propose a semver release — determine the bump from commits, draft a CHANGELOG entry, run the health gate. Waits for confirmation before committing/tagging.
agent: build
model: anthropic/claude-sonnet-4-5-20250929
subtask: true
---

Load the `release` skill and prepare a release proposal on the current branch.

`$ARGUMENTS` may be one of:
- (empty)              → infer the bump from commits since the last tag (`git describe --tags`).
- `patch`|`minor`|`major` → force that bump level (skill still validates the
  commit history is plausibly consistent with the chosen level).
- `--pre-release <alpha|beta|rc>` → cut a pre-release tag instead.
- `--dry-run` → produce the proposal + entry preview only; skip the health gate.

Run the §0 health gate, then §1 (bump determination) and §2 (CHANGELOG draft),
then show the §7 proposal block and **WAIT** for the user to reply
`yes release vX.Y.Z` before doing §3 (commit/tag/push). Do not auto-publish
(npm/PyPI/`gh release`); §3 step 6 always requires a separate user
confirmation in this turn.