# Beginner Path — First Steps with FreeAI

Follow this path to get your first model running and chat with an agent in under 10 minutes.

## Step 1: Install

```bash
git clone https://github.com/ProjectZeroDays/FreeAI_AI_Inference_Workstation.git
cd FreeAI_AI_Inference_Workstation
docker compose --profile allinone up -d
```

## Step 2: Run Your First Model

```bash
# Dev mode (no GPU required)
MOCK_LLM=1 python3 router/router.py

# Or with a real model
curl -X POST localhost:8010/route \
  -H "Content-Type: application/json" \
  -d '{"prompt":"Hello, what can you do?"}'
```

## Step 3: Explore the Dashboard

Open http://localhost:8030 to see:
- GPU utilization and model status
- Active agents and their tasks
- Service health indicators
- Settings and presets

## Step 4: Chat with an Agent

```bash
# Use the agent API directly
curl -X POST localhost:8020/agent/chat \
  -H "Content-Type: application/json" \
  -d '{"message":"Explain how the router works","session_id":"s1"}'
```

## Step 5: Run a Workflow

```bash
# List available workflows
curl localhost:8040/workflows

# Run the full_build template
curl -X POST localhost:8040/workflow/run \
  -H "Content-Type: application/json" \
  -d '{"workflow": "full_build", "context": {"spec": "Build a todo API"}}'
```

## Next

Continue to the [Intermediate Path](intermediate-path.md) when you're ready for workflows and external providers.
