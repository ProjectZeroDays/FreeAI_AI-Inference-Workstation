# FreeAI — Unified AI Inference Workstation

> **The AI workstation that thinks ahead.** Local models, autonomous agents, full SDLC automation — one self-hosted stack.

## What is FreeAI?

A production-grade, self-hosted AI inference workstation that unifies local model inference, autonomous agents, workflow orchestration, and a management dashboard into a single deployable stack.

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

## Learning Paths

Choose your path based on your experience level:

### Beginner Path
1. **[First Boot Guide](FIRST-BOOT-GUIDE.md)** — Hardware assembly through first token
2. **[Router Basics](pages/router-basics.md)** — How prompts get classified and routed
3. **[Build Your First Project](pages/build-first-project.md)** — Autonomous SDLC in action
4. **[Build Workflows](pages/build-workflows.md)** — Pipeline designer and templates

### Intermediate Path
1. **[Provider Integration](PROVIDER-INTEGRATION.md)** — OpenAI, Anthropic, Gemini integration
2. **[SDLC Agents](AUTONOMOUS-AGENTS.md)** — Plan → code → test → fix → package
3. **[GPU Tuning](pages/gpu-tuning.md)** — llama.cpp, vLLM, FreeToken configuration
4. **[Secure Deployment](pages/secure-deployment.md)** — Authentication and network hardening

### Advanced Path
1. **[GPU Performance](gpu-performance.md)** — Undervolt, clock lock, eco modes
2. **[Custom Agents](AUTONOMOUS-AGENTS.md)** — Write your own agent scripts
3. **[Cloud Deployment](DEPLOYMENT-PLANS.md)** — Vast.ai, RunPod, Kubernetes
4. **[Security Hardening](SECURITY_ADVANCED.md)** — UFW, fail2ban, API keys, SOPS

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

## Key Features

- **Model Router** — Classifies each prompt, routes to the best healthy backend, falls back automatically, caches repeats, blocks repetition loops
- **Autonomous Agents** — Plan → code → verify with real compilers/tests → fix → review → document → package. 7-phase SDLC with session memory
- **Workflow Engine** — Visual pipeline designer with validation, templates, audit logs, export/import
- **Security Suite** — Aikido integration, pentest agents, auto-patching, dependency management (21+ providers, 33 security skills)
- **MCP Registry** — 40+ pre-configured servers for memory, code intelligence, browser automation, search, LLM access
- **GPU Inference** — llama.cpp, vLLM, FreeToken — local GGUF serving with 21+ hosted API bridges
- **Desktop Environment** — Full XFCE + TigerVNC remote desktop, accessible via noVNC (:6080)
- **Live ISO** — Bootable FreeAIOS with Ubuntu/Kodachi/Kali/NixOS, install, live, and rescue modes

## Task-Based Guides

| Task | Guide |
|---|---|
| Run a model locally | [Router Basics](pages/router-basics.md) |
| Build a workflow pipeline | [Build Workflows](pages/build-workflows.md) |
| Generate a full project | [First Project](pages/build-first-project.md) |
| Deploy to cloud GPUs | [Cloud Deployment](DEPLOYMENT-PLANS.md) |
| Tune your GPU | [GPU Tuning](pages/gpu-tuning.md) |
| Secure your deployment | [Secure Deployment](pages/secure-deployment.md) |
| Use external providers | [Provider Integration](PROVIDER-INTEGRATION.md) |
| Browse agent capabilities | [Agent Capabilities](pages/agent-capabilities.md) |

## Model Roster

| Model | Size | Role | Context | Best For |
|---|---|---|---|---|
| qwen3.6-12b | ~7 GB | Primary coder | 4K | Full projects, architecture, CI/CD |
| claude-code-9b | ~5 GB | Code specialist | 4K | Tool calling, multi-file edits |
| qwythos-v2 | ~5 GB | Reasoning primary | **1M** | Deep analysis, planning, vision |
| moe-13b | ~8 GB | Fast coder | 4K | Refactor, debug, patch |
| qwable-9b | ~5 GB | General assistant | 4K | Chat, vision, creative coding |

Full model registry: [registry/registry.json](../registry/registry.json)

## Skill Catalog

33 security skills across Red, Blue, and Purple teams:

| Team | Count | Key Skills |
|---|---|---|
| 🔴 Red Team | 14 | API Sniffer, Cookie Harvester, Payload Engine, Vuln Scanner, Brute Force, Exploitation |
| 🔵 Blue Team | 12 | SIEM Integration, Forensics, Hunting, Hardening, Incident Response, Threat Intel |
| 🟣 Purple Team | 7 | SIM, Validate, Bridge, Purple Testing, Detection Engineering |

Full catalog: [SKILLS-CATALOG.md](SKILLS-CATALOG.md)

## Documentation

- [**Architecture**](ARCHITECTURE.md) — System design, service topology, data flow
- [**API Reference**](API.md) — Router, Agent, Workflow, and Dashboard API specs
- [**Deployment**](DEPLOYMENT.md) — Docker, bare metal, and cloud deployment guides
- [**Troubleshooting**](TROUBLESHOOTING.md) — Common issues and resolutions
- [**Roadmap**](ROADMAP.md) — Upcoming features and milestones
- [**Contributing**](CONTRIBUTING.md) — How to contribute to FreeAI

## Links

[![GitHub](https://img.shields.io/badge/github-ProjectZeroDays%2FFreeAI-blue?logo=github)](https://github.com/ProjectZeroDays/FreeAI_AI_Inference_Workstation)
[![Docker](https://img.shields.io/badge/docker-ghcr.io%2Ffreeai-blue?logo=docker)](https://github.com/ProjectZeroDays/FreeAI_AI_Inference_Workstation/pkgs/container/freeai)
[![License](https://img.shields.io/badge/license-GPL-3.0-green)](LICENSE)
