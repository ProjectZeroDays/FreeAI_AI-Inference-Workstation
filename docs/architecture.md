# Architecture

```
Tokugawa UI (ui/)          Workflow Designer (workflow/ui/)
        │                        │
        ▼                        ▼
  Agent API (:8020) ◄──── Workflow Engine (:8040)
        │                        │
        ▼                        │
   Router (:8010) ───────────────┘
   classify → confidence → fallback chain → cache/rate-limit/auth
        │
        ▼
  llama.cpp (:9001 GGUF)      vLLM (:9002, optional)

Dashboard (:8030) polls nvidia-smi + service ports, raises alerts.
Supervisor + health/recovery agents restart dead processes.
```

## Config resolution

`config/config.json` is the single source of truth. Every value can be
overridden by environment variables (see `router/settings.py`).
Docker Compose injects service-discovery envs (`LLAMA_BASE`,
`AGENT_API`, `ROUTER_URL`) so the same images run bare-metal or in K8s.

## Audit trail

Workflow steps append JSONL events to `logs/workflow-audit.jsonl`
(started/ok/retry/failed per step with workflow_id).
