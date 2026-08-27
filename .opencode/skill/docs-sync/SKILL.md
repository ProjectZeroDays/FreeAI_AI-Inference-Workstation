---
name: docs-sync
description: Keep README, CONTRIBUTING, and wiki in sync with the code. Detect drift ( scripted commands missing from README, env vars undocumented, CLI flags stale, version pins in docs that disagree with package.json ) and propose targeted diffs. Use when the user says "sync docs", "fix outdated README", "regenerate API docs", "update the wiki", "docs are behind", "rebuild docs".
---

# Docs sync — drift detection and repair

Docs rot faster than code. This skill is **propose-then-apply-on-confirm**: it
edits the docs only after the user (or coordinator) says "yes" to the proposed
diffs. Hand-written prose is treated as a source of truth — we don't rewrite it;
we only fix verifiable facts that drifted.

## 0. Decide what docs surfaces exist

Inspect (in order):
1. `README.md` — install commands, environment variables, scripts, CLI usage.
2. `CONTRIBUTING.md` — dev setup, test/lint commands, commit conventions.
3. `docs/` (or `wiki/`, or `.github/wiki/`) — long-form references.
4. Auto-generated API docs — `docs/api/`, `typedoc.json`, `mkdocs.yml`,
   `conf.py`/`.readthedocs.yaml`, `sphinx` config.
5. Badges in the top of `README.md` (CI, coverage, version, license).

If none of these exist, the deliverable is **not** to invent them — surface the
gap and let the user decide. This skill syncs; it doesn't doc-from-scratch (that's
the `documentation-generator` skill, if you have it).

## 1. Drift signals and how to detect each

### A. Script drift (`package.json`/`pyproject.toml`/`Makefile` vs README)
- Extract the live script names from the canonical config.
- Extract script names mentioned in README's "Scripts" section.
- Any script present in config but absent from README → drift (add a row).
- Any script mentioned in README that doesn't exist → drift (delete or fix).

### B. Env var drift (`.env`/`.env.example`/`config/*.ts` vs README)
- Grep the codebase for `process.env.<VAR>` / `os.getenv("<VAR>")` /
  `std::env::var("<VAR>")`.
- Cross-reference against `.env.example` and the README "Environment" section.
- A var read in code but missing from `.env.example` → drift (most important
  kind, because new contributors hit it first).
- A var in `.env.example` that's no longer read → drift (delete with care; could
  be a `require()`'d alias).

### C. CLI flag drift (commands defined in code vs README)
- For a Node CLI: parse commander/clipanion/yargs option defs; for Python:
  argparse groups in `main()`; for Go: `flag` block in `main()`.
- Compare with the `--help` output captured in the README as a fenced block.
- Re-run `<binary> --help` if safe, diff against the README block.

### D. Version-pin drift (docs pin a version; code uses a different one)
- Sample: `requires Python >=3.11` in README vs `python_requires=">=3.10"` in
  `pyproject.toml`; `Node 20+` in README vs `"engines": { "node": ">=20.11" }`
  in `package.json`.
- Same for Docker base images, CI matrix versions in `.github/workflows`.

### E. Code-symbol drift in API docs (auto-generated)
- For auto-generated docs (typedoc, sphinx-autodoc, mkdocstrings, godoc), the
  fix is to **regenerate**, not hand-edit.
- Run the generator, capture the diff, commit it as `docs(api): regenerate`.
- Don't commit a giant regenerated diff at the same time as a prose fix —
  reviewers can't read it. Separate PRs.

### F. Badge drift (top of README)
- Shields.io badges with a hardcoded version or coverage number that disagrees
  with the latest tag or coverage report.

## 2. The sync routine (proposed diffs, not direct edits)

For each drift found, prepare a precise edit, then **batch** the proposal:

1. Read the affected doc section in full before editing (don't blind-edit).
2. Match the doc's existing tone/formatting/markdown flavor (GFM vs CommonMark).
3. Apply minimal-change edits. Don't re-wrap paragraphs unless they're malformed.
4. Generate a single **proposed-diff preview** in your final message, grouped by
   file. Show the user:
   - the old line(s),
   - the new line(s),
   - one-line rationale.
5. **Wait** for the user or coordinator to say "apply". Then `edit` each file.

## 3. Wiki table of contents and anchor links

For a wiki (`docs/wiki/` or repo wiki pages):
- Rebuild the TOC from the real headings (`grep -E "^#+ " wiki/*.md`).
- Anchor links in GFM are lowercased, spaces→hyphens, punctuation stripped. Verify
  every TOC entry points at a real heading before committing.
- Don't invent anchor targets — if a wiki page is missing a section the TOC
  references, the fix is to add the section **and** write real content, not a
  placeholder.

## 4. Auto-generation boundaries

- Typedoc/jsdoc/sphinx/mkdocs → output goes into a path under `docs/api/` that's
  git-ignored or committed depending on project convention. Follow the existing
  convention; if the project has a build step for docs (e.g. `npm run docs`),
  prefer that over regenerating ad hoc.
- Don't hand-edit auto-generated `docs/api/*.html` or `*.md` files. Each
  regeneration will blow away your edits and create noise in the diff.

## 5. Output format

```
DOCS AUDIT:
  README.md              4 drifts (2 scripts, 1 env var, 1 version pin)
  CONTRIBUTING.md        0 drifts
  docs/api/             regeneration required (3 new exports)
  badges                 CI badge points at removed workflow

PROPOSED DIFF (preview; not applied):
  README.md:
    -  ## Scripts
    -  - `npm run maintain` — Run the maintenance bot.
    +  - `npm run maintain` — Run the maintenance bot.
    +  - `npm run coverage` — Generate coverage report (new).
       rationale: package.json gained `coverage` in v0.2.0; README missing it.
    ...
  docs/api/: run `npm run docs` and commit separately.

CONFIRM? reply "apply docs-sync" to make these edits.
```

## 6. Hard rules

- Only edit doc files — never source code under this skill. If a "drift" is
  actually a bug in the code (reads a var but the var is wrong), close this skill
  and open a `coder` task.
- Don't rewrite hand-authored prose. Fix facts, not voice.
- Don't add badges that hide the build status if it's actually red — sync to
  *current* state, not aspirational state.
- Never edit auto-generated API docs by hand; regenerate.
- Always run on a clean working tree so the user can `git diff` after applying.