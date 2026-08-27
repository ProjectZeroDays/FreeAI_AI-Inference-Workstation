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
  # disk preflight: require model size + 10GB headroom
  local need_gb=$(( min_bytes / 1000000000 + 10 ))
  local free_gb
  free_gb=$(df -BG --output=avail models 2>/dev/null | tail -n1 | tr -dc '0-9')
  if [ -n "$free_gb" ] && [ "$free_gb" -lt "$need_gb" ]; then
    echo "[models] ABORT: only ${free_gb}GB free, need ~${need_gb}GB for $2"
    return 1
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

# Vision projector (llmv port) - small BF16 mmproj for Qwen3.5-9B
if [ "${DOWNLOAD_VISION:-1}" = "1" ]; then
  download "https://huggingface.co/HauhauCS/Qwen3.5-9B-Uncensored-HauhauCS-Aggressive/resolve/main/mmproj-Qwen3.5-9B-Uncensored-HauhauCS-Aggressive-BF16.gguf" \
    "mmproj-Qwen3.5-9B-Uncensored-HauhauCS-Aggressive-BF16.gguf" 100000000
fi

# Qwythos-9B Claude-Mythos 1M (empero-ai) - reasoning specialist:
# Claude-trace post-train of Qwen3.5-9B, 1M ctx, function calling,
# +34 MMLU vs base. Reasoning model -> temp floor 0.6 (router clamps).
download "https://huggingface.co/empero-ai/Qwythos-9B-Claude-Mythos-5-1M-GGUF/resolve/main/Qwythos-9B-Claude-Mythos-5-1M-Q4_K_M.gguf" \
  "Qwythos-9B-Claude-Mythos-5-1M-Q4_K_M.gguf" 5000000000

# Optional MTP variant for speculative decoding (--spec-type draft-mtp):
# DOWNLOAD_MTP=1 bash models/auto-download-models.sh
if [ "${DOWNLOAD_MTP:-0}" = "1" ]; then
  download "https://huggingface.co/empero-ai/Qwythos-9B-Claude-Mythos-5-1M-GGUF/resolve/main/Qwythos-9B-Claude-Mythos-5-1M-MTP-Q4_K_M.gguf" \
    "Qwythos-9B-Claude-Mythos-5-1M-MTP-Q4_K_M.gguf" 5000000000
fi

# ---- empero-ai roster expansion (v2 + specialists) ----

# Qwythos-9B-v2: looping FIXED at model level (FTPO), 1M ctx, MTP, own mmproj
download "https://huggingface.co/empero-ai/Qwythos-9B-v2-GGUF/resolve/main/Qwythos-9B-v2-Q4_K_M.gguf" \
  "Qwythos-9B-v2-Q4_K_M.gguf" 5000000000
if [ "${DOWNLOAD_VISION:-1}" = "1" ]; then
  download "https://huggingface.co/empero-ai/Qwythos-9B-v2-GGUF/resolve/main/mmproj-Qwythos-9B-v2-BF16.gguf" \
    "mmproj-Qwythos-9B-v2-BF16.gguf" 500000000
fi

# CodeClawd: Qwen3.5-9B SFT on Claude Code + Codex agent traces
download "https://huggingface.co/empero-ai/Qwen3.5-9B-Claude-Code-GGUF/resolve/main/Qwen3.5-9B-Claude-Code-Q4_K_M.gguf" \
  "Qwen3.5-9B-Claude-Code-Q4_K_M.gguf" 5000000000

# Qwable: Claude Fable 5 + GPT-5.5 terminal-agent distill (multimodal)
download "https://huggingface.co/empero-ai/Qwable-9B-Claude-Fable-5-GGUF/resolve/main/Qwable-9B-Claude-Fable-5-Q4_K_M.gguf" \
  "Qwable-9B-Claude-Fable-5-Q4_K_M.gguf" 5000000000
if [ "${DOWNLOAD_VISION:-1}" = "1" ]; then
  download "https://huggingface.co/empero-ai/Qwable-9B-Claude-Fable-5-GGUF/resolve/main/mmproj-Qwable-9B-Claude-Fable-5-f16.gguf" \
    "mmproj-Qwable-9B-Claude-Fable-5-f16.gguf" 500000000
fi

# THINKING variant of the legacy HighIQ Heretic (imatrix quants by mradermacher)
download "https://huggingface.co/mradermacher/Qwen3.5-9B-Claude-4.6-HighIQ-THINKING-HERETIC-UNCENSORED-i1-GGUF/resolve/main/Qwen3.5-9B-Claude-4.6-HighIQ-THINKING-HERETIC-UNCENSORED.i1-Q4_K_M.gguf" \
  "Qwen3.5-9B-Claude-4.6-HighIQ-THINKING-HERETIC-UNCENSORED.i1-Q4_K_M.gguf" 5000000000

echo "[models] All models downloaded:"
ls -lh models/
