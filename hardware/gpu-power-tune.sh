#!/usr/bin/env bash
# GPU undervolt-equivalent profile for 24/7 inference (Linux).
#
# NVIDIA Linux drivers don't expose Afterburner-style voltage curves;
# locking the core clock lower forces a lower point on the V/F curve —
# same effect: -10..20°C under sustained load for ~3-5% throughput.
#
# Usage:
#   gpu-power-tune.sh apply    # cap power + lock clock (defaults below)
#   gpu-power-tune.sh reset    # back to stock boost/power limits
#   gpu-power-tune.sh status
set -euo pipefail

GPU_ID="${GPU_ID:-0}"
POWER_LIMIT_W="${GPU_POWER_LIMIT_W:-240}"   # stock max ~285-300W
LOCKED_CLOCK_MHZ="${GPU_LOCKED_CLOCK_MHZ:-2520}"  # stock boost ~2610-2640

require_nvidia() {
  command -v nvidia-smi >/dev/null 2>&1 \
    || { echo "[gpu-tune] nvidia-smi not found" >&2; exit 1; }
}

case "${1:-apply}" in
  apply)
    require_nvidia
    echo "[gpu-tune] applying: power cap ${POWER_LIMIT_W}W, "
    echo "[gpu-tune] clock lock ${LOCKED_CLOCK_MHZ} MHz on GPU $GPU_ID"
    sudo nvidia-smi -i "$GPU_ID" -pl "$POWER_LIMIT_W"
    sudo nvidia-smi -i "$GPU_ID" -lgc "$LOCKED_CLOCK_MHZ"
    echo "[gpu-tune] active. Reset with: $0 reset"
    ;;
  reset)
    require_nvidia
    echo "[gpu-tune] restoring defaults on GPU $GPU_ID"
    sudo nvidia-smi -i "$GPU_ID" -rgc || true
    sudo nvidia-smi -i "$GPU_ID" -rpl || true
    ;;
  status)
    require_nvidia
    nvidia-smi -i "$GPU_ID" \
      --query-gpu=name,clocks.sm,power.limit,temperature.gpu,utilization.gpu \
      --format=csv
    ;;
  *)
    echo "usage: $0 apply|reset|status" >&2
    exit 1
    ;;
esac
