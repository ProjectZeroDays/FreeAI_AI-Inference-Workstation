---
name: swarm-orchestrator
description: "Use when the user types [SWARM] to activate a multi-agent parallel workflow. Dispatches specialized subagents to work on independent tasks simultaneously, with progress tracking and result aggregation."
---

# [SWARM] Orchestrator

Activate a fleet of specialized agents to execute tasks in parallel. This skill handles task decomposition, agent dispatch, progress tracking, and result consolidation.

## Activation

User types `[SWARM]` followed by a task description or goal.

```
[SWARM] implement login page with JWT auth
[SWARM] refactor all API endpoints to use async/await
[SWARM] add comprehensive tests for auth module
```

## Execution Protocol

### 1. Analyze & Decompose

Break the user's request into **independent subtasks** that can execute in parallel.

**Rules:**
- Each subtask must have a clear input/output boundary
- No subtask should block another (true parallelism)
- Limit to 4-8 concurrent agents (more creates coordination overhead)
- Group dependent work into sequential phases

**Decomposition example:**
```
Request: "Add user authentication"

Phase 1 (parallel):
  ├── Agent-A: Backend auth API endpoints
  ├── Agent-B: Database schema migrations
  └── Agent-C: Auth middleware module

Phase 2 (parallel, after Phase 1):
  ├── Agent-D: Login page frontend
  ├── Agent-E: Session management
  └── Agent-F: Tests for auth flows

Phase 3 (sequential):
  └── Orchestrator: Integration verification
```

### 2. Dispatch Subagents

Spawn subagents with clear instructions:

```javascript
// Use actor tool with subagent_type: "general"
{
  "operation": {
    "action": "run",
    "subagent_type": "general",
    "description": "Implement auth API",
    "prompt": "Task: Build JWT authentication API endpoints.

Work directory: <current working directory>

Requirements:
1. POST /api/auth/login — accept email/password, return JWT
2. POST /api/auth/refresh — refresh expired tokens
3. POST /api/auth/logout — invalidate refresh token
4. All endpoints need @login_required decorator

Output artifacts:
- /src/auth/api.py — API routes
- /src/auth/middleware.py — JWT middleware
- /tests/test_auth.py — test coverage

Verification:
- Run: python -m pytest tests/test_auth.py -v
- All tests must pass before reporting completion

Handoff format when done:
Status: success | failed
Summary: <one-line description>
Files touched: <paths>
Tests: <count> passing
"
  }
}
```

### 3. Track Progress

Monitor all running agents. Log status updates:

```
[HH:MM:SS] SWARM ACTIVATED — Goal: "implement login page"
[HH:MM:SS] Phase 1: Dispatching 3 agents (auth-api, db-migrate, middleware)
[HH:MM:SS] Agent auth-api: In Progress
[HH:MM:SS] Agent db-migrate: In Progress  
[HH:MM:SS] Agent middleware: In Progress
[HH:MM:23] Agent db-migrate: Done — 4 migrations applied
[HH:MM:45] Agent middleware: Done — JWT middleware complete
[HH:MM:12] Agent auth-api: Done — 6 endpoints implemented
[HH:MM:13] Phase 2: Dispatching 3 agents (login-ui, session, tests)
...
[HH:MM:58] SWARM COMPLETE — All phases finished successfully
```

### 4. Aggregate Results

Collect outputs from all agents. Produce a final summary:

```
=== SWARM EXECUTION REPORT ===
Goal: implement login page with JWT auth
Duration: 4 minutes 23 seconds
Agents: 6 dispatched across 2 phases

Phase 1 Results:
  ✅ auth-api — 6 endpoints, 12 tests passing
  ✅ db-migrate — 4 migrations applied
  ✅ middleware — JWT validation complete

Phase 2 Results:
  ✅ login-ui — React component + form validation
  ✅ session — Redis session store implemented
  ✅ tests — 28 integration tests added

Final Verification:
  ✅ All tests passing (40/40)
  ✅ No lint errors
  ✅ Git diff: 8 files changed, +612/-45 lines

Status: COMPLETE
```

## Agent Types

Match agent specialization to task type:

| Agent Type | Best For | Model |
|-----------|----------|-------|
| `general` | Complex multi-step work, any domain | High-reasoning |
| `explore` | Code search, understanding, analysis | Any |
| `developer` | Code generation, refactoring, bug fixes | Mid-to-high tier |

## Common Patterns

### Parallel Implementation
```
[SWARM] implement CRUD for User model

→ Dispatch 4 agents:
  1. Backend routes (POST/GET/PUT/DELETE)
  2. Database schema + migrations
  3. Frontend list/create/edit views
  4. Test suite
```

### Research + Build
```
[SWARM] add real-time notifications

→ Phase 1 (research):
  1. Explore current codebase for event patterns
  2. Design notification schema

→ Phase 2 (build, parallel):
  1. Implement WebSocket handler
  2. Build notification model + API
  3. Create frontend notification panel
```

### Refactor Campaign
```
[SWARM] migrate to TypeScript

→ Dispatch 4 agents:
  1. Config setup (tsconfig, path aliases)
  2. Core types (models, APIs, utils)
  3. Migrate existing JS modules
  4. Update build pipeline + tests
```

## Error Handling

### Agent Failure
```
[HH:MM:SS] Agent auth-api: FAILED — SyntaxError in api.py:45

Recovery options:
1. Retry with clarified instructions
2. Fix the error directly if simple
3. Skip and continue with other agents (if non-critical)
4. Stop entire swarm (if blocking dependency)
```

### Timeout
- Set explicit timeouts: `"timeout_ms": 300000` (5 minutes)
- Agents that timeout are marked `failed — timeout`
- Orchestration continues with remaining agents

### Resource Limits
- Max 8 concurrent agents per swarm
- If queue exceeds limit, batch: run 4, wait, run next 4

## When NOT to Use [SWARM]

- **Single focused task** — Just do it directly
- **Sequential dependencies** — One thing must finish before next starts
- **Trivial changes** — Under 30 minutes of work
- **Ambiguous goals** — Clarify requirements first, then swarm

Use [SWARM] when you have **multiple independent workstreams** that can execute in parallel to save time.
