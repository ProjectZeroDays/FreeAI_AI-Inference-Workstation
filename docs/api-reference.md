# FreeAI API Reference

Complete REST endpoint reference for the FreeAI Unified AI Stack.

## Base URLs

| Service | URL |
|---|---|
| Dashboard | `http://localhost:8030` |
| Router | `http://localhost:8010` |
| Agent API | `http://localhost:8020` |
| Workflow Engine | `http://localhost:8040` |
| Autonomous SDLC | `http://localhost:8050` |
| MCP Server | `http://localhost:8090` |

All endpoints return JSON unless noted. Auth-required endpoints reject with `401` when `X-API-Key` or `X-Auth-Token` is missing/mismatched.

---

## Router (`:8010`)

| Method | Path | Description |
|---|---|---|
| GET | `/health` | Liveness probe + mock flag |
| GET | `/models` | Roster: name, role, strengths, endpoint |
| POST | `/route` | Classify + route prompt to best backend |
| GET | `/metrics` | Counters, per-task/model, latency avg |

### POST /route

```json
// Request
{"prompt": "Design a rate limiter", "model": "openai/gpt-4o-mini", "max_tokens": 1024, "temperature": 0.2, "agent": "project"}

// Response
{
  "model_used": "openai/gpt-4o-mini",
  "task_type": "general_code",
  "confidence": 0.87,
  "elapsed_ms": 342,
  "response": { "choices": [{"message": {"content": "..."}}] }
}
```

Headers: `X-Cache: HIT/MISS`, `X-Coherence-Retries: N`

---

## Agent API (`:8020`)

| Method | Path | Description |
|---|---|---|
| POST | `/agent/project` | Full project from spec |
| POST | `/agent/refactor` | Refactor code block |
| POST | `/agent/debug` | Debug error in code |
| POST | `/agent/analyze` | Analyze context |
| POST | `/agent/orchestrate` | Orchestrate multi-step |
| POST | `/agent/chat` | Multi-turn chat with session memory |
| GET | `/memory/{session_id}` | Inspect session memory |
| DELETE | `/memory/{session_id}` | Clear session memory |
| GET | `/profiles` | Temperature/max_tokens presets |
| GET | `/metrics` | Call counters |
| GET | `/health` | Liveness |

### POST /agent/chat

```json
{"message": "Design a rate limiter", "session_id": "s1"}
```

---

## Workflow Engine (`:8040`)

| Method | Path | Description |
|---|---|---|
| GET | `/workflows` | List registered workflows |
| POST | `/workflow/run` | Execute a named workflow |
| POST | `/workflow/run-inline` | Execute an inline definition |
| GET | `/workflow/export/{name}` | Export workflow as JSON |
| POST | `/workflow/validate` | Validate steps for missing deps |
| GET | `/health` | Liveness |

### POST /workflow/run

```json
{"workflow": "project_pipeline", "context": {"spec": "Build a FastAPI notes service"}, "strict_validation": false}
```

---

## Autonomous SDLC (`:8050`)

| Method | Path | Description |
|---|---|---|
| POST | `/auto/start` | Start a new SDLC run |
| GET | `/auto/runs` | List all runs |
| GET | `/auto/runs/{id}` | Get run status |
| POST | `/auto/runs/{id}/cancel` | Cancel a run |
| GET | `/auto/runs/{id}/artifact` | Download tarball artifact |
| POST | `/auto/runs/{id}/shell` | Run command in workspace (guarded) |

### POST /auto/start

```json
{"spec": "Build a FastAPI notes service with auth and tests", "profile": "balanced", "max_tasks": 20, "enable_shell": true}
```

Response: `{"run_id": "abc123", "status": "queued"}` (429 if over concurrency cap)

---

## Dashboard (`:8030`)

### Health & Status

| Method | Path | Description |
|---|---|---|
| GET | `/api/health` | Service health (ok/degraded) |
| GET | `/api/status` | GPU, services, alerts, power mode, router metrics |
| GET | `/api/stats` | Skills total, uptime |
| GET | `/api/config` | Runtime config |
| GET | `/api/services` | Service port health probes |
| GET | `/api/services/health` | Detailed service health |
| GET | `/api/metrics` | Aggregated metrics across services |
| GET | `/api/events` | SSE stream of settings changes |

### Settings & Presets

| Method | Path | Description |
|---|---|---|
| GET | `/api/settings` | Get current settings |
| POST | `/api/settings` | Update settings (requires auth token) |
| POST | `/api/settings/llama-restart` | Persist sampling env + restart llama |
| GET | `/api/presets` | List all presets |
| POST | `/api/presets` | Create custom preset |
| DELETE | `/api/presets/{name}` | Delete preset |
| POST | `/api/presets/{name}/apply` | Apply preset (+ `{duration_min}` for timed idle) |

### Models

| Method | Path | Description |
|---|---|---|
| GET | `/api/models-status` | Registry vs on-disk GGUFs + disk free |
| GET | `/api/providers` | Merged provider config |
| GET | `/api/runs` | Proxy to autonomous SDLC runs |
| GET | `/api/clients` | Client switchboard (mimocode manifests) |

### Skills

| Method | Path | Description |
|---|---|---|
| GET | `/api/skills` | List all skills from SKILLS_DIR |
| POST | `/api/skills/save` | Create/update skill |
| DELETE | `/api/skills/delete/{name}` | Delete skill |
| POST | `/api/skills/scan` | Auto-generate skills from activity log |
| GET | `/api/skills/activity` | Recent skill activity entries |
| POST | `/api/skills/log` | Log a skill activity entry |
| GET | `/api/skills/aggregated` | Aggregate skills from all sources |

### MCP Registry

| Method | Path | Description |
|---|---|---|
| GET | `/api/mcp` | List discovered MCP servers |
| POST | `/api/mcp/register` | Register a new MCP server |

### Workflow (Dashboard)

| Method | Path | Description |
|---|---|---|
| GET | `/api/workflow` | List workflow JSON files |
| GET | `/api/workflow/registries` | List registry JSON files |
| POST | `/api/workflow/run-and-schedule` | Run workflow with optional cron schedule |
| GET | `/api/workflow/runs` | List workflow runs |
| GET | `/api/workflow/runs/{run_id}` | Get workflow run detail |

### GPU

| Method | Path | Description |
|---|---|---|
| GET | `/api/gpu` | Current GPU state |
| POST | `/api/gpu/scan` | Rescan GPUs |

### Permissions

| Method | Path | Description |
|---|---|---|
| GET | `/api/permissions` | Role definitions + RBAC status |
| POST | `/api/permissions/check` | Check resource/action/role access |

### Sandbox

| Method | Path | Description |
|---|---|---|
| GET | `/api/sandbox` | Sandbox status |
| POST | `/api/sandbox/run` | Execute code in sandbox |

### Scheduler

| Method | Path | Description |
|---|---|---|
| GET | `/api/scheduler` | List scheduler jobs |
| GET | `/api/scheduler/jobs` | List jobs (alternative) |
| POST | `/api/scheduler/jobs` | Create a cron job |
| POST | `/api/scheduler/jobs/{id}/toggle` | Enable/disable job |
| DELETE | `/api/scheduler/jobs/{id}` | Delete job |

### Campaigns

| Method | Path | Description |
|---|---|---|
| GET | `/api/campaign` | List campaigns |
| POST | `/api/campaign/create` | Create a campaign |
| POST | `/api/campaign/{id}/run` | Run a campaign |
| DELETE | `/api/campaign/{id}` | Delete a campaign |

### Training

| Method | Path | Description |
|---|---|---|
| GET | `/api/training` | Training state (datasets, jobs, models) |
| GET | `/api/training/datasets` | List datasets |
| POST | `/api/training/datasets` | Create dataset |
| DELETE | `/api/training/datasets/{id}` | Delete dataset |
| POST | `/api/training/jobs` | Create training job (sft/dpo/abr) |
| POST | `/api/training/abliterate` | Abliterate a model |
| GET | `/api/training/models` | List trained models |
| DELETE | `/api/training/models/{id}` | Delete model |
| POST | `/api/training/models/{id}/deploy` | Deploy a model |

### Automations

| Method | Path | Description |
|---|---|---|
| GET | `/api/automations` | List automations |
| POST | `/api/automations` | Create automation |
| POST | `/api/automations/{id}/toggle` | Enable/disable |
| POST | `/api/automations/{id}/run` | Run now |
| DELETE | `/api/automations/{id}` | Delete |
| GET | `/api/automations/history` | Execution history |
| GET | `/api/automations/stats` | Stats summary |

### Gateway

| Method | Path | Description |
|---|---|---|
| GET | `/api/gateway` | Gateway overview |
| GET | `/api/gateway/platforms` | Available platforms |
| POST | `/api/gateway/platforms/{name}/connect` | Connect platform |
| POST | `/api/gateway/platforms/{name}/disconnect` | Disconnect platform |
| GET | `/api/gateway/messages` | Message history |
| POST | `/api/gateway/messages` | Send message |
| POST | `/api/gateway/voice/transcribe` | Transcribe voice input |
| GET | `/api/gateway/stats` | Routing stats |
| POST | `/api/gateway/transfer` | Transfer messages between platforms |

### Memory

| Method | Path | Description |
|---|---|---|
| GET | `/api/memory` | Memory overview |
| GET | `/api/memory/preferences` | Get preferences |
| POST | `/api/memory/preferences` | Update preferences |
| GET | `/api/memory/projects` | List projects |
| POST | `/api/memory/projects` | Create project |
| DELETE | `/api/memory/projects/{name}` | Delete project |
| GET | `/api/memory/learnings` | List learnings |
| POST | `/api/memory/learnings` | Add learning |
| GET | `/api/memory/stats` | Memory stats |

### Subagents

| Method | Path | Description |
|---|---|---|
| GET | `/api/subagents` | List subagents |
| POST | `/api/subagents` | Launch subagents |
| DELETE | `/api/subagents/{id}` | Remove subagent |
| POST | `/api/subagents/{id}/pause` | Pause subagent |
| POST | `/api/subagents/{id}/resume` | Resume subagent |
| GET | `/api/subagents/{id}/log` | Get subagent log |

### Hermes

| Method | Path | Description |
|---|---|---|
| GET | `/api/hermes-status` | Hermes proxy status |
| * | `/api/hermes/proxy/{subpath}` | Forward to Hermes |

### Salad

| Method | Path | Description |
|---|---|---|
| GET | `/api/salad` | Salad earnings |
| GET | `/api/salad/gpu` | Available GPUs |

### Aikido

| Method | Path | Description |
|---|---|---|
| GET | `/api/aikido` | Aikido status |
| POST | `/api/aikido/test` | Run a security test |

### Upload

| Method | Path | Description |
|---|---|---|
| POST | `/api/upload` | Upload file (multipart) |
| GET | `/api/uploads` | List uploaded files |

### Browser

| Method | Path | Description |
|---|---|---|
| GET | `/api/browser/settings` | Get browser config |
| POST | `/api/browser/settings` | Update browser config |
| GET | `/api/browser/reset` | Reset browser to defaults |

---

## Page Routes (`:8030`)

| Path | Template |
|---|---|
| `/` | index.html (main dashboard) |
| `/dashboard` | index.html |
| `/skills` | skills.html |
| `/sdlc` | sdlc.html |
| `/wiki-dashboard` | wiki-dashboard.html |
| `/blog` | blog.html |
| `/forum` | forum.html |
| `/logs` | logs.html |
| `/network` | network.html |
| `/mcp` | mcp.html |
| `/workflows` | workflows.html |
| `/hermes` | hermes.html |
| `/aikido` | aikido.html |
| `/salad` | salad.html |
| `/providers` | providers.html |
| `/browser` | browser-v2.html |
| `/scheduler` | scheduler.html |
| `/loot` | loot.html |
| `/c2` | c2.html |
| `/plugins-manage` | plugins-manage.html |

---

## Auth

| Header | Env Var | Used By |
|---|---|---|
| `X-API-Key` | `ROUTER_API_KEY` | Router |
| `X-Auth-Token` | `DASHBOARD_AUTH_TOKEN` | Dashboard writes |
| `Authorization: Bearer <key>` | `HERMES_API_KEY` | Hermes proxy |

---

## Error Codes

| Code | Meaning |
|---|---|
| 400 | Bad request (missing params, validation failure) |
| 401 | Unauthorized (missing/wrong auth token) |
| 404 | Not found |
| 429 | Rate limited or concurrency cap exceeded |
| 500 | Internal server error |
