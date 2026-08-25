## 1.2.0 - Unreleased

### Added
- Dashboard SDLC Runs panel (status badges, run IDs, 15s refresh) via /api/runs proxy; MkDocs site screenshots; docs sweep for 8-model roster
- Roster expansion (empero-ai + mradermacher): Qwythos-9B-v2 (FTPO loop-fix, reasoning primary), CodeClawd Qwen3.5-9B-Claude-Code (code specialist, agent-trace SFT), Qwable-9B-Claude-Fable-5 (multimodal general), Qwen3.5-9B-Claude-4.6-HighIQ-THINKING (mradermacher i1); per-model min_temperature floors; scripts/convert-hf.sh for safetensors-only repos (openNemo pair)

- Model: Qwythos-9B Claude Mythos 5 1M (empero-ai) as reasoning_specialist primary - Claude-trace post-train of Qwen3.5-9B, 1M context (YaRN), native function calling, vision-capable; router enforces per-model min_temperature floor (0.6) on sync + stream paths; optional MTP speculative-decoding download
- External AI provider bridge: 21+ hosted APIs as router backends (OpenAI/Anthropic/Gemini native adapters + openai-compatible for Groq/Mistral/DeepSeek/Together/Fireworks/OpenRouter/xAI/Perplexity/Cerebras/SambaNova/Cohere/Novita/DeepInfra/Hyperbolic/HuggingFace/Ollama/LM Studio); explicit model routing, keyed-fallback tails, streaming, /providers + /api/providers(+test), dashboard panel, CLI providers/provider-test, docs/PROVIDERS.md

- llmv parity: vision (mmproj --mmproj flag + downloader + compose env), Jupyter (:8888 compose profile + systemd), clients-provision.sh (OpenCode/ZCode/MimoCode/JCode servers wired to router+llama), mimocode/ switchboard manifests, Vast.ai kit (template.json + onstart w/ Instance Portal + Selkies + Guacamole), CUDA 13.0 images (driver >= 580), VNC password env, dashboard auth gate (X-Auth-Token on writes), /api/upload + /api/uploads, /api/clients switchboard + dashboard panels

- Autonomous releases: auto-release.yml cuts v<VERSION> tags from main (CHANGELOG-guarded); release.yml builds asset bundle (source, docs-site, deploy-kit, workflows.json, sha256sums) + generated notes
- Router SSE streaming: POST /route {stream:true} -> normalized data frames w/ model header + [DONE]; fallback across chain on empty streams
- Caddy TLS gateway (compose --profile tls, :8443 -> dashboard, write-guard on settings API)
- scripts/model-benchmark.sh: per-task-type latency benchmark (avg/min/max via router elapsed_ms + /metrics by_model)
- scripts/smoke-test.sh: 11-endpoint live sweep + inference round-trip -> ALL_SYSTEMS_OPERATIONAL
- install.sh --check: drift report (systemd units, bound ports, llama binary) -> CONVERGED/DRIFT
- Windows tooling: validate.ps1 (structure/JSON/py-compile/quant sanity), deploy.ps1 (SSH bundle+provision remote host)
- 3 new screenshots: dashboard idle state, UI in-use (refactor response), real CLI help

# Changelog

## 1.1.0 — Settings plane, presets, autonomous SDLC, local-deploy kit

### Added
- Autonomous SDLC agents (`autonomous/`): plan→code→verify→fix→review→document→package, sandboxed workspaces, real shell verification (compileall/pytest/node), artifact tarballs, REST :8050 + CLI `auto-*`
- Presets: 4 recommended (24-7 Balanced / Max Performance / Silent Eco / timed **Idle** w/ auto-restore) + named custom presets (CRUD) — dashboard dropdown
- Settings control plane: dashboard panel → `config/runtime-settings.json` → optimizer / autonomous concurrency cap / router rate-cache-timeout / llama sampling env; SSE `/api/events` live push
- AI resource optimizer service: thermal/util-driven performance/balanced/eco with hysteresis + cooldown; GPU undervolt tune script + systemd
- Dashboard: settings panel, preset picker, idle banner/countdown, alerts, Chart.js GPU graph, model shelf (registry vs disk + free space), router metrics embed, security headers, version display
- Backup/restore (`scripts/backup.sh` + weekly timer), daily cleanup timer (log rotation, workspace pruning)
- Router: degenerate-output detection → automatic fallback retry (`X-Coherence-Retries`), confidence scoring, LRU cache, API-key auth, rate limiting
- Agents: profiles (strict/balanced/creative/verbose/minimal), session memory + `/agent/chat`, metrics
- Workflow engine: validation warnings, audit JSONL, export/import, inline runs, api_build/microservice_build templates, retry+parallel+logging
- CLI: presets/preset/settings/auto-* commands; Makefile; `.env.example`; MkDocs site; auto-docs generator
- Hardware kit: verified parts list (MPN/ASIN), BUILD guide, one-shot provisioner, remote-access setup, LOCAL-DEPLOY min-spec guide

### Fixed
- llama.cpp launcher: absolute model/binary paths, modern `-DGGML_CUDA=ON`, `--jinja` chat template (Qwen3/DeepSeek repetition fix), `LLAMA_EXTRA_ARGS`
- install.sh: clone into empty dir (was colliding), CUDA autodetect fallback
- Watchdog pgrep patterns matched real process names; vLLM no longer crash-loop placeholder
- Workflow CI smoke test runs fully offline; docs generator sys.path fix; designer save = file download
- LF enforced via .gitattributes; runtime state files gitignored

## 1.0.0 — Initial public scaffold
Router/classifier/switcher, agent API + 5 CLIs, workflow engine, dashboard+UI, compose/K8s, CI.
