# FreeAI Workspace — VSCode Extension

VSCode extension for controlling the FreeAI AI-Inference Workstation.

## Features

- **Service Status** — Real-time health monitoring with color-coded dots
  - Green (ok): service responding on health endpoint
  - Yellow (degraded): port open but health check failing
  - Red (down): port unreachable
- **Route Prompt** — Send prompts through the FreeAI router with streaming output
  - Shows model used, task type classification, latency, token count
  - SSE streaming for long responses
- **Start/Stop Services** — Manage all FreeAI services via `launch.py`
- **Debug Mode** — Toggle `MOCK_LLM=1` for local dev without GPU
  - View request/response logs
  - Inspect metrics, models, and providers
- **Service Tree View** — Explorer sidebar with per-service start/stop

## Commands

| Command | Description |
|---------|-------------|
| `FreeAI: Show Service Status` | Probe all services, open status panel |
| `FreeAI: Route Prompt` | Quick pick -> prompt -> streaming response |
| `FreeAI: Start Services` | Start all services via `launch.py` |
| `FreeAI: Stop Services` | Stop all services via `launch.py` |
| `FreeAI: Toggle Mock LLM` | Enable/disable MOCK_LLM mode |
| `FreeAI: View Debug Logs` | Open full request/response log |
| `FreeAI: Show Metrics` | View router metrics (JSON) |
| `FreeAI: Show Models` | List registered models |
| `FreeAI: Show Providers` | List provider configs |

## Configuration

Settings under `freeai.*`:

| Setting | Default | Description |
|---------|---------|-------------|
| `freeai.routerHost` | `http://localhost:8010` | Router base URL |
| `freeai.dashboardHost` | `http://localhost:8080` | Dashboard base URL |
| `freeai.workstationRoot` | (auto) | Path to FreeAI repo root |
| `freeai.refreshIntervalMs` | `10000` | Health check interval |
| `freeai.autoStart` | `false` | Auto-start services on workspace open |
| `freeai.debugMode` | `false` | Enable mock LLM at startup |

## Installation

1. Open the extension folder in VSCode: `.vscode/extension/`
2. Run `npm install` in the extension folder
3. Run `npm run compile` to build
4. Press `F5` to launch extension host

## Service Ports

Key services from `config/services.json`:

| Service | Port | Description |
|---------|------|-------------|
| router | 8010 | Main LLM router -- `/route`, `/models`, `/metrics` |
| dashboard | 8080 | Web UI (15+ pages) |
| proxy | 8100 | Unified LLM proxy |
| agents | 8120 | 7 specialized agents |
| brain | 8150 | Three-tier router |
| autonomous | 8050 | Autonomous SDLC agent |
| browser | 8180 | Knight-Shade headless browser |

Full service registry: `config/services.json`

## Project

- Repo: `ProjectZeroDays/FreeAI_AI-Inference-Workstation`
- Dashboard: `http://localhost:8080`
- Router API: `http://localhost:8010`
