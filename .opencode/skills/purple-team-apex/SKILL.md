---
name: purple-team-apex
description: Autonomous Purple Team Apex — red↔blue orchestration, control validation, and remediation bridging. Powered by uncensored orchestrator models.
version: 2.0.0
author: FreeAI Security
license: MIT
models: [venice/qwen-edit-uncensored, freeai/qwythos-v2-9b, freeai/moe-13b]
requires: [router, agents/api, quantum-c2-operator, reporting-auditing]
---

# Purple Team Apex — Orchestrator & Validator

> Orchestrator model: `venice/qwen-edit-uncensored` + `freeai/qwythos-v2` (reasoning). Router hint `agent: purple`. Temp 0.3 for planning, 0.1 for scoring.

## When to Use
- `purple team`, `exercise`, `orchestrate`, `validate`, `bridge`, `score`, `continuous improvement`, `ATT&CK`
- Triggers: "run purple exercise", "validate control", "bridge finding", "score exercise"

## Autonomous Loop (APEX — 5 Phases)

1. **DESIGN** — Threat-informed exercise (APT29/FIN7/ransomware)
   - `attack-chain-orchestrator` + `agent-team-orchestration` → 5-8 steps with MITRE IDs, red tool, blue control, scoring rubric, safety rails

2. **ORCHESTRATE** — Live inject coordination
   - `quantum-c2-operator` + `quantum-c2-swarm-activator` → next inject, expected detection (rule + ETA), actual vs expected, coaching without spoiling

3. **VALIDATE** — Control effectiveness
   - `framework-certifier` + `quantum-build-verify` → lab reproduce, observe block/alert, test evasion variants, log completeness check

4. **BRIDGE** — Red finding → Blue ticket
   - `reporting-auditing` → root cause, ranked fixes (effort/owner), Sigma/KQL draft, re-test inject, risk reduction %

5. **SCORE** — `compliance-validation` + `ROADMAP.md` maturity → per-step 0-3, aggregates (MTTD/MTTR), ATT&CK heatmap, trend, navigator JSON

## Apex Improvements
- **Before:** Single exercise, no scoring. **Now:** Full program mgmt (quarterly roadmap, KPI dashboard spec, resource plan), navigator layer export, continuous improvement loop.
- **Swarm:** Parallel sub-agents for multi-phase exercises; auto-retry with variant TTPs if blue misses.

## FreeAI Integration
- **API:** `POST /agent/purple {operation, threat_actor, objective, exercise_id, control_id}` 
- **Dashboard:** Providers panel + SDLC Runs + `/api/status` idle banner (eco enforced) shows exercise state via `updateIdleBanner` pattern
- **Workflows:** `workflow/ui/designer.html` → purple step type (consumes red IOCs, produces bridge tickets)

## Verification
- Each control re-tested via red variant; score only counts if log source exists.
- Artifacts: `_run.json` + Quantum JSONL + ATT&CK navigator + exec/technical/purple reports
