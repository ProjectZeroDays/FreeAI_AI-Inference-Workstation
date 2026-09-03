# Intermediate Path — Workflows, Providers & SDLC

Build on your foundation with external AI providers, workflow pipelines, and autonomous agents.

## Step 1: Connect External Providers

```bash
# Add API keys to .env
export OPENAI_API_KEY=sk-...
export ANTHROPIC_API_KEY=sk-ant-...
export AGNES_API_KEY=sk-...

# Test routing to a specific provider
curl -X POST localhost:8010/route \
  -H "Content-Type: application/json" \
  -d '{"prompt":"Design a rate limiter","model":"openai/gpt-4o-mini"}'
```

## Step 2: Build a Workflow

Create a custom pipeline in `workflows/my-pipeline.json`:

```json
{
  "name": "my-pipeline",
  "steps": [
    {"name": "plan", "agent": "project", "input": "Build a REST API"},
    {"name": "test", "agent": "debug", "input": "Run tests and fix"},
    {"name": "package", "agent": "analyze", "input": "Package for deploy"}
  ]
}
```

Validate and run:
```bash
curl -X POST localhost:8040/workflow/validate -H "Content-Type: application/json" -d @workflows/my-pipeline.json
curl -X POST localhost:8040/workflow/run-inline -H "Content-Type: application/json" -d @workflows/my-pipeline.json
```

## Step 3: Run Autonomous SDLC

```bash
# One spec → complete project
python freeai.py auto-start "Build a FastAPI notes service with auth" --watch

# Check status
curl localhost:8050/auto/runs

# Download artifact
curl localhost:8050/auto/runs/<id>/artifact -o project.tar.gz
```

## Step 4: Configure GPU Inference

```bash
# Start llama.cpp with a model
LLAMA_CTX=8192 python3 launch.py --model qwen3.6-12b

# Check model status
curl localhost:9001/models
```

## Next

Continue to the [Advanced Path](advanced-path.md) for GPU tuning and custom integrations.
