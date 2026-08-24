# Unified GPU Inference Stack

Production-grade, self-hosted environment for running GGUF coder models on NVIDIA GPUs with automatic task-based model switching, a multi-agent REST layer, workflow engine, Tokugawa UI/dashboard, and a full XFCE + VNC desktop.

## Overview

- **GGUF inference** on NVIDIA GPUs (llama.cpp + CUDA)
- **Tokugawa Router** — classifies each prompt (with confidence) and routes it to the right model, with fallback chains, LRU caching, rate limiting, optional API-key auth, and a `/metrics` endpoint
- **Agent REST API** — project scaffolding, refactor, debug, analysis, orchestrator + memory-backed chat; profiles: strict/balanced/creative/verbose/minimal
- **Workflow Engine** — chains agents into pipelines (sequential + parallel, retries, validation, audit logs, export/import, inline execution)
- **Tokugawa UI** — model presets, agent buttons, prompt/output console
- **Workflow Designer** — visual step editor (`workflow/ui/designer.html`) with JSON export
- **Tokugawa Dashboard** — live GPU stats (util/mem/temp/power/clock), alerts panel, service health with charts
- **tokugawa-cli** — status / models / route / workflows / run from your shell
- **Desktop environment** — XFCE + TigerVNC + noVNC
- **Self-healing** — supervisor loop plus health/recovery agents
- **Docker Compose** — one command brings up every service

### Model roster

| Key | Model | Role |
|---|---|---|
| `qwen3.6-12b` | Qwen3.6 12B IQ Ultra Heretic Uncensored Thinking (GGUF) | Primary coder — architecture, full projects, CI/CD |
| `moe-13b` | L3.1 MOE 2x8B DeepSeek DeepHermes e32 Abliterated 13.7B (GGUF) | Fast coder — refactor, debug, patch |
| `qwen3.5-9b` | Qwen3.5 9B Claude HighIQ Heretic Uncensored (GGUF) | Reasoning — analysis, planning |

> Note: llama.cpp serves one loaded model per process; the router's task classification selects per-request metadata/params against that endpoint. Swap `LLAMA_MODEL_PATH` to change which roster entry is hot.

## Ports

| Port | Service |
|---|---|
| 8010 | Tokugawa Router — `POST /route`, `GET /models`, `GET /health` |
| 8020 | Agent REST API — `/agent/project` `/agent/refactor` `/agent/debug` `/agent/analyze` `/agent/orchestrate` |
| 8040 | Workflow Engine — `GET /workflows`, `POST /workflow/run` |
| 8050 | Autonomous SDLC — plan → code → test → fix → document → package |
| 8030 | Dashboard UI + `GET /api/status` |
| 9001 | llama.cpp completion endpoint |
| 9002 | vLLM (optional profile) |
| 5901 / 6080 | VNC / noVNC desktop |

## Architecture

```
Tokugawa UI (:ui assets)      Dashboard (:8030)
        │                            │
        ▼                            ▼
   Agent API (:8020) ──────► Router (:8010)
        │                     classify → select_model
        ▼                            │
   Workflow Engine (:8040)           ▼
                              llama.cpp (:9001)   vLLM (:9002, optional)
```

## Quick Start

```bash
./install.sh                          # system deps, venv, builds llama.cpp
bash models/auto-download-models.sh   # fetches all three GGUF models (resumable)
./start.sh                            # launches everything
./validate.sh                         # preflight checks
```

Open:
- UI: serve `ui/tokugawa.html` (any static server) or open directly in a browser
- Dashboard: http://localhost:8030

## Docker Compose

```bash
docker compose up -d --build                 # core: llama, router, agents, workflow, dashboard
docker compose --profile vllm up -d          # add vLLM backend
docker compose --profile desktop up -d       # add XFCE/VNC/noVNC container
```

## Router

The router classifies each prompt (`full_project` → qwen3.6-12b, `refactor` → moe-13b, `analysis` → qwen3.5-9b) and forwards it to the selected model endpoint:

```bash
curl -X POST http://localhost:8010/route \
  -H "Content-Type: application/json" \
  -d '{"prompt":"Write a production-ready API in Go","max_tokens":2048}'
```

Response includes `model_used`, `task_type`, and the backend `response`.

## Agent API examples

```bash
# Project scaffolding
curl -X POST http://localhost:8020/agent/project \
  -H "Content-Type: application/json" \
  -d '{"spec":"Build a rideshare backend with auth, trips, payments"}'

# Refactor
curl -X POST http://localhost:8020/agent/refactor \
  -H "Content-Type: application/json" \
  -d '{"code":"def add(a,b):return a+b"}'

# Debug
curl -X POST http://localhost:8020/agent/debug \
  -H "Content-Type: application/json" \
  -d '{"code":"print(1/0)", "error":"ZeroDivisionError"}'

# Analysis
curl -X POST http://localhost:8020/agent/analyze \
  -H "Content-Type: application/json" \
  -d '{"context":"We have 5 microservices sharing one DB","question":"What are the risks?"}'
```

## Workflow Engine

```bash
curl -X POST http://localhost:8040/workflow/run \
  -H "Content-Type: application/json" \
  -d '{
    "workflow": "full_build",
    "context": {
      "spec": "Build a production-ready FastAPI backend for a rideshare app."
    }
  }'
```

Runs architecture → codegen → tests through the model-switching router. Features: sequential or parallel steps (`run_parallel`), 3-attempt retry per step, validation warnings, JSONL audit log (`logs/workflow-audit.jsonl`), registry-based discovery (`GET /workflows`), export (`GET /workflow/export/{name}`), inline execution (`POST /workflow/run-inline`). Register new pipelines in `workflow/registry.py`.

## Autonomous SDLC Agents

One prompt in, a packaged project out — the full development life cycle unattended:

```
plan → code → test → fix → review → document → package
```

```bash
python3 tokugawa.py auto-start "Build a FastAPI notes service with tests" --watch 20
python3 tokugawa.py auto-fetch <run_id> -o project.tar.gz
```

- **Real verification**: shell tools (`ENABLE_SHELL_TOOLS=1`) run `compileall`/`pytest`/`node --check` inside the sandbox; fix loops are driven by actual error output, not vibes. Falls back to static placeholder scanning.
- **Sandboxed**: every write resolves inside `workspaces/<run_id>/`; traversal rejected. Shell off by default.
- **Deliverable**: tarball artifact per run, downloadable via API/CLI.

See [docs/autonomous-agents.md](docs/autonomous-agents.md).

## Workflow Designer

Open `workflow/ui/designer.html` in a browser (or `python3 -m http.server -d workflow/ui`): add steps, set name/agent/consumes, delete, and **Save Workflow** exports a definition JSON that `POST /workflow/run-inline` can execute.

## CLI

```bash
python3 tokugawa.py status                 # health + router metrics
python3 tokugawa.py models
python3 tokugawa.py route "Build a REST API" --profile strict
python3 tokugawa.py workflows
python3 tokugawa.py run full_build --context '{"spec":"..."}'
```

## Configuration & profiles

`config/config.json` is the single source of truth; every value is overridable by env (see `router/settings.py`). Docker Compose reads `.env` (copy `.env.example`). Dev without a GPU: `MOCK_LLM=1`.

## Security

- Router API keys: set `ROUTER_API_KEY`, send `X-API-Key`
- Per-client token-bucket rate limiting (429 when exhausted)
- Model servers stay on internal network; only router/dashboard/agents ports are published

## Testing

```bash
pip install -r requirements-dev.txt
pytest          # offline suite: classifier, switcher, cache, rate limiter,
                # router API (mock), agent profiles/memory, workflow engine
```

## Kubernetes

```bash
kubectl apply -f k8s/
```

Includes namespace, PVC for models, GPU nodeSelector/tolerations for llama & vLLM, deployments + services (llama, vLLM, router, agents, workflow), and HPAs for the CPU services. Images come from CI (`docker-publish.yml` pushes to GHCR on tags).

## Self-healing

- `supervisor.sh` — 10s loop restarting router, dashboard, llama-server, and vLLM (when enabled)
- `agents/health-agent.sh` — 30s GPU + router probes
- `agents/recovery-agent.sh` — 15s router restart guard

## Validation

```bash
./validate.sh     # venv, models/, registry, manifests, service ports
```

CI runs on push/PR: Python compile, bash syntax, JSON validity, JS syntax checks.

## File tree

```
unified-ai-stack/
├── install.sh · start.sh · validate.sh · supervisor.sh
├── docker-compose.yml · .env.example · tokugawa.py (CLI)
├── config/config.json              # centralized config
├── llama/            launch-llama.sh, Dockerfile
├── vllm/             launch-vllm.sh, Dockerfile
├── router/           router.py, classifier.py, switcher.py, models.py,
│                     settings.py, Dockerfile
├── agents/           api.py + 5 agent CLIs, health/recovery/gpu-warmup,
│                     run.sh, Dockerfile
├── workflow/         engine.py, registry.py, api.py, ui/designer.*,
│                     workflows/ (full_build, templates), Dockerfile
├── autonomous/       agent.py (SDLC loop), api.py :8050, workspace.py,
│                     prompts.py, Dockerfile
├── dashboard/        backend.py, templates/, static/ (Chart.js), Dockerfile
├── ui/               tokugawa.html/.js, theme.css, presets.json
├── models/           auto-download-models.sh (+ downloaded GGUFs, gitignored)
├── registry/         registry.json
├── manifest/         mimocode/jcode/opencode model maps
├── tests/            pytest suite (offline)
├── k8s/              namespace, PVC, deployments, services, HPAs
├── docs/             MkDocs site sources + generate_docs.py
└── .github/workflows/  ci · workflow-ci · docs · docker-publish · release
```

See [ROADMAP.md](ROADMAP.md) for the implemented/planned feature matrix.

## Hardware

The stack is designed for an always-on CUDA workstation — verified
parts list (MPN-level SKUs), assembly guide, and a one-shot Ubuntu
provisioner live in [`hardware/`](hardware/):

- [hardware/parts-list.md](hardware/parts-list.md) — Center AI Workstation v1 (~$2.3–2.6k, RTX 4070 Ti Super 16G)
- [hardware/LOCAL-DEPLOY.md](hardware/LOCAL-DEPLOY.md) — min requirements, build-vs-cloud economics
- [hardware/BUILD.md](hardware/BUILD.md) — step-by-step assembly + Ubuntu 24.04
- `sudo ./hardware/install-stack.sh` — drivers → CUDA → Docker → stack → watchdogs/GPU-tune/optimizer systemd units → UFW
- `./hardware/setup-remote-access.sh tailscale|cloudflare` — remote access
- `sudo ./hardware/gpu-power-tune.sh apply` — undervolt-equivalent profile (−10..20°C)
- `agents/resource_optimizer.py` — AI power-mode controller: watches GPU temp/utilization, shifts performance/balanced/eco automatically; mode shows on the dashboard

## Troubleshooting

| Symptom | Fix |
|---|---|
| `llama-server not found` | Run `./install.sh` (builds into `llama.cpp/build/bin/`) |
| Model download stalls | Re-run downloader — resumes via `wget -c` |
| Router 502 | llama.cpp not up yet; check `logs/llama.log` |
| CUDA build skipped | Install NVIDIA CUDA toolkit so `nvcc` is on PATH, re-run installer |
| Port conflicts | All ports overridable via env (`ROUTER_PORT`, `LLAMA_PORT`, etc.) |
