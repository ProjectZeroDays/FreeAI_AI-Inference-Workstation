# FreeAI — Self-Hosted AI Inference Workstation

> **Your own AI inference stack.** Local models, autonomous agents, full SDLC automation — one self-hosted stack.
> **Start here:** [Deploy in 5 minutes](#-five-minute-demo) · [Read the docs](https://projectzerodays.github.io/FreeAI_AI_Inference_Workstation) · [Dashboard demo](https://projectzerodays.github.io/FreeAI_AI_Inference_Workstation)

<div align="center">

[![version](https://img.shields.io/badge/version-1.11.0-blue)](https://github.com/ProjectZeroDays/FreeAI_AI_Inference_Workstation/releases)
[![python](https://img.shields.io/badge/python-3.10%2B-informational)](https://www.python.org/)
[![cuda](https://img.shields.io/badge/CUDA-12.x-76B900)](https://developer.nvidia.com/cuda)
[![tests](https://img.shields.io/badge/tests-1156_passing-brightgreen)](#15-testing-and-validation)
[![license](https://img.shields.io/badge/license-GPL-3.0-green)](LICENSE)
[![docker](https://img.shields.io/badge/docker-ghcr.io%2Ffreeai-blue?logo=docker)](https://github.com/ProjectZeroDays/FreeAI_AI_Inference_Workstation/pkgs/container/freeai)

**Website:** [projectzerodays.github.io/FreeAI_AI_Inference_Workstation](https://projectzerodays.github.io/FreeAI_AI_Inference_Workstation) · **Dashboard:** `http://localhost:8030`

</div>

## Quick Reference

| What | Command |
|---|---|
| **Run first model** | `MOCK_LLM=1 python3 router/router.py` |
| **Full stack** | `docker compose --profile allinone up -d` |
| **Build a project** | `python freeai.py auto-start "Build a FastAPI notes service" --watch` |
| **Route a prompt** | `curl -X POST localhost:8010/route -H "Content-Type: application/json" -d '{"prompt":"Design a rate limiter"}'` |
| **Check health** | `python freeai.py status` |

---

## Who Is FreeAI For?

| You are... | FreeAI helps you... |
|---|---|
| **Developer** | Run coding models locally 24/7, generate projects from specs, debug with real compilers |
| **Security Researcher** | Deploy 24 autonomous red/blue/purple team agents with 33 security skills |
| **GPU Owner** | Turn idle VRAM into a multi-model inference router with automatic fallback chains |
| **Team Lead** | Ship projects autonomously — plan → code → test → fix → package, zero manual handoff |
| **Cloud User** | Route between local models and 21+ cloud providers with confidence-scored classification |

---

## ⚡ Five-Minute Demo

```bash
# One spec → complete shipped project (with real verification)
python freeai.py auto-start "Build a FastAPI notes service with auth and tests" --watch
```

Watch the 7-phase SDLC agent: **plan → code → verify (real pytest) → fix → review → document → package**.

---

## TL;DR Install Matrix

| Environment | Command |
|---|---|
| **Docker (quickest)** | `docker compose --profile allinone up -d` |
| **No GPU (dev mode)** | `MOCK_LLM=1 python3 router/router.py` |
| **Bare metal** | `sudo ./hardware/install-stack.sh` |
| **Kubernetes** | `kubectl apply -f k8s/` |
| **Live ISO** | Boot `freeaios-amd64.iso` — Try / Install / Rescue |

---

## Core Concepts

```
Client ──► Router (:8010) ──► Agents (:8020/8050) ──► GPU Inference
                │
   classify → route → cache → fallback
                │
         MCP Registry (40+ servers)
```

The **Router** classifies every prompt (confidence score), routes to the best backend, falls back automatically, caches repeats, and blocks repetition loops. **Agents** execute real work — code generation, security scanning, workflow orchestration. **GPU Inference** runs local models via llama.cpp, vLLM, or FreeToken.

Full architecture: see [Section 4](#4-architecture)

---

## Quick Start

### Prerequisites
- Docker + NVIDIA Container Toolkit (or bare metal Ubuntu 22.04+)
- Python 3.10+ (for bare-metal installs)
- NVIDIA GPU with 8GB+ VRAM recommended (not required — MOCK_LLM=1 works on CPU)

### Developer Track

```bash
# 1. Clone and run the router (no GPU needed for dev)
git clone https://github.com/ProjectZeroDays/FreeAI_AI_Inference_Workstation.git
cd FreeAI_AI_Inference_Workstation
MOCK_LLM=1 python3 router/router.py

# 2. Route your first prompt
curl -X POST localhost:8010/route \
  -H "Content-Type: application/json" \
  -d '{"prompt":"Explain dependency injection"}'

# 3. Generate a project with autonomous SDLC
python freeai.py auto-start "Build a FastAPI notes API with SQLite" --watch
```

### Operator Track

```bash
# 1. Deploy the full stack
git clone https://github.com/ProjectZeroDays/FreeAI_AI_Inference_Workstation.git
cd FreeAI_AI_Inference_Workstation
docker compose --profile allinone up -d

# 2. Open the dashboard
open http://localhost:8030

# 3. Configure providers and models via the Settings panel
# 4. Set up security keys (ROUTER_API_KEY, AGENT_API_KEY, etc.)
```

**Bare metal:** `sudo ./hardware/install-stack.sh` · **Kubernetes:** `kubectl apply -f k8s/` · **Live ISO:** Boot `freeaios-amd64.iso`

---

## What's Inside

FreeAI is a **production-grade, self-hosted AI inference workstation** that unifies everything you need to run capable coding models 24/7 on your own hardware — with agents that actually ship work.

| Subsystem | Purpose |
|---|---|
| **Model Router** (:8010) | Classify → route → cache → fallback → rate-limit every prompt |
| **Agent API** (:8020) | project / refactor / debug / analyze / chat with session memory |
| **Workflow Engine** (:8040) | Visual pipeline designer, validation, export/import, audit logs |
| **Autonomous SDLC** (:8050) | 7-phase plan→code→test→fix→review→doc→package with real verification |
| **Security Suite** | 33 skills (14 Red, 12 Blue, 7 Purple), Aikido integration, auto-patching |
| **GPU Inference** | llama.cpp (:9001), vLLM (:9002), FreeToken (:9100) — 8-model roster |
| **Hermes CLI** | CLI agent orchestrator, 100+ ext provider SDKs, proxy forwarding |
| **Desktop** | XFCE + TigerVNC/noVNC (:6080) — full remote desktop |
| **Live ISO** | FreeAIOS — Ubuntu/Kodachi/Kali/NixOS bootable workstations |

---

## Local Model Comparison

| Model | Size | Role | Context | Best For |
|---|---|---|---|---|
| **qwen3.6-12b** | ~7 GB | Primary coder | 4K | Full projects, architecture, CI/CD, deep reasoning |
| **claude-code-9b** | ~5 GB | Code specialist | 4K | Tool calling, multi-file edits, production code |
| **qwythos-v2** | ~5 GB | Reasoning primary | **1M** | Deep analysis, planning, math, vision, function calling |
| **qwythos-9b** | ~5 GB | Reasoning fallback | **1M** | Long-context reasoning, logic, decomposition |
| **qwable-9b** | ~5 GB | General assistant | 4K | General chat, vision, creative coding, terminal agent |
| **qwen3.5-thinking** | ~5 GB | Reasoning fallback | 4K | Step-by-step thinking, planning, logic |
| **qwen3.5-9b** | ~5 GB | Legacy fallback | 4K | Analysis, explanation, general tasks |
| **moe-13b** | ~8 GB | Fast coder | 4K | Refactor, debug, patch, optimize, fast completion |

> Reasoning models clamp temperature to 0.6 automatically. 1M-context models (qwythos-*) require `LLAMA_CTX=1048576`. For MTP speculative decoding: set `DOWNLOAD_MTP=1` and `LLAMA_EXTRA_ARGS="--spec-type draft-mtp --spec-draft-n-max 6"`.

---

## Architecture

```
                    ┌───────────────────────────────────────────────────────┐
                    │              FreeAI Dashboard (:8030)                 │
                    │        Flask + Chart.js + SSE + Authentication        │
                    ├───────────────────────────┬────────────────┬──────────┤
                    │  Router  │ Agents    │ Workflow │      Autonomous     │
                    │  :8010   │ :8020     │  :8040   │       :8050         │
                    │          │           │          │                     │
                    │ classify │ plan→code │ chain    │   7-phase SDLC      │
                    │ fallback │ verify    │ validate │   real compilation  │
                    │ cache    │ fix       │ template │   auto-package      │
                    ├───────────────────────────┴────────────────┴──────────┤
                    │              MCP Registry (40+ servers)               │
                    │    Aikido · SendGrid · Twilio · Telegram · WhatsApp   │
                    ├───────────────────────────────────────────────────────┤
                    │                  GPU Inference Layer                  │
                    │ llama.cpp  (:9001) · vLLM (:9002) · FreeToken (:9100) │
                    └───────────────────────────────────────────────────────┘
```

**Request flow:** `Client → Router (classify + confidence score) → Best backend → Fallback chain on failure → LRU cache → Response with X-Cache header`

**SDLC flow:** `Spec → Plan JSON → Per-task code blocks → Sandboxed writes → Verifier (pytest/node --check) → Fix loop (3 rounds) → Reviewer verdict → Docs → Artifact tarball`

---

## Agent Capabilities

What can you delegate to FreeAI's 24 agents right now?

| Agent | Role | Out-of-the-box tasks |
|---|---|---|
| **ORCH** (Orchestrator) | Red team lead | Coordinates multi-agent campaigns, assigns sub-tasks, merges results |
| **RECON** (Reconnaissance) | Blue team | Network scanning, port discovery, service fingerprinting, CVE correlation |
| **EXPLOIT** (Exploitation) | Red team | Metasploit API, privilege escalation, lateral movement, persistence setup |
| **POSTEX** (Post-exploitation) | Red team | Credential dumping, screenshot capture, keylogging, data exfiltration |
| **HUNT** (Threat Hunter) | Blue team | ATT&CK mapping, IoC hunting, persistence detection, behavioral analysis |
| **FORENSIC** | Blue team | Memory dump analysis, timeline reconstruction, artifact extraction |
| **HARDEN** | Blue team | CIS benchmark auditing, vulnerability remediation, config hardening |
| **IR** (Incident Responder) | Blue team | Automated containment, evidence preservation, runbook execution |
| **DECEPT** (Deception) | Blue team | Honeypot deployment, canary token management, trap triggering |
| **SIM** (Simulator) | Purple team | Attack simulation, detection validation, gap analysis |
| **PATCH** | Blue team | Auto-generate and apply safe fixes for critical/high vulnerabilities |
| **BUILDER** | General | Generate fullstack apps, CRMs, chatbots, sales pipelines from specs |

Full agent catalog: [agents/](agents/) · Security skills: [skills/red_teaming/](skills/red_teaming/), [skills/blue_team/](skills/blue_team/), [skills/purple_team/](skills/purple_team/)

---

## Security Defaults

| Default | Detail |
|---|---|
| Router & model servers | **LAN-only** by default (UFW blocks external) |
| Exposed ports | Only `22` (SSH), `8030` (dashboard), `8050` (autonomous API) |
| Autonomous sandbox | Rejects path traversal, absolute paths, files >512 KB |
| API auth | Optional `X-API-Key` for router, agents, and autonomous endpoints |
| Dashboard headers | Strict CORS, CSP, and security headers enabled |
| Secrets | Encrypted with SOPS; never committed to repo |

See [SECURITY.md](SECURITY.md) for the full security model.

---

## What's New (v1.2.0)

- **Autonomous SDLC agents** — 7-phase lifecycle with real compiler verification
- **Aikido integration** — SAST/DAST scanning from the dashboard
- **33 security skills** — 14 Red, 12 Blue, 7 Purple team capabilities
- **Live ISO builder** — FreeAIOS with Ubuntu/Kali/Kodachi/NixOS variants
- **Website overhaul** — dark theme, responsive design, 15+ pages

---

## Service Ports

| Service | Port | Description |
|---|---|---|
| Dashboard | `8030` | Web UI + REST API |
| Router | `8010` | AI model routing engine |
| Agents | `8020` | Agent API |
| Workflow | `8040` | Workflow engine |
| Autonomous | `8050` | SDLC automation |
| llama.cpp | `9001` | Local GGUF inference |
| vLLM | `9002` | High-throughput serving |
| FreeToken | `9100` | Edge MoE engine (290B+ models) |
| JupyterLab | `8888` | Interactive Python |
| Desktop (VNC) | `6080` | XFCE remote desktop |
| Browser (Knight-Shade) | `8180` | Stealth browser engine API |

---

## Dashboard Pages

The dashboard serves 19 pages at `http://localhost:8030`:

| Page | Route | Description |
|---|---|---|
| Main Dashboard | `/` | GPU stats, alerts, services, settings, model shelf |
| Skills Manager | `/skills` | Browse, create, delete, scan for auto-generated skills |
| SDLC Runs | `/sdlc` | Autonomous run status, artifact download, shell access |
| Workflow Designer | `/workflows` | Pipeline builder, validation, export/import, run scheduling |
| MCP Registry | `/mcp` | Discover and register MCP servers |
| Hermes | `/hermes` | CLI agent proxy, multi-provider config, ext SDK routing |
| Salad | `/salad` | GPU earnings, available marketplace GPUs |
| Aikido | `/aikido` | Security scanning, vulnerability reports, test controls |
| Wiki | `/wiki-dashboard` | Project knowledge base, searchable docs |
| Blog | `/blog` | Team blog, release notes, tutorials |
| Forum | `/forum` | Community discussions, Q&A |
| Logs | `/logs` | Service log stream, audit trail |
| Network | `/network` | Network topology, service mesh view |
| Browser | `/browser` | Headless browser automation, stealth profiles |
| Scheduler | `/scheduler` | Cron job management, execution history |
| Loot | `/loot` | Exfiltrated data viewer, captured credentials |
| C2 | `/c2` | Quantum C2 unified dashboard |
| Plugins | `/plugins-manage` | Plugin registry, install/uninstall, skill loader |

---

## Key Features

### Model Router
- **21+ providers** — OpenAI, Anthropic, DeepSeek, Gemini, OpenRouter, Venice, Agnes AI, and more
- **Task-aware classification** — confidence-scored routing per prompt type
- **Automatic fallback chains** — if the primary fails, tries the next in line
- **Degenerate output detection** — catches repetition loops before they waste tokens
- **LRU response cache** — `X-Cache: HIT/MISS` headers, per-model TTL

```bash
# Route a prompt to the model router
curl -X POST localhost:8010/route \
  -H "Content-Type: application/json" \
  -d '{"prompt":"Design a rate limiter","model":"openai/gpt-4o-mini"}'

# Response:
# {
#   "model_used": "openai/gpt-4o-mini",
#   "task_type": "general_code",
#   "confidence": 0.87,
#   "elapsed_ms": 342,
#   "response": "..."
# }

# Check router health
curl localhost:8010/health

# View router metrics
curl localhost:8010/metrics
```

### Autonomous SDLC Agents
```bash
# One-line spec → complete shipped project
python freeai.py auto-start "Build a FastAPI notes service with auth and tests" --watch
```
- **7 phases**: plan → code → verify (real compilers/tests) → fix → review → document → package
- **Real verification**: `compileall`, `pytest`→`unittest`, `node --check` inside sandboxed workspaces
- **Artifact download**: tarball with full project, ready to deploy

### Builder Agents
Generate complete projects from natural language:
- **Fullstack apps** — FastAPI+React, Django+Next.js, Laravel+Vue
- **Websites** — landing pages, portfolios, SaaS sites
- **CRMs** — contacts, deals, tasks, email integration
- **Chatbots** — FAQ bots, ticketing, knowledge-base powered
- **Sales pipelines** — lead capture, CRM sync, email sequences
- **Marketing agents** — multi-channel campaigns with A/B testing

### Security
- **Aikido integration** — scan code, test apps, auto-patch from the dashboard
- **Pentest agents** — Semgrep, Bandit, Safety, Trivy (SAST/DAST)
- **Auto-patch** — generate and apply safe fixes for critical/high vulnerabilities
- **33 security skills** — 14 Red Team, 12 Blue Team, 7 Purple Team
- **API key rotation** — up to 10 keys per provider, auto-pause on 429

### Knight-Shade Browser (Stealth Automation)
- **Invisible Playwright** — `headless="new"` Chrome with 16-category stealth JS injection
- **70+ fingerprint vectors** — navigator, WebGL, audio, screen, timezone spoofing
- **5-tier anonymity** — Tor, VPN, Shadowsocks, DNSCrypt, full stack mix
- **Army orchestrator** — multi-agent coordination with division-aware configs
- **Manifest-X extensions** — CDP-native browser control with self-healing
- **Dashboard pages**: `/browser-v2`, `/loot`, `/c2`

### Red-Team Specialized Agents
- **API Sniffer** — CDP Network domain interception, endpoint mapping
- **Cookie Harvester** — session harvesting, cookie crafting, Netscape export
- **Payload Engine** — polymorphic AES-256-GCM + XOR encryption, 9 output formats
- **Vuln Scanner** — nmap, nuclei, sqlmap, ffuf, OWASP ZAP with NIST 800-115 reports
- **Brute Force** — hashcat GPU, rainbow tables, hydra, JWT/ZIP/SSH cracking
- **Exploitation** — Metasploit API, privilege escalation, lateral movement, persistence

### Cloud Integrations
- **Salad GPU** — rent out your GPU for profit via Salad marketplace
- **Aikido** — integrated security scanning and SAST/DAST
- **Vast.ai / RunPod / Hostinger** — cloud GPU provider dashboards

### Hermes CLI Integration
Hermes is a CLI agent orchestrator that routes through the FreeAI stack:
```bash
hermes config set model.provider custom
hermes config set model.base_url https://<host>:8010
hermes config set model.api_key <ROUTER_API_KEY>
```
- 100+ ext provider SDKs via `@ai-sdk/openai-compatible`
- Multi-provider model routing (OpenAI, Anthropic, Gemini, OpenRouter, Venice, HF, Zen, Agnes AI)
- Dashboard at `/hermes` — proxy forwarding to all configured providers

### Salad GPU Earnings
Monetize idle GPU capacity with Salad:
```bash
export SALAD_API_KEY=slhd_...
```
- Dashboard at `/salad` — earnings overview, available GPU listings
- REST: `GET /api/salad`, `GET /api/salad/gpu`

### Aikido Security Scanning
Integrated security posture from Aikido:
```bash
export AIKIDO_API_KEY=aikido_...
export AIKIDO_APP_ID=your-app-id
```
- Dashboard at `/aikido` — security overview, test controls
- REST: `GET /api/aikido`, `POST /api/aikido/test` (type: sAST/dAST/dependency)

---

## Deploy Anywhere

| Method | Command | Best For |
|---|---|---|
| **Bare Metal** | `curl -fsSL install-stack.sh \| bash` | Production servers with NVIDIA GPUs |
| **Docker Compose** | `docker compose --profile allinone up -d` | Any host with NVIDIA Docker |
| **Kubernetes** | `kubectl apply -f k8s/` | Cloud-native deployments |
| **Vast.ai** | Custom template (32GB+ VRAM) | On-demand GPU instances |
| **Live ISO** | Boot `freeaios-amd64.iso` | No-install, bootable workstation |

---

## Provider Guide

See [docs/PROVIDERS.md](docs/PROVIDERS.md) for the full matrix. Quick start:

```bash
# 1. Export keys for providers you use
export OPENAI_API_KEY=sk-...
export ANTHROPIC_API_KEY=sk-ant-...
export GROQ_API_KEY=gsk_...

# 2. (optional) customize config
cp config/providers.example.json config/providers.json

# 3. Route explicitly to any provider model
curl -X POST localhost:8010/route -H "Content-Type: application/json" \
  -d '{"prompt":"Design a rate limiter","model":"openai/gpt-4o-mini"}'
```

**Three wire styles:** `openai` (most hosts), `anthropic` (Claude), `gemini` (Google).  
**Fallback chains:** set `"fallback": true` in providers.json to append hosted models after all local GGUFs.  
**FreeToken edge MoE:** `docker compose --profile freetoken up -d` for 290B+ models on consumer GPUs.

---

## Hardware Requirements

| Tier | GPU VRAM | RAM | Storage | What Runs |
|---|---|---|---|---|
| Floor | 8 GB (RTX 3060 Ti / 4060) | 32 GB | 500 GB SSD | Subset of roster Q4_K (9B-class) |
| **Recommended** | 16 GB (RTX 4070 Ti SUPER / 4080) | 64 GB DDR5 | 1 TB + 2 TB models | Full 8-model roster Q6_K, 24/7 SDLC |
| Headroom | 24 GB (RTX 4090 / 3090) | 96-128 GB | +4 TB models | Larger coders + vLLM coexistence |

---

## Troubleshooting

### CUDA Out of Memory
- Reduce `LLAMA_CTX` (context window) in `config/llama.env`
- Run fewer models simultaneously (`--profile llama2` keeps a 2nd shard)
- Use MOCK_LLM=1 for CPU-only development

### Port Conflicts (:8010, :8030)
```bash
# Check what's using the port
lsof -i :8010
# Override port via environment
ROUTER_PORT=8110 docker compose up -d
```

### SOPS Secret Decryption Fails
- Ensure `SOPS_AGE_KEY_FILE` points to your age key
- Regenerate: `age-keygen -o age.key` and update `.sops.yaml`
- For CI: set `SOPS_AGE_KEY_FILE` in your workflow secrets

### Docker Compose Healthcheck Fails
```bash
# Check individual service logs
docker compose logs --tail=50 router
docker compose logs --tail=50 dashboard
# Restart a specific service
docker compose restart llama
```

### No GPU Detected
```bash
# Verify NVIDIA driver
nvidia-smi
# If missing, install drivers
sudo apt install nvidia-driver-570-server
# Or use mock mode
MOCK_LLM=1 python3 router/router.py
```

---

## Documentation

- **Full docs**: [projectzerodays.github.io/FreeAI_AI_Inference_Workstation](https://projectzerodays.github.io/FreeAI_AI_Inference_Workstation)
- **API Reference**: [API Reference](https://projectzerodays.github.io/FreeAI_AI_Inference_Workstation/api/)
- **Providers**: [docs/PROVIDERS.md](docs/PROVIDERS.md)
- **Wiki**: http://localhost:8030/wiki-dashboard
- **Blog**: http://localhost:8030/blog
- **Forum**: http://localhost:8030/forum

---

## License

GPL-3.0 — see [LICENSE](LICENSE) for details.

Built with ❤️‍🔥 by the FreeAI team.

> **Full docs:** https://projectzerodays.github.io/FreeAI_AI_Inference_Workstation/  
> **Try before you clone:** `MOCK_LLM=1` runs the entire stack without a GPU (`make test` is fully offline).

Production-grade, self-hosted **AI inference workstation stack**: GGUF coder models on NVIDIA GPUs, a task-classifying model router with fallback chains, a multi-agent REST layer, a workflow engine, **autonomous SDLC agents** that turn a one-line spec into a packaged project, a presets/settings control plane, an AI power optimizer, self-healing watchdogs, and a full XFCE + VNC remote desktop. Deployable bare-metal, via Docker Compose, Kubernetes, cloud GPU providers, or as a Live ISO.
