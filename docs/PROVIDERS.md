# External AI Providers — Connect Any Hosted Model

The FreeAI Router bridges **21+ hosted AI APIs** into the same
routing, caching, metrics, and fallback fabric as your local GGUFs.
Three wire styles cover effectively every host on the market:

| Style | Wire format | Providers |
|---|---|---|
| `openai` | `POST {base}/chat/completions` | OpenAI, Groq, Mistral, DeepSeek, Together, Fireworks, OpenRouter, xAI, Perplexity, Cerebras, SambaNova, Cohere (compat), Novita, DeepInfra, Hyperbolic, HuggingFace router, local Ollama, LM Studio, any vLLM |
| `anthropic` | `POST {base}/v1/messages` | Anthropic (Claude) |
| `gemini` | `POST {base}/models/{model}:generateContent` | Google Gemini |

## Quick start (60 seconds)

```bash
# 1. export keys for the providers you have
export OPENAI_API_KEY=sk-...
export ANTHROPIC_API_KEY=sk-ant-...
export GROQ_API_KEY=gsk_...

# 2. (optional) copy + tweak the provider config
cp config/providers.example.json config/providers.json

# 3. restart the router - provider models appear automatically
curl -s localhost:8010/models | jq 'keys'

# 4. route explicitly to any external model
curl -X POST localhost:8010/route -H "Content-Type: application/json" \
  -d '{"prompt":"Design a rate limiter","model":"openai/gpt-4o-mini"}'
```

Response shape is identical to local routing (`model_used`,
`task_type`, `elapsed_ms`, `response.content`) — clients cannot tell
the difference. External calls bypass the cache (`X-Cache: PASS`).

## Provider matrix

| Provider | Env var | Example models | Notes |
|---|---|---|---|
| **OpenAI** | `OPENAI_API_KEY` | `openai/gpt-4o`, `openai/gpt-4o-mini`, `openai/o3-mini` | also works with Azure via custom entry |
| **Anthropic** | `ANTHROPIC_API_KEY` | `anthropic/claude-sonnet-4-5`, `anthropic/claude-opus-4-1` | native messages API |
| **Google Gemini** | `GOOGLE_API_KEY` | `google/gemini-2.5-pro`, `google/gemini-2.5-flash` | native generateContent |
| **Groq** | `GROQ_API_KEY` | `groq/llama-3.3-70b-versatile` | fastest LPU tokens/sec |
| **Mistral** | `MISTRAL_API_KEY` | `mistral/mistral-large-latest`, `mistral/codestral-latest` | Codestral = code-specialized |
| **DeepSeek** | `DEEPSEEK_API_KEY` | `deepseek/deepseek-chat`, `deepseek/deepseek-reasoner` | R1 reasoning, cheap |
| **Together** | `TOGETHER_API_KEY` | `together/Qwen/Qwen2.5-Coder-32B-Instruct` | huge open-model catalog |
| **Fireworks** | `FIREWORKS_API_KEY` | `fireworks/accounts/fireworks/models/qwen2p5-coder-32b-instruct` | production-grade serving |
| **OpenRouter** | `OPENROUTER_API_KEY` | `openrouter/<any-slug>` | 400+ models behind one key |
| **xAI** | `XAI_API_KEY` | `xai/grok-4`, `xai/grok-3-mini` | Grok family |
| **Perplexity** | `PERPLEXITY_API_KEY` | `perplexity/sonar-pro`, `perplexity/sonar-reasoning` | online/search-grounded |
| **Cerebras** | `CEREBRAS_API_KEY` | `cerebras/llama-3.3-70b` | wafer-scale speed |
| **SambaNova** | `SAMBANOVA_API_KEY` | `sambanova/Meta-Llama-3.3-70B-Instruct` | RDU speed |
| **Cohere** | `COHERE_API_KEY` | `cohere/command-r-plus` | OpenAI-compat endpoint |
| **Novita** | `NOVITA_API_KEY` | `novita/qwen/qwen-2.5-coder-32b-instruct` | budget open models |
| **DeepInfra** | `DEEPINFRA_API_KEY` | `deepinfra/meta-llama/Llama-3.3-70B-Instruct` | budget open models |
| **Hyperbolic** | `HYPERBOLIC_API_KEY` | `hyperbolic/meta-llama/Llama-3.3-70B-Instruct` | |
| **HuggingFace** | `HF_TOKEN` | `huggingface/Qwen/Qwen2.5-Coder-32B-Instruct` | Inference router |
| **Ollama (local)** | none | `ollama/qwen2.5-coder` | localhost:11434 |
| **LM Studio (local)** | none | `lmstudio/local-model` | localhost:1234 |
| **FreeToken (local)** | none | `freetoken/deepseek-ai/DeepSeek-V4-Flash` | localhost:9100 — 290B+ MoE on consumer GPUs, auto-fallback when healthy |
| **Your vLLM** | none | custom entry | point base_url at :9002/v1 |

## Configuration

`config/providers.json` (copy from `providers.example.json`) merges over
built-in presets. Keys **always come from the environment** — never put
secrets in this file.

```json
{
  "providers": {
    "openai":     { "enabled": true, "fallback": false },
    "groq":       { "enabled": true, "fallback": true },
    "openrouter": { "enabled": true, "fallback": true },
    "azure-gpt4o": {
      "style": "openai",
      "base_url": "https://YOUR-RESOURCE.openai.azure.com/openai/deployments/gpt4o",
      "api_key": "ONLY-IF-YOU-MUST",
      "key_env": "AZURE_OPENAI_KEY",
      "models": ["gpt-4o"],
      "fallback": false
    },
    "my-vllm": {
      "style": "openai",
      "base_url": "http://10.0.0.5:9002/v1",
      "models": ["Qwen/Qwen2.5-7B-Instruct"],
      "fallback": true
    }
  }
}
```

Per-provider keys: `enabled` (default true) · `fallback` (append to
every local chain as last-resort, after all GGUFs) · `style` ·
`base_url` · `key_env` · `models[]` · `description`.

## Fallback semantics

With `fallback: true` on keyed providers, the chain for **every**
request becomes: local primary → local alternates → keyed external
providers (config order). If the GPU is OOM/down, hosted models take
over automatically — and the dashboard's optimizer keeps burning zero
local watts while they do.

## Streaming

| Style | Streaming |
|---|---|
| openai-style | true SSE passthrough (token deltas) |
| anthropic / gemini | single-frame emit (full text in one `data:` frame) |

```bash
curl -N -X POST localhost:8010/route -H "Content-Type: application/json" \
  -d '{"prompt":"Write a haiku about GPUs","model":"openai/gpt-4o-mini","stream":true}'
```


## FreeToken Local Setup (step-by-step)

FreeToken is keyless and auto-fallbacks when healthy.

**Option A - Docker (compose users):**
```bash
docker compose --profile freetoken up -d
curl -s http://localhost:9100/v1/models | jq
```

**Option B - Native (desktop app or CLI):**
```bash
# Desktop app: https://www.flashml.ai/
# CLI:
uv pip install "freetoken[accel]"
freetoken serve --model deepseek-ai/DeepSeek-V4-Flash --port 9100
```

**Models:** deepseek-ai/DeepSeek-V4-Flash (default), Qwen/Qwen3.6-35B-A3B, zai-org/GLM-5.2 - set via FREETOKEN_MODEL env.

**Router wiring (automatic):**
- Preset base_url http://localhost:9100/v1 (compose override: http://freetoken:9100/v1 via FREETOKEN_BASE_URL).
- auto_fallback_when_healthy true - every local chain appends freetoken/<model> when health probe passes; cached 30s.
- Explicit routing: model "freetoken/deepseek-ai/DeepSeek-V4-Flash"

**Verify:**
```bash
curl -s http://localhost:8010/models | jq "keys | map(select(startswith("freetoken/")))"
curl -X POST http://localhost:8010/route -H "Content-Type: application/json" -d "{"prompt":"haiku","model":"freetoken/deepseek-ai/DeepSeek-V4-Flash"}" | jq .response.content
```

## Dashboard & CLI

- Dashboard → **External AI Providers** panel: keyed/no-key badges,
  fallback flags, per-provider **Test** button (live `pong` ping with
  latency).
- CLI: `freeai.py providers` and `freeai.py provider-test groq`.

## Security & cost guardrails

- Keys live in env only (`.env`, systemd `Environment=`, or your shell)
  — `providers.json` is safe to commit.
- External calls skip the cache and are metered in `/metrics`
  (`by_model` uses `provider/model` ids) — watch it for spend spikes.
- Cap spend with `max_tokens` per call (agents default 2048-4096) and
  provider-side hard limits.
- `X-Cache: PASS` header marks external responses so log scrapers can
  attribute cost.

## Troubleshooting

| Symptom | Fix |
|---|---|
| Provider shows NO KEY | export its env var, restart router |
| 401 from provider | key invalid/expired; `freeai.py provider-test <name>` |
| model not found | provider model id mismatch — check provider docs, use exact slug |
| slow first call | cold-start on host side; router timeout default 300s |
| want local-only | set `"enabled": false` per provider or delete from providers.json |
