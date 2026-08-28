# FreeAI VSCode Extension

VSCode extension for the FreeAI AI-Inference-Workstation. Provides quick access to service health, prompt routing, agent listings, and log browsing directly from the editor.

## Features

| Command | Description |
|---------|-------------|
| `FreeAI: Show Service Status` | Opens a panel showing health of all FreeAI services (router, agents, dashboard, etc.) |
| `FreeAI: Route Prompt` | Sends a prompt through the FreeAI router and displays the response |
| `FreeAI: List Agents` | Shows all specialized agents and their model assignments |
| `FreeAI: Show Logs` | Retrieves and displays recent log entries from the FreeAI dashboard |

## Status Bar

A status bar item on the right shows live health dots for all connected services. Click it or run `FreeAI: Show Service Status` for details. The status auto-refreshes every 10 seconds (configurable).

## Configuration

Settings are under the `freeai` prefix in VSCode settings:

| Setting | Default | Description |
|---------|---------|-------------|
| `freeai.apiBaseUrl` | `http://localhost:8000` | Base URL for the FreeAI API |
| `freeai.refreshIntervalMs` | `10000` | Status bar health-check interval |

## API Endpoints Used

- `GET /health` — service health
- `POST /route` — route a prompt
- `GET /agents` — list agents
- `GET /logs` — fetch logs

## Development

```bash
cd vscode-extension
npm install
npm run compile
# Or watch mode:
npm run watch
```

Launch the extension with `F5` in VSCode (uses `.vscode/launch.json`).
