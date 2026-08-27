#!/usr/bin/env bash
set -u

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

ROUTER_URL="${ROUTER_URL:-http://localhost:8010}"

while true; do
  echo "[health] Checking GPU..."
  nvidia-smi >/dev/null 2>&1 || echo "[health] GPU not responding"

  echo "[health] Checking router..."
  curl -sf "$ROUTER_URL/health" >/dev/null || echo "[health] router not responding"

  sleep 30
done
