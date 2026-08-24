#!/usr/bin/env bash
set -u

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT"
mkdir -p logs

while true; do
  echo "[supervisor] Checking processes..."

  if ! pgrep -f "router/router.py" > /dev/null; then
    echo "[supervisor] Restarting router..."
    nohup python3 router/router.py >>logs/router.log 2>&1 &
  fi

  if ! pgrep -f "dashboard/backend.py" > /dev/null; then
    echo "[supervisor] Restarting dashboard..."
    nohup python3 dashboard/backend.py >>logs/dashboard.log 2>&1 &
  fi

  if ! pgrep -f "llama-server" > /dev/null; then
    echo "[supervisor] Restarting llama.cpp..."
    nohup bash llama/launch-llama.sh >>logs/llama.log 2>&1 &
  fi

  if ! pgrep -f "vllm.entrypoints" > /dev/null; then
    if [ "${VLLM_ENABLED:-false}" = "true" ]; then
      echo "[supervisor] Restarting vLLM..."
      nohup bash vllm/launch-vllm.sh >>logs/vllm.log 2>&1 &
    fi
  fi

  sleep 10
done
