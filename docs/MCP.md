# MCP Server (ROADMAP 16)

`mcp/server.py` exposes FreeAI as an MCP server:

- `GET /mcp/tools` -- list tools
- `POST /mcp/call {"tool": "route", "args": {"prompt": "..."}}` -- proxy to `/route`, `/agent/*`, `/workflow`, `/auto`

Run: `python mcp/server.py` (port 8090) or `docker compose --profile mcp up`.

Clients: OpenCode, Codex, or any MCP-compatible host can point at `http://localhost:8090` and get all FreeAI capabilities as tools.
