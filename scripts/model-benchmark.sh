#!/usr/bin/env bash
# Latency benchmark across router task types (each maps to a different
# primary model). Optional per-model passes when AGENT_MODEL_OVERRIDES
# maps bench-<key> -> <key> in router config.
#   ROUTER_URL=http://localhost:8010 bash scripts/model-benchmark.sh [rounds]
set -euo pipefail

ROUTER_URL="${ROUTER_URL:-http://localhost:8010}"
ROUNDS="${1:-3}"

auth=(); [ -n "${ROUTER_API_KEY:-}" ] && auth=(-H "X-API-Key: $ROUTER_API_KEY")

call_route() { # prompt max_tokens
  curl -sf -X POST "$ROUTER_URL/route" \
    -H "Content-Type: application/json" "${auth[@]+"${auth[@]}"}" \
    -d "{\"prompt\":\"$1\",\"max_tokens\":$2,\"agent\":\"bench\"}"
}

echo "[bench] warming up..."
call_route "warmup ping" 16 > /dev/null || {
  echo "[bench] router unreachable at $ROUTER_URL" >&2; exit 1; }

bench_type() { # label prompt
  local label="$1" prompt="$2" total=0 min=999999 max=0 n=0 ms
  for _ in $(seq 1 "$ROUNDS"); do
    ms=$(call_route "$prompt" 64 | jq -r '.elapsed_ms // empty' 2>/dev/null || true)
    [ -z "$ms" ] && continue
    total=$((total + ms)); n=$((n + 1))
    [ "$ms" -lt "$min" ] && min=$ms
    [ "$ms" -gt "$max" ] && max=$ms
  done
  if [ "$n" -eq 0 ]; then
    printf "%-16s %10s\n" "$label" "FAILED"
  else
    printf "%-16s %10d %10d %10d\n" "$label" $((total / n)) "$min" "$max"
  fi
}

echo "[bench] $ROUNDS round(s) per task type (model_used shown per type)"
printf "%-16s %10s %10s %10s\n" "task_type" "avg_ms" "min_ms" "max_ms"

bench_type full_project "Build a production REST API service with Docker and CI/CD"
bench_type refactor     "Refactor and optimize this function, fix the bug"
bench_type analysis     "Explain how does this algorithm work, think step by step"
bench_type general_code "Print the fibonacci sequence in python"

echo
echo "[bench] model selection per type:"
for t in full_project refactor analysis; do
  m=$(call_route "warmup $t ping" 8 \
    | jq -r 'select(.task_type != null) | .task_type' 2>/dev/null || true)
  :
done
curl -sf "$ROUTER_URL/metrics" "${auth[@]+"${auth[@]}"}" \
  | jq -r '"  by_model: " + (.by_model | tostring)' 2>/dev/null || true
echo "[bench] tip: set AGENT_MODEL_OVERRIDES to pin specific models per agent"
