# MCP Server (ROADMAP 16)

`mcp/server.py` exposes FreeAI as an MCP server:

- `GET /health` -- health check (no auth required)
- `GET /mcp/tools` -- list tools
- `POST /mcp/call {"tool": "route", "args": {"prompt": "..."}}` -- proxy to `/route`, `/agent/*`, `/workflow`, `/auto`

Run: `python mcp/server.py` (port 8090) or `docker compose --profile mcp up`.

## Authentication

Set `MCP_API_KEY` environment variable to require authentication. When configured, all endpoints except `/health` require one of:
- `X-API-Key` header
- `X-Auth-Token` header  
- `Authorization: Bearer <token>` header

The MCP server forwards the authentication header to downstream services (router, agents, workflow, autonomous).

## Usage

Clients: OpenCode, Codex, or any MCP-compatible host can point at `http://localhost:8090` and get all FreeAI capabilities as tools. When `MCP_API_KEY` is set, clients must include the API key in request headers.
