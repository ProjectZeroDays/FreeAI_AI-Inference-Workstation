#!/usr/bin/env python3
import os

from flask import Flask, request, jsonify
import requests

from classifier import classify_task
from switcher import select_model

app = Flask(__name__)

TIMEOUT = int(os.environ.get("BACKEND_TIMEOUT", "300"))
ROUTER_PORT = int(os.environ.get("ROUTER_PORT", "8010"))


@app.route("/route", methods=["POST"])
def route():
    data = request.get_json(silent=True) or {}
    prompt = data.get("prompt", "")
    if not prompt:
        return jsonify({"error": "prompt is required"}), 400

    # 1. classify task
    task_type = classify_task(prompt)

    # 2. select model
    model = select_model(task_type)

    # 3. forward request to model endpoint
    payload = {
        "prompt": prompt,
        "max_tokens": data.get("max_tokens", 2048),
        "temperature": data.get("temperature", 0.2),
    }

    try:
        response = requests.post(model["endpoint"], json=payload,
                                 timeout=TIMEOUT)
        result = response.json()
    except Exception as exc:
        return jsonify({"error": str(exc), "model": model["name"]}), 502

    return jsonify({
        "model_used": model["name"],
        "task_type": task_type,
        "response": result,
    })


@app.route("/models", methods=["GET"])
def models():
    from models import MODEL_REGISTRY
    return jsonify({
        key: {"name": m["name"], "role": m["role"], "strengths": m["strengths"]}
        for key, m in MODEL_REGISTRY.items()
    })


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=ROUTER_PORT, threaded=True)
