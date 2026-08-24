#!/usr/bin/env python3
"""AI resource optimizer — balances thermals, power, and agent load.

Samples the GPU on an interval, classifies the workload into
performance / balanced / eco (with hysteresis + cooldown so it never
flaps), applies matching nvidia-smi power/clock profiles, and publishes
config/runtime-state.json for the dashboard.

Modes:
  performance  stock power, full boost      — heavy SDLC runs
  balanced     ~240W / ~2520MHz             — default steady state
  eco          ~200W / ~2400MHz             — idle or hot; saves watts

Run standalone:  python3 agents/resource_optimizer.py [--once]
"""
import argparse
import json
import os
import subprocess
import time

try:
    from settings import load_config  # router's loader (repo root config)
except ImportError:
    def load_config():
        return {}

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STATE_PATH = os.path.join(ROOT, "config", "runtime-state.json")

INTERVAL_S = int(os.environ.get("OPTIMIZER_INTERVAL_S", "60"))
GPU_ID = os.environ.get("GPU_ID", "0")
COOLDOWN_S = int(os.environ.get("OPTIMIZER_COOLDOWN_S", "600"))

PROFILES = {
    "performance": {"power_w": None, "clock_mhz": None},       # stock
    "balanced": {"power_w": 240, "clock_mhz": 2520},
    "eco": {"power_w": 200, "clock_mhz": 2400},
}

# thresholds
HOT_TEMP_C = 82
HEAVY_UTIL = 85
IDLE_UTIL = 10


def sample_gpu():
    """One nvidia-smi sample: (util_pct, temp_c, power_w) or None."""
    try:
        out = subprocess.check_output(
            ["nvidia-smi", "-i", GPU_ID,
             "--query-gpu=utilization.gpu,temperature.gpu,power.draw",
             "--format=csv,noheader,nounits"],
            stderr=subprocess.DEVNULL, timeout=15).decode().strip()
        util_s, temp_s, power_s = [x.strip() for x in out.split(",")]

        def num(v):
            try:
                return float(v)
            except ValueError:
                return 0.0

        return num(util_s), num(temp_s), num(power_s)
    except Exception:
        return None


def decide_mode(history, current_mode, now):
    """Pure decision core — easy to unit test.

    history: list of (util, temp, power) tuples, oldest first.
    Returns new mode string.
    """
    if not history:
        return current_mode or "balanced"
    recent = history[-3:]
    avg_util = sum(h[0] for h in recent) / len(recent)
    max_temp = max(h[1] for h in recent)

    if max_temp >= HOT_TEMP_C:
        return "eco"
    if avg_util <= IDLE_UTIL:
        return "eco"
    if avg_util >= HEAVY_UTIL and max_temp <= HOT_TEMP_C - 7:
        return "performance"
    if current_mode == "eco" and avg_util < HEAVY_UTIL \
            and max_temp <= HOT_TEMP_C - 12:
        return "balanced"
    return current_mode or "balanced"


def apply_profile(mode):
    prof = PROFILES.get(mode)
    if not prof:
        return False
    try:
        if mode == "performance":
            subprocess.run(["nvidia-smi", "-i", GPU_ID, "-rpl"],
                           check=False, capture_output=True)
            subprocess.run(["nvidia-smi", "-i", GPU_ID, "-rgc"],
                           check=False, capture_output=True)
        else:
            if prof["power_w"]:
                subprocess.run(["nvidia-smi", "-i", GPU_ID,
                                "-pl", str(prof["power_w"])],
                               check=False, capture_output=True)
            if prof["clock_mhz"]:
                subprocess.run(["nvidia-smi", "-i", GPU_ID,
                                "-lgc", str(prof["clock_mhz"])],
                               check=False, capture_output=True)
        return True
    except Exception:
        return False


def publish_state(state):
    os.makedirs(os.path.dirname(STATE_PATH), exist_ok=True)
    with open(STATE_PATH, "w") as f:
        json.dump(state, f, indent=2)


def run_loop(once=False):
    cfg = load_config().get("dashboard", {})
    state = {
        "mode": "balanced",
        "since": time.time(),
        "reason": "startup",
        "history": [],
        "last_change": 0.0,
        "temp_alert_c": cfg.get("gpu_temp_alert_c", 85),
    }
    while True:
        sample = sample_gpu()
        if sample is not None:
            state["history"].append(sample)
            state["history"] = state["history"][-20:]

        proposed = decide_mode(state["history"], state["mode"],
                               time.time())
        now = time.time()
        if proposed != state["mode"] and \
                now - state["last_change"] >= COOLDOWN_S:
            print(f"[optimizer] {state['mode']} -> {proposed} "
                  f"(sample={sample})")
            state["mode"] = proposed
            state["since"] = now
            state["last_change"] = now
            state["reason"] = f"avg_util/temp driven at {int(now)}"
            apply_profile(proposed)

        publish_state({
            k: v for k, v in state.items() if k != "history"
        })
        if once:
            break
        time.sleep(INTERVAL_S)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--once", action="store_true")
    args = ap.parse_args()
    run_loop(once=args.once)
