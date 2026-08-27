#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

# prefer the dedicated vLLM venv when present (vllm/install-vllm.sh)
if [ -x "$ROOT/.venv-vllm/bin/python" ]; then
  PY="$ROOT/.venv-vllm/bin/python"
else
  PY="python3"
fi

PORT="${VLLM_PORT:-9002}"
MODEL="${VLLM_MODEL:-Qwen/Qwen2.5-7B-Instruct}"
EXTRA_ARGS=""
[ "${VLLM_PREFIX_CACHING:-true}" = "true" ] && EXTRA_ARGS="--enable-prefix-caching"

echo "[vllm] Starting vLLM on :$PORT (model: $MODEL)"
exec "$PY" -m vllm.entrypoints.openai.api_server \
  --host 0.0.0.0 \
  --port "$PORT" \
  --model "$MODEL" \
  $EXTRA_ARGS
