# Roadmap

Status of the master improvement list. ✅ implemented · 🕐 planned.

## 1. Infrastructure
- ✅ Health checks for all compose services
- ✅ Restart policies (tuned per service)
- ✅ GPU warmup container (`--profile warmup`)
- ✅ Centralized config (`config/config.json` + env overrides)
- ✅ Environment profiles (dev/staging/prod via env)
- ✅ AI resource optimizer (thermal/util-driven power modes, hysteresis,
  runtime-state published to dashboard) — saves watts/money 24/7
- ✅ Settings control plane: dashboard panel → runtime-settings.json →
  optimizer / autonomous cap / router / llama launcher
- ✅ Recommended + custom presets incl. timed idle window w/ auto-restore
- ✅ GPU undervolt-equivalent tune (power cap + clock lock, systemd)
- 🕐 Log aggregation (FluentBit → Loki → Grafana)
- 🕐 Secrets management (Vault / Kubernetes Secrets)
- 🕐 Request tracing (OpenTelemetry)

## 2. Router
- ✅ Task confidence scoring
- ✅ Model fallback logic
- ✅ Per-agent model overrides
- ✅ Response caching (LRU)
- ✅ Metrics endpoint
- ✅ API-key auth + rate limiting
- 🕐 Load balancing across parallel model instances
- 🕐 SSE streaming passthrough
- 🕐 Dashboard log streaming

## 3. Agents
- ✅ Agent profiles (strict/balanced/creative/verbose/minimal)
- ✅ Session memory (+ `/agent/chat`, memory inspect/clear)
- ✅ Error recovery envelopes + retry at router level
- ✅ Metrics counters
- 🕐 Sandboxed code execution
- 🕐 Long-term memory store

## 4. Workflow Engine
- ✅ Visual designer (workflow/ui/designer.html — export/import JSON)
- ✅ Validation (missing consumes/produces detection)
- ✅ Templates (api_build, microservice_build)
- ✅ Audit logs (JSONL)
- ✅ Export/import (definitions) + inline execution
- 🕐 Versioning, scheduling, pause/resume

## 5–6. UI & Dashboard
- ✅ GPU temp / power draw / clock speeds
- ✅ Alerts panel (services down, GPU util/temp thresholds)
- ✅ Chart.js utilization history
- ✅ Designer canvas with step config/delete/export
- 🕐 Drag-and-drop designer, prompt templates/history, theme toggle,
  multi-tab UI, model load-time charts, logs viewer

## 7. Performance
- ✅ Tunable llama.cpp flags (`N_GPU_LAYERS`, ctx via env)
- ✅ vLLM prefix caching enabled
- 🕐 CUDA graphs, quantized KV cache, speculative decoding,
  tensor parallelism, micro-batching, prompt compression, response
  streaming end-to-end

## 8. Security
- ✅ Router API keys
- ✅ Rate limiting
- 🕐 JWT for agents/workflows, TLS termination, RBAC, audit logs,
  network segmentation

## 9. Testing
- ✅ Unit tests: classifier/switcher/cache/rate-limiter
- ✅ API tests: router (mock), agent profiles/memory/metrics
- ✅ Workflow tests: validation, retries, definitions, extraction
- 🕐 Integration/load (Locust), GPU stress, prompt regression suites

## 10–11. DevEx & CI/CD
- ✅ tokugawa-cli (status/models/route/workflows/run)
- ✅ Local dev mode (MOCK_LLM=1)
- ✅ Docker build+push to GHCR on tags
- ✅ Release bundle workflow
- ✅ Workflow CI + docs generation pipelines
- 🕐 VSCode extension, hot reload, debug mode

## 12. Kubernetes
- ✅ HPA (router/agents/workflow)
- ✅ GPU nodeSelector + tolerations (llama/vLLM)
- ✅ Models PVC manifest
- 🕐 Prometheus/Grafana stack, Istio, Argo CD/Workflows, sealed secrets

## 13. Documentation
- ✅ MkDocs skeleton (architecture, API, switching, deployment,
  troubleshooting)
- ✅ Autonomous SDLC guide
- ✅ Auto-docs generator (docs/generate_docs.py → workflows.json)

## 14. Models
- ✅ Health-aware fallback routing
- ✅ GPU warmup (compose profile + agents/gpu-warmup.sh)
- 🕐 Model performance scoring, registry UI

## 15. Ops scripts (ported from center-control-plane)
- ✅ model-benchmark.sh (per-task latency), smoke-test.sh (11-endpoint sweep)
- ✅ validate.ps1 + deploy.ps1 (Windows validator + remote provisioner)
- ✅ install.sh --check drift report
- ✅ autonomous release pipeline (VERSION-tag-cut + multi-asset releases)

## 15b. Future
- ✅ Autonomous SDLC agents (plan → code → verify → fix → document →
  package, sandboxed workspaces, artifact delivery)
- 🕐 Function calling / tool use beyond file ops, RAG + vector DB,
  document ingestion, repo-wide auto-refactor of existing trees,
  multi-GPU distributed inference, model registry UI

## 16. Codex-class integration (planned epic)
- ?? MCP server wrapper over /route, /agent/*, /workflow, autonomous API
- ?? Approval profiles (suggest/auto/full-auto) + dashboard confirm queue
- ?? Diff-based surgical edits (`EDIT_MODE=diff`)
- ?? OS-level sandbox runner option (bwrap/nspawn, network-off profile)
- ?? Git-native runs (init/commit per green phase; branch archive export)
- See docs/CODEX-INTEGRATION.md and docs/GAP-ANALYSIS-CODEX.md

## 17. Distribution tracks (planned)
- ? All-in-one CUDA image starter (`docker/all-in-one.Dockerfile` +
  supervisord) behind compose `--profile allinone`
- ?? Live ISO ("TokugawaOS"): build script + boot-menu plan
  (`live/build-live.sh`, docs/DEPLOYMENT-PLANS.md Track C) - ISO v0.1 tag
- ?? Provider launch kits: RunPod template from GHCR image, Lambda/
  Hetzner bare-metal via install-stack.sh, spot-cloud Terraform module
