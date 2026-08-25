# Ubuntu-Desktop_XFCE_TigerVNC_noVNC_Tokugawa_llama.cpp_Opencode_Unified-AI-Stack

![version](https://img.shields.io/badge/version-1.1.0-blue)
![tests](https://img.shields.io/badge/tests-63_passing-brightgreen)
![python](https://img.shields.io/badge/python-3.10%2B-informational)
![cuda](https://img.shields.io/badge/CUDA-12.x-76B900)

Production-grade, self-hosted **AI inference workstation stack**: GGUF coder models on NVIDIA GPUs, a task-classifying model router with fallback chains, a multi-agent REST layer, a workflow engine, **autonomous SDLC agents** that turn a one-line spec into a packaged project, a presets/settings control plane, an AI power optimizer, self-healing watchdogs, and a full XFCE + VNC remote desktop. Deployable bare-metal, via Docker Compose, Kubernetes, cloud GPU providers, or as a Live ISO.

---

## Table of Contents

- [1. Overview](#1-overview)
- [2. Screenshots](#2-screenshots)
- [3. Feature Set Breakdown](#3-feature-set-breakdown)
- [4. Architecture](#4-architecture)
- [5. Ports and Services](#5-ports-and-services)
- [6. Getting Started](#6-getting-started)
- [7. Hardware Requirements](#7-hardware-requirements)
- [8. Install and Deploy Handbook](#8-install-and-deploy-handbook)
  - [8.1 Bare Metal Provisioner](#81-bare-metal-provisioner)
  - [8.2 Docker Compose Profiles](#82-docker-compose-profiles)
  - [8.3 Kubernetes](#83-kubernetes)
  - [8.4 GPU Providers](#84-gpu-providers)
  - [8.5 Live ISO](#85-live-iso)
- [9. Tool Handbook](#9-tool-handbook)
  - [9.1 Tokugawa Router](#91-tokugawa-router)
  - [9.2 Agent API](#92-agent-api)
  - [9.3 Workflow Engine](#93-workflow-engine)
  - [9.4 Autonomous SDLC Agents](#94-autonomous-sdlc-agents)
  - [9.5 Resource Optimizer and GPU Tune](#95-resource-optimizer-and-gpu-tune)
  - [9.6 Dashboard](#96-dashboard)
  - [9.7 tokugawa-cli](#97-tokugawa-cli)
  - [9.8 Watchdogs and systemd Units](#98-watchdogs-and-systemd-units)
  - [9.9 Backup and Cleanup Maintenance](#99-backup-and-cleanup-maintenance)
- [10. Configuration Reference](#10-configuration-reference)
- [11. API Reference](#11-api-reference)
- [12. Model Management](#12-model-management)
- [13. Custom Integrations](#13-custom-integrations)
- [14. Remote Access](#14-remote-access)
- [15. Testing and Validation](#15-testing-and-validation)
- [16. Performance Tuning Guide](#16-performance-tuning-guide)
- [17. Troubleshooting](#17-troubleshooting)
- [18. Security Notes](#18-security-notes)
- [19. Roadmap and Future Implementations](#19-roadmap-and-future-implementations)
- [20. Documentation Index](#20-documentation-index)
- [21. Help and FAQ](#21-help-and-faq)
- [22. Contributing and License](#22-contributing-and-license)

---

## 1. Overview

The stack answers one question: *how do I run capable coding models on my own GPU, 24/7, with agents that actually ship work - and reach it from anywhere?*

- **One URL for every client.** The Tokugawa Router classifies each prompt (with a confidence score), routes to the best healthy backend, falls back automatically, caches repeats, and blocks repetition-loop garbage before it reaches you.
- **Agents with teeth.** The Agent API exposes scaffolding/refactor/debug/analysis/chat personas with temperature profiles and session memory. The Workflow Engine chains them into pipelines. The Autonomous SDLC layer goes further: plan -> code -> **verify with real compilers/tests** -> fix -> review -> document -> package a tarball.
- **Ops that run themselves.** Watchdogs restart dead services in seconds. An AI resource optimizer watches GPU temperature/utilization and shifts between performance/balanced/eco power profiles. Daily cleanup rotates logs and prunes old workspaces; weekly backups snapshot your config.
- **Everything is one settings file.** The dashboard writes `config/runtime-settings.json`; the optimizer, autonomous API, router, and llama launcher all consume it on their own cadence. Change once, propagates everywhere.
- **Runs where you want.** Same code on bare-metal Ubuntu, Docker Compose (split or all-in-one), Kubernetes, Vast.ai/RunPod/Lambda/Hetzner, or a bootable Live ISO.

## 2. Screenshots

| Tokugawa Dashboard - active load | Dashboard - timed idle window |
|---|---|
| ![Dashboard active](docs/screenshots/dashboard.png) | ![Dashboard idle](docs/screenshots/dashboard-idle.png) |
| 74% util, alerts panel, service badges, settings + presets | Eco enforced (6% util, 198W/2400MHz), idle banner w/ auto-restore countdown |

| Tokugawa UI | UI in use (refactor via moe-13b) |
|---|---|
| ![Tokugawa UI](docs/screenshots/tokugawa-ui.png) | ![UI output](docs/screenshots/tokugawa-ui-output.png) |
| Model presets + agent picker + prompt console | Router response: model_used, task_type, confidence, elapsed_ms |

| Workflow Designer | tokugawa-cli |
|---|---|
| ![Designer](docs/screenshots/workflow-designer.png) | ![CLI](docs/screenshots/cli.png) |
| 3-step pipeline (architecture -> codegen -> tests) w/ step config | Real --help output: 14 subcommands |

> Dashboard shots use sample telemetry; on a live box the same panels stream real nvidia-smi data, router metrics, and idle-window state.

## 3. Feature Set Breakdown

| Subsystem | Highlights |
|---|---|
| **Router** (:8010) | Keyword classifier w/ confidence score - fallback chain across the roster - degenerate-output (repetition loop) detection w/ automatic retry - LRU response cache (`X-Cache: HIT/MISS`) - per-client token-bucket rate limiting (429) - optional `X-API-Key` auth - `/metrics` (counts, per-task/model, avg latency) - mock mode (`MOCK_LLM=1`) for GPU-less dev |
| **Agent API** (:8020) | project / refactor / debug / analyze / orchestrate / chat endpoints - profiles: `strict` (t0.0) `balanced` (t0.2) `creative` (t0.8) `verbose` (4096 tok) `minimal` (512 tok) - session memory w/ inspect + clear - error envelopes - call counters |
| **Workflow Engine** (:8040) | registry-based pipelines - sequential + parallel steps - 3-attempt retry per step - missing-dependency validation - JSONL audit log - export/import definitions - inline execution - 4 shipped templates |
| **Autonomous SDLC** (:8050) | 7-phase lifecycle (plan/coding/testing/fixing/documenting/packaging) - real verification: `compileall`, `pytest`->`unittest`, `node --check` inside sandboxed workspace - static placeholder scan fallback - artifact tarball download - run cancel - concurrency cap |
| **Presets & Settings** | 4 recommended presets + named custom presets (CRUD) - timed idle window w/ auto-restore (survives restarts) - one `runtime-settings.json` consumed live by 5 services |
| **Dashboard** (:8030) | GPU util/mem/temp/power/clock + Chart.js history - alerts (services down, thermal, util) - service UP/DOWN badges - settings panel - preset picker - idle countdown banner - model shelf (registry vs disk + free GB) - router metrics - SSE live updates - security headers |
| **Optimizer + Tune** | performance/balanced/eco power modes w/ hysteresis + 10-min cooldown - `gpu-power-tune.sh` power cap + clock lock (-10..20C) - `nvidia-persistenced` enablement |
| **Self-healing** | supervisor 10s loop - health agent 30s - recovery agent 15s - systemd units w/ auto-restart |
| **Maintenance** | daily cleanup timer (log rotation 25MB x5, workspace pruning) - weekly backup timer (config/registry/manifests + run manifests, keep 10, restore mode) |
| **Tooling** | `tokugawa-cli` (14 subcommands) - Makefile - MkDocs site - auto-docs generator - GitHub Actions CI (py/bash/js/json gates) + docker publish + release bundling |
| **Desktop** | XFCE + TigerVNC + noVNC (compose `--profile desktop`) |

## 4. Architecture

```
Tokugawa UI (ui/)        Workflow Designer (workflow/ui/)      tokugawa-cli
        |                        |                               |
        v                        v                               v
   Agent API (:8020) <---- Workflow Engine (:8040)      Autonomous SDLC (:8050)
        |                        |                          plan->code->verify
        v                        v                          ->fix->document->package
   Router (:8010) <---------------------------+
   classify -> confidence -> fallback chain
   cache / rate-limit / auth / metrics
        |
        v
   llama.cpp (:9001 GGUF CUDA)        vLLM (:9002, optional profile)

Dashboard (:8030) polls nvidia-smi + service ports + router metrics,
raises alerts, writes runtime-settings.json consumed by all services.
```

**Chat request flow:** client -> `POST /route` -> classifier scores task -> fallback chain tries backends in order -> degenerate check (repetition loop? try next) -> cache store -> response w/ `model_used`, `task_type`, `confidence`, `elapsed_ms`.

**Autonomous run flow:** spec -> plan JSON -> per-task code blocks (`=== FILE: path ===`) -> sandboxed writes -> verifier (shell tools or static scan) -> fix loop fed real errors -> reviewer verdict -> docs generation -> tarball artifact -> download via API/CLI.

**Settings propagation:** dashboard writes `config/runtime-settings.json` -> optimizer reacts within 60s, autonomous API per-request, router at restart, llama launcher via `config/llama.env` on "Save + restart llama". See `docs/architecture.md` for the full table.

## 5. Ports and Services

| Port | Service | Exposed by default |
|---|---|---|
| 8010 | Tokugawa Router (`/route`, `/models`, `/metrics`, `/health`) | LAN only (UFW blocks) |
| 8020 | Agent REST API | LAN only |
| 8030 | Dashboard UI + `/api/*` | **Yes** (UFW allow) |
| 8040 | Workflow Engine | LAN only |
| 8050 | Autonomous SDLC API | **Yes** (UFW allow) |
| 9001 | llama.cpp server (`--jinja`) | localhost/tailnet only |
| 9002 | vLLM (optional profile) | LAN only |
| 8888 | JupyterLab (`--profile jupyter` / clients-provision) | LAN only |
| 3000 / 5000 | OpenCode / ZCode (clients-provision) | LAN only |
| 8443 | Caddy TLS gateway (`--profile tls`) | optional public |
| 5901 / 6080 | VNC / noVNC desktop | via `--profile desktop` |

All ports overridable: `ROUTER_PORT`, `AGENT_API_PORT`, `DASHBOARD_PORT`, `WORKFLOW_PORT`, `AUTONOMOUS_PORT`, `LLAMA_PORT`, `VLLM_PORT`.

## 6. Getting Started

Fastest paths (details in [Section 8](#8-install-and-deploy-handbook)):

**Bare metal (Ubuntu 24.04 + NVIDIA):**
```bash
git clone https://github.com/ProjectZeroDays/Ubuntu-Desktop_XFCE_TigerVNC_noVNC_Tokugawa_llama.cpp_Opencode_Unified-AI-Stack.git
cd Ubuntu-Desktop_XFCE_TigerVNC_noVNC_Tokugawa_llama.cpp_Opencode_Unified-AI-Stack
sudo ./hardware/install-stack.sh          # drivers->CUDA->Docker->stack->systemd->UFW
bash models/auto-download-models.sh       # ~15GB of GGUFs, resumable
```

**Docker (split services):**
```bash
docker compose up -d --build
docker compose --profile vllm up -d       # optional second backend
```

**Docker (all-in-one):**
```bash
docker compose --profile allinone up -d   # supervisord runs everything in one CUDA container
```

**No GPU? Dev mode:**
```bash
python3 -m venv venv && source venv/bin/activate && pip install -r requirements.txt
MOCK_LLM=1 python3 router/router.py       # canned completions, full API surface
```

Verify: `python3 tokugawa.py status` - open `http://localhost:8030`.

## 7. Hardware Requirements

| Tier | GPU VRAM | RAM | Storage | What runs |
|---|---|---|---|---|
| Floor | 8 GB (RTX 3060 Ti / 4060) | 32 GB | 500 GB SSD | Qwen3.5-9B Q4_K, short ctx, 1-2 agents |
| **Recommended** | 16 GB (RTX 4070 Ti SUPER / 4080) | 64 GB DDR5-6000 | 1 TB OS + 2 TB models | All 3 roster models Q6_K, full SDLC loops 24/7 |
| Headroom | 24 GB (RTX 4090 / 3090) | 96-128 GB | +4 TB models | Larger coders, vLLM coexistence |

Verified parts list (MPN/ASIN): [hardware/parts-list.md](hardware/parts-list.md) - assembly: [hardware/BUILD.md](hardware/BUILD.md) - build-vs-cloud economics: [hardware/LOCAL-DEPLOY.md](hardware/LOCAL-DEPLOY.md).

## 8. Install and Deploy Handbook

### 8.1 Bare Metal Provisioner

`hardware/install-stack.sh` is idempotent and chains: base packages -> NVIDIA driver (570-server) -> CUDA toolkit (nvcc for source builds) -> Docker -> stack venv + llama.cpp CUDA build -> model downloads -> systemd units (core, watchdogs, gpu-tune, optimizer, cleanup + backup timers) -> UFW (22/8030/8050 only) -> unattended security upgrades + NTP.

```bash
sudo ./hardware/install-stack.sh                 # full provisioning
NO_START=1 sudo ./hardware/install-stack.sh      # install without starting
```

Reboot once after driver install, then `systemctl status tokugawa-stack`.

### 8.2 Docker Compose Profiles

| Command | Starts |
|---|---|
| `docker compose up -d --build` | llama, router, agents, workflow, autonomous, dashboard |
| `--profile vllm` | + vLLM :9002 (prefix caching on) |
| `--profile allinone` | single supervisord CUDA container, every service |
| `--profile warmup` | one-shot GPU warmup after healthy |
| `--profile desktop` | + XFCE/VNC/noVNC |

Config via `.env` (copy `.env.example`). Every core service has a compose healthcheck; `warmup` waits on router + llama health.

### 8.3 Kubernetes

```bash
kubectl apply -f k8s/namespace.yml
kubectl apply -f k8s/models-pvc.yml     # model storage first
kubectl apply -f k8s/
```

GPU nodeSelector + tolerations (llama/vLLM), HPAs on router/agents/workflow (CPU 70%, 1-4). Images published to GHCR by the `docker-publish` workflow on tags.

### 8.4 GPU Providers

| Provider | Path |
|---|---|
| Vast.ai | template env `PROVISIONING_SCRIPT=<release bundle URL>`; onstart fetch + run pipeline |
| RunPod | Docker template from GHCR all-in-one image; mount `/models` |
| Lambda / Paperspace | bare Ubuntu + `sudo ./hardware/install-stack.sh` |
| Hetzner GPU / OVH | same as Lambda; UFW included |
| AWS g5/g6, Azure NC, GCP G2 (spot) | Terraform module (roadmap); eco optimizer shines here |

Details: [docs/DEPLOYMENT-PLANS.md](docs/DEPLOYMENT-PLANS.md).

### 8.5 Live ISO

`live/build-live.sh` builds TokugawaOS via live-build: GRUB menu - **Try Live (RAM)** / **Install to disk (autoinstall)** / **Rescue shell** - bundled NVIDIA drivers, GPU-detect first boot (MOCK fallback in VMs), optional casper persistence. Plan: `docs/DEPLOYMENT-PLANS.md` Track C.

## 9. Tool Handbook

### 9.1 Tokugawa Router

- **Classification**: keyword hits -> `(task_type, confidence)`: `full_project` / `refactor` / `analysis` / `general_code` (0.5).
- **Fallback chain**: per-task primary + alternates; per-agent overrides via `AGENT_MODEL_OVERRIDES` JSON or config.
- **Degenerate guard**: tail-period repetition detector; loops trigger next backend (`X-Coherence-Retries` header).
- **Cache**: LRU 128, key = task+agent+prompt hash.
- **Rate limit**: token bucket per IP (60 cap, 60/min refill).
- **Auth**: `ROUTER_API_KEY` set -> `X-API-Key` required (except `/health`).
- **llama sampling backstop**: `--repeat-penalty 1.05 --repeat-last-n 64` server defaults.

### 9.2 Agent API

Personas: project, refactor, debug, analyze, orchestrate, chat. Profiles: strict/balanced/creative/verbose/minimal. Session memory: 20 turns x 100 sessions (LRU).

```bash
curl -X POST localhost:8020/agent/chat -H "Content-Type: application/json" \
  -d '{"message":"Design a rate limiter","session_id":"s1"}'
curl localhost:8020/memory/s1 && curl localhost:8020/profiles
```

### 9.3 Workflow Engine

Registry: `project_pipeline`, `full_build`, `api_build`, `microservice_build`. Steps declare `consumes`/`produces`; validation flags dangling deps; 3-attempt retry per step; JSONL audit at `logs/workflow-audit.jsonl`. Designer at `workflow/ui/designer.html` exports JSON -> `POST /workflow/run-inline`; export via `GET /workflow/export/{name}`.

### 9.4 Autonomous SDLC Agents

Lifecycle: `queued -> planning -> coding -> testing <-> fixing -> reviewing -> documenting -> packaging -> done | failed | cancelled`.

- Workspace `workspaces/<run_id>/`: traversal/absolute/drive paths rejected, 512KB/file cap.
- Verification: real commands in-workspace when shell enabled (`ENABLE_SHELL_TOOLS=1` + per-run `enable_shell`); else static placeholder scan.
- Fix loop: up to 3 rounds fed actual compiler/test output.
- Artifact: `_artifact.tar.gz` via API or `tokugawa.py auto-fetch`.
- Guard: `max_concurrent_runs` -> 429 over cap.

### 9.5 Resource Optimizer and GPU Tune

Samples nvidia-smi every 60s (3-sample window, hysteresis, 10-min cooldown):

| Mode | Power | Clock | Trigger |
|---|---|---|---|
| performance | stock | stock | util >= 85 pct and temp <= 75C |
| balanced | 240W | 2520MHz | steady state |
| eco | 200W | 2400MHz | temp >= 82C or util <= 10 pct |

Publishes config/runtime-state.json (dashboard shows live mode). Manual override: uncheck AI auto-management, pick mode, Save. Undervolt profile: hardware/gpu-power-tune.sh apply|reset|status (power cap + clock lock, -10..20C).

### 9.6 Dashboard

Panels: Alerts (services down, thermal, util thresholds) - GPU stats with Chart.js utilization history - Services UP/DOWN badges - Settings (preset dropdown, custom save/delete, idle timer, auto-management checkbox, power/clock caps, llama sampling, concurrency cap) - Model shelf (registry vs on-disk GGUFs + free GB) - router metrics embed - SSE /api/events pushes settings changes to every open tab.

### 9.7 tokugawa-cli

```bash
python3 tokugawa.py status                       # health + router metrics
python3 tokugawa.py models                       # roster
python3 tokugawa.py route "Build an API" --profile strict
python3 tokugawa.py workflows && python3 tokugawa.py run full_build --context {"spec":"..."}
python3 tokugawa.py auto-start "FastAPI notes service" --watch 20
python3 tokugawa.py auto-fetch <run_id> -o out.tar.gz
python3 tokugawa.py presets                      # recommended + custom
python3 tokugawa.py preset "Silent Eco"          # apply
python3 tokugawa.py preset "Idle (timed)" --idle 45
python3 tokugawa.py settings get auto_management
python3 tokugawa.py settings set max_concurrent_runs 2
```

### 9.8 Watchdogs and systemd Units

| Unit | Role |
|---|---|
| tokugawa-stack.service | start.sh: all services, Restart=on-failure |
| tokugawa-agents.service | health-agent (30s) + recovery-agent (15s) via run-watchdogs.sh |
| gpu-tune.service | applies eco power/clock at boot, resets on stop |
| resource-optimizer.service | the AI optimizer loop |
| tokugawa-cleanup.timer | daily: rotate logs 25MB x5, prune workspaces >7d |
| tokugawa-backup.timer | weekly: config/registry/manifests snapshot, keep 10 |

### 9.9 Backup and Cleanup Maintenance

```bash
bash scripts/backup.sh                # snapshot now (backups/backup-TS.tar.gz)
bash scripts/backup.sh list
bash scripts/backup.sh restore backups/backup-XXXX.tar.gz
WORKSPACE_RETENTION_DAYS=14 bash scripts/cleanup.sh
```

Backups cover config/, registry/, manifest/, VERSION and every workspaces/*/​_run.json run manifest.

## 10. Configuration Reference

Layering: defaults < config/config.json < config/runtime-settings.json < environment variables.

### config/config.json

| Section | Keys |
|---|---|
| router | port, api_key, rate_limit_capacity, rate_limit_refill_per_min, cache_enabled, cache_size, backend_timeout_s, mock_llm, model_overrides |
| agents | port, default_profile, memory_max_turns |
| workflow | port, audit_log, step_retries, retry_delay_s |
| dashboard | port, gpu_temp_alert_c (85), gpu_util_alert_pct (90) |

### config/runtime-settings.json (dashboard Settings panel)

| Key | Default | Consumed by |
|---|---|---|
| auto_management | true | optimizer (checkbox: AI owns power modes) |
| forced_mode | balanced | optimizer when auto off |
| power_limit_w / locked_clock_mhz | 240 / 2520 | optimizer + gpu tune |
| eco_power_w / eco_clock_mhz | 200 / 2400 | idle + eco windows |
| repeat_penalty / repeat_last_n | 1.05 / 64 | llama launcher (via llama.env + restart) |
| llama_ctx | 4096 | llama launcher (restart) |
| max_concurrent_runs | 3 | autonomous API (live, 429 over cap) |
| idle | - | timed idle window state + restore snapshot |

### Key environment variables

| Env | Used by | Default |
|---|---|---|
| ROUTER_API_KEY | router auth | empty (off) |
| RATE_LIMIT_CAPACITY / _REFILL_PER_MIN | router | 60 / 60 |
| CACHE_ENABLED / CACHE_SIZE | router | true / 128 |
| MOCK_LLM | router | false |
| LLAMA_BASE | router | http://localhost:9001 |
| AGENT_MODEL_OVERRIDES | switcher | {} |
| AGENT_API | workflow + autonomous | http://localhost:8020 |
| ENABLE_SHELL_TOOLS | autonomous | false |
| MAX_FIX_ROUNDS / SHELL_TIMEOUT_S | autonomous | 3 / 120 |
| OPTIMIZER_INTERVAL_S / COOLDOWN_S | optimizer | 60 / 600 |
| GPU_ID / GPU_POWER_LIMIT_W / GPU_LOCKED_CLOCK_MHZ | tune | 0 / 240 / 2520 |
| WORKSPACES_DIR / MAX_FILE_BYTES | autonomous | repo/workspaces / 524288 |

## 11. API Reference

Condensed; full curl examples in docs/api.md.

### Router :8010

| Method | Path | Notes |
|---|---|---|
| GET | /health | liveness + mock flag |
| GET | /models | roster: name/role/strengths/endpoint |
| POST | /route | {prompt, max_tokens?, temperature?, agent?} -> {model_used, task_type, confidence, elapsed_ms, response}; headers X-Cache, X-Coherence-Retries |
| GET | /metrics | counters, per-task/model, latency_avg_ms |

### Agent API :8020

| Method | Path |
|---|---|
| POST | /agent/project {spec, profile?, session_id?} |
| POST | /agent/refactor {code, language?, goals?} |
| POST | /agent/debug {code, error, language?} |
| POST | /agent/analyze {context, question} |
| POST | /agent/orchestrate {prompt, agent_hint?} |
| POST | /agent/chat {message, session_id} |
| GET/DELETE | /memory/{session_id} |
| GET | /profiles, /metrics, /health |

### Workflow Engine :8040

| Method | Path |
|---|---|
| GET | /workflows, /health |
| POST | /workflow/run {workflow, context, strict_validation?} |
| POST | /workflow/run-inline {definition} |
| GET | /workflow/export/{name} |
| POST | /workflow/validate {steps:[...]} |

### Autonomous SDLC :8050

| Method | Path |
|---|---|
| POST | /auto/start {spec, profile?, max_tasks?, enable_shell?} -> run_id (429 over cap) |
| GET | /auto/runs, /auto/runs/{id} |
| POST | /auto/runs/{id}/cancel |
| GET | /auto/runs/{id}/artifact (tar.gz) |
| POST | /auto/runs/{id}/shell {command} (guarded) |

### Dashboard :8030

| Method | Path |
|---|---|
| GET | /api/status (gpu, services, alerts, power_mode, router_metrics, version) |
| GET/POST | /api/settings ; POST /api/settings/llama-restart |
| GET/POST/DELETE | /api/presets[/{name}] ; POST /api/presets/{name}/apply {duration_min?} |
| GET | /api/models-status ; GET /api/events (SSE) |

## 12. Model Management

Roster (registry/registry.json):

| Key | GGUF | Role |
|---|---|---|
| qwen3.6-12b | Qwen3.6-12B IQ Ultra Heretic Uncensored Thinking Q6_K | primary_coder |
| moe-13b | L3.1 MOE 2x8B DeepSeek DeepHermes 13.7B Q6_K | fast_coder |
| qwen3.5-9b | Qwen3.5-9B Claude HighIQ Heretic Q6_K | reasoning_specialist |

- Download: `bash models/auto-download-models.sh` - resumable (wget -c) with disk preflight (size + 10GB headroom).
- Quant policy: Q4_K/Q5_K/Q6_K only; validate.sh warns on aggressive quants (IQ2/IQ3 degrade coherence).
- Add a model: drop the GGUF in models/, add a registry entry (key/id/name/role/endpoint/gguf), restart llama with `LLAMA_MODEL_PATH` pointing at it.
- llama.cpp serves one hot model per process; point registry entries at separate instances for true parallel serving.
- Keep fresh: `make update-llama` (pulls llama.cpp master + rebuilds) - stale builds mis-tokenize newer Qwen/DeepSeek GGUFs.
- Chat templates: `--jinja` is always on; missing it causes tool-tag soup and repetition on Qwen3/DeepSeek.

## 13. Custom Integrations

- **OpenCode / JCode / MimoCode**: manifests ship in mimocode/ (opencode.json, jcode.json, mimocode.json + *-models.json). Point the provider base_url at the router (:8010) or llama direct (:9001) - model ids match the registry. Recommended host analysis + MCP plan: docs/CODEX-INTEGRATION.md.
- **Hermes CLI**: `hermes config set model.provider custom; model.base_url https://<host>:8010; model.api_key <ROUTER_API_KEY>`.
- **Any OpenAI-ish client**: llama.cpp (:9001) and vLLM (:9002) speak /v1/chat/completions natively.
- **MCP (roadmap)**: server wrapper over /route + /agent/* + /workflow so Codex/OpenCode-class clients consume the stack natively.
- **Webhooks (idea)**: POST /auto/start from GitHub Issues label; run-status webhook on done/failed.
- **Custom agents**: subclass pattern in agents/ - a function that builds a prompt + calls call_router(); expose via agents/api.py and add a workflow Step.

## 14. Remote Access

```bash
./hardware/setup-remote-access.sh tailscale    # private mesh, --ssh enabled
./hardware/setup-remote-access.sh cloudflare   # cloudflared + tunnel steps
./hardware/setup-remote-access.sh both
```

UFW opens only 22/8030/8050. Router (8010) and llama (9001) stay off the public internet by design; reach them via tailnet. noVNC desktop: compose `--profile desktop`, port 6080.

## 15. Testing and Validation

```bash
make test     # 63-test offline pytest suite
make lint     # bash -n + py_compile + node --check + json.tool over tracked files
```

Suite map: router unit (classifier/switcher/cache/limiter) - router API via Flask test client (mock backend) - coherence (degenerate detector + retry) - agents (profiles/memory/metrics via TestClient) - workflow (validation/retries/definitions) - autonomous SDLC (full lifecycle, fix loop, cancellation, sandbox safety) - optimizer (mode decisions) - presets (CRUD/apply/idle expiry/cap).

CI (.github/workflows): ci.yml (compile/syntax/JSON gates) - workflow-ci.yml (offline smoke) - docs.yml (auto-generate workflows.json) - docker-publish.yml (5 images to GHCR on tags) - release.yml (source bundle on tags).

> Note: if Actions shows startup failures reading account locked due to a billing issue, that is GitHub-side billing - resolve at github.com -> Settings -> Billing; the workflows themselves are fine.

## 16. Performance Tuning Guide

1. **Power first**: gpu-tune 240W/2520MHz loses ~3-5% throughput for -10..20C; let the optimizer ride performance only under real load.
2. **Context**: LLAMA_CTX up to 16-32K if RAM allows (KV cache grows linearly); pair with llama.cpp KV quant flags via LLAMA_EXTRA_ARGS.
3. **Offload**: N_GPU_LAYERS=80 default; drop for smaller cards.
4. **Speculative decoding**: opt-in via LLAMA_EXTRA_ARGS=--model-draft <small.gguf> --draft-max 16 - validate output coherence before keeping.
5. **Concurrency**: max_concurrent_runs caps GPU thrash; 2-3 is the sweet spot on 16GB.
6. **Cache**: leave CACHE_ENABLED on; prompts with identical task+agent+text return instantly.
7. **vLLM**: enable only when you need HF-hosted models concurrently - it owns VRAM; prefix caching is on.

## 17. Troubleshooting

| Symptom | Fix |
|---|---|
| llama-server not found | run ./install.sh; binary at llama.cpp/build/bin/ |
| CUDA build skipped | install CUDA toolkit (nvcc on PATH), re-run installer |
| Download aborts: disk | preflight needs size+10GB; free space or move models dir |
| Port already in use at start | stop the other stack, or ALLOW_PORT_REUSE=1 |
| Router 502 | all backends unhealthy; check logs/llama.log, :9001/health |
| 401 from router | ROUTER_API_KEY set - send X-API-Key |
| 429 rate limited | raise RATE_LIMIT_CAPACITY/_REFILL_PER_MIN |
| Repetition loops in output | router auto-retries next model; if persistent lower temperature, verify --jinja active, refresh llama.cpp (make update-llama) |
| Settings changed, router unchanged | rate/cache/timeout apply on router restart |
| Idle window stuck | resource-optimizer service down? systemctl status resource-optimizer |
| Workflow step fails 3x | inspect logs/workflow-audit.jsonl for agent + error |
| Dashboard zeros | nvidia-smi missing/no GPU in container |
| Actions startup failures: billing | github.com -> Settings -> Billing (account lock), then re-run |

More: docs/troubleshooting.md.

## 18. Security Notes

- Only 22/8030/8050 exposed by UFW; router + model servers private/tailnet.
- Router API keys optional but recommended off-LAN: ROUTER_API_KEY + X-API-Key.
- Rate limiting per-IP on every route; health endpoint exempt.
- Autonomous sandbox: path-traversal/absolute/drive-letter rejection, 512KB file cap, shell double-gated (server env + per-run flag), command timeouts, output caps.
- Dashboard: security headers (nosniff, frame-deny, referrer-policy); settings writes validated + bounded.
- Secrets: ROUTER_API_KEY lives in .env / systemd env - never committed (gitignored); CI scans for stray secrets.
- Generated code runs in workspace sandbox; treat artifacts as untrusted until reviewed.

## 19. Roadmap and Future Implementations

Full matrix: [ROADMAP.md](ROADMAP.md). Headliners:

- Codex-class integration epic: MCP server wrapper, approval profiles (suggest/auto/full-auto), diff-based surgical edits, OS-sandbox runner (bwrap/nspawn, network-off), git-native runs - see docs/CODEX-INTEGRATION.md + docs/GAP-ANALYSIS-CODEX.md
- Distribution: all-inone GHCR image in CI, TokugawaOS Live ISO v0.1 (build script shipped), provider kits (RunPod template, spot-cloud Terraform)
- Ops: Prometheus exporter, off-site backup sync (rclone), dashboard auth on write endpoints
- Agents: prompt-template library, run artifacts panel, two-model review gate, token accounting
- Models: performance scoring, registry UI

## 20. Documentation Index

| Doc | Contents |
|---|---|
| docs/api.md | full endpoint reference + curl |
| docs/architecture.md | diagrams, request flows, settings interconnection |
| docs/model-switching.md | classifier -> chain -> overrides tuning guide |
| docs/autonomous-agents.md | SDLC lifecycle, safety model, API/CLI |
| docs/deployment.md | bare-metal / compose / k8s / profiles / dev mode |
| docs/troubleshooting.md | symptom -> fix table |
| docs/ENHANCEMENT-PLAN.md | shipped vs planned matrix |
| docs/CODEX-INTEGRATION.md | OpenCode vs JCode host choice, Codex feature port map |
| docs/GAP-ANALYSIS-CODEX.md | capability gap matrix vs Codex |
| docs/DEPLOYMENT-PLANS.md | Live ISO / all-in-one / provider rollout plans |
| hardware/parts-list.md | verified workstation SKUs |
| hardware/BUILD.md | assembly + Ubuntu install walkthrough |
| hardware/LOCAL-DEPLOY.md | min requirements, build-vs-cloud economics |
| CHANGELOG.md | release notes |

## 21. Help and FAQ

- **Where do I ask?** GitHub Issues on this repo - include `tokugawa.py status` output and relevant logs/ *.log tail.
- **No GPU, can I try?** Yes: MOCK_LLM=1 runs the entire API surface with canned completions; pytest is fully offline.
- **Is my model garbage or is the stack?** Check /metrics degenerate_skips - if climbing, the model loops; router already retries the next backend. Verify --jinja and quant tier first.
- **Windows?** Development-friendly (tests run anywhere python does); serving targets Linux + NVIDIA. WSL2 works for API-only dev with MOCK_LLM.
- **Multiple GPUs?** Point registry entries at per-GPU llama instances (different LLAMA_PORT + CUDA_VISIBLE_DEVICES); the fallback chain becomes a pool.
- **Upgrade llama.cpp?** make update-llama (safe, rebuilds only).

## 22. Contributing and License

PRs welcome: keep the CI gates green (make lint && make test), match the existing ASCII-doc style, add tests for new behavior.

Ideas with the highest leverage right now (see ROADMAP): MCP server, approval profiles, diff edits, sandbox runner, Prometheus exporter.

License: MIT - see [LICENSE](LICENSE).
