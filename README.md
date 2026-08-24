# Unified GPU Inference Stack

Production-grade, self-hosted environment for running GGUF coder models on NVIDIA GPUs with automatic task-based model switching, a multi-agent REST layer, workflow engine, Tokugawa UI/dashboard, and a full XFCE + VNC desktop.

## Overview

- **GGUF inference** on NVIDIA GPUs (llama.cpp + CUDA)
- **Tokugawa Router** — classifies each prompt and routes it to the right model
- **Agent REST API** — project scaffolding, refactor, debug, analysis agents
- **Workflow Engine** — chains agents into pipelines (sequential + parallel, retries, logging)
- **Tokugawa UI** — model presets, agent buttons, prompt/output console
- **Tokugawa Dashboard** — live GPU stats and service health with charts
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

Runs architecture → codegen → tests through the model-switching router. Features: sequential or parallel steps (`run_parallel`), 3-attempt retry per step, step logging, registry-based discovery (`GET /workflows`). Register new pipelines by adding a `Workflow` to `workflow/registry.py`.

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
├── docker-compose.yml · requirements.txt
├── llama/            launch-llama.sh, Dockerfile
├── vllm/             launch-vllm.sh, Dockerfile
├── router/           router.py, classifier.py, switcher.py, models.py, Dockerfile
├── agents/           api.py + 5 agent CLIs, health/recovery/gpu-warmup, run.sh, Dockerfile
├── workflow/         engine.py, registry.py, api.py, workflows/full_build.py, Dockerfile
├── dashboard/        backend.py, templates/, static/ (Chart.js GPU graph), Dockerfile
├── ui/               tokugawa.html/.js, theme.css, presets.json
├── models/           auto-download-models.sh (+ downloaded GGUFs, gitignored)
├── registry/         registry.json
├── manifest/         mimocode/jcode/opencode model maps
└── desktop/          start_xfce.sh, start_vnc.sh, start_novnc.sh
```

## Troubleshooting

| Symptom | Fix |
|---|---|
| `llama-server not found` | Run `./install.sh` (builds into `llama.cpp/build/bin/`) |
| Model download stalls | Re-run downloader — resumes via `wget -c` |
| Router 502 | llama.cpp not up yet; check `logs/llama.log` |
| CUDA build skipped | Install NVIDIA CUDA toolkit so `nvcc` is on PATH, re-run installer |
| Port conflicts | All ports overridable via env (`ROUTER_PORT`, `LLAMA_PORT`, etc.) |
