---
name: release
description: Cut a versioned release — determine the semver bump from commits, update CHANGELOG (Keep a Changelog format), sign the tag, push with --follow-tags. Includes a rollback plan and never amends a published tag. Use when the user says "release", "cut a release", "bump version", "tag a release", "publish a new version", "ship a release".
---

# Release — semver + changelog + tag

Cut a release on the repo you live in. This skill is read-only *until* the user
confirms the proposed release artifacts (version number + CHANGELOG entry); then
it commits and tags exactly once.

## 0. Pre-flight gate (non-negotiable)

A release is a push to a shared ref. Never ship red.

1. `git status` — must be clean (no unstaged changes on the release branch).
2. `git fetch --tags origin` and confirm you're on the release branch (default
   `main`; override with `release.branch` if set).
3. Run the project's health gate (the `repo-maintenance` skill defines it):
   lint, typecheck, format check, tests. **All must pass.**
4. If any check fails → STOP. Report. Do not release. Do not "just this once."

## 1. Determine the bump

### SemVer rules (MAJOR.MINOR.PATCH)
- **MAJOR** — incompatible API changes. For `0.x.y` it's a **MINOR** instead
  (the public API isn't stable yet); bump to `1.0.0` only when the user says the
  API is now stable.
- **MINOR** — new features, backward-compatible.
- **PATCH** — backward-compatible bug fixes only.

A CHANGELOG-worthy entry can be PATCH-worthy as a fix but still warrant a
"notable" callout. Don't let a notable note push you to MINOR — bump level is
governed by *compatibility*, not newsworthiness.

### From commits (Conventional Commits -> bump)
Walk `git log <last-tag>..HEAD --format="%s"`:

| commit prefix                 | bump    |
|-------------------------------|---------|
| `feat!:` / `BREAKING CHANGE:`| MAJOR * |
| `feat:`                       | MINOR   |
| `fix:`, `perf:`, `refactor:`  | PATCH   |
| `docs:`, `test:`, `chore:`    | (none)  |

\* In `0.x`, `feat!:` is MINOR.
If you only see `docs/test/chore`, that's still a PACK-only bump (`0.0.x` →
`0.0.(x+1)`) so users get the change; flag it explicitly.

### Pre-release / build metadata
- `-alpha.1`, `-beta.2`, `-rc.1` for testing releases. Each pre-release series
  increments the trailing number; never reuse a pre-release tag.
- `+build.20260809` is build metadata, not part of precedence.

## 2. Generate the CHANGELOG entry

Use the "Keep a Changelog" format. Group commits under `Added`/`Changed`/`Fixed`/
`Deprecated`/`Removed`/`Security`. Verbs past tense, third person. One bullet
per user-visible change; collapse `chore:` commits into a single "Internal
dependencies and tooling" line.

Drop a new section at the top of `Unreleased` (the **next** version's slot):

```markdown
## [1.2.3] - 2026-08-09

### Added
- New `ratelimit_status` probe tool for breaker introspection. ([#42])

### Fixed
- `withRetry` no longer mutates shared state on partial failure. ([#47])

### Security
- Bump `requests` to patch CVE-2026-1234 (advisory linked in [#50]).
```

If `Unreleased` is empty after the bump, **delete** the empty `## [Unreleased]`
skeleton and add a fresh one above the new version. Compare-link footers
(`[#42]: ...`) go at the bottom of the file, not inline.

## 3. The release sequence (run only after user confirms §1+§2)

```
# 1. Bump version in the canonical file(s):
#    package.json, pyproject.toml [project.version], Cargo.toml version=,
#    VERSION file, go.mod (Go has no version; tag only). One source of truth.

# 2. Write CHANGELOG entry per §2.

# 3. Stage BOTH together as one atomic commit:
git add package.json CHANGELOG.md
git commit -m "chore(release): v1.2.3"

# 4. Annotated (and optionally signed) tag:
git tag -a v1.2.3 -m "v1.2.3"        # add -s for GPG sign, -Z? via ssh-key if configured

# 5. Push branch + tags atomically:
git push origin <release-branch>
git push origin --follow-tags

# 6. Publish artifacts if the project does that (npm publish, cargo publish,
#    gh release create --notes-file CHANGELOG.md's section, PyPI upload).
#    Each has its own credential step — don't assume. Confirm before publish.
```

## 4. Tag signing (optional)

- GPG: `git config tag.gpgSign true` then `git tag -s`.
- SSH: `git config gpg.format ssh` + `user.signingKey ~/.ssh/id_ed25519` then
  `git tag -s`.
- Defaults: if `git config tag.forcesigntrue` is unset, an **unsigned** annotated
  tag (`-a`) is fine for internal projects.

## 5. Rollback plan (know this before you run §3)

If something goes wrong before `git push` succeeds:
- `git tag -d v1.2.3` (deletes the local tag)
- `git reset --hard HEAD~1` (undoes the release commit; the only sanctioned
  hard-reset this skill permits)

If `git push` already succeeded:
- **Do NOT** rewrite the tag. A published tag is immutable. Instead cut a
  patch release (`v1.2.4`) titled "Revert the broken v1.2.3" with the revert
  commit, and update CHANGELOG with a `[Unreleased]` entry noting the revert.
- If the release shipped broken binaries (npm/PyPI): `npm deprecate` /
  `yank`/`hatch` accordingly per the registry's policy, then cut the patch.

## 6. Hard limits

- One release commit + one tag per release. No amend, no force-push of the
  release branch or the tag.
- Never overwrite an existing tag (`git tag -f`). If a tag with the name exists,
  STOP and ask the user — they may be re-cutting on a wrong branch.
- Never push tags without also pushing their commit (`--follow-tags`).
- Never auto-run publish steps (`npm publish`/`cargo publish`/`gh release create`)
  without explicit user confirmation in this turn. They are irreversible.
- Never release off `main` if your repo's release branch is `release/*` —
  confirm the branch naming first (`.github/workflows/release.yml` is the source
  of truth).

## 7. Output

```
PROPOSED:
  previous: v1.2.2
  next:     v1.2.3  (PATCH — 4 feat/ 7 fix commits since v1.2.2)
  changelog: 3 Added, 2 Fixed, 1 Security  (preview above)
  artifacts: <git tag only | npm publish | gh release create>

HEALTH: green  (lint ok, types ok, 184/184 tests pass)

CONFIRM? reply "yes release v1.2.3" to proceed, or edit the changelog section.
```

Wait for confirmation. After push, report tag URL + publish URL (if any).