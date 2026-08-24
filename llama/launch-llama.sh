#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PORT="${LLAMA_PORT:-9001}"
MODEL="${LLAMA_MODEL_PATH:-$ROOT/models/Qwen3.6-12B-IQ-Ultra-Heretic-Uncensored-Thinking-Q6_K.gguf}"

BIN="${LLAMA_SERVER_BIN:-$ROOT/llama.cpp/build/bin/llama-server}"
if [ ! -x "$BIN" ]; then
  BIN="$(command -v llama-server || true)"
fi
if [ -z "$BIN" ]; then
  echo "[llama] llama-server not found — run ./install.sh first" >&2
  exit 1
fi
if [ ! -f "$MODEL" ]; then
  echo "[llama] model missing: $MODEL — run bash models/auto-download-models.sh" >&2
  exit 1
fi

echo "[llama] Starting llama.cpp server on :$PORT"
exec "$BIN" \
  -m "$MODEL" \
  -c "${LLAMA_CTX:-4096}" \
  --host 0.0.0.0 \
  --port "$PORT" \
  --threads "$(nproc)" \
  -ngl "${N_GPU_LAYERS:-80}"
