# Build Workflows — Pipeline Designer Guide

Learn how to create, validate, and run workflow pipelines in FreeAI.

## What Are Workflows?

Workflows are predefined pipelines that chain multiple agent tasks together. Each step can:
- Call an agent endpoint
- Run a shell command
- Wait for a condition
- Branch based on output

## Quick Start

```bash
# List available workflows
curl localhost:8040/workflows

# Run a workflow
curl -X POST localhost:8040/workflow/run \
  -H "Content-Type: application/json" \
  -d '{"workflow": "full_build", "context": {"spec": "Build a FastAPI app"}}'
```

### Copy-Paste Examples

```bash
# Create a custom workflow
cat > my-workflow.json << 'EOF'
{
  "name": "full-build-pipeline",
  "steps": [
    {"name": "plan", "agent": "project", "input": "Build a REST API"},
    {"name": "code", "agent": "builder", "input": "Write the implementation"},
    {"name": "test", "agent": "debug", "input": "Run tests and fix failures"},
    {"name": "package", "agent": "analyze", "input": "Package for deployment"}
  ]
}
EOF

# Validate before running
curl -X POST localhost:8040/workflow/validate \
  -H "Content-Type: application/json" \
  -d @my-workflow.json

# Run it
curl -X POST localhost:8040/workflow/run-inline \
  -H "Content-Type: application/json" \
  -d @my-workflow.json
```

## Built-in Templates

| Template | Purpose |
|---|---|
| `full_build` | Complete project build with tests |
| `api_build` | API endpoint generation |
| `microservice_build` | Microservice scaffold |
| `security_scan` | Multi-tool security scan |

## Creating a Custom Workflow

Workflows are defined as JSON:

```json
{
  "name": "my-pipeline",
  "steps": [
    {
      "name": "plan",
      "agent": "project",
      "input": "Build a REST API"
    },
    {
      "name": "test",
      "agent": "debug",
      "input": "Run tests and fix failures"
    },
    {
      "name": "package",
      "agent": "analyze",
      "input": "Package for deployment"
    }
  ]
}
```

Validate before running:

```bash
curl -X POST localhost:8040/workflow/validate \
  -H "Content-Type: application/json" \
  -d @workflow.json
```

## Export / Import

```bash
# Export a workflow
curl localhost:8040/workflow/export/full_build > my-workflow.json

# Run inline definition
curl -X POST localhost:8040/workflow/run-inline \
  -H "Content-Type: application/json" \
  -d @my-workflow.json
```

## Dashboard

Access the visual workflow designer at `http://localhost:8030/workflows`.

## Next Steps

- [SDLC Agents](../AUTONOMOUS-AGENTS.md) — Autonomous project generation
- [API Reference](../API.md) — Complete workflow API docs
