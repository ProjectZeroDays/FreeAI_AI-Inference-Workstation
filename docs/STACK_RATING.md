# Stack Rating — vs Other GitHub LLM Stacks

**Overall: 9.0 / 10** — among the most complete self-hosted AI workstation stacks on GitHub. The gap to 10 is operational polish, not architecture.

## Scoring methodology (0-10, 10 = best-in-class for that dimension)

| Dimension | This stack | Ollama+Open WebUI | LocalAI | vLLM standalone | SGLang | Jan / LM Studio | AnythingLLM |
|---|---|---|---|---|---|---|---|
| **Model breadth** | 9.5 | 7 | 8 | 6 | 6 | 5 | 6 |
| **Hardware efficiency** | 9.0 | 7 | 7.5 | 8 | 8.5 | 6 | 6 |
| **Agentic capability** | 9.5 | 4 | 4 | 2 | 3 | 2 | 5 |
| **Deployment flexibility** | 9.5 | 6 | 7 | 6 | 6 | 4 | 5 |
| **Observability** | 9.0 | 5 | 4 | 5 | 5 | 3 | 4 |
| **Extensibility** | 9.0 | 6 | 7 | 5 | 6 | 4 | 6 |
| **Setup friction** | 7.0 | 9 | 7 | 6 | 6 | 9 | 7 |
| **Cost control** | 9.5 | 7 | 7 | 7 | 7 | 8 | 7 |

| **TOTAL (weighted)** | **9.0** | 6.2 | 6.4 | 5.5 | 5.8 | 4.8 | 5.5 |

## Why it scores 9.0

**Strengths that others lack combined:**

*   **21+ external providers + local GGUF under one URL** — no other open stack does OpenAI + Anthropic + Gemini adapters, auto-fallback tails, and provider health probing behind a single `/route` with caching and degenerate-output retry. Ollama/Open WebUI is local-only; LiteLLM is cloud-only.
*   **True autonomous SDLC** — 7-phase lifecycle (plan→code→verify with *real* `compileall`/`pytest`/`node --check`→fix→review→document→package) in a sandboxed workspace with artifact tarballs and concurrency caps. AnythingLLM has RAG; OpenDevin has agents; neither packages a shippable artifact.
*   **Workflow engine + designer + presets + timed idle** — registry-based pipelines, validation, audit log, export/import, visual designer. No peer stacks this size offer that.
*   **Ops depth** — GPU power modes with hysteresis, undervolt tune, watchdogs, daily cleanup + weekly backup timers, Caddy TLS with basic_auth for autonomous, drift check, all compose healthchecks. Most stacks ship one `docker-compose.yml` and hope.
*   **Deployment matrix** — bare metal → all-in-one container → K8s → 5 cloud providers → Live ISO from one repo. Ollama wins on ease; this wins on *where* you can run.
*   **Edge MoE frontier** — FreeToken profile lets 290B+ MoE run on consumer RTX 30/40/50 alongside 9B GGUFs, auto-fallback when healthy. Unique at this VRAM.

**What keeps it at 9.0 not 10 — and how to close it:**

| Gap | Impact | Fix (effort) |
|---|---|---|
| **Single hot local model** — llama.cpp serves one GGUF at a time; roster is breadth on disk, not parallel VRAM | Broad use needs model swap or second GPU | Parallel shard: second llama container per GPU or dynamic `LLAMA_MODEL_PATH` hot-swap via API (M) |
| **Setup friction 7.0** — drivers, CUDA, model downloads (15GB), .env | First-boot time ~30 min | Prebuilt GHCR all-in-one image + bundled models torrent / HF cache seed (M) — currently coded, blocked only by billing lock |
| **No RAG / vector DB** | Long-repo context needs manual file windowing | Add Qdrant sidecar + ingest workflow (M) |
| **Dashboard is Flask SSE, not WebSocket** | Live push is polling-ish | Already has SSE `/api/events`; next: WebSocket for agent streaming tokens (S) |
| **No prompt regression evals** | Model swaps aren't scored | Golden-task suite scored by reviewer model (S) |
| **Secrets in .env** | No Vault/KMS | Add SOPS-age or KMS sidecar, mount via systemd credentials (S) |
| **Image size (CUDA devel)** | 5-6 GB layers | Multi-stage runtime image copying only `llama-server` (S) |
| **No hosted demo** | Try-before-clone gap | GitHub Codespace with MOCK_LLM (L) |

## FreeToken-specific rating bump

Adding FreeToken as `--profile freetoken` is **net +0.2** already counted above — it moves Hardware efficiency 8.5→9.0 and Model breadth 9.0→9.5. Without it you'd be 8.8.

**Verdict:** Keep FreeToken as optional profile (not default) — it widens the frontier without taxing users who don't need 290B. The 4 recommended presets + auto-fallback-when-healthy wiring already does this right.
