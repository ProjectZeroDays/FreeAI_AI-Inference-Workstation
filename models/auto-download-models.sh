#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT"
mkdir -p models

download() {
  local url="$1" out="models/$2" min_bytes="${3:-1000000000}"
  if [ -f "$out" ] && [ "$(stat -c%s "$out" 2>/dev/null || echo 0)" -ge "$min_bytes" ]; then
    echo "[models] $2 already present, skipping."
    return 0
  fi
  echo "[models] Downloading $2 ..."
  wget -c -O "$out.part" "$url" && mv "$out.part" "$out"
}

download "https://huggingface.co/DavidAU/Qwen3.6-12B-IQ-Ultra-Heretic-Uncensored-Thinking/resolve/main/Qwen3.6-12B-IQ-Ultra-Heretic-Uncensored-Thinking-Q6_K.gguf" \
  "Qwen3.6-12B-IQ-Ultra-Heretic-Uncensored-Thinking-Q6_K.gguf" 5000000000

download "https://huggingface.co/DavidAU/L3.1-MOE-2X8B-Deepseek-DeepHermes-e32-uncensored-abliterated-13.7B-gguf/resolve/main/L3.1-MOE-2X8B-Deepseek-DeepHermes-e32-uncensored-abliterated-13.7B-Q6_K.gguf" \
  "L3.1-MOE-2X8B-Deepseek-DeepHermes-e32-uncensored-abliterated-13.7B-Q6_K.gguf" 5000000000

download "https://huggingface.co/DavidAU/Qwen3.5-9B-Claude-4.6-HighIQ-INSTRUCT-HERETIC-UNCENSORED/resolve/main/Qwen3.5-9B-Claude-4.6-HighIQ-INSTRUCT-HERETIC-UNCENSORED-Q6_K.gguf" \
  "Qwen3.5-9B-Claude-4.6-HighIQ-INSTRUCT-HERETIC-UNCENSORED-Q6_K.gguf" 4000000000

echo "[models] All models downloaded:"
ls -lh models/
