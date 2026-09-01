---
name: readme-standard
description: "House README standard: structure, badge row, tone, per-archetype templates, and verification gates for steipete/openclaw repos."
---

# README Standard

One structure for every public README in the steipete and openclaw orgs. Load
this skill before writing or reviewing a README. The reference implementation
is [`openclaw/fs-safe`](https://github.com/openclaw/fs-safe) — read its README
first if unsure what "good" looks like.

## The spine

Every README answers, in order, with no detours:

1. **What is this?** — one sentence a stranger understands.
2. **How do I use it?** — smallest real install + a quickstart that *proves the pitch*.
3. **Progressively more complex** — each section assumes the previous one; deep
   reference material moves to `docs/` (or the docs site) and gets linked.

Concretely:

```
# <name> <one emoji> — <playful tagline, one line>

<badge row>

<1–2 sober sentences: what it is, who it is for. No adjectives doing the work
nouns should do.>

<OPTIONAL: one small code/terminal sample (≤10 lines) that demonstrates the
core value. If one sample can prove the pitch, put it here.>

## Install          ← smallest path first (brew/npm/npx), alternatives after
## Quick start      ← 60 seconds to first success; commands must actually run
## <core sections>  ← 2–6 sections, each one level deeper than the last
## Development      ← build/test/lint in ≤10 lines, link CONTRIBUTING if present
## License          ← one line
```

## Rules

- **Title/tone**: playful tagline with one emoji is welcome; the body is sober.
  First paragraph states plainly what the tool does and for whom.
- **No feature walls.** A list of >6 marketing bullets is a smell. Fold real
  capabilities into the sections where they are demonstrated.
- **No changelog-speak** ("now supports", "new in 3.2", "coming soon"). The
  README describes the present tense of the tool. Version-specific migration
  notes live in the changelog or `docs/`.
- **Length**: aim ≤250 lines for tools/libraries, ≤350 for large surfaces.
  Anything beyond that moves to `docs/` with a link. Exhaustive command/flag
  references belong in `docs/` or the docs site, never in the README — a
  summary table with links is fine.
- **Progressive depth**: a reader should be able to stop after any section and
  have a working setup for that level of use.
- **Screenshots/banners**: keep existing project art. Apps and TUIs should show
  one screenshot near the top. Compress; no >500 KB images.
- **Docs sites win**: when the repo has a docs site (fs-safe.io, gitcrawl.sh,
  …), the README is a front door, not a mirror. Link, don't duplicate.

## Badge row

Style: `flat-square`, always **dynamic** — a badge that can go stale is a bug.
Never hardcode versions into `img.shields.io/badge/...` URLs.

Order: CI · version · platform/runtime · license · extras (Homebrew, docs).

```markdown
[![CI](https://img.shields.io/github/actions/workflow/status/OWNER/REPO/ci.yml?branch=main&style=flat-square&label=ci)](https://github.com/OWNER/REPO/actions/workflows/ci.yml)
```

Per ecosystem, add what applies:

- **npm**: `https://img.shields.io/npm/v/PKG?style=flat-square` → npm page
- **GitHub release** (Go/Swift binaries): `https://img.shields.io/github/v/release/OWNER/REPO?style=flat-square`
- **Runtime/platform**: `npm/node/v` badge for npm packages; static
  `badge/platforms-...` or `badge/Swift-6.x-...` is acceptable for facts that
  only change with a commit (platforms, language version, min OS).
- **License**: `https://img.shields.io/github/license/OWNER/REPO?style=flat-square`
- **Homebrew**: static badge linking the tap, when a formula/cask exists.

Use the repo's *actual* workflow filename and default branch in the CI badge.
Verify every badge URL renders (HTTP 200 and not the shields "invalid" card)
before shipping.

## Per-archetype templates

**CLI tool (Go/TS binary)** — Install (brew → go install/npm), Quick start
(3–6 commands with one-line comments showing a real session), Commands
(summary table linking `docs/`), Configuration, JSON/automation output if
agent-facing, Development, License.

**npm library** — Install, one core-usage sample that compiles, then one
section per capability tier (basic → options → advanced/edge), API reference
link (docs site or generated docs), Development, License.

**Swift package** — badges (Swift version, platforms, CI), SPM install snippet
(both `Package.swift` lines), Quick start compiling sample, capability
sections, platform notes, Development, License.

**macOS app** — screenshot first, Install (brew cask → direct download link),
what-it-does tour keyed to the screenshot, permissions/setup notes,
Development, License.

**Web service / site** — what it is + hosted URL, self-host/deploy path,
local development, architecture pointer, License.

## Verification gates (all mandatory)

1. **Every command in the README runs.** Build the repo binary (or install the
   package) and execute each quickstart/example command, or validate flags
   against real `--help` output when execution needs credentials/hardware.
   Fix the README, not the transcript.
2. **Every code sample compiles/typechecks** against the current API (a scratch
   file in the repo's toolchain is enough).
3. **Every relative link resolves** to a file in the repo; every external link
   returns non-404; every badge renders.
4. **Version facts are dynamic or current**: no hardcoded package versions,
   stale minimums, or "coming soon" for shipped things. Check `package.json`/
   `go.mod`/`Package.swift` for the real runtime floors.
5. Existing factual content that gets removed from the README must either
   exist in `docs/` already, be moved there in the same PR, or be genuinely
   obsolete (state which in the PR body).
