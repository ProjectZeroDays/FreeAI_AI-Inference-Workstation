# Provider Integration Guide

## Overview

FreeAI consolidates providers from 5 sources into a unified registry at `config/providers-merged.json`.

## Sources

| Source | File | Providers |
|---|---|---|
| mimocode | `mimocode/mimocode-providers.json` | Agnes AI, DeepSeek, local models |
| jcode | `mimocode/jcode-providers.json` | JCode-specific endpoints |
| opencode | `mimocode/opencode-providers.json` | OpenCode routing |
| openclaw | `mimocode/openclaw-providers.json` | OpenClaw bridge |
| hermes | `mimocode/hermes-providers.json` | Hermes agent providers |

## Provider Types

- **primary** — External API (OpenAI, Anthropic, Google, etc.)
- **local** — Local model serving (llama.cpp, vLLM)
- **internal** — Internal FreeAI services (router, agentrouter)
- **tool** — Tool-use providers (Aikido, Salad)
- **aggregator** — Multi-provider aggregators (OpenRouter)

## Environment Variables

Required keys (set in `.env`):

```
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
GOOGLE_API_KEY=AIza...
DEEPSEEK_API_KEY=sk-...
PERPLEXITY_API_KEY=llx-...
OPENROUTER_API_KEY=sk-or-...
SALAD_API_KEY=salad-...
AIKIDO_API_KEY=aikido-...
AIKIDO_APP_ID=...
HERMES_API_KEY=...
```

## Adding a New Provider

1. Add entry to `config/providers-merged.json`:
```json
"new_provider": {
  "type": "primary",
  "base_url": "https://api.example.com/v1",
  "models": ["model-1", "model-2"],
  "auth": "env:EXAMPLE_API_KEY"
}
```

2. Add env var to `.env.example`
3. Restart dashboard

## Sync Script

`scripts/sync_providers.py` reads all provider JSON files and outputs merged config:
```bash
python scripts/sync_providers.py
```
