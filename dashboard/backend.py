#!/usr/bin/env python3
import os
import subprocess
import time

from flask import Flask, jsonify, send_from_directory

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

app = Flask(__name__,
            static_folder=os.path.join(BASE_DIR, "static"),
            template_folder=os.path.join(BASE_DIR, "templates"))


def get_gpu_stats():
    try:
        out = subprocess.check_output(
            ["nvidia-smi",
             "--query-gpu=utilization.gpu,memory.used,memory.total",
             "--format=csv,noheader,nounits"],
            stderr=subprocess.DEVNULL,
        ).decode().strip()
        util, used, total = [x.strip() for x in out.split(",")]
        return {
            "utilization": int(util),
            "memory_used": int(used),
            "memory_total": int(total),
        }
    except Exception:
        return {"utilization": 0, "memory_used": 0, "memory_total": 0}


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
        "dashboard": up(8030),
        "workflow": up(8040),
        "llama": up(9001),
        "vllm": up(9002),
    }


@app.route("/api/status")
def status():
    return jsonify({
        "timestamp": int(time.time()),
        "gpu": get_gpu_stats(),
        "services": listening_ports(),
    })


@app.route("/")
def index():
    return send_from_directory(app.template_folder, "index.html")


@app.route("/static/<path:path>")
def static_files(path):
    return send_from_directory(app.static_folder, path)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("DASHBOARD_PORT", "8030")))
