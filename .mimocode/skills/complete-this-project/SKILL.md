---
name: complete-this-project
description: "Use when the user types [COMPLETE_THIS_PROJECT] to activate a full-spectrum project completion workflow. Orchestrates autonomous agents to audit, identify gaps, plan, implement, test, and ship the project to 10/10 quality."
---

# [COMPLETE_THIS_PROJECT] Orchestrator

Activate a complete project completion workflow. This skill orchestrates a fleet of specialized autonomous agents to audit source code, identify missing dashboards/features/UI, plan implementation, execute in parallel, test, debug, and ship to production.

## Activation

User types `[COMPLETE_THIS_PROJECT]` optionally followed by a target quality score or specific focus area.

```
[COMPLETE_THIS_PROJECT]
[COMPLETE_THIS_PROJECT] to 10/10
[COMPLETE_THIS_PROJECT] focus on missing dashboards
[COMPLETE_THIS_PROJECT] focus on security
[COMPLETE_THIS_PROJECT] focus on tests
```

## Execution Protocol

### Phase 0: Project Audit & Gap Analysis (Sequential — Orchestrator)

The orchestrator performs a comprehensive audit before dispatching any agents.

**Audit checklist:**
1. **Dashboard inventory** — Enumerate all templates in `dashboard/templates/`, cross-reference with sidebar navigation
2. **Backend-API coverage** — Map every Flask route to its frontend counterpart
3. **UI component audit** — Check for missing: buttons, widgets, scrollbars, graphs, charts, dividers, web cards, tooltips, nav tabs, media elements, settings panels
4. **Test coverage gap** — Run `pytest --collect-only` and identify untested modules
5. **Documentation gap** — Check README, API docs, CHANGELOG, SKILL.md files
6. **Security audit** — Scan for hardcoded secrets, missing auth, input validation gaps
7. **Integration audit** — Verify all cross-module imports work, no circular deps
8. **Config audit** — Check all JSON/YAML configs are present and valid

**Output:** `PROJECT_AUDIT.md` in working directory with structured gap report.

### Phase 1: Planning (Sequential — Orchestrator)

Based on audit results, produce:
- **Implementation plan** with priority-ordered tasks
- **Dev checklist** — each task with acceptance criteria
- **UI/UX design spec** for missing dashboards (layout, components, interactions)
- **Risk assessment** — identify blocking dependencies

**Output:** `IMPLEMENTATION_PLAN.md` and `DEV_CHECKLIST.md`

### Phase 2: Parallel Implementation (Batch — Orchestrator dispatches 4-6 agents)

Dispatch agents in waves based on dependency analysis.

**Wave 1 — Core Infrastructure:**
- Agent-DB: Database schema fixes, migrations
- Agent-API: Missing backend endpoints
- Agent-Config: Config files, env vars, .env.example updates

**Wave 2 — Frontend Dashboards:**
- Agent-FE-1: Dashboard template #1 (highest priority gap)
- Agent-FE-2: Dashboard template #2
- Agent-FE-3: Dashboard template #3
- Agent-FE-4: Dashboard template #4

**Wave 3 — UI Polish:**
- Agent-UI: Shared components, CSS consistency, theme enforcement
- Agent-NAV: Navigation fixes, sidebar, routing
- Agent-RESP: Responsive design, accessibility (WCAG 2.1 AA)

**Wave 4 — Testing:**
- Agent-TEST-1: Unit tests for backend modules
- Agent-TEST-2: Integration tests
- Agent-TEST-3: E2E tests for new dashboards

**Wave 5 — Documentation:**
- Agent-DOCS-1: API documentation
- Agent-DOCS-2: README updates
- Agent-DOCS-3: Screenshot generation

### Phase 3: Verification (Sequential — Orchestrator)

Run full test suite, verify no regressions, check CI status.

### Phase 4: Ship (Sequential — Orchestrator)

Commit, push, create PR if needed, merge to main, delete feature branches.

## Agent Types

| Agent Type | Role | Focus |
|-----------|------|-------|
| `general` | Implementation | Complex multi-step development tasks |
| `explore` | Audit/Analysis | Codebase exploration, gap identification |
| `developer` | Code Generation | Specific feature implementation |

## Project-Specific Configuration

### Target Repository
- **Repo:** `ProjectZeroDays/FreeAI_AI-Inference-Workstation`
- **Working Directory:** `C:\Users\Project Zero\FreeAI_AI-Inference-Workstation`
- **Platform:** Windows (git at `C:\Program Files\Git\cmd\git.exe`)
- **Python:** 3.14.6, pytest, Flask
- **Frontend:** HTML/CSS/JS templates with FreeAI dark theme (CSS variables: `--bg`, `--panel`, `--border`, `--accent`, `--accent-2`, `--muted`, `--muted-2`, `--warn`, `--danger`)

### Existing Dashboard Pages
- `index.html`, `dashboard.html`
- `remote-access.html`, `skills-catalog.html`, `encryption.html`, `salad.html`
- `desktop.html`, `subagents.html`, `aikido.html`, `hermes.html`
- `providers.html`, `skills.html`, `workflows.html`, `scheduler.html`, `mcp.html`
- `plugins-manage.html`, `browser-v2.html`, `reports.html`, `sandbox.html`
- `vast-ai.html`, `loot.html`, `c2.html`, `automations.html`, `gateway.html`
- `memory.html`, `training.html`, `todos.html`
- `secrets.html`, `rbac.html`, `login.html`

### Existing Backend Modules
- `dashboard/backend.py` — Flask app (8000+ lines)
- `router/router.py` — Router API
- `auth/` — JWT auth, RBAC, users
- `todos/` — Todo API (newly added)
- `browser/` — Knight-Shade browser engine
- `agents/` — Specialized agents
- `skills/` — Skill catalog
- `workflow/` — Workflow engine
- `services/` — Service integrations
- `mcp/` — MCP servers

### Test Suite
- **Total:** 975+ tests
- **Target:** 100% pass rate
- **Coverage target:** 90%+

## Implementation Plan Template

```markdown
# IMPLEMENTATION_PLAN.md

## Audit Summary
- Dashboard gaps: X missing
- Backend-API gaps: Y endpoints uncovered
- Test gaps: Z modules untested
- Security issues: N findings
- Documentation gaps: M files missing

## Priority Tasks
### P0 — Blocking (must complete first)
1. [ ] Task name — reason, effort, dependency

### P1 — Core Features
1. [ ] Task name — reason, effort, dependency

### P2 — Polish & UX
1. [ ] Task name — reason, effort, dependency

### P3 — Documentation
1. [ ] Task name — reason, effort, dependency

## Dev Checklist
- [ ] All P0 tasks complete
- [ ] All P1 tasks complete
- [ ] Tests: X/Y passing
- [ ] Lint: clean
- [ ] Security scan: clean
- [ ] CI: green
- [ ] Docs: updated
- [ ] Committed and pushed
```

## Dev Checklist Template

```markdown
# DEV_CHECKLIST.md

## Pre-Flight
- [ ] Audit complete
- [ ] Plan approved
- [ ] Branch created: `feat/project-completion`

## Implementation
- [ ] Phase 2 Wave 1 (Infrastructure) complete
- [ ] Phase 2 Wave 2 (Frontend) complete
- [ ] Phase 2 Wave 3 (UI Polish) complete
- [ ] Phase 2 Wave 4 (Testing) complete
- [ ] Phase 2 Wave 5 (Documentation) complete

## Verification
- [ ] All tests passing: X/X
- [ ] No lint errors
- [ ] No security alerts (CodeQL clean)
- [ ] No broken imports
- [ ] Backend starts without errors
- [ ] Frontend builds successfully
- [ ] Dashboard pages render correctly
- [ ] API endpoints respond correctly

## Post-Flight
- [ ] Committed with descriptive message
- [ ] Pushed to origin
- [ ] PR created (if applicable)
- [ ] Merged to main
- [ ] Feature branch deleted
- [ ] CHANGELOG updated
- [ ] Git tag created (if version bump)
```

## Quality Gates

### 10/10 Criteria
1. **All dashboards have corresponding backend APIs**
2. **All backend APIs have frontend UI coverage**
3. **All modules have test coverage (≥90%)**
4. **No security vulnerabilities (CodeQL clean)**
5. **All tests passing (100%)**
6. **Consistent UI/UX across all pages**
7. **Documentation complete (README, API docs, CHANGELOG)**
8. **No merge conflicts, clean git history**
9. **CI/CD pipeline green**
10. **Zero known issues or TODOs in production code**

### UI Consistency Rules
- Use project CSS variables: `--bg`, `--panel`, `--border`, `--accent`, `--accent-2`, `--muted`, `--muted-2`, `--warn`, `--danger`
- Dark theme by default (glass-morphism style)
- Consistent card layout: `<div class="q-card">` with `.q-card-header`, `.q-card-content`
- Sidebar navigation: collapsible, icon + label
- Toast notifications: success (green), error (red), info (blue)
- Loading states: spinner + skeleton screens
- Error states: inline error messages with icons

## Error Handling

### Agent Failure
1. Log failure to `.completion/failures.log`
2. Analyze root cause from error output
3. Retry once with modified approach
4. Escalate to orchestrator if second failure
5. Continue with other agents (don't block entire workflow)

### Test Failures
1. Read failure output
2. Diagnose root cause (import error, logic error, test isolation)
3. Fix code or test
4. Re-run failing test in isolation
5. Re-run full suite
6. Report to orchestrator

### Timeouts
- Set explicit timeouts: `"timeout_ms": 600000` (10 minutes per agent)
- Agents that timeout are marked `failed — timeout`
- Orchestration continues with remaining agents
- Timeout agents are retried in next wave with simplified scope

## Output Artifacts

### During Execution
- `PROJECT_AUDIT.md` — Gap analysis report
- `IMPLEMENTATION_PLAN.md` — Prioritized task list
- `DEV_CHECKLIST.md` — Trackable completion checklist
- `.completion/progress.json` — Real-time progress tracking
- `.completion/failures.log` — Failed agent logs

### Final Deliverables
- All missing dashboards implemented
- All missing backend APIs implemented
- All tests passing
- Documentation updated
- Commit pushed to main (or PR created)
- Feature branches cleaned up

## When NOT to Use [COMPLETE_THIS_PROJECT]

- **Already complete project** — If all quality gates pass, skip
- **Single focused fix** — Use [SWARM] for targeted work
- **No access to repo** — Cannot audit or implement without code access
- **External dependencies blocking** — If CI/build requires external access not available

Use [COMPLETE_THIS_PROJECT] when you want **autonomous end-to-end project completion** with full audit, planning, implementation, testing, and deployment.
