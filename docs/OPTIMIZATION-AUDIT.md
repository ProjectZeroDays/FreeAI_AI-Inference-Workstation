# Repo Optimization Audit

High-impact changes for scale, reliability, and multi-tenant use.
Status: ✅ shipped · 🔜 planned (approach sketched) · 🕐 needs infra.

## 1. Logging & observability

| Item | Status | Notes |
|---|---|---|
| Centralized structured (JSON) logging | 🔜 | wrap stdlib logging with a JSONFormatter; one `logs/<service>.jsonl` per service; Loki/Grafana ship later (ROADMAP §1) |
| Per-agent correlation IDs | 🔜 | router mints `X-Correlation-ID` (uuid4) if absent, echoes it in responses; agents + workflow propagate it into log records and JSONL audit rows |
| Configurable log level via env | 🔜 | `LOG_LEVEL=DEBUG\|INFO\|WARN\|ERROR` read by every service entrypoint; default INFO |
| Disable verbose per-token logs in prod | 🔜 | gate llama request/response dumps + WS frame logs behind `LOG_LEVEL=DEBUG`; prod default keeps only route decisions + errors |

## 2. Config & secrets

| Item | Status | Notes |
|---|---|---|
| Single config layer | ✅ | `config/config.json` (models, ports, GPUs, router weights) + `config/runtime-settings.json` control plane + env overrides |
| Env-only secrets | ✅ | `.env.example` ships empty values only; real keys via env or SOPS (`config/secrets.enc.yaml`, `scripts/up-secure.sh`, age/Vault) |
| YAML/TOML option | 🕐 | JSON is fine today; revisit only if config grows beyond ~200 lines |

## 3. Health & watchdogs

| Item | Status | Notes |
|---|---|---|
| Unified `/healthz` per service | 🔜 | add tiny `/_health` route to router/agents/workflow/autonomous returning `{gpu, disk_free, queue_depth, uptime}`; dashboard `/api/status` aggregates them instead of port probes where available |
| Stuck-agent watchdog ("no tokens in N s") | 🔜 | supervisor loop already restarts dead processes; extend with token-progress check: if a streaming request emits 0 tokens for `STREAM_STALL_SECS` (default 30), kill + recycle the llama child and fail the request to the next fallback |
| Watchdogs (process-level) | ✅ | supervisor 10s loop + health agent 30s + recovery agent 15s + systemd auto-restart |

## 4. Model lifecycle

| Item | Status | Notes |
|---|---|---|
| Model registry module | ✅ | `registry/registry.json`: name → gguf → backend → endpoint → role; `/models` API + model shelf UI |
| Registry knows quant + GPU layers | 🔜 | add `quant` + `n_gpu_layers` + `ctx_train` fields; llama launcher reads them per model instead of global `N_GPU_LAYERS` |
| Lazy-load cold models | ✅ | one hot model per llama process; `/admin/model-switch` swaps on demand; `--profile llama2` keeps a 2nd shard resident |
| Explicit hot/cold pool config | 🔜 | `config/config.json` `hot_pool: [ids]` consumed by launcher + warmup container; cold models load on first request |

## 5. Networking

| Item | Status | Notes |
|---|---|---|
| Per-client/IP rate limit | ✅ | token bucket (429 + `Retry-After`), `RATE_LIMIT_CAPACITY` env |
| WebSocket streaming | ✅ | `ws://:8011/ws/route` alongside SSE |
| Backpressure-aware queues | 🔜 | bounded `asyncio.Queue(maxsize=N)` per WS client; drop slowest subscriber on overflow instead of buffering unbounded |
| Concurrent stream cap per model | 🔜 | llama.cpp queues internally; add router-side cap (`MAX_STREAMS_PER_MODEL`, default 4) returning 429 with active count |
| TLS termination | ✅ | Caddy gateway (`--profile tls`, ACME) |

## 6. RAG & Qdrant

| Item | Status | Notes |
|---|---|---|
| Batched vector inserts | 🔜 | ingest watcher: buffer chunks, `upsert` in batches of 128 every ~2 s instead of per-chunk calls |
| Batched queries | 🔜 | multi-query retrieval (question + rewritten variants) in one `search` batch |
| Top-K result cache | 🔜 | LRU keyed on `(collection, query-hash, k)`; docs/codebase paths hit repeatedly during SDLC runs — cache TTL 10 min, invalidated on collection change |

## Priority order

1. Correlation IDs + JSON logs (makes every other fix debuggable)
2. Stuck-agent watchdog (biggest real-world reliability win)
3. Registry quant/layers fields (unlocks per-model tuning)
4. RAG batching + cache (cheapest latency win under load)
5. Stream caps + backpressure (matters only with >2 concurrent agents)
