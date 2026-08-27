# FreeAI — Dashboard API Reference

All endpoints served by `dashboard/backend.py` on port 8080 (default).

## Pages

| Route | Template | Description |
|---|---|---|
| `/` | `index.html` | Main dashboard |
| `/skills` | `skills.html` | Skills manager |
| `/sdlc` | `sdlc.html` | SDLC & pipelines |
| `/providers` | `providers.html` | Provider registry |
| `/hermes` | `hermes.html` | Hermes integration |
| `/workflows` | `workflows.html` | Workflow engine |
| `/scheduler` | `scheduler.html` | Cron scheduler |
| `/mcp` | `mcp.html` | MCP registry |
| `/plugins-manage` | `plugins-manage.html` | Plugin management |
| `/browser-v2` | `browser-v2.html` | Knight-Shade browser |
| `/loot` | `loot.html` | Harvested loot |
| `/c2` | `c2.html` | C2 dashboard |
| `/salad` | `salad.html` | Salad GPU integration |
| `/aikido` | `aikido.html` | Aikido security |
| `/desktop` | `desktop.html` | FreeToken desktop |
| `/wiki-dashboard` | `wiki-dashboard.html` | Wiki |
| `/blog` | `blog.html` | Blog |
| `/forum` | `forum.html` | Forum |
| `/logs` | `logs.html` | Logs |
| `/network` | `network.html` | Network telemetry |
| `/subagents` | `subagents.html` | Sub-agent manager |
| `/training` | `training.html` | Training jobs |
| `/memory` | `memory.html` | Memory store |
| `/gateway` | `gateway.html` | Comms gateway |
| `/automations` | `automations.html` | Automation jobs |

## API Endpoints

### Health & Stats
- `GET /api/health` — `{status: "ok"}`
- `GET /api/stats` — skills count, activity entries
- `GET /api/status` — `{ok: true, uptime: int}`
- `GET /api/metrics` — per-service health check

### Providers
- `GET /api/providers` — merged provider registry
- `GET /api/providers/all` — all sources combined

### Browser
- `GET /api/browser/status` — engine status, army size
- `GET /api/browser/settings` — stealth/anonymity config
- `POST /api/browser/settings` — update settings
- `GET /api/browser/reset` — reset to defaults
- `POST /army/close-all` — close all browser instances

### Loot
- `GET /api/loot` — harvested cookies, creds, hashes, sessions, files
- `DELETE /api/loot/<tab>/<idx>` — delete single item
- `POST /api/loot/clear` — clear all loot

### C2
- `GET /api/c2/events` — hosts, listeners, scan count, events
- `POST /api/c2/scan` — trigger network scan
- `POST /api/c2/shell` — execute command on host

### Salad
- `GET /api/salad` — earnings (requires `SALAD_API_KEY`)
- `GET /api/salad/gpu` — GPU systems list

### Aikido
- `GET /api/aikido` — connection status (requires `AIKIDO_API_KEY`)
- `POST /api/aikido/test` — run quick scan

### Skills
- `GET /api/skills` — skill catalog from `skills/`
- `POST /api/skills/save` — create/update skill
- `DELETE /api/skills/delete/<name>` — remove skill
- `POST /api/skills/scan` — auto-discover skills from activity
- `GET /api/skills/activity` — recent activity log
- `POST /api/skills/log` — log activity entry
- `GET /api/skills/aggregated` — all skills from all directories

### Subagents
- `GET /api/subagents` — list subagents
- `POST /api/subagents` — create subagent team
- `DELETE /api/subagents/<id>` — remove
- `POST /api/subagents/<id>/pause` — pause
- `POST /api/subagents/<id>/resume` — resume
- `GET /api/subagents/<id>/log` — log entries

### Training
- `GET /api/training` — datasets, jobs, models
- `GET /api/training/datasets` — list datasets
- `POST /api/training/datasets` — upload dataset
- `DELETE /api/training/datasets/<id>` — delete dataset
- `POST /api/training/jobs` — create SFT/DPO/ABL job
- `POST /api/training/abliterate` — start abliteration
- `GET /api/training/models` — trained models
- `DELETE /api/training/models/<id>` — delete model
- `POST /api/training/models/<id>/deploy` — deploy model

### Automations
- `GET /api/automations` — cron jobs list
- `POST /api/automations` — create job
- `POST /api/automations/<id>/toggle` — enable/disable
- `POST /api/automations/<id>/run` — run now
- `DELETE /api/automations/<id>` — delete
- `GET /api/automations/history` — run history
- `GET /api/automations/stats` — aggregate stats

### Gateway
- `GET /api/gateway` — full gateway state
- `GET /api/gateway/platforms` — connected platforms
- `POST /api/gateway/platforms/<name>/connect` — connect
- `POST /api/gateway/platforms/<name>/disconnect` — disconnect
- `GET /api/gateway/messages` — recent messages
- `POST /api/gateway/messages` — send message
- `POST /api/gateway/voice/transcribe` — transcribe voice memo
- `GET /api/gateway/stats` — aggregate stats
- `POST /api/gateway/transfer` — transfer between platforms

### Hermes
- `GET /api/hermes-status` — port detection, connection
- `GET/POST/PUT/DELETE /api/hermes/proxy/<path>` — proxy to Hermes

### Scheduler
- `GET /api/scheduler` — config + jobs
- `GET /api/scheduler/jobs` — list jobs
- `POST /api/scheduler/jobs` — create job
- `POST /api/scheduler/jobs/<id>/toggle` — enable/disable
- `DELETE /api/scheduler/jobs/<id>` — delete

### Workflow
- `GET /api/workflow` — workflows from `workflow/workflows/`
- `GET /api/workflow/registries` — registry files

### MCP
- `GET /api/mcp` — MCP servers from `mcp/servers/`
- `POST /api/mcp/register` — register new server
- `GET /api/mcp/tools` — aggregated tool definitions

### GPU
- `GET /api/gpu` — GPU state (mock or nvidia-smi)
- `POST /api/gpu/scan` — rescan GPUs

### Permissions
- `GET /api/permissions` — roles, current role
- `POST /api/permissions/check` — check permission

### Sandbox
- `GET /api/sandbox` — sandbox config
- `POST /api/sandbox/run` — execute code (Python)

### Campaign
- `GET /api/campaign` — campaigns list
- `POST /api/campaign/create` — create campaign
- `POST /api/campaign/<id>/run` — run campaign
- `DELETE /api/campaign/<id>` — delete campaign

### Memory
- `GET /api/memory` — full memory state
- `GET /api/memory/preferences` — preferences
- `POST /api/memory/preferences` — update preferences
- `GET /api/memory/projects` — project list
- `POST /api/memory/projects` — add project
- `DELETE /api/memory/projects/<name>` — delete project
- `GET /api/memory/learnings` — learnings list
- `POST /api/memory/learnings` — add learning
- `GET /api/memory/stats` — memory stats

### Settings
- `GET /api/settings` — GPU settings
- `POST /api/settings` — update settings

### Presets
- `GET /api/presets` — builtin + custom presets
- `POST /api/presets` — create custom preset
- `DELETE /api/presets/<name>` — delete preset
- `POST /api/presets/<name>/apply` — apply preset

### Upload
- `POST /api/upload` — multipart file upload
- `GET /api/uploads` — upload list

### Clients
- `GET /api/clients` — merged client configs
