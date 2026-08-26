# Model Switching Guide

## How it works

1. `classifier.classify_task(prompt)` returns a task type and a
   confidence score (keyword-hit based).
2. `switcher.select_chain(task, agent)` resolves an ordered fallback
   chain: primary → alternates. Per-agent overrides (config
   `router.model_overrides` or env `AGENT_MODEL_OVERRIDES` JSON like
   `{"debug": "moe-13b"}`) move a model to the front.
3. The router tries each candidate endpoint in order; first healthy
   response wins. If all fail → 502 with the last error.

## Current roster

| Task type | Primary | Fallbacks |
|---|---|---|
| full_project | qwen3.6-12b | moe-13b → qwen3.5-9b |
| refactor | moe-13b | qwen3.6-12b → qwen3.5-9b |
| analysis | qwen3.5-9b | qwen3.6-12b → moe-13b |
| general_code | qwen3.6-12b | moe-13b → qwen3.5-9b |

> llama.cpp serves one hot model per process; all three roster entries
> currently share the :9001 endpoint. Point entries at separate
> instances to get true parallel serving.

## Tuning

Edit `config/config.json` → `router.model_overrides`, or set:

```bash
export AGENT_MODEL_OVERRIDES='{"refactor": "qwen3.5-9b"}'
```
