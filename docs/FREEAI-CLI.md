# freeai-cli

The `freeai` CLI controls the FreeAI unified service stack from the terminal.

## Installation

The CLI lives at `scripts/freeai.py`. Add it to your PATH:

```bash
# Linux / macOS
export PATH="$PATH:$(pwd)/scripts"
# or add to ~/.bashrc / ~/.zshrc:
echo 'export PATH="$PATH:$(pwd)/ai-workstation/scripts"' >> ~/.bashrc

# Windows (PowerShell)
$env:PATH += ";$(Get-Location)\scripts"
# or add permanently:
[Environment]::SetEnvironmentVariable("PATH", $env:PATH + ";$(Get-Location)\scripts", "User")
```

A Windows `.cmd` wrapper is also provided at `scripts/freeai.cmd`.

## Commands

```bash
freeai status                # show all service health (ports from config/services.json)
freeai models                # list available models from /models endpoint
freeai route "<prompt>"      # send prompt to router and print response
freeai workflows             # list workflows from /workflows endpoint
freeai run <workflow_id>     # execute a workflow
freeai start                 # start all services via launch.py
freeai stop                  # stop all services
freeai logs <service> [-n N] # tail logs for a service (-n N: show last N lines)
```

## Route options

```bash
freeai route "Build a FastAPI app" --profile strict --max-tokens 2048
freeai route "Explain this bug" --task analysis
```

## Workflow options

```bash
freeai workflows
freeai run full_build --context "{\"spec\":\"Build a REST API\"}"
```

## Local dev mode (no GPU required)

Set `MOCK_LLM=1` to run the router and models commands without a running backend:

```bash
MOCK_LLM=1 freeai models          # shows canned model registry
MOCK_LLM=1 freeai route "hello"   # returns canned responses
```

## Environment variables

| Variable | Default | Description |
|---|---|---|
| `FREEAI_HOST` | `localhost` | Override the host for all API calls |
| `MOCK_LLM` | `0` | Set to `1` for local dev mode with canned responses |
