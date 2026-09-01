---
name: control-session-orchestrator
description: "Control-plane workflow for coordinating multi-agent, multi-session project work from a single Codex, GitHub Copilot, or agent-app control session. Use this skill whenever the user asks to orchestrate agents, create or steer worker sessions, run a workflow-like effort, fan out audits/research/migrations, coordinate parallel implementation streams, monitor other project sessions, or compare this control-session pattern to Claude Code dynamic workflows."
---

# Control Session Orchestrator

Use the current session as the control plane for project work that is too broad, risky, or stateful for one conversation. The control session owns intent, decomposition, routing, status, verification, and consolidation. Worker sessions own scoped execution.

## Mental Model

```
User
  -> Control session (strategy, dispatch, tracking, integration)
       -> Worker session A (persistent branch/workstream)
            -> Subagents for research, implementation, review
       -> Worker session B (persistent branch/workstream)
       -> Verifier session (optional independent gate)
```

## Machine-Checkable Contracts

### Worker Result Block
Every worker MUST end with a fenced JSON block:

```json control-result
{
  "worker_id": "auth-api",
  "wave_id": "w1",
  "unit_key": "service/auth",
  "scope": "src/auth/** — refresh-token rotation",
  "status": "complete",
  "files_changed": ["src/auth/rotate.ts"],
  "verification": { "command": "pnpm test auth", "result": "pass", "evidence": "42 passed" },
  "subagents_used": "2",
  "risks": ["rotation interacts with logout"],
  "next_step": "ready for review",
  "report_ref": "thread/PR/path to full report"
}
```

### Control-State Manifest
Durable artifact tracking all workers:

```json
{
  "mission": "MCP tool parity audit",
  "budget": { "max_concurrent_workers": 5, "spawned": 0, "in_flight": 0 },
  "workers": [
    {
      "unit_key": "surface/http",
      "worker_id": "http-audit",
      "status": "pending",
      "session_ref": "...",
      "blocker": null
    }
  ]
}
```

## Control Workflow

### 0. Rehydrate
On session start, look for existing control-state manifest. Load it and reconcile worker statuses.

### 1. Frame the Mission
Capture: objective, non-goals, repos/branches in scope, success criteria, verification gates, merge expectations, constraints.

### 2. Detect Control Surface
Identify available tools (Codex threads, Copilot sessions, generic agent tools).

### 3. Choose Topology
- **One worker**: isolated implementation
- **Parallel workers**: independent modules
- **Research then implement**: exploratory first
- **Implementer + verifier**: separate sessions
- **Control-only**: inspect state only

### 4. Dispatch Workers
Respect budget limits. Each worker prompt must be self-contained with:
- Mission and exact scope
- Files/subsystems boundaries
- Verification commands
- Required result block format

### 5. Track State
Update manifest every turn. Parse worker result blocks to update status.

### 6. Route Follow-ups
Run result-gate: validate the JSON block, check verification passes, route blockers.

### 7. Iterate to Convergence
Apply convergence rule (single-pass, loop-until-dry, loop-until-budget, accumulate-to-target).

### 8. Verify and Consolidate
Run verification gate. Review diffs. Ensure all workers in terminal state (complete/failed/dropped).

## Safety Rules

- Don't spawn workers for trivial tasks
- Don't let workers edit same files without coordination
- Don't assume app connectors exist — discover and fall back
- Don't silently create branches/commits/PRs
- Worker subagents are leaf helpers — max 2 levels deep
- Enforce concurrency caps
- Record all dropped/failed units with reasons

## Reporting Format

```markdown
**Status:** <on track | blocked | needs decision | complete>
**Budget:** in-flight <X/Y> · spawned <A/B> · wave <N>

| Workstream | Session | Scope | State | Evidence |
|---|---|---|---|---|
```
