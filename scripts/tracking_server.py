#!/usr/bin/env python3
"""
Tracking Server for Email Campaigns
Flask-based tracking endpoint for opens and clicks.
"""

import json
import os
import uuid
from datetime import datetime
from pathlib import Path

from flask import Flask, jsonify, request, send_file

app = Flask(__name__)

RESULTS_DIR = Path(__file__).parent.parent / "data" / "campaign_results"
RESULTS_DIR.mkdir(parents=True, exist_ok=True)


@app.route("/track/pixel/<campaign_id>/<variant_id>/<tracking_id>")
def track_pixel(campaign_id, variant_id, tracking_id):
    """Track email open via tracking pixel."""
    ip = request.remote_addr
    user_agent = request.headers.get("User-Agent", "Unknown")
    timestamp = datetime.now().isoformat()
    
    result = {
        "type": "open",
        "campaign_id": campaign_id,
        "variant_id": variant_id,
        "tracking_id": tracking_id,
        "timestamp": timestamp,
        "ip": ip,
        "user_agent": user_agent
    }
    
    _save_result(result)
    
    # Return 1x1 transparent pixel
    return send_file(Path(__file__).parent.parent / "templates" / "tracking" / "pixel.png")


@app.route("/track/redirect/<campaign_id>/<variant_id>/<tracking_id>")
def track_redirect(campaign_id, variant_id, tracking_id):
    """Track link click and redirect to landing page."""
    target_url = request.args.get("url", "/")
    ip = request.remote_addr
    timestamp = datetime.now().isoformat()
    
    result = {
        "type": "click",
        "campaign_id": campaign_id,
        "variant_id": variant_id,
        "tracking_id": tracking_id,
        "timestamp": timestamp,
        "ip": ip,
        "target_url": target_url
    }
    
    _save_result(result)
    
    # Redirect to target
    return f"<html><body><script>window.location.href='{target_url}'</script></body></html>"


@app.route("/track/submit", methods=["POST"])
def track_submit():
    """Track form submission."""
    data = request.get_json() or {}
    campaign_id = request.args.get("campaign_id", "unknown")
    variant_id = request.args.get("variant_id", "unknown")
    email = data.get("email", request.remote_addr)
    
    result = {
        "type": "submit",
        "campaign_id": campaign_id,
        "variant_id": variant_id,
        "email": email,
        "timestamp": datetime.now().isoformat(),
        "data": data
    }
    
    _save_result(result)
    
    return jsonify({"status": "ok"})


@app.route("/campaigns/<campaign_id>")
def get_campaign(campaign_id):
    """Get campaign results."""
    results_file = RESULTS_DIR / f"{campaign_id}-results.json"
    
    if not results_file.exists():
        return jsonify({"error": "Campaign not found"}), 404
    
    with open(results_file) as f:
        data = json.load(f)
    
    return jsonify(data)


@app.route("/campaigns")
def list_campaigns():
    """List all campaigns."""
    campaigns = []
    for f in RESULTS_DIR.glob("*-results.json"):
        with open(f) as fp:
            data = json.load(fp)
            campaigns.append({
                "campaign_id": data.get("campaign_id"),
                "generated_at": data.get("generated_at"),
                "stats": data.get("stats")
            })
    return jsonify(campaigns)


@app.route("/")
def index():
    """Health check."""
    return jsonify({
        "service": "campaign-tracking",
        "status": "running",
        "endpoints": [
            "/track/pixel/<campaign_id>/<variant_id>/<tracking_id>",
            "/track/redirect/<campaign_id>/<variant_id>/<tracking_id>",
            "/track/submit",
            "/campaigns",
            "/campaigns/<campaign_id>"
        ]
    })


def _save_result(result: dict):
    """Save tracking result to file."""
    campaign_id = result.get("campaign_id", "unknown")
    results_file = RESULTS_DIR / f"{campaign_id}-results.json"
    
    if results_file.exists():
        with open(results_file) as f:
            data = json.load(f)
    else:
        data = {
            "campaign_id": campaign_id,
            "generated_at": datetime.now().isoformat(),
            "stats": {
                "total_sent": 0,
                "total_opened": 0,
                "total_clicked": 0,
                "total_submitted": 0
            },
            "results": []
        }
    
    data["results"].append(result)
    
    # Update stats
    for r in data["results"]:
        if r["type"] == "open":
            data["stats"]["total_opened"] += 1
        elif r["type"] == "click":
            data["stats"]["total_clicked"] += 1
        elif r["type"] == "submit":
            data["stats"]["total_submitted"] += 1
    
    with open(results_file, "w") as f:
        json.dump(data, f, indent=2)


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Campaign Tracking Server")
    parser.add_argument("--port", type=int, default=9090)
    parser.add_argument("--host", default="0.0.0.0")
    args = parser.parse_args()
    
    print(f"Tracking server starting on http://{args.host}:{args.port}")
    print(f"Results directory: {RESULTS_DIR}")
    print("\nEndpoints:")
    print("  GET  /                          - Health check")
    print("  GET  /track/pixel/<id>/<v>/<t>  - Track email open")
    print("  GET  /track/redirect/<id>/<v>/<t> - Track link click")
    print("  POST /track/submit              - Track form submission")
    print("  GET  /campaigns                 - List campaigns")
    print("  GET  /campaigns/<id>            - Get campaign results")
    print()
    
    app.run(host=args.host, port=args.port, debug=False)
