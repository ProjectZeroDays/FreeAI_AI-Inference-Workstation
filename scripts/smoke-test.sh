#!/usr/bin/env bash
# Live endpoint sweep against a running stack.
# Success prints ALL_SYSTEMS_OPERATIONAL.
#   bash scripts/smoke-test.sh [BASE_HOST]   (default http://localhost)
set -euo pipefail

BASE="${1:-http://localhost}"
ROUTER="${ROUTER_URL:-$BASE:8010}"
AGENTS="${AGENT_API:-$BASE:8120}"
DASH="${DASH_API:-$BASE:8030}"
WORKFLOW="${WORKFLOW_API:-$BASE:8040}"
AUTON="${AUTONOMOUS_API:-$BASE:8050}"

auth=(); [ -n "${ROUTER_API_KEY:-}" ] && auth=(-H "X-API-Key: $ROUTER_API_KEY")

fail=0
check() { # name url
  local name="$1" url="$2"
  if curl -sf -o /dev/null --max-time 10 "${auth[@]+"${auth[@]}"}" "$url"; then
    echo "PASS  $name ($url)"
  else
    echo "FAIL  $name ($url)"; fail=1
  fi
}

check router-health      "$ROUTER/health"
check router-models      "$ROUTER/models"
check agents-health      "$AGENTS/health"
check agents-profiles    "$AGENTS/profiles"
check dashboard-status   "$DASH/api/status"
check dashboard-settings "$DASH/api/settings"
check dashboard-presets  "$DASH/api/presets"
check workflow-health    "$WORKFLOW/health"
check workflow-list      "$WORKFLOW/workflows"
check autonomous-health  "$AUTON/health"
check autonomous-runs    "$AUTON/auto/runs"

# live inference round-trip (mock or real)
if resp=$(curl -sf --max-time 120 -X POST "$ROUTER/route" \
    -H "Content-Type: application/json" "${auth[@]+"${auth[@]}"}" \
    -d '{"prompt":"Build a production smoke test service","max_tokens":32}'); then
  task=$(printf '%s' "$resp" | sed -n 's/.*"task_type"[[:space:]]*:[[:space:]]*"\([^"]*\)".*/\1/p')
  model=$(printf '%s' "$resp" | sed -n 's/.*"model_used"[[:space:]]*:[[:space:]]*"\([^"]*\)".*/\1/p')
  echo "PASS  router /route round-trip (${task:-?} via ${model:-?})"
else
  echo "FAIL  router /route round-trip"; fail=1
fi

echo
if [ "$fail" -eq 0 ]; then
  echo "ALL_SYSTEMS_OPERATIONAL"
else
  echo "SMOKE_TEST_FAILURES - see FAIL lines above"
  exit 1
fi
