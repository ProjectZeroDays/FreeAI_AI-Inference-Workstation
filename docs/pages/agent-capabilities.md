# Agent Capabilities — What Each Agent Can Do

Detailed breakdown of FreeAI's 24 autonomous agents and their out-of-the-box capabilities.

## Agent Summary

| Agent | Team | Role | Key Capabilities |
|---|---|---|---|
| **ORCH** | Red | Orchestrator | Multi-agent coordination, campaign management, result merging |
| **RECON** | Blue | Reconnaissance | Network scanning, port discovery, service fingerprinting |
| **EXPLOIT** | Red | Exploitation | Privilege escalation, lateral movement, persistence |
| **POSTEX** | Red | Post-exploitation | Credential dumping, screenshots, keylogging |
| **HUNT** | Blue | Threat Hunter | IoC hunting, ATT&CK mapping, behavioral analysis |
| **FORENSIC** | Blue | Forensics | Memory analysis, timeline reconstruction |
| **HARDEN** | Blue | Hardening | CIS benchmarks, vulnerability remediation |
| **IR** | Blue | Incident Response | Automated containment, evidence preservation |
| **DECEPT** | Blue | Deception | Honeypots, canary tokens, trap triggering |
| **SIM** | Purple | Simulation | Attack simulation, detection validation |
| **PATCH** | Blue | Auto-Patch | Generate and apply safe fixes |
| **BUILDER** | General | Builder | Fullstack app generation from specs |

## Red Team Agents (14)

| Agent | Trigger Commands | Output |
|---|---|---|
| API Sniffer | `api sniff`, `endpoint map` | Transaction logs, auth detection |
| Cookie Harvester | `cookie harvest`, `session steal` | Netscape format, JSON, Python dicts |
| Payload Engine | `payload gen`, `encode shell` | PowerShell, Python, Go, ELF, DLL |
| Vuln Scanner | `vuln scan`, `nmap`, `nuclei` | NIST 800-115, MITRE ATT&CK reports |
| Brute Force | `brute force`, `hash crack` | Cracked passwords, hash types |
| Exploitation | `exploit`, `priv esc` | Shell access, persistence tokens |
| Deserialization | `deser attack`, `gadget chain` | Exploit payloads |
| SSRF Exploit | `ssrf probe`, `internal scan` | Internal endpoint mapping |
| Memory Corruption | `heap spray`, `buffer overflow` | Exploit code, ROP chains |
| File Parse | `pdf exploit`, `xxe probe` | Format-specific payloads |
| Messaging RCE | `sms exploit`, `email rce` | Protocol-specific payloads |
| Android Exploit | `android pwn`, `apk analyze` | DEX payloads, tropicana |
| IoT Exploit | `iot scan`, `firmware anal` | Device configs, backdoors |
| Chained Zero-Day | `chain exploit`, `multi-stage` | Multi-exploit chains |

## Blue Team Agents (12)

| Agent | Trigger Commands | Output |
|---|---|---|
| SIEM Integration | `siem collect`, `log aggregate` | Correlated alerts, dashboards |
| Forensics | `forensic dump`, `timeline` | Memory artifacts, event logs |
| Hunting | `hunt threats`, `ioc search` | IoC lists, TTP mappings |
| Hardening | `harden system`, `cis audit` | Remediation scripts |
| Incident Response | `ir contain`, `evidence preserve` | Containment actions, chains |
| Threat Intel | `intel feed`, `ttp map` | Threat reports, indicators |
| Network Defense | `ids config`, `traffic analyze` | Rules, anomaly reports |
| Malware Analysis | `malware static`, `malware dynamic` | Behavior reports, IOCs |
| Compliance | `compliance check`, `pci audit` | Compliance reports |
| Vuln Scanner | `vuln audit`, `trivy scan` | CVE lists, severity reports |
| Identity Mgmt | `iam audit`, `access review` | Access reports, recommendations |
| Security Config | `config audit`, `baseline check` | Config diffs, hardening guides |

## Purple Team Agents (7)

| Agent | Trigger Commands | Output |
|---|---|---|
| SIM | `sim attack`, `detect validate` | Detection gaps, false positives |
| Validate | `validate defense`, `gap analyze` | Gap reports, remediation plans |
| Bridge | `bridge red-blue`, `jira ticket` | Handoff reports, tickets |
| Purple Testing | `purple test`, `attack-defend` | Cycle reports, effectiveness metrics |
| Detection Engineering | `detect rule`, `sig tune` | YARA/Suricata rules |
| Tabletop Exercises | `tt exercise`, `scenario sim` | Exercise reports, improvement plans |
| Threat Emulation | `emulate threat`, `apt sim` | Emulation reports, TTP coverage |

## Usage

Agents are invoked through the Agent API or autonomous SDLC:

```bash
# Direct agent call
curl -X POST localhost:8020/agent/project \
  -H "Content-Type: application/json" \
  -d '{"spec":"Build a FastAPI app","profile":"strict"}'

# Via SDLC
python freeai.py auto-start "Build a notes API" --watch

# Via workflow
curl -X POST localhost:8040/workflow/run \
  -H "Content-Type: application/json" \
  -d '{"workflow": "security_scan", "context": {}}'
```

## Next Steps

- [SDLC Tutorial](SDLC-TUTORIAL.md) — Autonomous development workflow
- [Workflow Engine](build-workflows.md) — Chain agents into pipelines
- [Skills Catalog](SKILLS-CATALOG.md) — 33 security skills reference
