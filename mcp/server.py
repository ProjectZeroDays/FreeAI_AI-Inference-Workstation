"""MCP server wrapper over FreeAI APIs (ROADMAP 16)."""
from flask import Flask, request, jsonify
import requests, os
app = Flask(__name__)
ROUTER = os.environ.get("ROUTER_URL", "http://localhost:8010")
AGENT_API = os.environ.get("AGENT_API", "http://localhost:8020")
WORKFLOW_API = os.environ.get("WORKFLOW_API", "http://localhost:8040")
AUTO_API = os.environ.get("AUTO_API", "http://localhost:8050")

# Outbound auth for downstream services
AUTONOMOUS_API_KEY = os.environ.get("AUTONOMOUS_API_KEY", "")
AGENT_API_KEY = os.environ.get("AGENT_API_KEY", "")
MCP_API_KEY = os.environ.get("MCP_API_KEY", "")

def _build_headers(service="auto"):
    """Build authentication headers for API calls."""
    headers = {}
    if service == "auto" and AUTONOMOUS_API_KEY:
        headers["X-API-Key"] = AUTONOMOUS_API_KEY
    elif service == "agent" and AGENT_API_KEY:
        headers["X-API-Key"] = AGENT_API_KEY
    return headers

def _check_auth():
    """Verify API key if MCP_API_KEY is configured."""
    if not MCP_API_KEY:
        return None
    provided = (request.headers.get("X-API-Key") or
                request.headers.get("X-Auth-Token") or
                request.headers.get("Authorization", "").replace("Bearer ", ""))
    if provided != MCP_API_KEY:
        return jsonify({"error": "unauthorized"}), 401
    return None

@app.before_request
def guard():
    """Authentication gate for all endpoints except /health."""
    if request.path == "/health":
        return None
    auth_result = _check_auth()
    if auth_result:
        return auth_result
    return None

@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok", "auth_required": bool(MCP_API_KEY)})

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
    # Forward inbound auth to downstream services
    if MCP_API_KEY:
        auth_header = (request.headers.get("X-API-Key") or
                      request.headers.get("X-Auth-Token") or
                      request.headers.get("Authorization", "").replace("Bearer ", ""))
        if auth_header:
            headers["X-API-Key"] = auth_header
    r = requests.post(url, json=payload, headers=headers, timeout=120)
    return jsonify(r.json()), r.status_code

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("MCP_PORT", 8090)))
