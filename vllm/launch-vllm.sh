#!/usr/bin/env bash
set -euo pipefail

PORT="${VLLM_PORT:-9002}"
MODEL="${VLLM_MODEL:-Qwen/Qwen2.5-7B-Instruct}"

echo "[vllm] Starting vLLM on :$PORT (model: $MODEL)"
exec python3 -m vllm.entrypoints.openai.api_server \
  --host 0.0.0.0 \
  --port "$PORT" \
  --model "$MODEL"
