# FreeAI — Unified AI Inference Workstation

> **The AI workstation that thinks ahead.** Local models, autonomous agents, full SDLC automation — one self-hosted stack.

<div class="hero-callout" markdown>

![]({{ config.site_url }}assets/logo.svg){ width="48" style="float:left;margin-right:16px" }

### What is FreeAI?

A production-grade, self-hosted AI inference workstation that unifies local model inference, autonomous agents, workflow orchestration, and a management dashboard into a single deployable stack.

</div>

## Stack Overview

| Service | Port | Purpose |
|---|---|---|
| **Router** | :8010 | Prompt classifier + multi-backend fallback chain |
| **Agent API** | :8020 | Plan → code → verify → fix → review SDLC agents |
| **Workflow Engine** | :8040 | Visual pipeline designer with validation & audit logs |
| **Autonomous SDLC** | :8050 | 7-phase autonomous development with real compilation |
| **Dashboard** | :8030 | GPU telemetry, alerts, service health, C2 controls |
| **llama.cpp** | :9001 | GGUF inference backend |
| **vLLM** | :9002 | High-throughput inference (optional) |
| **FreeToken** | :9100 | Edge MoE 290B+ serving |
| **Hermes** | :8090 | CLI agent orchestrator with proxy forwarding |

## Quick Start

```bash
# Install (auto-detects GPU, configures everything)
curl -fsSL https://raw.githubusercontent.com/ProjectZeroDays/FreeAI_AI_Inference_Workstation/main/hardware/install-stack.sh | bash

# Or Docker (any host with NVIDIA Docker)
docker compose --profile allinone up -d

# Or Live ISO (no install needed)
# Download from Releases → boot → Try FreeAI Ubuntu/Kodachi/Kali/NixOS
```

> **No GPU?** Set `MOCK_LLM=1` — the full stack runs on CPU for development and testing.

## Key Features

- **Model Router** — Classifies each prompt, routes to the best healthy backend, falls back automatically, caches repeats, blocks repetition loops
- **Autonomous Agents** — Plan → code → verify with real compilers/tests → fix → review → document → package. 7-phase SDLC with session memory
- **Workflow Engine** — Visual pipeline designer with validation, templates, audit logs, export/import
- **Security Suite** — Aikido integration, pentest agents, auto-patching, dependency management (21+ providers, 33 security skills)
- **MCP Registry** — 40+ pre-configured servers for memory, code intelligence, browser automation, search, LLM access
- **GPU Inference** — llama.cpp, vLLM, FreeToken — local GGUF serving with 21+ hosted API bridges
- **Desktop Environment** — Full XFCE + TigerVNC remote desktop, accessible via noVNC (:6080)
- **Live ISO** — Bootable FreeAIOS with Ubuntu/Kodachi/Kali/NixOS, install, live, and rescue modes

## Documentation

- [**Architecture**](ARCHITECTURE.md) — System design, service topology, data flow
- [**API Reference**](API.md) — Router, Agent, Workflow, and Dashboard API specs
- [**Deployment**](DEPLOYMENT.md) — Docker, bare metal, and cloud deployment guides
- [**Troubleshooting**](TROUBLESHOOTING.md) — Common issues and resolutions
- [**Roadmap**](ROADMAP.md) — Upcoming features and milestones

## Links

[![GitHub](https://img.shields.io/badge/github-ProjectZeroDays%2FFreeAI-blue?logo=github)](https://github.com/ProjectZeroDays/FreeAI_AI_Inference_Workstation)
[![Docker](https://img.shields.io/badge/docker-ghcr.io%2Ffreeai-blue?logo=docker)](https://github.com/ProjectZeroDays/FreeAI_AI_Inference_Workstation/pkgs/container/freeai)
[![License](https://img.shields.io/badge/license-MIT-green)](https://github.com/ProjectZeroDays/FreeAI_AI_Inference_Workstation/blob/main/LICENSE)
