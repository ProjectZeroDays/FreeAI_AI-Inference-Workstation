#!/usr/bin/env python3
"""Tokugawa Dashboard — GPU telemetry, service health, alerts."""
import os
import subprocess
import time

from flask import Flask, jsonify, send_from_directory

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

try:
    from settings import load_config
    _CFG = load_config().get("dashboard", {})
except ImportError:
    _CFG = {}

PORT = int(_CFG.get("port", os.environ.get("DASHBOARD_PORT", 8030)))
GPU_TEMP_ALERT_C = int(_CFG.get("gpu_temp_alert_c", 85))
GPU_UTIL_ALERT_PCT = int(_CFG.get("gpu_util_alert_pct", 90))

app = Flask(__name__,
            static_folder=os.path.join(BASE_DIR, "static"),
            template_folder=os.path.join(BASE_DIR, "templates"))

_GPU_FIELDS = ("utilization.gpu,memory.used,memory.total,"
               "temperature.gpu,power.draw,clocks.current.sm")


def get_gpu_stats():
    try:
        out = subprocess.check_output(
            ["nvidia-smi", f"--query-gpu={_GPU_FIELDS}",
             "--format=csv,noheader,nounits"],
            stderr=subprocess.DEVNULL,
        ).decode().strip()
        parts = [x.strip() for x in out.split(",")]
        util, used, total, temp, power, clock = (
            parts + ["0"] * 6)[:6]

        def _num(v):
            try:
                return float(v)
            except ValueError:
                return 0.0

        return {
            "utilization": int(float(util)),
            "memory_used": int(float(used)),
            "memory_total": int(float(total)),
            "temperature": int(float(temp)),
            "power_watts": round(_num(power), 1),
            "clock_mhz": int(float(clock)),
        }
    except Exception:
        return {"utilization": 0, "memory_used": 0, "memory_total": 0,
                "temperature": 0, "power_watts": 0.0, "clock_mhz": 0}


def listening_ports():
    try:
        out = subprocess.check_output(
            ["ss", "-tuln"], stderr=subprocess.DEVNULL).decode()
    except Exception:
        out = ""

    def up(port):
        return f":{port}" in out

    return {
        "router": up(8010),
        "agents": up(8020),
        "dashboard": up(PORT),
        "workflow": up(8040),
        "llama": up(9001),
        "vllm": up(9002),
    }


def build_alerts(services, gpu):
    alerts = []
    down = [name for name, ok in services.items() if not ok]
    if down:
        alerts.append({"level": "critical",
                       "message": f"services down: {', '.join(down)}"})
    if gpu.get("utilization", 0) >= GPU_UTIL_ALERT_PCT:
        alerts.append({"level": "warning",
                       "message": f"GPU utilization "
                                  f"{gpu['utilization']}% >= "
                                  f"{GPU_UTIL_ALERT_PCT}%"})
    if gpu.get("temperature", 0) >= GPU_TEMP_ALERT_C:
        alerts.append({"level": "critical",
                       "message": f"GPU temperature "
                                  f"{gpu['temperature']}C >= "
                                  f"{GPU_TEMP_ALERT_C}C"})
    return alerts


@app.route("/api/status")
def status():
    gpu = get_gpu_stats()
    services = listening_ports()
    return jsonify({
        "timestamp": int(time.time()),
        "gpu": gpu,
        "services": services,
        "alerts": build_alerts(services, gpu),
    })


@app.route("/")
def index():
    return send_from_directory(app.template_folder, "index.html")


@app.route("/static/<path:path>")
def static_files(path):
    return send_from_directory(app.static_folder, path)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=PORT)
