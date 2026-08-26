# Quantum C2 — Skills Index

> Auto-generated skills registry for the Quantum C2 opencode framework.

## Directory

All skills live under: `.config/opencode/skills/quantum/`

## Registered Skills (21)

| # | Name | Description | Trigger Keywords | Path |
|---|------|-------------|-----------------|------|
| 1 | `agent-orchestration` | Coordinate AI agents for Quantum C2 operations. Use when managing agent teams, delegating tasks, or orchestrating autonomous operations. | agent, orchestrate, autonomous, multi-agent, team, delegate, coordinate, AI agent | `agent-orchestration/SKILL.md` |
| 2 | `backup-restore` | Backup and restore Quantum C2 data and configuration. Use when creating backups, restoring from backup, or managing disaster recovery. | backup, restore, disaster recovery, snapshot, migrate, data protection | `backup-restore/SKILL.md` |
| 3 | `business-plan-creator` | Comprehensive workflow for creating investor-ready business plans, pitch decks, and prospectuses for Quantum C2. | BUSINESS_PLAN, PITCH_DECK, PROSPECTUS, INVESTOR_DOC, create business plan, generate pitch deck | `business-plan-creator/SKILL.md` |
| 4 | `compliance-check` | Run compliance checks and generate reports for Quantum C2. | compliance, compliance check, run compliance, compliance report, assessment, NIST, SOC2, ISO | `compliance-check/SKILL.md` |
| 5 | `compliance-validation` | Validate compliance controls against NIST, SOC2, ISO, and other frameworks. | compliance, NIST, SOC2, ISO, audit, controls, regulatory, validation | `compliance-validation/SKILL.md` |
| 6 | `database-migration` | Manage database migrations for Quantum C2 (SQLite ↔ PostgreSQL). | migrate, database migration, db migrate, postgres, postgresql, schema, alembic | `database-migration/SKILL.md` |
| 7 | `debug-workflow` | Debug common Quantum C2 issues — import errors, routing problems, database issues, service failures. | debug, error, fix, troubleshoot, issue, problem, crash, failing | `debug-workflow/SKILL.md` |
| 8 | `deployment-guide` | Deploy Quantum C2 to Docker, Kubernetes, and cloud providers. | deploy, deploy to, install, setup, docker, kubernetes, k8s, provision | `deployment-guide/SKILL.md` |
| 9 | `docs-update` | Update Quantum C2 project documentation including README, API docs, architecture, and inline docs. | docs, documentation, README, generate docs, update docs, documentation sync, doc update | `docs-update/SKILL.md` |
| 10 | `expert-readme` | Auto-scan codebase for new features/endpoints and update README.md. Triggered by `[README-UPDATE]`. | README-UPDATE, readme update, update readme, sync readme, generate readme, README | `expert-readme/SKILL.md` |
| 11 | `expert-wiki` | Auto-scan `docs/` and update the comprehensive wiki (`docs/getting-started/WIKI.md`). Triggered by `[WIKI-UPDATE]`. | WIKI-UPDATE, wiki update, update wiki, sync wiki, generate wiki, wiki | `expert-wiki/SKILL.md` |
| 12 | `exploit-testing` | Test and validate exploit modules, vulnerability scanning, and attack simulation frameworks. | exploit, test exploits, vulnerability, attack, payload, PoC, fuzzing | `exploit-testing/SKILL.md` |
| 13 | `issue-triage` | Analyze, categorize, and triage GitHub issues for Quantum C2. | triage, triage issue, categorize issue, issue management, label issue, bug report | `issue-triage/SKILL.md` |
| 14 | `pr-review` | Review pull requests for code quality, security, and performance. Generates changelog summaries. | review PR, pr review, code review, review changes, changelog, analyze PR | `pr-review/SKILL.md` |
| 15 | `production-readiness` | Check production readiness of Quantum C2 (tests, security, compliance, health). | production readiness, production check, deploy status, verify production, ready to deploy | `production-readiness/SKILL.md` |
| 16 | `production-readiness-check` | Verify Quantum C2 production readiness before deployment with systematic checks. | production readiness, deploy, verify, health check, pre-flight, production check, is ready | `production-readiness-check/SKILL.md` |
| 17 | `release` | Full release workflow — version bumping, building, testing, tagging, GitHub release, changelog. Triggered by `[RELEASE]`. | release, RELEASE, create release, bump version, tag release, release workflow | `release/SKILL.md` |
| 18 | `security-audit` | Perform comprehensive security audits — static analysis, dependency checks, config verification. | security audit, scan, vulnerabilities, bandit, safety, security check, pentest | `security-audit/SKILL.md` |
| 19 | `test-runner` | Run and analyze Quantum C2 test suites (unit, integration, security, E2E) with coverage. | test, run tests, coverage, pytest, validate, verify tests | `test-runner/SKILL.md` |
| 20 | `update-protocol` | Autonomous update protocol — generates suggestions, implements features, tests, and deploys. Triggered by `[UPDATE]`. | UPDATE, update, enhance, implement suggestions, update protocol, generate improvements | `update-protocol/SKILL.md` |

---

## Global Skills (Already Installed)

These 13 skills are installed in the global opencode skills directory and are always available:

| Name | Description |
|------|-------------|
| `quantum-c2-operator` | Master operator skill — all C2 operations, sessions, devices, vault, reporting |
| `quantum-c2-recon` | Reconnaissance — network scanning, domain intel, OSINT, CVE search |
| `quantum-c2-exploit` | Exploitation — payload generation, brute force, fuzzing, zero-click |
| `quantum-c2-postex` | Post-exploitation — session management, privilege escalation, persistence |
| `quantum-c2-deception` | Deception and evasion — honeypots, honeytokens, attack simulation |
| `quantum-c2-forced-entry` | Full lifecycle exploitation operations |
| `quantum-c2-agents` | AI agent team orchestration |
| `quantum-c2-sessions` | C2 session management and command execution |
| `quantum-c2-devices` | Device control — commands, screenshots, camera/mic |
| `quantum-c2-listeners` | C2 channel listener management (TCP, HTTPS, DNS, Telegram) |
| `quantum-c2-vault` | Credential vault and encryption operations |
| `quantum-c2-reporting` | Report generation and analytics |
| `quantum-c2-deploy` | Deployment and configuration for Quantum C2 |
| `quantum-c2-auto-complete` | Autonomous project completion engine |

## Framework Skills (Global)

These 9 skills are in the global `quantum/` subdirectory:

| Name | Description |
|------|-------------|
| `quantum-build-verify` | Verify build integrity — syntax, FastAPI, React, tests |
| `quantum-flask-router` | Add new Flask/FastAPI API routes and WebSocket handlers |
| `quantum-fullstack-dev` | Build complete full-stack features (frontend + backend) |
| `quantum-gui-builder` | Build new pages for the AEGIS-Q tkinter GUI |
| `quantum-launcher` | Start and verify the Quantum framework (Flask, GUI, backend) |
| `quantum-module-writer` | Create new defensive modules (detection rules, hunting, threat intel) |
| `quantum-router-bugfix` | Diagnose and fix routing errors and 500s |
| `quantum-router-exploit` | Router vulnerability & exploitation dashboards |
| `quantum-test-runner` | Run Quantum framework test suites |
| `quantum/release` | Release workflow (global copy) |
| `quantum/update-protocol` | Update protocol (global copy) |

---

## Configuration

The project `opencode.json` registers the skills path as:

```json
{
  "skills": {
    "path": "./.config/opencode/skills"
  }
}
```

This means opencode will load all `SKILL.md` files from:
- `C:\Projects\Quantum C2\.config\opencode\skills\quantum\` (project skills)
- `C:\Users\Project Zero\.config\opencode\skills\` (global skills)

---

*Generated: 2026-08-17*
