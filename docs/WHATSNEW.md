# What's New — FreeAI

Recent features, model updates, and agent additions.

---

## v1.11 — Latest Release

### Autonomous SDLC Enhancement
- **zero_click_exploits** rewritten from simulated stubs to real implementations — covers Android, Windows, Linux, iOS, IoT, Bluetooth, NFC, and macOS exploit chains
- 7-phase SDLC now verified with real compilers and test suites inside sandboxed workspaces
- Artifact tarballs include full project structure ready to deploy

### CI Pipeline Hardened
- requirements.txt version conflicts resolved — numpy, scipy, pandas, matplotlib pinned to Python 3.11-compatible ranges
- autopep8/flake8/pycodestyle incompatibility fixed
- pytest-asyncio aligned to 0.23.x range
- All CI workflows passing (Python 3.11 verify, CodeQL, docker-publish)

### Infrastructure
- Circuit breakers added to `router/load_balancer.py` — sliding-window pattern with configurable ratio and minimum request thresholds
- HITL (Human-in-the-Loop) approval system in `autonomous/approval.py` — 6 danger categories gate autonomous execution
- Resource quotas enforced in `docker-compose.yml` — prevents GPU/memory exhaustion

---

## v1.10 — Model Router

- **21+ provider bridges** — native OpenAI, Anthropic, Gemini adapters plus OpenAI-compatible bridges for Groq, Mistral, DeepSeek, Together, Fireworks, OpenRouter, xAI, Perplexity, Cerebras, SambaNova, Cohere, Novita, DeepInfra, Hyperbolic, HuggingFace, Ollama, LM Studio
- **Task-aware classification** — confidence-scored routing per prompt type (coder, reasoning, general, vision)
- **Degenerate output detection** — catches repetition loops and low-confidence responses before wasting tokens
- **LRU response cache** — `X-Cache: HIT/MISS` headers, per-model TTL configuration

---

## v1.9 — Autonomous Agents

- **ORCH** orchestrator — coordinates multi-agent campaigns, assigns sub-tasks, merges results
- **RECON** — network scanning, port discovery, service fingerprinting, CVE correlation
- **EXPLOIT** — Metasploit API, privilege escalation, lateral movement, persistence
- **POSTEX** — credential dumping, screenshot capture, keylogging, data exfiltration
- **HUNT** — ATT&CK mapping, IoC hunting, persistence detection, behavioral analysis
- **FORENSIC** — memory dump analysis, timeline reconstruction, artifact extraction
- **HARDEN** — CIS benchmark auditing, vulnerability remediation, config hardening
- **IR** — automated containment, evidence preservation, runbook execution
- **DECEPT** — honeypot deployment, canary token management, trap triggering
- **SIM** — attack simulation, detection validation, gap analysis
- **PATCH** — auto-generate and apply safe fixes for critical/high vulnerabilities
- **BUILDER** — generate fullstack apps, CRMs, chatbots, sales pipelines from specs

---

## v1.8 — GPU Inference Layer

- **llama.cpp** (:9001) — GGUF inference with CUDA acceleration, MLC support
- **vLLM** (:9002) — high-throughput PagedAttention serving (optional)
- **FreeToken** (:9100) — edge MoE 290B+ models on consumer GPUs via CPU-GPU co-execution
- **GPU warmup** profile — pre-warms GPU memory to reduce first-request latency
- **GPU optimizer** — eco / balanced / perf modes with dynamic clock and voltage tuning

---

## v1.7 — Workflow Engine

- Visual pipeline designer at `:8040`
- Parallel and sequential step execution
- Validation, audit logs, and export/import
- Template library for common workflows (CI/CD, security scan, model training)
- Real-time step status with SSE streaming

---

## v1.6 — Dashboard

- Multi-page dashboard with 19 routes
- GPU telemetry (nvidia-smi aggregation, per-GPU utilization)
- Alert system with configurable severity levels
- Service health monitoring with automatic restart
- Model shelf — browse and configure available models
- Settings panel — environment configuration without editing files

---

## v1.5 — Desktop Environment

- Full XFCE desktop via TigerVNC on `:6080`
- noVNC web access — browser-based remote desktop
- Pre-installed developer tools: VS Code, terminal, file manager
- Accessible from any device on the network

---

## v1.4 — Live ISO

- FreeAIOS bootable ISO with Ubuntu/Kodachi/Kali/NixOS variants
- Three boot options: Install, Live Try, Rescue
- Unattended install with auto-detection of GPU and drivers
- Default login: `freeai/freeai`

---

## v1.3 — Security Suite

- Aikido integration — SAST/DAST scanning from the dashboard
- 33 security skills: 14 Red Team, 12 Blue Team, 7 Purple Team
- Pentest agents: Semgrep, Bandit, Safety, Trivy
- Auto-patch for critical/high vulnerabilities
- API key rotation (up to 10 keys per provider, auto-pause on 429)

---

## v1.2 — MCP Registry

- 40+ pre-configured MCP servers
- Memory, code intelligence, browser automation, search, LLM access
- One-click install from dashboard or CLI
- Persistent configuration across restarts

---

## v1.1 — Hermes CLI

- CLI agent orchestrator at `:8090`
- 100+ external provider SDKs via `@ai-sdk/openai-compatible`
- Multi-provider model routing with fallback chains
- Dashboard proxy forwarding to all configured providers

---

## v1.0 — Initial Release

- Model router with classification and fallback
- Agent API with session memory
- Basic dashboard with GPU telemetry
- Docker Compose deployment
- llama.cpp integration
