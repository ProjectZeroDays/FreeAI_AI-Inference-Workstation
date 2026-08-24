# API Reference

## Router (:8010)

| Method | Path | Notes |
|---|---|---|
| GET | /health | liveness |
| GET | /models | roster + endpoints |
| POST | /route | `{prompt, max_tokens?, temperature?, agent?, profile?}` → `{model_used, task_type, confidence, elapsed_ms, response}`; headers `X-Cache: HIT/MISS` |
| GET | /metrics | request/cache/error counters, per-task/model counts, avg latency |

Auth: if `ROUTER_API_KEY` is set, send `X-API-Key` on all paths except
`/health`. Rate limiting: token bucket per client IP (429 when empty).

## Agent API (:8020)

| Method | Path | Body |
|---|---|---|
| POST | /agent/project | `{spec, profile?, session_id?}` |
| POST | /agent/refactor | `{code, language?, goals?}` |
| POST | /agent/debug | `{code, error, language?}` |
| POST | /agent/analyze | `{context, question}` |
| POST | /agent/orchestrate | `{prompt, agent_hint?}` |
| POST | /agent/chat | `{message, session_id}` — memory-backed multi-turn |
| GET/DELETE | /memory/{session_id} | inspect/clear history |
| GET | /profiles | temperature/max_tokens presets |

Profiles: `strict` (t0.0), `balanced` (t0.2), `creative` (t0.8),
`verbose` (4096 tok), `minimal` (512 tok).

## Workflow Engine (:8040)

| Method | Path | Purpose |
|---|---|---|
| GET | /workflows | registered names |
| POST | /workflow/run | `{workflow, context, strict_validation?}` |
| POST | /workflow/run-inline | execute an imported definition |
| GET | /workflow/export/{name} | JSON definition export |
| POST | /workflow/validate | `{steps:[{name,agent,consumes}]}` → warnings |

Registered workflows: `project_pipeline`, `full_build`, `api_build`,
`microservice_build`.
