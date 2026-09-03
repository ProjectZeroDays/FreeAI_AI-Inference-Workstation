# Router Basics — How FreeAI Routes Prompts

This guide explains how the FreeAI model router works and how to use it effectively.

## How It Works

```
User Prompt → Classifier → Confidence Score → Best Backend → Fallback Chain → Response
                    │
              Task Type:
              - full_project
              - refactor
              - analysis
              - general_code
```

## Quick Commands

```bash
# Check router health
curl localhost:8010/health

# View available models
curl localhost:8010/models

# Route a prompt
curl -X POST localhost:8010/route \
  -H "Content-Type: application/json" \
  -d '{"prompt":"Design a rate limiter"}'

# View metrics
curl localhost:8010/metrics
```

### Copy-Paste Examples

```bash
# Route with explicit model
curl -X POST localhost:8010/route \
  -H "Content-Type: application/json" \
  -d '{"prompt":"Explain dependency injection","model":"qwen3.6-12b"}'

# Stream a response (SSE)
curl -N -X POST localhost:8010/route/stream \
  -H "Content-Type: application/json" \
  -d '{"prompt":"Write a Python function"}'

# WebSocket streaming
ws://localhost:8011/ws/route
```

## Response Format

```json
{
  "model_used": "openai/gpt-4o-mini",
  "task_type": "general_code",
  "confidence": 0.87,
  "elapsed_ms": 342,
  "response": "...",
  "x-cache": "MISS"
}
```

## Fallback Chains

When the primary backend fails, the router automatically tries the next in line:

```
Primary (local llama.cpp) → Fallback 1 (Venice) → Fallback 2 (OpenRouter) → Fallback 3 (Agnes AI)
```

Set fallback providers in `config/providers.json`:

```json
{
  "openai/gpt-4o": {
    "primary": true,
    "fallback": false
  },
  "openrouter/any": {
    "primary": false,
    "fallback": true
  }
}
```

## Rate Limiting

The router enforces per-IP rate limits:
- Default: 60 requests per minute
- Configurable via `RATE_LIMIT_CAPACITY` and `RATE_LIMIT_REFILL_PER_MIN`

## Authentication

Optionally protect the router with an API key:

```bash
export ROUTER_API_KEY=your-secret-key
curl -X POST localhost:8010/route \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-secret-key" \
  -d '{"prompt":"Hello"}'
```

## Next Steps

- [External Providers](PROVIDER-INTEGRATION.md) — Connect OpenAI, Anthropic, etc.
- [Model Switching](MODEL-SWITCHING.md) — Configure per-prompt model selection
- [API Reference](API.md) — Complete endpoint documentation
