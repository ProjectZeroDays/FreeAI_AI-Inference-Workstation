---
name: expert-wiki
description: Expert wiki auto-updater — scans docs/, hardware/, registry, and live API to regenerate a comprehensive wiki. Triggered by [WIKI-UPDATE].
version: 1.0.0
author: FreeAI Docs
license: MIT
---

# Expert Wiki

## Trigger
- `[WIKI-UPDATE]` in prompt, or `python scripts/generate_wiki.py`, or `POST /agent/purple {operation: improve}` with doc scope.

## Scans
- `docs/*.md` (INDEX, ARCHITECTURE, API, AUTONOMOUS-AGENTS, DEPLOYMENT, PROVIDERS, etc.)
- `hardware/PARTS-LIST.md`, `BUILD.md`, `docs/BUILD-SHEET.md`, `FIRST-BOOT-GUIDE.md`
- `registry/registry.json` (8-model roster), `config/runtime-settings.json`, live `GET /api/status`
- `mkdocs.yml` nav, `README.md` screenshots

## Generates
- `site/wiki.md` + `docs/wiki/` tree (if exists) with cross-linked pages per subsystem (Router, Agents, Workflow, Dashboard, Models, Hardware, Security)
- Updates `mkdocs.yml` nav if new pages added
- Embeds live model shelf, provider health, and hardware tables

## Verification
- `mkdocs build` must pass (yaml valid, no missing nav files)
- Every internal link `(...md)` resolves (stale lowercase check)
- `pytest -q` still 88/88 (does not touch code)

## Install
- Local: `cp -r .opencode/skills/expert-wiki ~/.config/opencode/skills/` + `~/.agents/skills/`
- GitHub: committed under `.opencode/skills/expert-wiki/` → CI sync job copies to runner
