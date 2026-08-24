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
# --jinja activates the GGUF's embedded chat template; Qwen3/DeepSeek
# reasoning models degrade into tag-soup/repetition loops without it.
# Server-side sampling guards below are the anti-repetition backstop;
# clients (agent profiles) still send their own temperature.
# Pass extra flags via LLAMA_EXTRA_ARGS (e.g. draft model for spec dec).
exec "$BIN" \
  -m "$MODEL" \
  --jinja \
  -c "${LLAMA_CTX:-4096}" \
  --host 0.0.0.0 \
  --port "$PORT" \
  --threads "$(nproc)" \
  -ngl "${N_GPU_LAYERS:-80}" \
  --repeat-penalty "${REPEAT_PENALTY:-1.05}" \
  --repeat-last-n "${REPEAT_LAST_N:-64}" \
  ${LLAMA_EXTRA_ARGS:-}
