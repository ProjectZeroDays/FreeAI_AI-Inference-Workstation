# Changelog

All notable changes to FreeAI will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [1.3.1] - 2026-08-28

### Added
- **task_printer skill**: CLI tool (`skills/task_printer/scripts/task_printer.py`) that reads a JSON task list and prints each task's id, name, and description in a formatted console layout; includes input validation and non-zero exit on errors.
- **Shodan integration**: dashboard card, API endpoints (`/api/shodan/*`), and settings panel for querying Shodan.io reconnaissance data.
- **Docs polish**: hero orbs with gradient CSS, dot-grid page backgrounds, macOS-style code chrome (traffic-light window buttons), scroll-spy active nav highlighting, animated stat counters.

### Changed
- **mkdocs.yml cleanup**: removed 17 broken nav references to deleted pages; removed stale `ai-badge.js` script include.
- **Test suite**: workspace tests for memory_primitives agent, aggregate chained_zero_day agent tests; all 570 tests passing.
- **VERSION bump** 1.2.0 → 1.3.1.

---

## [2.0.0] - 2026-08-27

### Added
- Browser Engine with Army Orchestrator: Full CDP-based browser automation with hierarchical multi-agent orchestration (14 ranks, 6 divisions, 1000+ concurrent agents). Includes stealth/anonymity layers (Tor, SOCKS), Manifest-X integration, and extension support (scrapling, burp, zaproxy, ghidra, frida).
- Loot and C2 Dashboard: New dashboard pages for harvested cookies/credentials/hashes and connected host management. REST API for loot CRUD and C2 event streaming.
- MCP Server (mcp/server.py): Exposes FreeAI as an MCP server on :8090 for Codex, OpenCode, and other MCP-compatible clients. Supports tool proxying to /route, /agent/*, /workflow, /auto endpoints.
- Swarm Orchestrator (swarm/orchestrator.py): Parallel multi-agent execution with isolated worktrees, dependency-ordered merges, cost tracking, and memory guards.
- 21+ External Provider Bridge: Native adapters for OpenAI, Anthropic, Google Gemini; OpenAI-compatible bridge for Groq, Mistral, DeepSeek, Together, Fireworks, OpenRouter, xAI, Perplexity, Cerebras, SambaNova, Cohere, Novita, DeepInfra, Hyperbolic, HuggingFace, Ollama, LM Studio.
- FreeToken Edge MoE (--profile freetoken): 290B+ frontier models on consumer GPUs via CPU-GPU co-execution. Auto-fallback when healthy.
- LoLLMs Chat UI (--profile lollms): Optional chat-centric frontend on :9600.
- WebSocket Token Streaming: ws://:8011/ws/route alongside existing SSE streaming.
- Parallel Model Shards (--profile llama2): Secondary llama.cpp instance on :9003 with per-GPU CUDA_VISIBLE_DEVICES.
- Qdrant RAG Sidecar (--profile rag): Vector search with MiniLM 384-dim embeddings, hash fallback for CI.
- JupyterLab (--profile jupyter): Python notebook on :8888 with systemd template.
- Caddy TLS Gateway (--profile tls): Automatic ACME HTTPS via FREEAI_DOMAIN/ACME_EMAIL, basic-auth-protected /auto/* proxy.
- Coding Client Provisioning: OpenCode (:3000), ZCode (:5000), MimoCode, JCode servers wired to router + llama /v1. mimocode/ switchboard manifests + dashboard Clients panel.
- Vast.ai Deployment Kit: template.json (Instance Portal + Selkies + Guacamole) + onstart.sh for one-click GPU instance deployment.
- CUDA 13.0 Images: llama/all-in-one/vLLM images updated to CUDA 13.0 base (driver >= 580), with 12.6 fallback.
- UI Auth Gate: Dashboard write protection via X-Auth-Token. /api/upload + Files panel.
- VNC Password Support: Configure remote desktop password via VNC_PASSWORD env var.
- Per-Model min_temperature Floors: Router enforces temperature minimums per model (e.g., 0.6 for Qwythos-9B).
- model-benchmark.sh: Per-task-type latency benchmarking via router elapsed_ms + /metrics by_model.
- smoke-test.sh: 11-endpoint live sweep + inference round-trip verification.
- validate.ps1 + deploy.ps1: Windows validator (structure/JSON/py-compile/quant sanity) and remote provisioner via SSH.
- install.sh --check: Drift report (systemd units, bound ports, llama binary) -> CONVERGED/DRIFT.
- Model Registry Expansion: Qwythos-9B-v2 (FTPO loop-fix), CodeClawd Qwen3.5-9B-Claude-Code, Qwable-9B-Claude-Fable-5, Qwen3.5-9B-Claude-4.6-HighIQ-THINKING. Scripts/convert-hf.sh for safetensors-only repos.
- Dashboard SDLC Runs Panel: Status badges, run IDs, 15s auto-refresh via /api/runs proxy.
- Auto-Release Pipeline: auto-release.yml cuts v<VERSION> tags from main (CHANGELOG-guarded); release.yml builds asset bundle (source, docs-site, deploy-kit, workflows.json, sha256sums).

### Changed
- OLED Dark Theme: FreeToken-inspired dark theme with Inter + Fira Code fonts, bento-grid dashboard with sidebar.
- Router Fallback Chain: Degenerate-output detection with automatic fallback retry (X-Coherence-Retries header).
- Dashboard SSE Events: Live settings-changed push via /api/events for real-time UI updates.
- Settings Control Plane: runtime-settings.json as single source of truth; all consumers react on their own cadence (dashboard: instant poll; optimizer: 60s loop; router: on restart; llama: on save+restart).
- Timed Idle: Applying timed idle preset snapshots current settings into settings.idle.restore and forces eco mode immediately; optimizer restores snapshot automatically when window expires, even across service restarts.
- Docker Compose: Multi-stage image diet (~60% smaller all-in-one image).
- SOPS/Vault Secrets: scripts/up-secure.sh for encrypted secret management.
- Golden-Task Eval Harness: evals/golden_tasks.json with reviewer-scored run_eval.py.

### Fixed
- llama.cpp Launcher: Absolute model/binary paths, modern -DGGML_CUDA=ON, --jinja chat template (Qwen3/DeepSeek repetition fix), LLAMA_EXTRA_ARGS support.
- install.sh: Clone into empty dir (was colliding with existing directories), CUDA autodetect fallback.
- Watchdog pgrep Patterns: Matched real process names; vLLM no longer crash-looped placeholder.
- Workflow CI Smoke Test: Runs fully offline.
- Docs Generator sys.path: Fixed import resolution.
- LF Enforcement: Enforced via .gitattributes; runtime state files gitignored.

---

## [1.2.0] - 2026-08-25

### Added
- LoLLMs chat UI (--profile lollms :9600) + FreeToken edge MoE engine (--profile freetoken :9100) as optional compose profiles; pytest-asyncio pinned <0.24 to silence deprecation warnings.
- Caddy gateway expansion: basic-auth-protected /auto/* proxy with env-injected bcrypt, public-domain template with automatic ACME HTTPS.
- Dashboard SDLC Runs panel via /api/runs proxy; MkDocs site screenshots; docs sweep for 8-model roster.
- Model roster expansion: empero-ai + mradermacher models (Qwythos-9B-v2, CodeClawd, Qwable, Qwen3.5-9B-HighIQ).
- External AI provider bridge: 21+ hosted APIs with OpenAI/Anthropic/Gemini native adapters.
- llmv parity: vision (mmproj), Jupyter (:8888), clients-provision.sh, mimocode/ switchboard, Vast.ai kit, CUDA 13.0 images, VNC password env, dashboard auth gate, /api/upload, /api/clients.
- Autonomous release pipeline (VERSION-tag-cut + multi-asset releases).
- Router SSE streaming: POST /route {stream:true} -> normalized data frames.
- scripts/model-benchmark.sh and scripts/smoke-test.sh.
- install.sh --check drift report.
- Windows tooling: validate.ps1 and deploy.ps1.

### Changed
- UI polish: FreeToken-inspired OLED dark theme (Inter + Fira Code), bento-grid dashboard with sidebar.

---

## [1.1.0] - 2026-07-15

### Added
- Autonomous SDLC Agents (autonomous/): plan -> code -> verify -> fix -> review -> document -> package, sandboxed workspaces, real shell verification, artifact tarballs, REST :8050 + CLI auto-*.
- Presets: 4 recommended (24-7 Balanced / Max Performance / Silent Eco / timed Idle w/ auto-restore) + named custom presets (CRUD) via dashboard dropdown.
- Settings Control Plane: dashboard panel + config/runtime-settings.json + optimizer / autonomous concurrency cap / router rate-cache-timeout / llama sampling env; SSE /api/events live push.
- AI Resource Optimizer: thermal/util-driven performance/balanced/eco with hysteresis + cooldown; GPU undervolt tune script + systemd.
- Dashboard Enhancements: settings panel, preset picker, idle banner/countdown, alerts, Chart.js GPU graph, model shelf (registry vs disk + free space), router metrics embed, security headers, version display.
- Backup/Restore (scripts/backup.sh + weekly timer), daily cleanup timer (log rotation, workspace pruning).
- Router Improvements: degenerate-output detection + automatic fallback retry, confidence scoring, LRU cache, API-key auth, rate limiting.
- Agent Profiles: strict/balanced/creative/verbose/minimal with session memory and /agent/chat.
- Workflow Engine: validation warnings, audit JSONL, export/import, inline runs, api_build/microservice_build templates, retry+parallel+logging.
- CLI: presets/preset/settings/auto-* commands; Makefile; .env.example; MkDocs site; auto-docs generator.
- Hardware Kit: verified parts list (MPN/ASIN), BUILD guide, one-shot provisioner, remote-access setup, LOCAL-DEPLOY min-spec guide.

### Fixed
- llama.cpp launcher: absolute model/binary paths, modern -DGGML_CUDA=ON, --jinja chat template.
- install.sh: clone into empty dir, CUDA autodetect fallback.
- Watchdog pgrep patterns matched real process names; vLLM no longer crash-looped.
- Workflow CI smoke test runs fully offline.
- LF enforced via .gitattributes; runtime state files gitignored.

---

## [1.0.0] - 2026-05-01

### Added
- Initial public release
- Router with task classification, fallback chain, caching, rate limiting (:8010)
- Agent API with project/refactor/debug/analyze/chat agents (:8020)
- Workflow engine with visual designer (:8040)
- Dashboard with GPU telemetry, alerts, settings (:8030)
- Docker Compose deployment
- Kubernetes manifests (deployments, HPA, PVC)
- Live ISO build script (Ubuntu remaster)
- CLI (scripts/freeai.py)
- 262 passing tests
- MkDocs documentation site
- MIT License

---

## Version History Summary

| Version | Date | Key Theme |
|---|---|---|
| 1.0.0 | 2026-05-01 | Initial release |
| 1.1.0 | 2026-07-15 | Settings plane, presets, autonomous SDLC |
| 1.2.0 | 2026-08-25 | External providers, FreeToken, LoLLMs, TLS gateway |
| 1.3.1 | 2026-08-28 | task_printer skill, Shodan integration, docs polish |
| 2.0.0 | 2026-08-27 | Browser engine, Army orchestrator, MCP server, Vast.ai kit |
