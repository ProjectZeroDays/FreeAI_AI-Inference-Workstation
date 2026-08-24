#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

if [ -f venv/bin/activate ]; then
  # shellcheck disable=SC1091
  source venv/bin/activate
fi

exec python3 -m uvicorn autonomous.api:app --host 0.0.0.0 --port "${AUTONOMOUS_PORT:-8050}"
