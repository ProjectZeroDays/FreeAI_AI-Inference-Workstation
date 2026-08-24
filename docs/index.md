# Unified GPU Inference Stack

Self-hosted LLM operations stack:

- **Tokugawa Router** (:8010) — classifies prompts and routes with fallback
- **Agent API** (:8020) — project/refactor/debug/analyze/chat agents with profiles and session memory
- **Workflow Engine** (:8040) — multi-agent pipelines with retries, validation, audit logs
- **Dashboard** (:8030) — GPU telemetry, alerts, service health
- **llama.cpp** (:9001) / **vLLM** (:9002) — GGUF inference backends

See [Architecture](architecture.md), [API Reference](api.md),
[Deployment](deployment.md), [Troubleshooting](troubleshooting.md).
