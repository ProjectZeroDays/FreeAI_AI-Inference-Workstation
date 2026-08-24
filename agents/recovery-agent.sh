#!/usr/bin/env bash
set -u

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

while true; do
  if ! pgrep -f "router/router.py" > /dev/null; then
    echo "[recovery] Router down, restarting..."
    nohup python3 router/router.py >>logs/router.log 2>&1 &
  fi

  sleep 15
done
