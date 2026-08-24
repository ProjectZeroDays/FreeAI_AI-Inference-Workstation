#!/usr/bin/env bash
set -euo pipefail

ROUTER_URL="${ROUTER_URL:-http://localhost:8010}"

echo "[gpu-warmup] Running warmup prompt..."
curl -s -X POST "$ROUTER_URL/route" \
  -H "Content-Type: application/json" \
  -d '{"prompt":"Warm up GPU with a short completion.","max_tokens":32}' \
  | head -c 400

echo
echo "[gpu-warmup] Done."
