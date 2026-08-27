"""MCP server wrapper over FreeAI APIs (ROADMAP 16)."""
from flask import Flask, request, jsonify
import requests, os
app = Flask(__name__)
ROUTER = os.environ.get("ROUTER_URL", "http://localhost:8010")
AGENT_API = os.environ.get("AGENT_API", "http://localhost:8020")
WORKFLOW_API = os.environ.get("WORKFLOW_API", "http://localhost:8040")
AUTO_API = os.environ.get("AUTO_API", "http://localhost:8050")
AUTONOMOUS_API_KEY = os.environ.get("AUTONOMOUS_API_KEY", "")
AGENT_API_KEY = os.environ.get("AGENT_API_KEY", "")

def _build_headers(service="auto"):
    """Build authentication headers for API calls."""
    headers = {}
    if service == "auto" and AUTONOMOUS_API_KEY:
        headers["X-API-Key"] = AUTONOMOUS_API_KEY
    elif service == "agent" and AGENT_API_KEY:
        headers["X-API-Key"] = AGENT_API_KEY
    return headers

@app.route("/mcp/tools", methods=["GET"])
def tools():
    return jsonify({"tools": ["route","agent/project","agent/refactor","workflow/run","auto/start"]})

@app.route("/mcp/call", methods=["POST"])
def call():
    d = request.get_json() or {}
    tool, args = d.get("tool"), d.get("args", {})
    mapping = {
        "route": (f"{ROUTER}/route", args, None),
        "agent/project": (f"{AGENT_API}/agent/project", args, "agent"),
        "workflow/run": (f"{WORKFLOW_API}/workflow/run", args, None),
        "auto/start": (f"{AUTO_API}/auto/start", args, "auto"),
    }
    if tool not in mapping:
        return jsonify({"error": "unknown tool"}), 400
    url, payload, service = mapping[tool]
    headers = _build_headers(service) if service else {}
    r = requests.post(url, json=payload, headers=headers, timeout=120)
    return jsonify(r.json()), r.status_code

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("MCP_PORT", 8090)))
