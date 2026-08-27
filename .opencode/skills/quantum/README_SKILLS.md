---
name: quantum-skills-launcher
description: >
  Master launcher for all Quantum C2 opencode skills. Use this as the entry point to discover and trigger any Quantum C2 skill. Lists all available skills, explains how to trigger them, and shows the skill tree and dependencies. Triggers on: "list skills", "available skills", "skill tree", "what can you do", " Quantum C2 skills", "show skills".
trigger_keywords: skills, list skills, available skills, skill tree, quantum skills, what can you do
---

# Quantum C2 — Skills Launcher

This is the master skill launcher for the Quantum C2 opencode framework. It provides a complete overview of all 21 project skills plus 13+ global skills, how to trigger each one, and their dependency relationships.

---

## Project Skills (21)

All project skills are located in `.config/opencode/skills/quantum/` and are loaded automatically by opencode when working in the Quantum C2 project.

### Development & Code Quality

| Skill | Trigger | What It Does |
|-------|---------|-------------|
| `debug-workflow` | "debug", "fix", "troubleshoot", "error", "crash" | Systematic debugging for import errors, routing issues, DB problems, service failures |
| `test-runner` | "run tests", "coverage", "pytest", "validate" | Execute unit/integration/security/E2E tests with coverage reporting |
| `pr-review` | "review PR", "code review", "analyze PR" | Review recent PRs for quality, security, performance; generate changelog summaries |
| `issue-triage` | "triage", "categorize issue", "label issue" | Analyze and triage GitHub issues — label, assign, deduplicate, close |
| `exploit-testing` | "test exploits", "vulnerability", "fuzzing" | Validate exploit modules, run CVE tests, fuzzing campaigns |
| `security-audit` | "security audit", "scan", "bandit", "safety" | Full security audit — static analysis, dependency check, config verification |
| `database-migration` | "migrate", "db migrate", "postgres", "alembic" | Migrate between SQLite and PostgreSQL, run Alembic migrations |

### Deployment & Operations

| Skill | Trigger | What It Does |
|-------|---------|-------------|
| `deployment-guide` | "deploy", "setup", "docker", "kubernetes" | Deploy to Docker, K8s, or cloud providers (Hetzner, DO, OVH, Vultr) |
| `production-readiness` | "production readiness", "production check" | Check if the system is ready for production (tests, security, compliance) |
| `production-readiness-check` | "pre-flight", "health check", "is ready" | Detailed pre-deployment production readiness verification |
| `backup-restore` | "backup", "restore", "disaster recovery" | Backup/restore databases, config, K8s manifests; disaster recovery |
| `release` | `[RELEASE]`, "create release", "bump version" | Full release lifecycle — version bump, build, test, tag, GitHub release |

### Documentation

| Skill | Trigger | What It Does |
|-------|---------|-------------|
| `docs-update` | "update docs", "generate documentation" | Update README, API docs, architecture docs, inline docstrings |
| `expert-readme` | `[README-UPDATE]` | Auto-scan codebase and update README.md with new features/endpoints |
| `expert-wiki` | `[WIKI-UPDATE]` | Auto-scan docs/ and update the comprehensive wiki |

### Compliance & Validation

| Skill | Trigger | What It Does |
|-------|---------|-------------|
| `compliance-check` | "compliance", "compliance check", "assessment" | Run compliance checks against NIST 800-53, SOC2, ISO frameworks |
| `compliance-validation` | "validate compliance", "NIST", "SOC2", "audit" | Validate individual compliance controls and generate reports |

### Autonomous Workflows

| Skill | Trigger | What It Does |
|-------|---------|-------------|
| `agent-orchestration` | "orchestrate agents", "deploy agents", "multi-agent" | Coordinate AI agent teams for parallel operations and task delegation |
| `update-protocol` | `[UPDATE]`, "enhance Quantum" | Autonomous update cycle — generate suggestions, implement, test, deploy |
| `business-plan-creator` | "business plan", "pitch deck", "prospectus", "investor" | Create investor-ready business plans, pitch decks, and prospectuses |

---

## Global Skills (13+14)

These are installed in `~/.config/opencode/skills/` and available in all opencode sessions:

### Quantum C2 Operator Suite
| Skill | Trigger | Dependency |
|-------|---------|------------|
| `quantum-c2-operator` | "operate Quantum", "C2 operations", "deploy C2" | Master skill — all others |
| `quantum-c2-recon` | "scan network", "recon", "OSINT", "port scan" | Depends on operator auth |
| `quantum-c2-exploit` | "exploit", "payload", "attack", "brute force" | Depends on operator auth |
| `quantum-c2-postex` | "post-exploit", "privilege escalation", "persistence" | Depends on sessions |
| `quantum-c2-deception` | "deception", "honeypot", "evasion", "canary" | Optional companion |
| `quantum-c2-forced-entry` | "forced entry", "full lifecycle", "pegasus" | Depends on exploit + postex |
| `quantum-c2-agents` | "agent team", "deploy agents", "parallel tasks" | Depends on operator |
| `quantum-c2-sessions` | "session", "implant", "reverse shell", "command" | Depends on operator auth |
| `quantum-c2-devices` | "device control", "screenshot", "camera", "microphone" | Depends on sessions |
| `quantum-c2-listeners` | "listener", "C2 channel", "reverse shell listener" | Depends on operator |
| `quantum-c2-vault` | "vault", "credentials", "encrypt", "decrypt" | Optional companion |
| `quantum-c2-reporting` | "report", "analytics", "audit log" | Depends on operator |
| `quantum-c2-deploy` | "deploy Quantum", "install", "configure" | Standalone |
| `quantum-c2-auto-complete` | "complete Quantum C2", "auto-complete", "production ready" | Depends on all skills |

### Framework Skills (quantum/ subdirectory)
| Skill | Purpose |
|-------|---------|
| `quantum-build-verify` | Verify build integrity — syntax, FastAPI, React, tests |
| `quantum-flask-router` | Add new FastAPI routes and WebSocket handlers |
| `quantum-fullstack-dev` | Build complete full-stack features |
| `quantum-gui-builder` | Build new AEGIS-Q tkinter GUI pages |
| `quantum-launcher` | Start and verify the Quantum framework |
| `quantum-module-writer` | Create new defensive modules |
| `quantum-router-bugfix` | Fix routing errors and 500s |
| `quantum-router-exploit` | Router vulnerability & exploitation dashboards |
| `quantum-test-runner` | Run Quantum framework test suites |

---

## Skill Tree / Dependency Map

```
quantum-c2-operator (master)
├── quantum-c2-recon          (network scanning, OSINT, CVE)
├── quantum-c2-exploit        (payloads, brute force, fuzzing)
│   ├── quantum-c2-forced-entry
│   └── exploit-testing (project)
├── quantum-c2-sessions       (implant management, commands)
│   ├── quantum-c2-devices    (screenshot, camera, mic)
│   └── quantum-c2-postex     (privilege escalation, persistence)
├── quantum-c2-listeners      (TCP, HTTPS, DNS, Telegram)
├── quantum-c2-agents         (multi-agent orchestration)
│   └── agent-orchestration (project)
├── quantum-c2-deception      (honeypots, canaries)
├── quantum-c2-vault          (credentials, encryption)
├── quantum-c2-reporting      (analytics, audit logs)
└── quantum-c2-deploy         (Docker, K8s, cloud)
    ├── deployment-guide (project)
    └── backup-restore (project)

quantum-c2-auto-complete      (autonomous full completion)
└── depends on all skills above

┌── Project Development Skills ──────────────────────────────┐
│  debug-workflow     ← first stop for any errors            │
│  test-runner        ← before commits/deploy                 │
│  pr-review          ← after merges                         │
│  issue-triage       ← new GitHub issues                    │
│  security-audit     ← before any deployment                │
│  database-migration ← schema changes                       │
└────────────────────────────────────────────────────────────┘

┌── Project Operations Skills ───────────────────────────────┐
│  production-readiness      ← is it ready?                  │
│  production-readiness-check← detailed pre-flight           │
│  release                   ← [RELEASE] command             │
│  update-protocol           ← [UPDATE] command              │
│  compliance-check          ← framework compliance          │
│  compliance-validation     ← control-level validation      │
└────────────────────────────────────────────────────────────┘

┌── Project Documentation Skills ────────────────────────────┐
│  docs-update       ← general doc maintenance              │
│  expert-readme     ← [README-UPDATE] command              │
│  expert-wiki       ← [WIKI-UPDATE] command                │
│  business-plan-creator ← investor documents               │
└────────────────────────────────────────────────────────────┘
```

---

## How to Use

### Basic Usage
Just describe what you want to do in natural language. Opencode will match your request to the appropriate skill based on trigger keywords.

### Explicit Skill Triggering
Some skills respond to bracketed commands:
- `[RELEASE]` — run the full release workflow
- `[UPDATE]` — run the autonomous update protocol
- `[README-UPDATE]` — regenerate README.md
- `[WIKI-UPDATE]` — regenerate the wiki

### Example Commands
```
"debug this import error"         → debug-workflow
"run the tests"                   → test-runner
"review the last PR"              → pr-review
"triage the open issues"          → issue-triage
"deploy to Hetzner"               → deployment-guide / quantum-c2-deploy
"check production readiness"      → production-readiness-check
"create a release"                → [RELEASE] / release
"scan network 192.168.1.0/24"    → quantum-c2-recon
"run a security audit"            → security-audit
"update the documentation"        → docs-update
"list all available skills"       → quantum-skills-launcher (this file)
```

---

## Quick Reference by Task

| Task | Skill |
|------|-------|
| Fix an error | `debug-workflow` |
| Run tests | `test-runner` |
| Check test coverage | `test-runner` |
| Review a PR | `pr-review` |
| Triage an issue | `issue-triage` |
| Security scan | `security-audit` |
| Test exploits | `exploit-testing` |
| Migrate database | `database-migration` |
| Deploy | `deployment-guide` or `quantum-c2-deploy` |
| Check readiness | `production-readiness-check` |
| Create release | `[RELEASE]` |
| Auto-update | `[UPDATE]` |
| Update README | `[README-UPDATE]` |
| Update wiki | `[WIKI-UPDATE]` |
| Run compliance | `compliance-validation` |
| Create business docs | `business-plan-creator` |
| Orchestrate agents | `agent-orchestration` |
| Network scan | `quantum-c2-recon` |
| Deploy exploit | `quantum-c2-exploit` |
| Manage sessions | `quantum-c2-sessions` |
| Full auto-complete | `quantum-c2-auto-complete` |

---

*Master Skill Launcher — Quantum C2*
*Version: 1.0 | Date: 2026-08-17*
