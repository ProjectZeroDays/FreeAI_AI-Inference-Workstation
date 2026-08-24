#!/usr/bin/env bash
set -e

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT"

if [ ! -d venv ]; then
  echo "[start] venv missing — run ./install.sh first" >&2
  exit 1
fi

# shellcheck disable=SC1091
source venv/bin/activate
mkdir -p logs

echo "[start] Starting llama.cpp..."
bash llama/launch-llama.sh >>logs/llama.log 2>&1 &

echo "[start] Starting vLLM..."
bash vllm/launch-vllm.sh >>logs/vllm.log 2>&1 &

echo "[start] Starting router (:8010)..."
python3 router/router.py >>logs/router.log 2>&1 &

echo "[start] Starting agent API (:8020)..."
python3 -m uvicorn agents.api:app --host 0.0.0.0 --port 8020 >>logs/agents.log 2>&1 &

echo "[start] Starting workflow engine (:8040)..."
python3 -m uvicorn workflow.api:app --host 0.0.0.0 --port 8040 >>logs/workflow.log 2>&1 &

echo "[start] Starting dashboard (:8030)..."
python3 dashboard/backend.py >>logs/dashboard.log 2>&1 &

echo "[start] Starting desktop environment..."
bash desktop/start_xfce.sh >>logs/desktop.log 2>&1 &
bash desktop/start_vnc.sh >>logs/desktop.log 2>&1 &
bash desktop/start_novnc.sh >>logs/desktop.log 2>&1 &

echo "[start] Starting supervisor..."
bash supervisor.sh >>logs/supervisor.log 2>&1 &

echo "[start] Stack up. Logs in ./logs/"
