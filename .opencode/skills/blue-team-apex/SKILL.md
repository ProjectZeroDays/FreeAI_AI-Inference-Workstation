---
name: blue-team-apex
description: Autonomous Blue Team Apex — uncensored, full-spectrum defensive operator. Evolved from autonomous-blue-ops with AI-driven hardening, hunting, and purple validation. Powered by uncensored reasoning models.
version: 2.0.0
author: FreeAI Security
license: MIT
models: [venice/gemma-4-uncensored, freeai/qwythos-v2-9b, freeai/qwable-9b]
requires: [router, agents/api, dashboard, resource_optimizer]
---

# Blue Team Apex — Autonomous Defensive Operator

> Powered by `venice/gemma-4-uncensored` (analysis), `freeai/qwythos-v2` (FTPO loop-fix, 1M ctx), `freeai/qwable-9b` (multimodal triage). Temp 0.1-0.3 for deterministic hardening. Router hint `agent: blue`.

## When to Use
- `blue team`, `defend`, `harden`, `detect`, `hunt`, `triage`, `forensics`, `compliance`, `SOC`, `incident response`
- Triggers: "harden system", "hunt APT", "triage alert", "compliance check", "SOC automation"

## Autonomous Loop (APEX — 6 Workflows)

### 1. Hardening
- **Surface Reduction:** `system-hardening-configurator` + `network-security-hardening` → disable services/ports, CIS/STIG apply, kernel tuning (audit, FIM)
- **Network:** `network-security-hardening` + `tunnel-optimizer` → firewall/IDS/IPS, segmentation, TLS, packet dispersal
- **Container/K8s:** seccomp/AppArmor/read-only rootfs, `azure-kubernetes` hardening

### 2. Hunting (APT)
- **TTP Mapping:** `apt-hunting-detection` + `forensic-analysis` → process tree, registry, shimcache, beaconing
- **IoC Correlation:** `network-monitoring-ops` (C2 heartbeat decode) + threat intel feeds
- **Queries:** Auto-generates KQL/Sigma/YARA with `azure-kusto` + `kusto` skill

### 3. Triage & IR
- `health-agent.sh` / `recovery-agent.sh` + `network-monitoring-ops` → fidelity, scope, timeline, containment (isolate host, block IOC), evidence preservation (memory/disk/pcap)

### 4. Forensics
- `forensic-analysis` + `hash-cracking` + `voip-interception` → super-timeline, malware static/dynamic, C2 decode, patient zero

### 5. Compliance
- `compliance-check` + `compliance-validation` + `reporting-auditing` → NIST 800-53/SOC2/ISO/CMMC scorecard, SSP/POA&M generation

### 6. Detection Engineering
- `network-monitoring-ops` → Sigma/Splunk/KQL per ATT&CK, tuning, dashboards (SOC/exec)

## Apex Improvements over v1 (autonomous-blue-ops)
- **Before:** CIS L1 only, single IoC feed. **Now:** CIS L2/STIG/NIST 800-53, multi-feed correlation, MLX-style anomaly baselines via `backtest-expert` + `resource_optimizer` telemetry.
- **Purple Validation:** Every hardening gap is re-tested via `autonomous-red-teaming` → detection gap heatmap → iterative fix.
- **Uncensored Reasoning:** Uses heretic models to reason about attacker tradecraft without refusal (defensive use is permitted).

## FreeAI Integration
- **API:** `POST /agent/blue {operation, target, telemetry, framework}` → heretic model pool
- **UI:** Dashboard alerts panel (GPU util/temp thresholds, service DOWN) + `/api/status` → `updateIdleBanner` style health
- **Watchdogs:** `supervisor.sh` (10s) + `health-agent` (30s) + `recovery-agent` (15s) + systemd `freeai-agents.service`
- **Optimizer:** `agents/resource_optimizer.py` hysteretic eco/balanced/performance + `SAMPLE_TELEMETRY=1` demo

## Metrics
- Coverage matrix (ATT&CK technique → log source → rule)
- MTTD/MTTR, detection/prevention rate, control coverage %
- Continuous: `dashboard/backend.py:get_gpu_stats()` + `listening_ports()` TCP fallback

## Safety
- Hardening requires `confirm: true` for production; lab default is dry-run + diff.
