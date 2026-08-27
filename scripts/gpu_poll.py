#!/usr/bin/env python3
"""GPU telemetry poller — reads NVIDIA GPU stats via nvidia-smi,
falls back to WMI on Windows, then to psutil CPU temps, then to mock data."""

import json
import subprocess
import sys
import time
import random

# ── Config ──────────────────────────────────────────────────────────
DEFAULTS = {
    "name": "NVIDIA GeForce RTX 4090",
    "total_vram_mb": 24576,
    "power_limit_w": 450,
    "max_temp_c": 90,
    "base_clock_mhz": 2520,
}

TEMP_THRESHOLD_C = 80
POWER_THRESHOLD_W = 300

# ── Data store (in-memory ring buffer for history) ──────────────────
_history = {"timestamps": [], "temp": [], "power": [], "util": [], "clock": [], "vram": []}
MAX_HISTORY = 60


def _push_sample(s):
    _history["timestamps"].append(time.time())
    _history["temp"].append(s["temperature_c"])
    _history["power"].append(s["power_w"])
    _history["util"].append(s["utilization_pct"])
    _history["clock"].append(s["clock_mhz"])
    _history["vram"].append(s["vram_used_mb"])
    for k in _history:
        _history[k] = _history[k][-MAX_HISTORY:]


def _read_nvidia_smi():
    """Parse nvidia-smi JSON output for all GPUs."""
    try:
        result = subprocess.run(
            ["nvidia-smi", "--query-gpu=timestamp,name,temperature.gpu,power.draw,power.limit,"
             "utilization.gpu,utilization.memory,clocks.current.graphics,memory.used,memory.total,"
             "ecc.errors.corrected.volatile.total",
             "--format=json"],
            capture_output=True, text=True, timeout=5
        )
        if result.returncode != 0:
            return None
        data = json.loads(result.stdout)
        gpus = data.get("gpus", [])
        if not gpus:
            return None
        samples = []
        for g in gpus:
            temp = int(g.get("temperature.gpu", "0 N/A").split()[0]) if g.get("temperature.gpu") else 0
            pow_str = g.get("power.draw", "0 N/A")
            power_w = float(pow_str.split()[0]) if pow_str else 0
            pow_limit_str = g.get("power.limit", "0 N/A")
            power_limit_w = float(pow_limit_str.split()[0]) if pow_limit_str else 0
            util_str = g.get("utilization.gpu", "0 N/A")
            util_pct = int(util_str.split()[0]) if util_str else 0
            mem_util_str = g.get("utilization.memory", "0 N/A")
            mem_util_pct = int(mem_util_str.split()[0]) if mem_util_str else 0
            clock = int(g.get("clocks.current.graphics", "0 N/A").split()[0]) if g.get("clocks.current.graphics") else 0
            vram_used = int(g.get("memory.used", "0 N/A").split()[0]) if g.get("memory.used") else 0
            vram_total = int(g.get("memory.total", "0 N/A").split()[0]) if g.get("memory.total") else 0
            name = g.get("name", "Unknown GPU")
            ecc = g.get("ecc.errors.corrected.volatile.total", "")
            samples.append({
                "index": gpus.index(g),
                "name": name,
                "temperature_c": temp,
                "power_w": power_w,
                "power_limit_w": power_limit_w,
                "utilization_pct": util_pct,
                "memory_util_pct": mem_util_pct,
                "clock_mhz": clock,
                "vram_used_mb": vram_used,
                "vram_total_mb": vram_total,
                "ecc_errors": ecc,
                "alert_temp": temp > TEMP_THRESHOLD_C,
                "alert_power": power_w > POWER_THRESHOLD_W,
            })
        return samples
    except (FileNotFoundError, subprocess.TimeoutExpired, json.JSONDecodeError, Exception):
        return None


def _read_wmi():
    """Fallback: Windows WMI for basic GPU temperature (requires pywin32)."""
    try:
        import wmi
        c = wmi.WMI()
        samples = []
        for gpu in c.Win32_VideoController():
            name = getattr(gpu, "Name", "Unknown")
            driver_version = getattr(gpu, "DriverVersion", "")
            adapter_ram = getattr(gpu, "AdapterRAM", 0)
            current_clock = getattr(gpu, "CurrentClockSpeed", 0)
            samples.append({
                "index": len(samples),
                "name": name,
                "temperature_c": 0,
                "power_w": 0,
                "power_limit_w": 0,
                "utilization_pct": 0,
                "memory_util_pct": 0,
                "clock_mhz": current_clock,
                "vram_used_mb": 0,
                "vram_total_mb": adapter_ram // (1024 ** 2) if adapter_ram else 0,
                "ecc_errors": "",
                "alert_temp": False,
                "alert_power": False,
                "_wmi": True,
            })
        return samples if samples else None
    except Exception:
        return None


def _mock_sample(index=0):
    """Realistic mock data for systems without GPU telemetry."""
    base_temp = 55 + random.uniform(-5, 15)
    base_power = 120 + random.uniform(-20, 80)
    base_util = 30 + random.uniform(-10, 50)
    base_clock = DEFAULTS["base_clock_mhz"] + random.randint(-50, 100)
    base_vram = int(DEFAULTS["total_vram_mb"] * (0.2 + random.random() * 0.5))
    return {
        "index": index,
        "name": DEFAULTS["name"],
        "temperature_c": round(base_temp, 1),
        "power_w": round(base_power, 1),
        "power_limit_w": DEFAULTS["power_limit_w"],
        "utilization_pct": int(base_util),
        "memory_util_pct": int(base_util * 0.7),
        "clock_mhz": base_clock,
        "vram_used_mb": base_vram,
        "vram_total_mb": DEFAULTS["total_vram_mb"],
        "ecc_errors": "N/A",
        "alert_temp": base_temp > TEMP_THRESHOLD_C,
        "alert_power": base_power > POWER_THRESHOLD_W,
        "_mock": True,
    }


def poll(n_gpus=1):
    """Return list of GPU samples. Tries nvidia-smi → WMI → mock."""
    result = _read_nvidia_smi()
    if result is not None and result:
        return result
    result = _read_wmi()
    if result is not None and result:
        return result
    return [_mock_sample(i) for i in range(n_gpus)]


def poll_and_history():
    """Poll + push into ring buffer, return combined payload."""
    samples = poll()
    if samples:
        for s in samples:
            _push_sample(s)
    # Backward-compatible flat fields for existing consumers
    flat = {}
    if samples:
        flat["devices"] = [{
            "name": s["name"],
            "total_vram_mb": s["vram_total_mb"],
            "used_vram_mb": s["vram_used_mb"],
            "utilization_pct": s["utilization_pct"],
            "temperature_c": s["temperature_c"],
            "power_w": s["power_w"],
        } for s in samples]
        flat["total_vram_mb"] = sum(s["vram_total_mb"] for s in samples)
        flat["used_vram_mb"] = sum(s["vram_used_mb"] for s in samples)
        flat["utilization_pct"] = samples[0]["utilization_pct"]
        flat["temperature_c"] = samples[0]["temperature_c"]
        flat["power_w"] = samples[0]["power_w"]
    return {
        "timestamp": time.time(),
        "samples": samples,
        "history": {
            "timestamps": _history["timestamps"],
            "temp": _history["temp"],
            "power": _history["power"],
            "util": _history["util"],
            "clock": _history["clock"],
            "vram": _history["vram"],
        },
        "thresholds": {
            "temp_c": TEMP_THRESHOLD_C,
            "power_w": POWER_THRESHOLD_W,
        },
        "source": "nvidia-smi" if not samples[0].get("_mock") else
                   "wmi" if samples[0].get("_wmi") else "mock",
        **flat,
    }


if __name__ == "__main__":
    payload = poll_and_history()
    print(json.dumps(payload, indent=2))
