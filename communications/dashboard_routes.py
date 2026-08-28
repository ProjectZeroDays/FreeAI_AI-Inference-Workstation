"""Flask Blueprint routes for the Communications dashboard.

Registers endpoints under /api/comm/* prefix.
"""
import json
import time
import threading
from pathlib import Path
from flask import Blueprint, request, jsonify

comm_bp = Blueprint("communications", __name__, url_prefix="/api/comm")

COMM_CONFIG_PATH = Path(__file__).parent.parent.parent / "config" / "communications.json"
_LOCK = threading.Lock()

# In-memory state (mirrors config)
_COMM_STATE = {
    "providers": {},
    "messages": [],
    "stats": {
        "total_sent": 0,
        "total_received": 0,
        "by_provider": {},
    },
}


def _load_comm_config():
    if COMM_CONFIG_PATH.exists():
        try:
            return json.loads(COMM_CONFIG_PATH.read_text())
        except (json.JSONDecodeError, OSError):
            pass
    return {"providers": {}, "global": {"max_log_entries": 500}}


def _save_comm_config(data):
    COMM_CONFIG_PATH.write_text(json.dumps(data, indent=2), encoding="utf-8")


# ── Provider management ──────────────────────────────────────────

@comm_bp.route("/providers", methods=["GET"])
def comm_list_providers():
    with _LOCK:
        return jsonify(_COMM_STATE["providers"])


@comm_bp.route("/providers/<pid>", methods=["GET"])
def comm_get_provider(pid):
    with _LOCK:
        prov = _COMM_STATE["providers"].get(pid)
    if not prov:
        return jsonify({"error": "provider not found"}), 404
    return jsonify(prov)


@comm_bp.route("/providers/<pid>/connect", methods=["POST"])
def comm_connect_provider(pid):
    from ..shared_api import get_hub
    hub = get_hub()
    hub.register_provider(pid)
    prov = hub.get_provider(pid)
    if not prov:
        return jsonify({"error": "provider not found"}), 404
    ok = prov.connect()
    with _LOCK:
        if pid not in _COMM_STATE["providers"]:
            _COMM_STATE["providers"][pid] = prov.to_dict()
        _COMM_STATE["providers"][pid]["connected"] = ok
        _COMM_STATE["providers"][pid]["last_error"] = prov._last_error
    return jsonify({"ok": ok, "provider": pid, "connected": ok})


@comm_bp.route("/providers/<pid>/disconnect", methods=["POST"])
def comm_disconnect_provider(pid):
    with _LOCK:
        if pid in _COMM_STATE["providers"]:
            _COMM_STATE["providers"][pid]["connected"] = False
    return jsonify({"ok": True, "provider": pid, "connected": False})


@comm_bp.route("/providers/<pid>/configure", methods=["POST"])
def comm_configure_provider(pid):
    data = request.get_json(silent=True) or {}
    cfg = _load_comm_config()
    if "providers" not in cfg:
        cfg["providers"] = {}
    cfg["providers"][pid] = {
        "enabled": data.get("enabled", True),
        "config": data.get("config", {}),
    }
    _save_comm_config(cfg)
    return jsonify({"ok": True, "provider": pid})


@comm_bp.route("/providers/<pid>/test", methods=["POST"])
def comm_test_provider(pid):
    data = request.get_json(silent=True) or {}
    recipient = data.get("recipient", "")
    content = data.get("content", "FreeAI test message")

    from ..shared_api import get_hub
    hub = get_hub()
    if not hub.get_provider(pid):
        hub.register_provider(pid)

    result = hub.send(pid, recipient, content)
    return jsonify(result)


@comm_bp.route("/providers/<pid>/health", methods=["GET"])
def comm_health_provider(pid):
    from ..shared_api import get_hub
    hub = get_hub()
    if not hub.get_provider(pid):
        hub.register_provider(pid)
    prov = hub.get_provider(pid)
    if not prov:
        return jsonify({"error": "provider not found"}), 404
    return jsonify(prov.health_check())


@comm_bp.route("/providers/test-all", methods=["POST"])
def comm_test_all():
    from ..shared_api import get_hub
    hub = get_hub()
    results = hub.test_all()
    with _LOCK:
        for pid, health in results.items():
            _COMM_STATE["providers"][pid] = health
    return jsonify(results)


# ── Messaging ────────────────────────────────────────────────────

@comm_bp.route("/send", methods=["POST"])
def comm_send():
    data = request.get_json(silent=True) or {}
    pid = data.get("provider", "")
    recipient = data.get("recipient", "")
    content = data.get("content", "")
    if not pid or not recipient or not content:
        return jsonify({"error": "provider, recipient, and content required"}), 400

    from ..shared_api import get_hub
    hub = get_hub()
    result = hub.send(pid, recipient, content, **{k: v for k, v in data.items() if k not in ("provider", "recipient", "content")})
    return jsonify(result)


@comm_bp.route("/receive/<pid>", methods=["GET"])
def comm_receive(pid):
    limit = request.args.get("limit", 20, type=int)
    from ..shared_api import get_hub
    hub = get_hub()
    messages = hub.receive(pid, limit)
    return jsonify({"provider": pid, "messages": messages})


@comm_bp.route("/messages", methods=["GET"])
def comm_messages():
    limit = request.args.get("limit", 50, type=int)
    from ..shared_api import get_hub
    hub = get_hub()
    return jsonify(hub.get_message_log(limit))


@comm_bp.route("/messages/clear", methods=["POST"])
def comm_clear_messages():
    from ..shared_api import get_hub
    hub = get_hub()
    count = hub.clear_log()
    return jsonify({"cleared": count})


# ── Stats & Config ───────────────────────────────────────────────

@comm_bp.route("/stats", methods=["GET"])
def comm_stats():
    with _LOCK:
        total_sent = sum(p.get("messages_sent", 0) for p in _COMM_STATE["providers"].values())
        total_recv = sum(p.get("messages_received", 0) for p in _COMM_STATE["providers"].values())
        connected = sum(1 for p in _COMM_STATE["providers"].values() if p.get("connected"))
        return jsonify({
            "total_sent": total_sent,
            "total_received": total_recv,
            "providers_connected": connected,
            "providers_total": len(_COMM_STATE["providers"]),
            "by_provider": {pid: p.to_dict() for pid, p in _COMM_STATE["providers"].items()},
        })


@comm_bp.route("/config", methods=["GET"])
def comm_get_config():
    cfg = _load_comm_config()
    cfg["_state"] = _COMM_STATE["providers"]
    return jsonify(cfg)


@comm_bp.route("/config", methods=["POST"])
def comm_save_config():
    data = request.get_json(silent=True) or {}
    _save_comm_config(data)
    return jsonify({"ok": True})
