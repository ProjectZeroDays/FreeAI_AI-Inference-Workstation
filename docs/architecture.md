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
### Settings & preset interconnection

Single source of truth: **`config/runtime-settings.json`** (written by
the dashboard Settings panel). Every consumer reacts on its own cadence:

| Consumer | Reads | Reaction timing |
|---|---|---|
| Dashboard UI | file via `/api/settings`, `/api/presets` | instant on save; 30s idle-countdown poll |
| Resource optimizer | file each loop | ≤60s: mode/profile changes, manual override, idle window start/end |
| Autonomous SDLC API | file per request | live concurrency cap (`max_concurrent_runs`) → 429 when full |
| Router | file at process start | rate-limit/cache/timeout after restart |
| llama.cpp launcher | `config/llama.env` written by "Save + restart llama" | sampling guards + ctx on restart |

Preset apply is just a batched settings write (+ immediate GPU tune
when auto-management is off, or eco caps for timed idle), so all of
the above propagate identically whether the change came from a single
toggle or a full preset.

Timed idle: applying "Idle (timed)" with `duration_min` snapshots the
current settings into `settings.idle.restore`, forces eco immediately,
and the optimizer restores the snapshot automatically when the window
expires — even across service restarts (state lives in the file).
