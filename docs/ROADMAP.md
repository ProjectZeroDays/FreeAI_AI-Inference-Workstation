# Roadmap

Status: `v` implemented, `>` in progress, `o` planned.

---

## 1. Infrastructure
- v Health checks for all compose services
- v Restart policies (tuned per service)
- v GPU warmup container (`--profile warmup`)
- v Centralized config (`config/config.json` + env overrides)
- v Environment profiles (dev/staging/prod via env)
- v AI resource optimizer (thermal/util-driven power modes, hysteresis, runtime-state published to dashboard)
- v Settings control plane: dashboard panel + runtime-settings.json + optimizer / autonomous cap / router / llama launcher
- v Recommended + custom presets incl. timed idle window w/ auto-restore
- v GPU undervolt-equivalent tune (power cap + clock lock, systemd)
- o Log aggregation (FluentBit + Loki + Grafana)
- o Secrets management (Vault / Kubernetes Secrets)
- o Request tracing (OpenTelemetry)

## 2. Router
- v Task confidence scoring
- v Model fallback logic
- v Per-agent model overrides
- v Response caching (LRU)
- v Metrics endpoint
- v API-key auth + rate limiting
- o Load balancing across parallel model instances
- v SSE streaming passthrough
- o Dashboard log streaming

## 3. Agents
- v Agent profiles (strict/balanced/creative/verbose/minimal)
- v Session memory (+ `/agent/chat`, memory inspect/clear)
- v Error recovery envelopes + retry at router level
- v Metrics counters
- o Sandboxed code execution
- o Long-term memory store

## 4. Workflow Engine
- v Visual designer (workflow/ui/designer.html — export/import JSON)
- v Validation (missing consumes/produces detection)
- v Templates (api_build, microservice_build)
- v Audit logs (JSONL)
- v Export/import (definitions) + inline execution
- o Versioning, scheduling, pause/resume

## 5-6. UI & Dashboard
- v GPU temp / power draw / clock speeds
- v Alerts panel (services down, GPU util/temp thresholds)
- v Chart.js utilization history
- v Designer canvas with step config/delete/export
- o Drag-and-drop designer, prompt templates/history, theme toggle, multi-tab UI, model load-time charts, logs viewer — `docs/UI_ENHANCEMENTS.md`

## 7. Performance
- v Tunable llama.cpp flags (`N_GPU_LAYERS`, ctx via env)
- v vLLM prefix caching enabled
- o CUDA graphs, quantized KV cache, speculative decoding, tensor parallelism (`LLAMA_TP=2`), micro-batching, prompt compression

## 8. Security
- v Router API keys
- v Rate limiting
- o JWT for agents/workflows, TLS termination, RBAC, audit logs, network segmentation — `k8s/network-policy.yml`

## 9. Testing
- v Unit tests: classifier/switcher/cache/rate-limiter
- v API tests: router (mock), agent profiles/memory/metrics
- v Workflow tests: validation, retries, definitions, extraction
- o Integration/load (Locust), GPU stress, prompt regression suites

## 10-11. DevEx & CI/CD
- v freeai-cli (status/models/route/workflows/run)
- v Local dev mode (MOCK_LLM=1)
- v Docker build+push to GHCR on tags
- v Release bundle workflow
- v Workflow CI + docs generation pipelines
- o VSCode extension, hot reload, debug mode

## 12. Kubernetes
- v HPA (router/agents/workflow)
- v GPU nodeSelector + tolerations (llama/vLLM)
- v Models PVC manifest
- o Prometheus/Grafana stack, Istio, Argo CD/Workflows, sealed secrets

## 13. Documentation
- v MkDocs skeleton (architecture, API, switching, deployment, troubleshooting)
- v Autonomous SDLC guide
- v Auto-docs generator (docs/generate_docs.py + workflows.json)

## 14. Models
- v Health-aware fallback routing
- v GPU warmup (compose profile + agents/gpu-warmup.sh)
- o Model performance scoring, registry UI

## 15. Ops Scripts
- v model-benchmark.sh (per-task latency), smoke-test.sh (11-endpoint sweep)
- v validate.ps1 + deploy.ps1 (Windows validator + remote provisioner)
- v install.sh --check drift report
- v Autonomous release pipeline (VERSION-tag-cut + multi-asset releases)

## 15b. External Providers & Expansion
- v Parallel hot models: llama2 shard :9003 (`--profile llama2`) + per-GPU CUDA_VISIBLE_DEVICES
- v Qdrant RAG sidecar + ingest watcher (`--profile rag`)
- v WebSocket token streaming (ws://:8011/ws/route) alongside SSE
- v Golden-task eval harness (evals/golden_tasks.json + run_eval.py)
- v Multi-stage image diet (~60% smaller all-in-one) + SOPS/Vault secrets
- v Local-build.yml workflow (artifact tarballs instead of GHCR push)
- v FreeToken edge MoE serving engine (`--profile freetoken`) — 290B+ frontier models
- v LoLLMs chat UI (`--profile lollms`)
- v 21+ hosted API bridge with explicit model routing and keyed-fallback tails

## 16. Codex-Class Integration
- v MCP server wrapper over /route, /agent/*, /workflow, autonomous API
- o Approval profiles (suggest/auto/full-auto) + dashboard confirm queue
- o Diff-based surgical edits (`EDIT_MODE=diff`)
- o OS-level sandbox runner option (bwrap/nspawn, network-off profile)
- o Git-native runs (init/commit per green phase; branch archive export)
- See docs/CODEX-INTEGRATION.md and docs/GAP-ANALYSIS-CODEX.md

## 17. Distribution Tracks
- v All-in-one CUDA image (`docker/all-in-one.Dockerfile` + supervisord) behind compose `--profile allinone`
- v Live ISO ("FreeAIOS"): build script + boot-menu plan — ISO v1.2.1 artifact
- v Provider launch kits: Vast.ai template, RunPod template from GHCR

## 18. llmv-Llama.cpp-CUDA-13.0-Desktop Integration
- v Vision (mmproj): launcher flag, downloader entry, compose env
- v JupyterLab :8888 (compose --profile jupyter)
- v Coding-clients provisioning (OpenCode :3000, ZCode :5000, MimoCode, JCode)
- v mimocode/ switchboard manifests + dashboard Clients panel
- v Vast.ai kit: template.json + onstart.sh
- v CUDA 13.0 images (llama/all-in-one/vLLM; driver >= 580)
- v UI auth gate (X-Auth-Token write protection), /api/upload + Files panel
- v VNC password via VNC_PASSWORD env

## 19. Browser Engine & Army (Shipped)
- v CDP-based browser engine with Manifest-X integration
- v Army orchestrator: 14 ranks (E-1 Grunt to O-7 Brigadier General), 6 divisions
- v Isolated browser sessions per agent with anonymity config
- v Stealth/anonymity modes: none, Tor, SOCKS
- v Extensions: scrapling, proxycrawl, burp, zaproxy, ghidra, frida, cloakbrowser
- v Loot management (cookies, credentials, hashes)
- v C2 dashboard (connected hosts, listeners, shell)
- v Scales to 1000+ concurrent agents

## 20. Future
- o Multi-GPU distributed inference (`router/load_balancer.py`)
- o Model performance scoring and auto-selection
- o Real-time collaborative workspaces
- o WebGPU inference backend
- o Federated learning support
- o On-device fine-tuning (SFT/DPO via `docs/TRAINING.md`)
- o Plugin marketplace for skills and agents
