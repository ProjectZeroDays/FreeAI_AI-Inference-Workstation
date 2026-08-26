#!/usr/bin/env python3
"""
Autonomous Purple Team Agent — Red ↔ Blue Orchestration & Validation

Role: Adversarial emulation orchestrator. Plans exercises where Red attacks,
Blue defends, then validates, scores, and turns findings into fixes.

Capabilities:
- Exercise design (MITRE ATT&CK, threat-informed)
- Live orchestration (inject → detect → respond → score)
- Control validation (are our detections/rules actually firing?)
- Remediation bridging (red TTP → blue control → verification)
- Reporting (executive, technical, purple, compliance)

Skills: reporting-auditing, framework-certifier, framework-evolver,
        autonomous-blue-ops, autonomous-red-teaming, attack-chain-orchestrator
"""
import os
import requests

ROUTER_URL = os.environ.get("ROUTER_URL", "http://localhost:8010/route")

PROFILES = {
    "plan":   {"temperature": 0.3, "max_tokens": 4096, "agent_hint": "project"},
    "orch":   {"temperature": 0.4, "max_tokens": 4096, "agent_hint": "analyze"},
    "score":  {"temperature": 0.1, "max_tokens": 4096, "agent_hint": "analyze"},
}

def _call(prompt: str, profile: str = "orch", max_tokens: int | None = None):
    cfg = PROFILES.get(profile, PROFILES["orch"])
    payload = {
        "prompt": prompt,
        "max_tokens": max_tokens or cfg["max_tokens"],
        "temperature": cfg["temperature"],
        "agent": cfg["agent_hint"],
    }
    r = requests.post(ROUTER_URL, json=payload, timeout=660)
    r.raise_for_status()
    return r.json()

# ── Core Operations ──────────────────────────────────────────────

def design_exercise(threat_actor: str, objective: str, scope: str = "enterprise"):
    """Design a threat-informed purple team exercise."""
    prompt = f"""
You are a PURPLE TEAM exercise designer.

Threat Actor: {threat_actor}  (e.g., APT29, FIN7, generic ransomware)
Objective: {objective}
Scope: {scope}

Design:
1. Threat profile (actor TTPs, preferred initial access, tooling)
2. Scenario narrative (business context, crown jewels, constraints)
3. Attack flow (5-8 steps, each with MITRE ATT&CK ID, red tool, blue control to test)
4. Success criteria (per step: did red succeed? did blue detect? time to detect/respond)
5. Rules of engagement (what's in/out of bounds, safety rails, comms)

Deliver:
- Exercise plan (executable, with inject schedule)
- ATT&CK navigator layer (techniques covered)
- Scoring rubric (detect/prevent/respond, 0-3 per step)
- Safety & rollback plan
- Pre-requisite checklist (accounts, tooling, logging enabled)
"""
    return _call(prompt, "plan")

def orchestrate(exercise_id: str, live_telemetry: str = ""):
    """Live orchestration — coordinate red injects and blue response."""
    prompt = f"""
You are a PURPLE TEAM orchestrator (live exercise).

Exercise: {exercise_id}
Live Telemetry:
{live_telemetry or "(no telemetry yet — first inject pending)"}

Orchestrate next step:
1. Choose next inject (red action) based on exercise plan + blue readiness
2. Predict blue detection (which rule/sensor should fire, expected latency)
3. Observe actual (from telemetry: did alert fire? was it triaged?)
4. Decide: continue, re-inject with variation, or pivot

Deliver:
- Next inject (exact command/TTP, target, timing)
- Expected detection (rule name, log source, ETA)
- Actual vs expected (gap analysis, 1 sentence per)
- Coaching note for blue (what to tune, without spoiling next inject)
- Go/no-go for next phase
"""
    return _call(prompt, "orch")

def validate(control_id: str, technique: str):
    """Control validation — does this control actually stop/detect this technique?"""
    prompt = f"""
You are a PURPLE TEAM control validator.

Control: {control_id}  (e.g., EDR rule, firewall block, Sigma, hardening)
Technique: {technique}  (e.g., T1059.001 PowerShell, T1078 Valid Accounts)

Validate:
1. Reproduce technique in lab (safe, isolated)
2. Observe control (block? alert? nothing?)
3. Evasion variants (obfuscated, LOLBin, indirect syscall) — does control still hold?
4. Log completeness (is the telemetry even collected to detect this?)

Deliver:
- Validation verdict (effective / partial / ineffective) with evidence
- Evasion gap (which variant bypasses it)
- Fix (rule tuning, new data source, hardening)
- Re-test plan (how to prove fix works)
"""
    return _call(prompt, "score")

def bridge(red_finding: str, blue_gap: str):
    """Translate red finding into blue remediation."""
    prompt = f"""
You are a PURPLE TEAM remediation bridge.

Red Finding (what attacker did):
{red_finding}

Blue Gap (why it wasn't stopped/detected):
{blue_gap}

Bridge:
1. Root cause (missing control, misconfig, blind log source, FP-tuned-away rule)
2. Fix options (ranked: quick win vs durable, with effort + owner)
3. Detection opportunity (new Sigma/KQL/YARA, with draft rule)
4. Verification (how to prove fix in next exercise — exact re-inject to run)

Deliver:
- Remediation ticket (title, description, acceptance criteria, priority)
- Detection rule draft (Sigma or KQL, with test log)
- Validation inject (exact red step to replay)
- Risk reduction estimate (how much this fix shrinks exposure)
"""
    return _call(prompt, "score")

def score_exercise(exercise_log: str):
    """Score completed exercise and generate reports."""
    prompt = f"""
You are a PURPLE TEAM scoring lead.

Exercise Log:
{exercise_log}

Score:
1. Per-step (0=missed, 1=detected late, 2=detected on time, 3=prevented) with evidence
2. Aggregates (detection rate %, prevention rate %, MTTD/MTTR)
3. Heatmap (ATT&CK tactic coverage, with blind spots highlighted)
4. Trend vs last exercise (improving / flat / regressing, by tactic)
5. Top 3 fixes (highest risk reduction per effort) + owners

Deliver:
- Executive summary (1 page, for leadership)
- Technical deep dive (per-step, with logs + rule hits)
- Purple report (red + blue + bridge, with tickets)
- ATT&CK navigator JSON (for import)
- Next exercise recommendation (what to test next, and why)
"""
    return _call(prompt, "score", max_tokens=4096)

def continuous_improvement(program_state: str):
    """Program-level improvement planning."""
    prompt = f"""
You are a PURPLE TEAM program manager.

Current program state:
{program_state}

Plan next quarter:
1. Maturity assessment (where are we: initial → managed → optimized, per NIST/CMMC)
2. Exercise cadence (frequency, rotation of actors/TTPs, coverage goal)
3. Tooling investment (what to buy/build vs tune)
4. Metrics to track (detection rate, prevention rate, MTTD, control coverage %)
5. Reporting rhythm (exec brief, technical deep dive, board-level)

Deliver:
- Quarterly roadmap (exercises + controls to add, ordered)
- KPI dashboard spec (what to measure, how, thresholds)
- Resource plan (people, tooling, time)
"""
    return _call(prompt, "plan")

if __name__ == "__main__":
    print(design_exercise("APT29", "exfiltrate crown-jewel repo"))
