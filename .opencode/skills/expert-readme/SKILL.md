---
name: expert-readme
description: Expert README auto-updater — scans codebase for new endpoints, models, and docs to keep README.md accurate. Triggered by [README-UPDATE].
version: 1.0.0
author: FreeAI Docs
license: MIT
---

# Expert README

## Trigger
- `[README-UPDATE]` or `python scripts/generate_readme.py` or any commit touching `router/`, `agents/`, `workflow/`, `dashboard/`

## Scans
- `router/router.py` endpoints + `agents/api.py` (+ red/blue/purple) + `workflow/api`, `autonomous/agent`
- `registry/registry.json` (model roster count, names), `dashboard/backend.py` (`/api/status` fields), `freeai.py` CLI
- `docs/CLOUD-FALLBACK.md`, `OPTIMIZATION-AUDIT.md`, `BUILD-SHEET.md`, screenshots in `docs/screenshots/`
- `mkdocs.yml` doc list, `VERSION`, `hardware/PARTS-LIST.md`

## Generates
- `README.md` §§ 3, 7, 12, 15, 20: badges (tests, version), model table (8-model), CI list (iso-build), hardware table, doc index
- Screenshot gallery order + captions (GRUB → freeai-cli → dashboard → FreeAI UI → designer/providers → model shelf → idle → desktop)
- Fixes stale `Ubuntu-Desktop...` refs, duplicate parentheticals, lowercase doc links

## Verification
- No `tokugawa` tokens remain (byte-level scan)
- `python -m py_compile` on touched `agents/api.py`, `dashboard/backend.py`
- `pytest -q` green

## Install
- Local + GitHub: same as expert-wiki (see that skill)
