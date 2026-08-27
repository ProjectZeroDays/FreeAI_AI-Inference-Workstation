#!/usr/bin/env bash
# Bare-metal vLLM installer (isolated venv, does not touch stack venv).
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
VENV="$ROOT/.venv-vllm"
PY="${PYTHON:-python3}"

echo "[vllm] creating venv at $VENV"
[ -d "$VENV" ] || "$PY" -m venv "$VENV"
# shellcheck disable=SC1091
source "$VENV/bin/activate"
pip install --upgrade pip

echo "[vllm] installing vLLM (pulls CUDA-enabled torch wheels)..."
pip install --no-cache-dir -U vllm

cat <<EOF

[vllm] installed. Run the backend with:
  source $VENV/bin/activate
  VLLM_ENABLED=true bash $ROOT/vllm/launch-vllm.sh

Or via docker compose instead:
  docker compose --profile vllm up -d
EOF
