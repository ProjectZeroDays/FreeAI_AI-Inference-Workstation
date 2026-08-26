#!/usr/bin/env python3
"""
Autonomous Blue Team Agent — Defensive Operations & Hardening

Capabilities:
- Threat detection & hunting (APT, C2 heartbeats, exfil, lateral movement)
- System & network hardening (OS, container, firewall, IDS/IPS)
- Incident response (triage, containment, eradication, recovery)
- Compliance & auditing (NIST 800-53, SOC2, ISO, CMMC)
- SOC automation (alert triage, playbooks, threat intel)

Integrates with FreeAI Router (8010) and Quantum C2 hardening/monitoring.
Skills: autonomous-blue-ops, apt-hunting-detection, forensic-analysis,
        network-monitoring-ops, system-hardening, compliance-check
"""
import os
import requests

ROUTER_URL = os.environ.get("ROUTER_URL", "http://localhost:8010/route")

PROFILES = {
    "hunt":        {"temperature": 0.2, "max_tokens": 4096, "agent_hint": "analyze"},
    "harden":      {"temperature": 0.1, "max_tokens": 4096, "agent_hint": "refactor"},
    "respond":     {"temperature": 0.3, "max_tokens": 4096, "agent_hint": "debug"},
    "compliance":  {"temperature": 0.1, "max_tokens": 4096, "agent_hint": "analyze"},
}

def _call(prompt: str, profile: str = "hunt", max_tokens: int | None = None):
    cfg = PROFILES.get(profile, PROFILES["hunt"])
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

def hunt(telemetry: str, hypothesis: str = "auto"):
    """Threat hunting — TTP + IoC + behavioral analysis."""
    prompt = f"""
You are an autonomous BLUE TEAM threat hunter.

Telemetry (logs, netflows, EDR alerts):
{telemetry}

Hypothesis: {hypothesis}

Hunt:
1. Map telemetry to MITRE ATT&CK (tactic/technique)
2. Correlate IoCs (hash, IP, domain, JA3, cert) with intel feeds
3. Baseline vs anomaly (process tree, registry, network beaconing)
4. Hunt for stealthy persistence (WMI, scheduled tasks, services, bootkit)

Deliver:
- Hunting hypothesis + query (KQL/Sigma/YARA)
- Findings ranked (true positive confidence %)
- ATT&CK coverage heatmap (what's blind)
- Next hunt to run (with data source needed)
- Containment recommendation if active intrusion
"""
    return _call(prompt, "hunt")

def harden(target: str, profile: str = "cis_l1"):
    """System/network hardening plan and execution."""
    prompt = f"""
You are a BLUE TEAM hardening lead.

Target: {target}
Profile: {profile}  (cis_l1 | cis_l2 | stig | nist_800_53 | custom)

Harden:
1. OS baseline (patch level, services, auth, auditd, FIM)
2. Network (firewall, segmentation, IDS/IPS rules, TLS)
3. Container/K8s (seccomp, AppArmor, read-only rootfs, no-new-priv)
4. Identity (MFA, least privilege, vault secrets rotation)

For each control:
- Current state (pass/fail, evidence)
- Remediation command (ansible/terraform or shell)
- Validation check (test that proves fix)
- Rollback plan

Deliver:
- Hardening playbook (executable steps, ordered by risk reduction)
- CIS/NIST control mapping
- Verification report (before/after scan diff)
"""
    return _call(prompt, "harden")

def triage(alert: str, severity: str = "high"):
    """Alert triage & incident scoping."""
    prompt = f"""
You are a BLUE TEAM SOC analyst (L3).

Alert: {alert}
Severity: {severity}

Triage:
1. Alert fidelity (true vs false positive, with reasoning)
2. Scope (single host vs lateral movement indicators)
3. Timeline reconstruction (first seen, progression)
4. Business impact (data at risk, blast radius)

Deliver:
- Verdict (TP/FP/benign) with confidence
- Scope (hosts/users/processes involved)
- Immediate containment (isolate host? block IOC? kill process?)
- Evidence preservation steps (memory dump, disk image, logs)
- Escalation (HIR needed? who to notify)
"""
    return _call(prompt, "respond")

def forensics(artifact: str, artifact_type: str = "memory_dump"):
    """Forensic analysis of an artifact."""
    prompt = f"""
You are a BLUE TEAM forensic analyst.

Artifact: {artifact}
Type: {artifact_type}  (memory_dump | disk_image | log_bundle | pcap | file)

Analyze:
1. Timeline (MFT, registry, shimcache, amcache, logs)
2. Malware (static + dynamic, IOC extraction, C2 decode)
3. Persistence & execution artifacts
4. Data access/exfil indicators

Deliver:
- Timeline (super-timeline excerpt)
- IOCs (hashes, IPs, domains, mutexes, registry keys)
- Root cause + patient zero
- Remediation (eradication + recovery steps)
- Chain-of-custody notes
"""
    return _call(prompt, "hunt")

def compliance(framework: str = "nist_800_53", scope: str = "full_stack"):
    """Compliance assessment & audit prep."""
    prompt = f"""
You are a BLUE TEAM compliance engineer.

Framework: {framework}  (nist_800_53 | soc2 | iso27001 | cmmc | fedramp)
Scope: {scope}

Assess:
1. Control coverage (implemented / partial / missing) with evidence
2. Gap analysis (what fails audit, by control ID)
3. Remediation roadmap (priority by audit risk, effort, owner)
4. Artifact generation (SSP, POA&M, evidence bundle)

Deliver:
- Compliance scorecard (% per family)
- Gap register (control → finding → remediation → owner → due)
- Audit-ready evidence package outline
- Continuous monitoring plan (what to watch to stay compliant)
"""
    return _call(prompt, "compliance")

def monitor_config(telemetry_sources: str = "all"):
    """Design monitoring & detection coverage."""
    prompt = f"""
You are a BLUE TEAM detection engineer.

Sources: {telemetry_sources}

Design:
1. Log source matrix (EDR, firewall, DNS, proxy, cloud audit, app logs)
2. Detection rules (Sigma/Splunk/KQL) per ATT&CK technique
3. Alert tuning (thresholds, suppressions, correlation)
4. Dashboards (SOC, exec, threat intel)

Deliver:
- Coverage matrix (technique → log source → rule → status)
- 5 highest-value detections to add next (with Sigma rule draft)
- Tuning plan (FP reduction without losing TP)
- Runbook link per alert (so L1 can act)
"""
    return _call(prompt, "hunt")

if __name__ == "__main__":
    print(hunt("Suspicious powershell -enc beacon every 60s to 185.220.101.47"))
