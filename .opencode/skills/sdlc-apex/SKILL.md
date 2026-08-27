---
name: sdlc-apex
description: Autonomous SDLC Apex — full lifecycle orchestrator with security gates (red/blue/purple), powered by uncensored heretic models and FreeAI router fallback chains.
version: 2.0.0
author: FreeAI Engineering
license: MIT
models: [freeai/qwen3.6-12b-heretic, freeai/moe-13b, freeai/claude-code-9b-abliterated, venice/qwen-edit-uncensored]
requires: [autonomous/agent, router, workflow/engine, dashboard]
---

# SDLC Apex — Full Lifecycle Orchestrator

> Lifecycle: `queued → planning → coding → testing → fixing → reviewing → documenting → packaging → done|failed|cancelled` (see `docs/AUTONOMOUS-AGENTS.md`). Now with **security gates**.

## Apex Phases (Extended)

1. **PLANNING** — `PLAN_PROMPT` → JSON plan (tasks with files) → `parse_plan` (heretic model, temp 0.3)
2. **CODING** — `CODE_PROMPT` per task → `parse_file_blocks` → `Workspace.write_file` (path traversal guarded)
3. **TESTING** — `run_verification` (compileall/pytest/unittest/node --check) if `ENABLE_SHELL_TOOLS=1` else static scan
4. **FIXING** — `FIX_PROMPT` loop up to `MAX_FIX_ROUNDS=3` with real compiler output
5. **REVIEWING** — `REVIEW_PROMPT` → `parse_verdict` (PASS/FIX)
6. **SECURITY GATE (NEW)** — Purple validates: run `red-team-apex` recon on generated code → `blue-team-apex` harden → `purple-team-apex` bridge → block packaging if critical
7. **DOCUMENTING** — `DOC_PROMPT` → README + docs/API.md from final tree
8. **PACKAGING** — tar artifact `workspaces/<run_id>/_artifact.tar.gz`

## When to Use
- `sdlc`, `autonomous`, `full lifecycle`, `spec → project`, `unattended coding`
- Triggers: "build X", "auto-start", "run SDLC", "full dev lifecycle"

## Uncensored Power
- Uses heretic/abliterated pool for code gen without refusal on dual-use research tools.
- Router chain: `freeai/qwen3.6-12b-heretic` → `moe-13b` → `claude-code-9b-abliterated` → `venice/qwen-edit-uncensored` fallback.
- `profile: balanced` (0.2) for planning, `creative` (0.8) for coding, `strict` (0.0) for fixing.

## Integration
- **API:** `POST :8050/auto/start {spec, profile, max_tasks, enable_shell}` → run_id (see `autonomous/agent.py:start_async`)
- **CLI:** `freeai.py auto-start "Build FastAPI notes service" --watch`
- **UI:** Dashboard SDLC Runs panel + `/api/runs` polling
- **Safety:** `workspaces/<run_id>/` chroot-lite, shell requires `ENABLE_SHELL_TOOLS=1` + per-run `enable_shell:true`, cancellable at phase boundary

## Red/Blue/Purple Gates
- After `reviewing`, invoke `POST /agent/red {operation: chain}` on generated tree → `POST /agent/blue {operation: harden}` → `POST /agent/purple {operation: validate}`. Only `PASS` + no critical purple score proceeds to packaging.

## Artifacts
- `_run.json` (state), `_artifact.tar.gz` (downloadable), report (duration, tasks_failed, fix_rounds, review_verdict)
