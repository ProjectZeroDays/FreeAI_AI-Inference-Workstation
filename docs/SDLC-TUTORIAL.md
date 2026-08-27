# Autonomous SDLC Agents — Tutorial

FreeAI's Autonomous SDLC layer turns a single-line project specification
into a fully packaged codebase by automatically walking through a complete
software development lifecycle.

---

## 1. Understanding the 7-Phase Lifecycle

When you submit a spec to the autonomous agents, they execute a strict
7-phase pipeline:

| Phase | What happens |
|---|---|
| **Plan** | The agent breaks your one-line spec down into a system architecture
and actionable ordered tasks (JSON plan). |
| **Code** | Code generation begins using the optimal model selected by the
FreeAI router for the task type. |
| **Test** | The system relies on **real verification**, not static guessing. It runs
`compileall`, `pytest` / `unittest`, or `node --check` inside a sandboxed
workspace. When shell tools are off, a placeholder-content scan is used as
fallback. |
| **Fix** | If the compilers or tests fail, the agent iterates and patches the
code until the tests pass — up to `MAX_FIX_ROUNDS` (default 3). |
| **Review** | A strict reviewer assesses the final tree and emits a `VERDICT: PASS`
or `VERDICT: FIX` with concrete issues. |
| **Document** | README.md (and docs/API.md where applicable) are automatically
generated from the final tree and code sample. |
| **Package** | The final, verified workspace is compressed into a downloadable
artifact tarball. |

```
queued → planning → coding → testing → fixing → reviewing
       → documenting → packaging → done | failed | cancelled
```

---

## 2. Launching an Autonomous Run

The Autonomous SDLC layer operates as a dedicated service on **port 8050**.

### Via API

```bash
# Start a run
curl -X POST http://localhost:8050/auto/start \
  -H "Content-Type: application/json" \
  -d '{"spec": "Build a Python REST API using FastAPI with SQLite that handles user authentication",
       "profile": "balanced",
       "max_tasks": 8,
       "enable_shell": true}'

# Response: {"run_id": "a1b2c3d4e5f6"}
```

### Via Dashboard

Open the FreeAI Dashboard (`http://localhost:8080/dashboard`), go to **SDLC Runs**,
and paste your spec into the input box. Click **Launch Run**.

### CLI

```bash
python freeai.py auto-start "Build a Python REST API using FastAPI with SQLite that handles user authentication" --watch 20
python freeai.py auto-runs
python freeai.py auto-fetch <run_id> -o my-project.tar.gz
```

---

## 3. Monitoring the Workflow

Track live progress from the FreeAI Dashboard:

1. Open **http://localhost:8080/dashboard**
2. Navigate to the **SDLC Runs** panel
3. The panel refreshes every 15 seconds and shows:
   - **Run ID** — unique identifier for the run
   - **Spec** — the project specification submitted
   - **Status badge** — current phase (Planning, Coding, Testing, Fixing, Reviewing, Documenting, Packaging, Done, Failed, Cancelled)
   - **Files** — count of files written so far
   - **Progress** — percentage complete

You can **cancel** a running run at any time via the dashboard or:

```bash
curl -X POST http://localhost:8050/auto/runs/<run_id>/cancel
```

> **Note:** The system enforces a concurrency cap (default: 3 parallel runs) to
> prevent GPU/CPU overload. If the cap is reached you'll see a `429` error —
> raise `max_concurrent_runs` in the Dashboard Settings.

---

## 4. Retrieving the Final Artifact

Once the agents complete the **Package** phase, the output is a downloadable
tarball containing your fully planned, coded, tested, and documented project.

### Via Dashboard
Navigate to the SDLC Runs panel and click **Download Artifact** on a completed run.

### Via API
```bash
curl -o my-project.tar.gz http://localhost:8050/auto/runs/<run_id>/artifact
```

### Via CLI
```bash
python freeai.py auto-fetch <run_id> -o my-project.tar.gz
```

---

## 5. Custom Pipelines — Manual Agent Invocation

Instead of relying solely on the autonomous loop, you can manually call any
agent persona via the **Agent API** on **port 8020**. This gives you full control
over the workflow, model profiles, and parameters.

### Available Personas

| Endpoint | Persona | Best For |
|---|---|---|
| `POST /agent/project` | **Scaffolding** | Turning a spec into a full project plan |
| `POST /agent/refactor` | **Refactoring** | Improving existing code quality |
| `POST /agent/debug` | **Debugging** | Fixing bugs and errors |
| `POST /agent/analyze` | **Analysis** | Deep technical reasoning |
| `POST /agent/orchestrate` | **Coordinator** | Multi-step coordination |
| `POST /agent/chat` | **Chat** | Conversational assistance |

### Temperature Profiles

| Profile | Temperature | Max Tokens | Use Case |
|---|---|---|---|
| `strict` | 0.0 | 2048 | Deterministic, precise output |
| `balanced` | 0.2 | 2048 | General purpose (default) |
| `creative` | 0.8 | 4096 | Brainstorming, design |
| `verbose` | 0.4 | 4096 | Detailed explanations |
| `minimal` | 0.2 | 512 | Short answers |

### Examples

```bash
# Scaffold a project from a spec
curl -X POST http://localhost:8020/agent/project \
  -H "Content-Type: application/json" \
  -d '{"spec": "Build a FastAPI app with SQLite auth",
       "profile": "creative",
       "session_id": "project-001"}'

# Refactor existing code
curl -X POST http://localhost:8020/agent/refactor \
  -H "Content-Type: application/json" \
  -d '{"code": "def sort(arr): return sorted(arr)",
       "language": "python",
       "goals": "add type hints and docstrings",
       "profile": "strict"}'

# Debug an error
curl -X POST http://localhost:8020/agent/debug \
  -H "Content-Type: application/json" \
  -d '{"code": "def divide(a,b): return a/b",
       "error": "TypeError: unsupported operand type(s)",
       "language": "python",
       "profile": "strict"}'

# Deep analysis
curl -X POST http://localhost:8020/agent/analyze \
  -H "Content-Type: application/json" \
  -d '{"context": "We have a FastAPI service with PostgreSQL",
       "question": "How should we handle connection pooling?",
       "profile": "balanced"}'

# Multi-agent orchestration
curl -X POST http://localhost:8020/agent/orchestrate \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Design a microservices architecture for an e-commerce platform",
       "profile": "creative"}'

# Persistent chat with memory
curl -X POST http://localhost:8020/agent/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "What did we decide about the auth strategy?",
       "session_id": "project-001",
       "profile": "balanced"}'
```

### Building Custom Pipelines

You can compose agents into custom pipelines by chaining calls:

```python
import requests

BASE = "http://localhost:8020"

# Pipeline: spec → plan → code → review → document
spec = "Build a CLI tool for file deduplication"

# Step 1: Get a project plan
plan = requests.post(f"{BASE}/agent/project", json={"spec": spec}).json()
print("Plan:", plan["response"])

# Step 2: Refactor the plan into code structure
refactor = requests.post(f"{BASE}/agent/refactor", json={
    "code": plan["response"],
    "language": "python",
    "goals": "convert to production-ready code structure"
}).json()
print("Refactored:", refactor["response"])

# Step 3: Analyze for potential issues
analysis = requests.post(f"{BASE}/agent/analyze", json={
    "context": refactor["response"],
    "question": "What edge cases should we handle?"
}).json()
print("Analysis:", analysis["response"])
```

---

## 6. Safety & Sandboxing

- All file writes in autonomous runs resolve inside
  `workspaces/<run_id>/`; path traversal is rejected.
- Shell execution is **off by default**. Enable with
  `ENABLE_SHELL_TOOLS=1` in the environment.
- Per-run shell access requires `enable_shell: true` in the request body.
- Commands run in the workspace directory with timeouts and capped output.
- Runs are cancellable at every phase boundary.

---

## 7. Configuration

Edit `config/runtime-settings.json` to adjust:

```json
{
  "max_concurrent_runs": 3,
  "max_fix_rounds": 3,
  "shell_timeout_s": 120
}
```

Or set via environment variables:
- `ENABLE_SHELL_TOOLS=1` — enable shell verification
- `MAX_FIX_ROUNDS=5` — allow more fix iterations
- `SHELL_TIMEOUT_S=180` — longer shell command timeout
