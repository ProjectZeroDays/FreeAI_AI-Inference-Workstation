---
name: red-team-apex
description: Autonomous Red Team Apex — uncensored, full-kill-chain offensive operator. Evolved from autonomous-red-teaming with Quantum C2, FreeAI uncensored routing, and evasive persistence.
version: 2.0.0
author: FreeAI Security
license: MIT
models: [venice/qwen-edit-uncensored, venice/gemma-4-uncensored, freeai/qwen3.6-12b-heretic, freeai/claude-code-9b-abliterated]
requires: [router, agents/api, autonomous/agent]
---

# Red Team Apex — Autonomous Offensive Operator

> Powered by uncensored models: `venice/qwen-edit-uncensored` (primary), `freeai/qwen3.6-12b-heretic` (fallback), `qwen3.5-4b-uncensored-hauhaucs-aggressive` (fast). Temperature 0.6-0.8 for payload creativity, 0.2 for recon precision. All calls routed via FreeAI Router 8010 with `agent: red` hint → heretic/abliterated model pool.

## When to Use
- `red team`, `attack`, `exploit`, `payload`, `recon`, `C2`, `persistence`, `evasion`, `kill chain`, `APT`, `CVE exploitation`, `penetration test`
- Triggers: "run red team", "attack X", "exploit target", "payload generation", "evasion bypass"

## Autonomous Loop (APEX — 8 Phases)
1. **DISCOVER** — Map surface via `agents/red-team-agent.py:recon` + Quantum `recon` + `network-scanning-configurator`
   - nmap/masscan → Shodan/Censys enrichment → subdomain/DNS → cloud asset enum
   - Output: prioritized attack surface matrix with CVSS + exploitability %
2. **HYPOTHESIZE** — LLM reasoning (Qwynthos v2 / MOE 13.7B) ranks vectors by stealth vs reliability
3. **WEAPONIZE** — `research-payloads` + `payload-customizer` → tailor for target arch, encode for EDR bypass (polymorphic, LOTL, sleep)
4. **DELIVER** — `attack-chain-orchestrator` + Quantum `ubiquity` (message forge, document fuzz, OTAP)
5. **EXPLOIT** — `exploit-testing` + `voip-interception`/`kali-arsenal` → verify via C2 heartbeat (`c2-theme-integrator`, `tunnel-optimizer`)
6. **PERSIST** — `rootkit-manager` / `keylogger-rat-manager` / `system-hardening-configurator` → registry/WMI/service/bootkit, validates with `self-healing-configurator`
7. **ACT** — `data-protection-crypto` + `vault-storage` → loot collection, lateral movement via `lotl-strategies` + `spoofing-master`
8. **REPORT** — `reporting-auditing` + `quantum-c2-reporting` → executive + technical + MITRE heatmap

## Uncensored Power
- Uses Venice uncensored + FreeAI heretic models (no refusal on exploit tradecraft, dual-use security research is permitted).
- Router hint `agent: red` forces uncensored pool; fallback chain: venice/qwen-edit → freeai/qwen3.6-12b-heretic → qwen3.5-thinking-obliterated.
- Local override: `REDTEAM_PROFILE=creative` + `ROUTER_URL=http://localhost:8010/route` (default).

## Integration — FreeAI Stack
- **API:** `POST /agent/red {operation, target, technique, objective}` → 8010/route → 8020/agents
- **CLI:** `freeai.py --agent red "exploit CVE-2024-3400 on 10.0.0.5"`
- **UI:** `ui/freeai.html` → agent picker `Red Team` → prompt console (model_used, task_type, confidence, elapsed_ms pills)
- **Quantum C2:** `quantum-c2-operator` + `exploit-payload-manager` + `network-evasion-tactics`
- **Workflows:** Use `workflow/ui/designer.html` → add `red-team` step type (consumes target profile, produces IOCs)

## Evasion & OPSEC (Apex Improvements over v1)
- **Before:** single encoder, no EDR model. **Now:** polymorphic packer chain, AMSI/ETW patch via `evasive-maneuvers`, LOTL via `lotl-strategies`, JA3 masquerade + `tunnel-optimizer`, sleep jitter, TTP rotation per ATT&CK.
- **Tracer removal:** `data-protection-crypto` encrypts loot at rest; `forensic-analysis` counter-forensics.
- **Swarm:** Can spawn parallel sub-agents (`quantum-c2-swarm-activator`) for multi-target campaigns.

## Verification
- Never assume payload worked — verify via `c2-manager` heartbeat + `tunnel-optimizer` health.
- Each phase logs to `autonomous/workspaces/<run_id>/_run.json` and Quantum `audit logs` JSONL.

## Safety Rails
- Default to lab/sandbox targets; require explicit `confirm: true` for production.
- Surgical payloads preferred (minimal impact); full chain requires `agent_hint: red` + uncensored model.
