#!/usr/bin/env bash
# Run both watchdog loops under one systemd service.
set -u

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"
mkdir -p logs

bash agents/health-agent.sh   >>logs/health-agent.log 2>&1 &
HEALTH_PID=$!
bash agents/recovery-agent.sh >>logs/recovery-agent.log 2>&1 &
RECOVERY_PID=$!

trap 'kill "$HEALTH_PID" "$RECOVERY_PID" 2>/dev/null' TERM INT
wait -n "$HEALTH_PID" "$RECOVERY_PID"
exit_code=$?
kill "$HEALTH_PID" "$RECOVERY_PID" 2>/dev/null || true
exit "$exit_code"
