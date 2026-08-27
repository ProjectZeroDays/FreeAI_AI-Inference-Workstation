#!/usr/bin/env bash
# Convert a HuggingFace safetensors repo (e.g. empero-ai/openNemo-9B-*)
# to GGUF using the llama.cpp checkout from ./install.sh, then quantize.
#
# Nemotron-H note: openNemo uses a hybrid Mamba2 + sparse-attention arch;
# conversion needs a recent llama.cpp (fresh installs qualify).
#
# Usage:
#   bash scripts/convert-hf.sh empero-ai/openNemo-9B-abliterated [Q4_K_M]
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
REPO_ID="${1:?usage: convert-hf.sh <hf-repo-id> [QUANT]}"
QUANT="${2:-Q4_K_M}"
OUT_DIR="$ROOT/models"
LLAMA_DIR="$ROOT/llama.cpp"
NAME="$(basename "$REPO_ID")"

command -v python3 >/dev/null || { echo "python3 required"; exit 1; }
[ -d "$LLAMA_DIR/.git" ] || { echo "run ./install.sh first (llama.cpp checkout)"; exit 1; }

mkdir -p "$OUT_DIR/$NAME-hf"
echo "[convert] downloading $REPO_ID (safetensors)..."
python3 - "$REPO_ID" "$OUT_DIR/$NAME-hf" <<'EOF'
import sys
from huggingface_hub import snapshot_download
snapshot_download(sys.argv[1], local_dir=sys.argv[2],
                  allow_patterns=["*.safetensors", "*.json", "*.txt"])
EOF

echo "[convert] converting to f16 GGUF..."
python3 "$LLAMA_DIR/convert_hf_to_gguf.py" \
  "$OUT_DIR/$NAME-hf" --outfile "$OUT_DIR/$NAME-f16.gguf"

echo "[convert] quantizing to $QUANT..."
"$LLAMA_DIR/build/bin/llama-quantize" \
  "$OUT_DIR/$NAME-f16.gguf" "$OUT_DIR/$NAME-$QUANT.gguf" "$QUANT"

rm -f "$OUT_DIR/$NAME-f16.gguf"
rm -rf "$OUT_DIR/$NAME-hf"
echo "[convert] done: models/$NAME-$QUANT.gguf"
echo "[convert] add a registry entry pointing at it, then restart llama."
