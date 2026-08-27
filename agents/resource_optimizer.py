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
SETTINGS_PATH = os.path.join(ROOT, "config", "runtime-settings.json")

INTERVAL_S = int(os.environ.get("OPTIMIZER_INTERVAL_S", "60"))
GPU_ID = os.environ.get("GPU_ID", "0")
COOLDOWN_S = int(os.environ.get("OPTIMIZER_COOLDOWN_S", "600"))

# Recommended defaults — also the shipped settings file contents.
SETTINGS_DEFAULTS = {
    "auto_management": True,       # checkbox: AI tunes GPU power modes
    "forced_mode": "balanced",     # used only when auto_management=False
    "power_limit_w": 240,          # balanced profile cap (stock ~285W)
    "locked_clock_mhz": 2520,      # balanced clock (stock boost ~2610)
    "eco_power_w": 200,
    "eco_clock_mhz": 2400,
    # llama.cpp anti-repetition sampling (applied after restart)
    "repeat_penalty": 1.05,
    "repeat_last_n": 64,
    "llama_ctx": 4096,
    # autonomous SDLC concurrency guard (GPU thrash protection)
    "max_concurrent_runs": 3,
}

# Shipped recommended presets — switchable from the dashboard.
# "idle_default_minutes" marks the timed-idle preset.
BUILTIN_PRESETS = [
    {
        "name": "24-7 Balanced",
        "builtin": True,
        "description": "Recommended always-on: AI auto-management ON",
        "settings": dict(SETTINGS_DEFAULTS),
    },
    {
        "name": "Max Performance",
        "builtin": True,
        "description": "Stock clocks/power, manual mode — heavy SDLC runs",
        "settings": {
            "auto_management": False, "forced_mode": "performance",
            "power_limit_w": 285, "locked_clock_mhz": 2610,
            "eco_power_w": 200, "eco_clock_mhz": 2400,
            "repeat_penalty": 1.05, "repeat_last_n": 64,
            "llama_ctx": 4096, "max_concurrent_runs": 4,
        },
    },
    {
        "name": "Silent Eco",
        "builtin": True,
        "description": "Cool & quiet — light duty, manual eco lock",
        "settings": {
            "auto_management": False, "forced_mode": "eco",
            "power_limit_w": 180, "locked_clock_mhz": 2300,
            "eco_power_w": 170, "eco_clock_mhz": 2200,
            "repeat_penalty": 1.05, "repeat_last_n": 64,
            "llama_ctx": 4096, "max_concurrent_runs": 1,
        },
    },
    {
        "name": "Idle (timed)",
        "builtin": True,
        "description": "Eco now, auto-restore after N minutes",
        "idle_default_minutes": 60,
        "settings": {
            "auto_management": True, "forced_mode": "balanced",
            "power_limit_w": 200, "locked_clock_mhz": 2400,
            "eco_power_w": 160, "eco_clock_mhz": 2200,
            "repeat_penalty": 1.05, "repeat_last_n": 64,
            "llama_ctx": 4096, "max_concurrent_runs": 1,
        },
    },
]


def get_builtin_preset(name):
    for p in BUILTIN_PRESETS:
        if p["name"] == name:
            return p
    return None


def load_settings():
    """Defaults merged with config/runtime-settings.json.

    Unknown keys (e.g. the nested "idle" block) pass through untouched
    so callers see the full persisted state.
    """
    cfg = dict(SETTINGS_DEFAULTS)
    try:
        with open(SETTINGS_PATH) as f:
            user = json.load(f)
        for k, v in user.items():
            cfg[k] = v
    except (OSError, ValueError):
        pass
    return cfg


def save_settings(settings):
    os.makedirs(os.path.dirname(SETTINGS_PATH), exist_ok=True)
    with open(SETTINGS_PATH, "w") as f:
        json.dump(settings, f, indent=2)


def expire_if_due(settings, now):
    """If a timed-idle window has elapsed, restore its snapshot.
    Returns (settings, changed)."""
    idle = settings.get("idle") or {}
    if not idle.get("active"):
        return settings, False
    if now < float(idle.get("until_epoch") or 0):
        return settings, False

    restored = dict(idle.get("restore") or {})
    restored.pop("idle", None)
    restored["idle"] = {"active": False}
    merged = dict(SETTINGS_DEFAULTS)
    merged.update(restored)
    print(f"[optimizer] idle window over — restoring previous settings")
    save_settings(merged)
    return merged, True


def build_profiles(settings):
    """Power/clock table derived from user settings."""
    return {
        "performance": {"power_w": None, "clock_mhz": None},   # stock
        "balanced": {"power_w": int(settings["power_limit_w"]),
                     "clock_mhz": int(settings["locked_clock_mhz"])},
        "eco": {"power_w": int(settings["eco_power_w"]),
                "clock_mhz": int(settings["eco_clock_mhz"])},
    }


PROFILES = build_profiles(SETTINGS_DEFAULTS)

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


def apply_profile(mode, profiles=None):
    prof = (profiles or PROFILES).get(mode)
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
        settings = load_settings()

        # ---- timed-idle window handling ----
        settings, expired = expire_if_due(settings, time.time())
        idle = settings.get("idle") or {}
        if idle.get("active"):
            if state["mode"] != "eco":
                print("[optimizer] idle window active -> eco")
                apply_profile("eco", build_profiles(settings))
                state["mode"] = "eco"
                state["since"] = time.time()
                state["reason"] = "timed idle window"
            publish_state({k: v for k, v in state.items()
                           if k != "history"})
            if once:
                break
            time.sleep(INTERVAL_S)
            continue
        if expired:
            apply_profile(settings.get("forced_mode", "balanced"),
                          build_profiles(settings))
            state["mode"] = settings.get("forced_mode", "balanced")
            state["since"] = time.time()
            state["reason"] = "idle window ended (restored)"

        # ---- manual mode: user turned AI auto-management off ----
        if not settings.get("auto_management", True):
            desired = settings.get("forced_mode", "balanced")
            if desired != state["mode"]:
                print(f"[optimizer] manual override -> {desired}")
                apply_profile(desired, build_profiles(settings))
                state["mode"] = desired
                state["since"] = time.time()
                state["reason"] = "manual override (auto-management off)"
            publish_state({k: v for k, v in state.items()
                           if k != "history"})
            if once:
                break
            time.sleep(INTERVAL_S)
            continue

        # ---- auto mode: sample + decide + apply ----
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
            apply_profile(proposed, build_profiles(settings))

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
