---
name: project-audit
description: Deep read-only audit of a project's root folder and all reachable files to find redundancy, exact/near duplicates, dead or unreferenced files, outdated documentation, misconfigured config files, and orphaned dependencies. Produces a prioritized, confidence-scored cleanup plan and NEVER deletes without confirmation. Use when the user says "audit my repo", "find dead code", "clean up the project", "find duplicate files", "orphaned dependencies", "what can I delete", "project health check".
---

# Project audit — find what's stale, dead, or duplicated

This skill is **read-only until the user approves** specific cleanup actions.
It produces a prioritized, confidence-scored report; it never deletes, never
runs `rm`, and never unpublishes. False positives kill trust, so we require
**three independent signals** before flagging a file "verified-safe-to-delete".

## 0. Scope and safe-exclusion

Walk the project root, but **always** exclude:
- Version control: `.git/`, `.hg/`, `.svn/`
- Build output: `dist/`, `build/`, `target/`, `out/`, `*.min.js`
- Dependency dirs: `node_modules/`, `.venv/`, `venv/`, `__pycache__/`,
  `target/`, `bin/obj/`
- Editor/OS cruft: `.idea/`, `.vscode/` (keep settings.json/, only skip cache),
  `.DS_Store`, `Thumbs.db`
- Auto-generated docs under `docs/api/` produced by typedoc/sphinx/mkdocs.

Record the exclude set so the user can verify nothing was unfairly skipped.

## 1. Inventory (one pass, store results in memory)

For every file included:
- path, size, hash (SHA-256 for small/medium files; only size for >50MB),
- language (from extension; flag `.txt`/`.md` separately as docs),
- last commit date (`git log -1 --format=%ct -- <path>`),
- importer count (zero-by-default; populated in §3).

## 2. Duplicates

### A. Exact duplicates (binary-safe)
Group by SHA-256. Any group with >1 file is an exact-duplicate. Keep the one
that:
- lives closest to the project root (less likely to be the leftover), OR
- has the newest commit date, OR
- is referenced by code/docs (prefer keeping the referenced copy).

Always report **all** copies; let the user pick which to keep — never assume.

### B. Near-duplicates (name confusion)
Two files in the same dir differing only by extension, version suffix, or
`_old`/`_bak`/`_v2`/`-copy`/`-new` → flag as a likely rename/remnant pair.
Inspect both before recommending deletion: the older one may still be the live
import target if the newer was an abandoned rewrite.

## 3. Dead / unreferenced files (the hardest call)

A "dead" file is one no other file imports, references, or chains to. **This
has the highest false-positive rate** — be careful.

Order of evidence (collect in this order, stop early when you find a hit):

1. **Static importer search** with `ripgrep`:
   - `rg -l --no-ignore "<basename-without-ext>"` (covers Python/JS/TS imports
     that drop the extension).
   - `rg -l --no-ignore "<basename-with-ext>"` (covers markdown links, shell
     paths, config refs).
2. **Build-manifest check**: is the file in `package.json#files`, `pyproject`
   `[tool.*.packages]`, `Cargo.toml` `[[bin]]`, `tsconfig.include`? If so → it
   IS a published entry point; not dead.
3. **CI / Dockerfile mention**: `rg -l "<path>" .github/ Dockerfile* docker/` —
   the file may only be referenced at build/deploy time.
4. **Dynamic loader / globbed dir**: e.g. `fastapi.APIRouter` populated by
   `app.include_router(*glob.glob("routers/*.py"))`, or a Flask
   `Blueprint` auto-import. Detect: `rg -l "glob\(|importlib|require.context|(
   __import__|pkgutil.walk_packages"`. Files in those globs are NOT dead.
5. **Fixtures / test data**: lives under `tests/fixtures/` or `__tests__
   /fixtures` → not dead by definition; the test suite references them.
6. **Static-only assets**: `favicon.ico`, `robots.txt`, `manifest.json`, files
   under `public/` / `static/` / `assets/` → served verbatim, never imported.
   Not dead.

If all six signals are **negative**, you can call it dead with confidence→MED.
Three independent negatives required before HIGH-confidence dead call.

### Stale-doc detection (subset of dead-detector)
A doc is "stale" when it references a path or symbol that no longer exists:
- For each `README.md` link of form `[text](./src/foo.py)` or `[text](./docs/x
  .md)`, check the target exists.
- For each fenced "Installation" block listing a pinned version, check the
  version matches the canonical config (see `docs-sync` skill §1).
- For each symbol reference like `@see MyClass`, check the symbol still exists
  via ripgrep.

Stale refs are deadness of the **reference**, not the file. Report them as
"docs/reference drift" rather than "delete this doc".

## 4. Misconfigured configs

Run a parse check on every config file:
- JSON: `node -e "JSON.parse(require('fs').readFileSync(f,'utf8'))"` or `jq empty`.
- YAML (with optional schema): `yq` or `python -c "import yaml; yaml.safe_load_all(open(f))"` (catches tabs-vs-spaces, duplicate keys).
- TOML (Python ≥3.11): `python -c "import tomllib; tomllib.load(open(f,'rb'))"`.
- `tsconfig.json`: `tsc --showConfig` parses it; exit-ne-non-zero = broken.
- `package.json`: `npm ls --depth=0 >/dev/null` flags it.

Flag anything that fails to parse — those break the user's tool silently. Also
flag common smell: `package.json` entry missing `"name"`; `tsconfig.json`
missing `"include"`; `pyproject.toml` with `[build-system]` but no `build-
backend`; `.github/workflows/*.yml` missing `on:`.

## 5. Orphaned dependencies

Dependency in the manifest file that no source file imports:
- JS: `depcheck` (or heuristic — `rg -l "require\(['\"]<pkg>['\"]\)|from
  ['\"]<pkg>['\"]"`).
- Python: `pipreqs`/`pip-missing-reqs` against imports in `*.py`.
- Rust: `cargo machete` (or `cargo udeps` for accurate but nightly-only).
- Go: `go mod tidy --diff` then `go vet ./...`.

Also flag the **reverse**: imports in code with no manifest entry (would fail
fresh install). Distinguish `devDependencies` from `dependencies` before
flagging.

## 6. Prioritization and confidence

Each finding carries a 3-level priority and 3-level confidence:

| priority | description                                         |
|----------|-----------------------------------------------------|
| P1       | blocks the build / produces a wrong product          |
| P2       | slows the team or hides bugs                        |
| P3       | hygiene                                             |

| confidence | meaning                                              |
|------------|------------------------------------------------------|
| HIGH       | verified by 3+ independent signals                   |
| MED        | verified by 2 signals or single very strong one      |
| LOW        | single weak signal (surface, don't action)          |

Only **P1** or **P2 + HIGH** are actionable. The rest go in "FYI" sections.

## 7. Output (read-only report, before any edits)

```
PROJECT AUDIT — <root> (excluded: <dirs>)

P1 — fix soon:
  [1] misconfig · package.json:12 · `"browser"` field is malformed JSON ·
        `npm ls` errors; fix the trailing comma.
  [2] dead      · src/old_api.py · 0 imports, not in pyproject `[tool.setuptools
        .packages]`, not in CI. HIGH confidence (4 signals). Keep? delete?
  ...

P2 — recommended:
  [3] dup exact · { assets/logo.svg, public/assets/logo.svg } · same SHA-256 ·
        keep public/assets/logo.svg (referenced in index.html).
  [4] orphan dep · "marked" in package.json#dependencies · 0 imports · run
        `npm uninstall marked` (verify no dynamic require).
  ...

P3 / FYI:
  11 files > 90 days untouched since last commit. No action needed unless
  you're pruning stale experiments.

DOCS DRIFT (delegated to docs-sync skill):
  README.md L42: links to ./src/old_api.py which is dead (cf. [2]).
  CONTRIBUTING.md L88: claims `npm test` runs jest; package.json has node:test.

NEXT: reply "apply [n]" for any P1/P2 item you want me to action. Edits are
shaped against your current branch; deletions open a draft PR for review.
```

## 8. Hard limits (non-negotiable)

- Never run `rm`, `del`, `Remove-Item`, or `git rm`. The most this skill does is
  open a draft PR with proposed deletions for human review.
- Never delete a file with **less than HIGH confidence**, even if asked.
- Never run `rm -rf`, `git reset --hard`, `--force`, or `--no-verify`.
- Files older than 90 days without commits ≠ dead — they may be stable
  infrastructure code. Don't list them as actionable, only as FYI.
- A file imported **only** by tests is NOT dead and NOT orphaned.
- If a "dead" file is referenced in `node_modules/`, in `dist/`, or anywhere in
  the exclude set, that reference does NOT count — go back to source.
- Don't trust `git log --follow` to track renames for "files older than…"
  reasoning — it's heuristic. Mark confidence MED.