# Unified GPU Inference Stack

Self-hosted LLM operations stack:

- **FreeAI Router** (:8010) – classifies prompts and routes with fallback
- **Agent API** (:8020) – project/refactor/debug/analyze/chat agents with profiles and session memory
- **Workflow Engine** (:8040) – multi-agent pipelines with retries, validation, audit logs
- **Dashboard** (:8030) – GPU telemetry, alerts, service health
- **llama.cpp** (:9001) / **vLLM** (:9002) – GGUF inference backends
- **freeai-cli** (`scripts/freeai.py`) – shell CLI for health, routing, workflows, and service management

See [Architecture](ARCHITECTURE.md), [API Reference](API.md),
[Deployment](DEPLOYMENT.md), [Troubleshooting](TROUBLESHOOTING.md),
[freeai-cli](FREEAI-CLI.md).
