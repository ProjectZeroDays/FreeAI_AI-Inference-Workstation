---
name: autonomous-sdlc-orchestrator
description: "Expert SDLC orchestration skill for launching custom subagent teams through the full development lifecycle — plan, code, test, fix, review, document, package. Triggers: 'autonomous development', 'SDLC agent', 'plan code test fix', 'build from spec', 'autonomous SDLC', 'custom agent team', 'dev lifecycle', 'self-healing development', 'autonomous coding', 'spec-to-delivery', 'full SDLC pipeline', 'autonomous project', '[COMPLETE]'. Use when user wants a complete project built autonomously with real verification at every phase."
license: MIT
---

# Autonomous SDLC Orchestrator — Expert Skill

Master orchestrator for end-to-end software development with custom subagent teams. Plans, codes, tests, fixes, reviews, documents, and packages — with real shell verification at every gate.

## Core Principles

1. **Spec-first, never skip planning** — Every project starts with a structured plan before a single line of code.
2. **Real verification, not static analysis** — Run actual compilers, test suites, and linters inside sandboxed workspaces.
3. **Self-healing fix loop** — Failed tests feed directly back into the fix phase; up to 3 rounds before escalation.
4. **Specialist subagents per phase** — Each phase uses a purpose-built subagent with domain-specific prompts.
5. **Audit trail always** — Every action logged to JSONL; runs are inspectable at any time.

---

## The 7-Phase Lifecycle

```
┌─────────┐   ┌─────────┐   ┌─────────┐   ┌─────────┐   ┌─────────┐   ┌─────────┐   ┌─────────┐
│  PLAN   │ → │  CODE   │ → │  TEST   │ → │  FIX    │ → │  REVIEW │ → │  DOC    │ → │ PACKAGE │
└─────────┘   └─────────┘   └─────────┘   └─────────┘   └─────────┘   └─────────┘   └─────────┘
                                                 ↑
                                                 └────── LOOP (up to 3 rounds)
```

### Phase 1: PLAN — Architect Subagent

**Role:** Decomposes the spec into executable, ordered tasks with file-level detail.

**Subagent Prompt Template:**
```
You are a senior software architect. Given this spec, produce a numbered task list.

SPEC:
{spec}

OUTPUT (JSON array only):
[
  {{
    "id": "task_1",
    "title": "One-line title",
    "detail": "What exactly to build",
    "files": ["path/to/file.py"],
    "dependencies": [],
    "estimated_tokens": 2048,
    "verify_command": "pytest tests/test_task1.py"
  }}
]

Rules:
- First task creates the project skeleton
- Each task is independently completable
- Include a final task for integration tests
- Never exceed {max_tasks} tasks
```

**Output:** `workspaces/<run_id>/plan.json` + `_run.json` status `planning → coding`

---

### Phase 2: CODE — Implementation Subagent

**Role:** Writes complete, runnable files per task. No placeholders.

**Subagent Prompt Template:**
```
You are a senior developer. Implement the following task in full.

PROJECT SPEC:
{spec}

TASK:
- id: {task_id}
- title: {task_title}
- detail: {task_detail}
- files to create/modify: {task_files}

EXISTING WORKSPACE:
{file_tree}

CODE SAMPLES (first 4 files):
{code_sample}

OUTPUT FORMAT — one block per file, nothing else:
=== FILE: relative/path ===
<entire file content, no truncation>
=== END ===

RULES:
- Complete files only. No "..." or "TODO" or stubs.
- Use stdlib first, third-party only if spec requires it.
- Every file must be syntactically valid on output.
- Follow existing project style (see code samples).
```

**Verification:** After each task, run `verify_command` if specified.

---

### Phase 3: TEST — Verification Subagent

**Role:** Runs real tests, linters, type checkers, and static analysis.

**Verification Matrix:**
| Language | Commands |
|----------|----------|
| Python | `python -m py_compile`, `pytest`, `flake8`, `mypy --ignore-missing-imports` |
| JavaScript/TS | `node --check`, `tsc --noEmit`, `eslint .`, `jest` |
| Go | `go build ./...`, `go vet`, `golangci-lint run` |
| Rust | `cargo check`, `cargo clippy -- -D warnings` |
| Any | `bash -n` on shell scripts, `json.tool` on JSON files |

**Subagent Prompt Template:**
```
You are a QA engineer. Run verification on the workspace and report findings.

WORKSPACE ROOT: {workspace_root}
COMMANDS TO RUN:
{commands}

For each command:
1. Run it in the workspace directory
2. Capture stdout/stderr (last 2000 chars each)
3. Report exit code, command, and output summary
4. Classify each issue: BUG | STYLE | SECURITY | PERFORMANCE

OUTPUT FORMAT:
{{
  "ran": true,
  "results": [
    {{"label": "python:pytest", "command": "...", "exit": 0, "output": "...", "issues": []}}
  ],
  "issues": ["[pytest] tests/test_auth.py::test_login FAILED — assertion error on line 42"]
}}
```

---

### Phase 4: FIX — Remediation Subagent

**Role:** Fixes every issue found in TEST phase. Loops up to MAX_FIX_ROUNDS.

**Subagent Prompt Template:**
```
You are a debugging specialist. Fix every reported issue.

SPEC:
{spec}

ISSUES TO FIX:
{issues}

CURRENT FILES:
{file_tree}

KEY FILE EXCERPTS:
{code_sample}

OUTPUT — only modified files:
=== FILE: relative/path ===
<complete fixed file>
=== END ===

RULES:
- Fix the root cause, not symptoms
- Don't change unrelated code
- Every fix must be self-contained
- If an issue can't be fixed, explain why in the issue report
```

**Loop Logic:**
```
fix_round = 0
while issues and fix_round < MAX_FIX_ROUNDS:
    fix_result = run_fix_subagent(issues)
    issues = run_test_subagent()  # re-verify
    fix_round += 1
if issues:
    state["error"] = f"Fix loop exhausted after {fix_round} rounds. Remaining: {issues[:3]}"
    state["status"] = "failed"
else:
    state["status"] = "reviewing"
```

---

### Phase 5: REVIEW — Code Review Subagent

**Role:** Critical review pass before documentation.

**Review Criteria:**
- Correctness against spec
- Security (injection, auth, input validation)
- Error handling completeness
- API consistency
- Edge cases covered
- No hardcoded secrets

**Subagent Prompt Template:**
```
You are a principal engineer doing a final code review.

PROJECT: {spec}
FILES REVIEWED: {file_list}

REVIEW CHECKLIST:
1. Does the code match the spec exactly?
2. Are there any security vulnerabilities?
3. Is error handling complete?
4. Are there any hardcoded secrets or credentials?
5. Is the API surface clean and consistent?
6. Are edge cases handled?

VERDICT: APPROVE | REVISE | REJECT
REASON: <detailed explanation>
SUGGESTED_CHANGES: [<list>]
```

---

### Phase 6: DOC — Documentation Subagent

**Role:** Generates README, API docs, architecture docs, usage examples.

**Subagent Prompt Template:**
```
You are a technical writer. Generate complete project documentation.

PROJECT: {spec}
FINAL FILE TREE: {file_tree}
KEY MODULES: {key_files}

GENERATE:
1. README.md — overview, install, usage, examples, architecture
2. docs/API.md — all public endpoints/functions with signatures
3. docs/ARCHITECTURE.md — system design, data flow, component diagram
4. CHANGELOG.md — what was built
5. docs/CONTRIBUTING.md — how to extend

OUTPUT FORMAT:
=== FILE: path ===
<complete markdown content>
=== END ===
```

---

### Phase 7: PACKAGE — Distribution Subagent

**Role:** Creates distributable artifact (tar.gz, ZIP, or wheel).

**Subagent Prompt Template:**
```
You are a release engineer. Package this project for distribution.

PROJECT: {spec}
WORKSPACE: {workspace_root}

TARS:
1. _artifact.tar.gz — full project excluding .git, __pycache__, *.pyc, node_modules
2. VERSION file with current version
3. metadata.json with build info:
   {{
     "run_id": "{run_id}",
     "created_at": "<ISO timestamp>",
     "task_count": {n},
     "file_count": {n},
     "test_count": {n},
     "pass_rate": "{pct}%"
   }}
```

---

## Custom Subagent Factory

Launch specialized subagents per phase using the `actor` tool with skill context:

```javascript
// Plan phase
actor({
  operation: "run",
  subagent_type: "general",
  description: "SDLC planner",
  prompt: `You are the PLAN subagent. ${PLAN_PROMPT}`
})

// Code phase (spawn per task)
actor({
  operation: "run",
  subagent_type: "general",
  description: `SDLC coder: ${task.id}`,
  prompt: `You are the CODE subagent for ${task.title}. ${CODE_PROMPT}`
})

// Test phase
actor({
  operation: "run",
  subagent_type: "explore",
  description: "SDLC verifier",
  prompt: `You are the TEST subagent. Run these commands in ${workspace_root}: ${commands}`
})

// Fix phase
actor({
  operation: "run",
  subagent_type: "general",
  description: "SDLC fixer",
  prompt: `You are the FIX subagent. Fix these issues: ${issues}`
})
```

---

## Workspace Management

Each run gets an isolated workspace:
```
workspaces/<run_id>/
  _run.json          # full state machine
  plan.json          # parsed task list
  _artifact.tar.gz   # final distribution
  <task_1_files>/    # per-task scratch (optional)
  README.md
  src/
  tests/
  docs/
```

**Workspace lifecycle:**
1. `Workspace(run_id).init()` — creates isolated directory
2. Path traversal blocked: rejects `../`, absolute paths, drive letters
3. 512KB per-file cap enforced
4. Shell double-gated: `ENABLE_SHELL_TOOLS=1` env + per-run `enable_shell` flag

---

## Concurrency & Safety

| Guard | Mechanism |
|-------|-----------|
| Max concurrent runs | `max_concurrent_runs` from config (default 3) |
| Over-capacity | Returns HTTP 429 immediately |
| Run cancellation | `POST /auto/runs/<id>/cancel` sets cancel flag |
| Shell safety | Commands timeout at `SHELL_TIMEOUT_S`; output capped at 3000 chars |
| File safety | Path traversal, absolute paths, and drive letters rejected |

---

## Integration Points

| Component | How to Use |
|-----------|------------|
| **FreeAI Router** | All LLM calls go through `AGENT_API` — profile selection, caching, metrics apply |
| **Workflow Engine** | SDLC run can be a workflow step; export/import pipeline definitions |
| **Dashboard** | `SDLC Runs` panel shows live status, 15s SSE refresh |
| **CLI** | `freeai.py auto-start "spec" --watch` for TTY execution |
| **API** | `POST /auto/start {spec, profile, max_tasks, enable_shell}` |

---

## Quick Start Examples

```bash
# One spec, full lifecycle
freeai.py auto-start "Build a FastAPI notes service with SQLite, JWT auth, and pytest"

# With shell verification (compiles, runs tests)
freeai.py auto-start "Build a Python CLI tool" --shell

# Watch mode — prints progress to terminal
freeai.py auto-start "Build a REST API" --watch 30

# Fetch artifact when done
freeai.py auto-fetch <run_id> -o project.tar.gz
```

```python
# Programmatic usage
from autonomous.agent import run_agent

result = run_agent(
    spec="Build a Flask blog with markdown support",
    profile="balanced",
    max_tasks=5,
    enable_shell=True,
    run_id="my-project-001",
)
print(result["artifact"])  # path to _artifact.tar.gz
```

---

## Error Handling

| Scenario | Behavior |
|----------|----------|
| LLM returns invalid JSON | Falls back to single task: `{id: "task_1", title: "implement spec", detail: spec}` |
| Test fails after 3 fix rounds | `status: "failed"`, error captured in `_run.json`, artifact still packaged |
| Workspace write blocked | Task marked with error, continues to next task |
| Cancelled during coding | Saves partial state, packages what exists |
| Cancelled during testing | Reports partial test results, doesn't package |

---

## Metrics & Observability

Every run emits:
- `logs/audit.jsonl` — phase transitions, file writes, verification results
- `workspaces/<id>/_run.json` — full state snapshot at every step
- `/api/evals/runs` — historical run list via dashboard
- `/metrics` — router-level counters (tasks completed, fix rounds, pass rate)

---

## Design Decisions

1. **Real shell > static analysis** — `python -m py_compile` catches more bugs than any linter. Shell tools are opt-in per-run.
2. **Fix loop bounded** — 3 rounds prevents infinite repair cycles. After that, escalate to human review.
3. **One workspace per run** — isolation prevents cross-contamination; artifacts are tarballs not live directories.
4. **Spec-driven, not iteratively prompted** — the full spec is injected once at planning; tasks are derived, not negotiated mid-flow.
5. **Review is a gate, not a suggestion** — APPROVE required to proceed; REVISE returns to fix; REJECT stops the run.

---

## Enhanced Workflow Patterns

### Pattern A: Parallel Wave Execution

When tasks are **independent** (no shared files), dispatch them in parallel waves:

```
Task dependency graph analysis:
  task_1 → task_2 → task_3
  task_1 → task_4
  task_5 (independent)

Wave 1 (parallel): task_1, task_5
Wave 2 (parallel): task_2, task_4
Wave 3 (parallel): task_3
```

**Dispatch rule:** Only one task per workspace. Shared-file tasks stay sequential; independent tasks go parallel.

```javascript
// Parallel dispatch example
const parallelTasks = tasks.filter(t => t.dependencies.length === 0);
await Promise.all(parallelTasks.map(task =>
  actor({ operation: "run", subagent_type: "general",
    description: `SDLC coder: ${task.id}`,
    prompt: CODE_PROMPT.replace("{task_id}", task.id) })
));
```

---

### Pattern B: Spec Clarification (Pre-Flight)

Before planning, resolve ambiguity. Ask **one question at a time**:

```
Spec: "Build a todo API"

Orchestrator asks:
  Q: SQLite or PostgreSQL?
  A: SQLite

  Q: Auth required?
  A: No

  Q: Pagination on list endpoint?
  A: Yes, limit/offset
```

**When to skip:** Spec is already specific (includes tech stack, constraints, acceptance criteria).

---

### Pattern C: TDD Enforcement

Every task MUST follow test-first discipline:

```
1. Write failing test (test_<feature>.py)
2. Watch it fail
3. Write implementation
4. Watch it pass
5. Commit
```

**Hard gate:** No code without a green test. If tests were skipped, flag as `review_notes` and return to FIX phase.

---

### Pattern D: Systematic Debugging (Root Cause First)

Before fixing, investigate:

```
1. READ the error — don't guess
2. REPRODUCE — run the failing command manually
3. TRACE — check recent changes, data flow, inputs
4. HYPOTHESIZE — one cause at a time
5. TEST — verify hypothesis before applying fix
```

**Hard gate:** Never patch symptoms. Fix the root cause.

---

### Pattern E: Structured Handoffs

Every subagent completion must include:

```
Status: success | failed | blocked
Summary: <one-line what was done>
Files touched: [<path>, ...]
Tests: <N> passing, <M> failing
Known issues: <none | list>
Next action: <what should happen next>
```

Bad handoff: *"Done with the auth module."*
Good handoff: *"Built JWT auth at src/auth/. 12 tests passing. Known: refresh token rotation not implemented. Next: frontend login form."*

---

### Pattern F: Git Integration (Per-Phase Commits)

Commit at each phase boundary for rollback and audit:

```bash
# After PLAN
git add plan.json && git commit -m "plan: <spec summary>"

# After each CODE task
git add -p && git commit -m "feat(<task_id>): <title>"

# After REVIEW approval
git add -A && git commit -m "review: <verdict> — <summary>"

# After PACKAGE
git tag v1.0.0-<run_id> && git push --tags
```

---

### Pattern G: Progress Logging

Timestamped status log for every action:

```
[00:00:00] SDLC START — run_id=abc123 spec="Build X"
[00:00:05] PLAN   — 5 tasks generated
[00:00:12] CODE   — task_1: src/main.py (234B) ✓
[00:00:25] CODE   — task_2: src/routes.py (512B) ✓
[00:00:41] TEST   — python:pytest exit=0, 14 tests passing
[00:00:42] FIX    — skipped (0 issues)
[00:00:48] REVIEW — APPROVE
[00:00:55] DOC    — README.md, docs/API.md generated
[00:01:02] PACKAGE — _artifact.tar.gz (4.2KB)
[00:01:02] SDLC DONE — 62s total, 5 tasks, 14 tests
```

---

## Quality Gates (10/10 Criteria)

Before marking a run COMPLETE, verify:

| # | Gate | Pass Condition |
|---|------|---------------|
| 1 | All specs implemented | Every task in plan has corresponding files |
| 2 | Tests green | All `verify_command` outputs exit=0 |
| 3 | No hardcoded secrets | grep for `api_key`, `password`, `token` in source |
| 4 | Error handling complete | Every API endpoint has error response |
| 5 | Documentation exists | README.md present with setup + usage |
| 6 | Artifact packages cleanly | `tar tzf _artifact.tar.gz` lists all files |
| 7 | Follows project style | Matches existing code patterns in the repo |
| 8 | No placeholder code | grep for `TODO`, `FIXME`, `pass` at top-level |
| 9 | Type hints where applicable | Python: `def fn(x: int) -> str:` not `def fn(x):` |
| 10 | Git history clean | Descriptive commit messages, no merge conflicts |

**All 10 gates must pass.** Any failure returns to the appropriate phase.

---

## Output Artifacts

### During Execution
- `workspaces/<run_id>/_run.json` — phase-by-phase state machine
- `workspaces/<run_id>/plan.json` — parsed task list with dependencies
- `logs/audit.jsonl` — timestamped action log
- `.completion/progress.json` — real-time progress tracker
- `.completion/failures.log` — per-agent failure records

### Final Deliverables
- `_artifact.tar.gz` — distributable project tarball
- `metadata.json` — build info (run_id, timestamps, task/test counts)
- Committed to git with descriptive messages at each phase boundary

---

## Skill Integration Matrix

| Existing Skill | How It Complements SDLC |
|---------------|------------------------|
| `superpowers` | Use brainstorming + TDD references before PLAN phase |
| `swarm-orchestrator` | Use parallel dispatch pattern for independent CODE tasks |
| `agent-team-orchestration` | Use handoff protocol + role definitions |
| `ui-ux-architect` | Use for any frontend/UI components in the spec |
| `complete-this-project` | Use after SDLC for repo-level gap filling |
| `debug-pro` | Use when systematic debugging is needed in FIX phase |
| `code-review` | Use for REVIEW phase review gate |
| `simplify-and-harden` | Use after PACKAGE for final polish pass |

---

## [COMPLETE] Command

Type `[COMPLETE]` to activate the full SDLC pipeline on the current spec. The orchestrator will:

1. Run Phase 0 audit (if workspace exists) or Phase 1 brainstorm (if new spec)
2. Execute all 7 phases sequentially with quality gates
3. Commit at each phase boundary
4. Produce `_artifact.tar.gz` and full audit trail
5. Report: run_id, duration, task count, test count, pass rate, git hash

