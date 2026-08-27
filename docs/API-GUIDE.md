# API Guide

## Authentication Methods

FreeAI supports three authentication methods:

| Method | Header | Description |
|---|---|---|
| API Key | `X-API-Key` | Set `ROUTER_API_KEY` in config, send key in header |
| JWT Token | `Authorization: Bearer <token>` | For agent and workflow APIs |
| Dashboard Token | `X-Auth-Token` | For dashboard write operations |

### Example: API Key Auth

```bash
curl -H "X-API-Key: your-key-here" http://localhost:8010/route \
  -H "Content-Type: application/json" \
  -d '{"prompt":"hello"}'
```

## Error Codes

| Code | Meaning | Description |
|---|---|---|
| 400 | Bad Request | Invalid request format or parameters |
| 401 | Unauthorized | Missing or invalid API key |
| 403 | Forbidden | Insufficient permissions |
| 404 | Not Found | Endpoint or resource not found |
| 429 | Rate Limited | Too many requests, token bucket empty |
| 500 | Internal Server Error | Server-side error |
| 502 | Bad Gateway | Backend service unavailable |

## Router API (:8010)

### GET /health
Check router health status.

**Response:**
```json
{"status": "ok"}
```

### GET /models
Get available models list.

**Response:**
```json
{
  "models": [
    {"name": "qwen/qwen3.6-12b", "status": "healthy", "type": "local"},
    {"name": "openai/gpt-4o", "status": "healthy", "type": "external"}
  ]
}
```

### POST /route
Route a prompt to the best available model.

**Request:**
```json
{
  "prompt": "Write a Python function",
  "model": "qwen/qwen3.6-12b",
  "stream": false,
  "max_tokens": 2048,
  "temperature": 0.7
}
```

**Response:**
```json
{
  "model_used": "qwen/qwen3.6-12b",
  "task_type": "coding",
  "confidence": 0.95,
  "elapsed_ms": 1234,
  "response": "Here is the Python function...",
  "cache": "MISS"
}
```

### GET /metrics
Get router metrics (requests, cache hits, errors, latency).

## Agent API (:8020)

### POST /agent/project
Create a new project agent.

**Request:**
```json
{
  "spec": "Build a FastAPI app with CRUD operations",
  "profile": "balanced",
  "session_id": "session-123"
}
```

### POST /agent/refactor
Refactor existing code.

**Request:**
```json
{
  "code": "def old_function():\n    pass",
  "language": "python",
  "goals": ["improve performance", "add type hints"]
}
```

### POST /agent/debug
Debug code with error.

**Request:**
```json
{
  "code": "print(1/0)",
  "error": "ZeroDivisionError: division by zero",
  "language": "python"
}
```

### POST /agent/chat
Multi-turn chat with session memory.

**Request:**
```json
{
  "message": "Tell me more about this",
  "session_id": "session-123"
}
```

### GET /profiles
Get available agent profiles.

**Response:**
```json
{
  "profiles": [
    {"name": "strict", "temperature": 0.0},
    {"name": "balanced", "temperature": 0.2},
    {"name": "creative", "temperature": 0.8}
  ]
}
```

## Dashboard API (:8030)

### GET /api/status
Get system status including GPU info and service health.

### GET /api/settings
Get current settings.

### POST /api/settings
Update settings (requires auth).

### GET /api/presets
Get available presets.

### POST /api/presets/{name}/apply
Apply a preset.

## Workflow Engine API (:8040)

### GET /workflows
List registered workflows.

### POST /workflow/run
Execute a workflow.

**Request:**
```json
{
  "workflow": "project_pipeline",
  "context": {"spec": "Build a REST API"},
  "strict_validation": true
}
```

### POST /workflow/validate
Validate workflow steps.

## Autonomous SDLC API (:8050)

### POST /auto/start
Start an autonomous SDLC run.

**Request:**
```json
{
  "spec": "Build a FastAPI notes service with tests",
  "profile": "balanced",
  "max_tasks": 10,
  "enable_shell": false
}
```

**Response:**
```json
{
  "run_id": "run-123",
  "status": "started"
}
```

### GET /auto/runs/{id}
Get run status.

### POST /auto/runs/{id}/cancel
Cancel a run.

### GET /auto/runs/{id}/artifact
Download artifact (tar.gz).

## MCP Server API (:8090)

### GET /health
Health check.

### GET /mcp/tools
List available tools.

### POST /mcp/call
Call a tool.

**Request:**
```json
{
  "tool": "route",
  "args": {"prompt": "Hello"}
}
```