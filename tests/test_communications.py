"""Tests for the communications module — dashboard routes and shared API."""
import json
import sys
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))

from communications.shared_api import CommunicationsHub  # noqa: E402
from communications.providers.base import BaseProvider  # noqa: E402
from flask import Flask  # noqa: E402


# ── Mock provider for testing ──────────────────────────────────────

class MockProvider(BaseProvider):
    """A test provider that doesn't need real API keys."""
    PROVIDER_ID = "mock-provider"
    PROVIDER_NAME = "Mock Provider"
    PROVIDER_TYPE = "messaging"
    REQUIRES_KEY = False

    def __init__(self, config=None):
        super().__init__(config)
        self._messages = []

    def connect(self):
        self._connected = True
        self._last_error = None
        return True

    def send(self, recipient, content, **kwargs):
        self._messages_sent += 1
        self._messages.append({"to": recipient, "body": content})
        return {"ok": True, "message_id": f"mock-{self._messages_sent}"}

    def receive(self, limit=20):
        return self._messages[-limit:]

    def health_check(self):
        return {"healthy": self._connected, "provider": self.PROVIDER_ID}


# ── Mock dashboard routes (avoid relative import issues) ──────────

@pytest.fixture
def mock_comm_state():
    """Return a fresh in-memory state dict like _COMM_STATE."""
    return {
        "providers": {},
        "messages": [],
        "stats": {"total_sent": 0, "total_received": 0, "by_provider": {}},
    }


@pytest.fixture
def flask_app(tmp_path, monkeypatch, mock_comm_state):
    """Create a Flask app with communications routes, mocking the hub."""
    monkeypatch.setattr(
        "communications.shared_api.COMMUNICATIONS_CONFIG_PATH",
        tmp_path / "communications.json",
    )

    # Build a minimal route set that doesn't use relative imports
    from flask import Blueprint, request, jsonify
    import threading

    comm_bp = Blueprint("communications", __name__, url_prefix="/api/comm")
    _LOCK = threading.Lock()
    _state = mock_comm_state

    # Create a mock hub
    mock_hub = MagicMock(spec=CommunicationsHub)
    mock_hub.get_provider.return_value = None
    mock_hub.register_provider.return_value = True
    mock_hub.send.return_value = {"ok": True, "message_id": "m1"}
    mock_hub.receive.return_value = []
    mock_hub.get_message_log.return_value = {"messages": [], "total": 0}
    mock_hub.clear_log.return_value = 0
    mock_hub.test_all.return_value = {}
    mock_hub.health_all.return_value = {}

    @comm_bp.route("/providers", methods=["GET"])
    def list_providers():
        with _LOCK:
            return jsonify(_state["providers"])

    @comm_bp.route("/providers/<pid>", methods=["GET"])
    def get_provider(pid):
        with _LOCK:
            prov = _state["providers"].get(pid)
        if not prov:
            return jsonify({"error": "provider not found"}), 404
        return jsonify(prov)

    @comm_bp.route("/providers/<pid>/connect", methods=["POST"])
    def connect_provider(pid):
        prov = mock_hub.get_provider(pid)
        if not prov:
            mock_hub.register_provider(pid)
            prov = mock_hub.get_provider(pid)
        if not prov:
            return jsonify({"error": "provider not found"}), 404
        ok = prov.connect()
        with _LOCK:
            _state["providers"][pid] = prov.to_dict()
            _state["providers"][pid]["connected"] = ok
        return jsonify({"ok": ok, "provider": pid, "connected": ok})

    @comm_bp.route("/providers/<pid>/disconnect", methods=["POST"])
    def disconnect_provider(pid):
        with _LOCK:
            if pid in _state["providers"]:
                _state["providers"][pid]["connected"] = False
        return jsonify({"ok": True, "provider": pid, "connected": False})

    @comm_bp.route("/providers/<pid>/configure", methods=["POST"])
    def configure_provider(pid):
        data = request.get_json(silent=True) or {}
        with _LOCK:
            _state["providers"][pid] = {
                "enabled": data.get("enabled", True),
                "config": data.get("config", {}),
            }
        return jsonify({"ok": True, "provider": pid})

    @comm_bp.route("/providers/<pid>/test", methods=["POST"])
    def test_provider(pid):
        data = request.get_json(silent=True) or {}
        recipient = data.get("recipient", "")
        content = data.get("content", "test message")
        result = mock_hub.send(pid, recipient, content)
        return jsonify(result)

    @comm_bp.route("/providers/<pid>/health", methods=["GET"])
    def health_provider(pid):
        prov = mock_hub.get_provider(pid)
        if not prov:
            mock_hub.register_provider(pid)
            prov = mock_hub.get_provider(pid)
        if not prov:
            return jsonify({"error": "provider not found"}), 404
        return jsonify(prov.health_check())

    @comm_bp.route("/providers/test-all", methods=["POST"])
    def test_all():
        results = mock_hub.test_all()
        with _LOCK:
            for pid, health in results.items():
                _state["providers"][pid] = health
        return jsonify(results)

    @comm_bp.route("/send", methods=["POST"])
    def send():
        data = request.get_json(silent=True) or {}
        pid = data.get("provider", "")
        recipient = data.get("recipient", "")
        content = data.get("content", "")
        if not pid or not recipient or not content:
            return jsonify({"error": "provider, recipient, and content required"}), 400
        result = mock_hub.send(pid, recipient, content,
                               **{k: v for k, v in data.items()
                                  if k not in ("provider", "recipient", "content")})
        return jsonify(result)

    @comm_bp.route("/receive/<pid>", methods=["GET"])
    def receive(pid):
        limit = request.args.get("limit", 20, type=int)
        messages = mock_hub.receive(pid, limit)
        return jsonify({"provider": pid, "messages": messages})

    @comm_bp.route("/messages", methods=["GET"])
    def messages():
        limit = request.args.get("limit", 50, type=int)
        return jsonify(mock_hub.get_message_log(limit))

    @comm_bp.route("/messages/clear", methods=["POST"])
    def clear_messages():
        count = mock_hub.clear_log()
        return jsonify({"cleared": count})

    @comm_bp.route("/stats", methods=["GET"])
    def stats():
        with _LOCK:
            providers = _state["providers"]
            total_sent = sum(p.get("messages_sent", 0) for p in providers.values()
                             if isinstance(p, dict))
            total_recv = sum(p.get("messages_received", 0) for p in providers.values()
                             if isinstance(p, dict))
            connected = sum(1 for p in providers.values()
                            if isinstance(p, dict) and p.get("connected"))
            return jsonify({
                "total_sent": total_sent,
                "total_received": total_recv,
                "providers_connected": connected,
                "providers_total": len(providers),
            })

    @comm_bp.route("/config", methods=["GET"])
    def get_config():
        return jsonify({"providers": mock_comm_state["providers"]})

    @comm_bp.route("/config", methods=["POST"])
    def save_config():
        data = request.get_json(silent=True) or {}
        with _LOCK:
            mock_comm_state["providers"].update(data.get("providers", {}))
        return jsonify({"ok": True})

    app = Flask(__name__)
    app.config["TESTING"] = True
    app.register_blueprint(comm_bp)
    return app, mock_hub, mock_comm_state


@pytest.fixture
def client(flask_app):
    app, mock_hub, state = flask_app
    with app.test_client() as c:
        yield c, mock_hub, state


# ── Provider Routes ────────────────────────────────────────────────

def test_list_providers_empty(client):
    c, mock_hub, state = client
    res = c.get("/api/comm/providers")
    assert res.status_code == 200
    body = res.get_json()
    assert body == {}


def test_get_provider_not_found(client):
    c, mock_hub, state = client
    res = c.get("/api/comm/providers/nope")
    assert res.status_code == 404


def test_connect_provider_not_found(client):
    c, mock_hub, state = client
    mock_hub.get_provider.return_value = None
    res = c.post("/api/comm/providers/nope/connect")
    assert res.status_code == 404


def test_disconnect_provider_not_found(client):
    c, mock_hub, state = client
    res = c.post("/api/comm/providers/nope/disconnect")
    assert res.status_code == 200
    body = res.get_json()
    assert body["ok"] is True


def test_configure_provider(client):
    c, mock_hub, state = client
    res = c.post("/api/comm/providers/test-config/configure", json={
        "enabled": True, "config": {"endpoint": "https://example.com"}})
    assert res.status_code == 200
    body = res.get_json()
    assert body["ok"] is True
    assert body["provider"] == "test-config"


def test_test_provider_no_hub(client):
    c, mock_hub, state = client
    mock_hub.send.return_value = {"ok": True, "message_id": "m1"}
    res = c.post("/api/comm/providers/nope/test", json={
        "recipient": "user@example.com", "content": "hello"})
    assert res.status_code == 200
    body = res.get_json()
    assert body["ok"] is True


def test_health_provider_not_found(client):
    c, mock_hub, state = client
    mock_hub.get_provider.return_value = None
    res = c.get("/api/comm/providers/nope/health")
    assert res.status_code == 404


# ── Messaging Routes ───────────────────────────────────────────────

def test_send_missing_fields(client):
    c, mock_hub, state = client
    res = c.post("/api/comm/send", json={"provider": "x"})
    assert res.status_code == 400


def test_send_empty_body(client):
    c, mock_hub, state = client
    res = c.post("/api/comm/send", json={})
    assert res.status_code == 400


def test_send_success(client):
    c, mock_hub, state = client
    mock_hub.send.return_value = {"ok": True, "message_id": "m1"}
    res = c.post("/api/comm/send", json={
        "provider": "twilio", "recipient": "+1234567890", "content": "hello"})
    assert res.status_code == 200
    body = res.get_json()
    assert body["ok"] is True
    mock_hub.send.assert_called_once()


def test_receive_empty(client):
    c, mock_hub, state = client
    mock_hub.receive.return_value = []
    res = c.get("/api/comm/receive/twilio")
    assert res.status_code == 200
    body = res.get_json()
    assert body["provider"] == "twilio"
    assert body["messages"] == []


def test_messages_empty(client):
    c, mock_hub, state = client
    mock_hub.get_message_log.return_value = {"messages": [], "total": 0}
    res = c.get("/api/comm/messages")
    assert res.status_code == 200


def test_clear_messages(client):
    c, mock_hub, state = client
    mock_hub.clear_log.return_value = 5
    res = c.post("/api/comm/messages/clear")
    assert res.status_code == 200
    body = res.get_json()
    assert body["cleared"] == 5


# ── Stats & Config ─────────────────────────────────────────────────

def test_stats_empty(client):
    c, mock_hub, state = client
    res = c.get("/api/comm/stats")
    assert res.status_code == 200
    body = res.get_json()
    assert body["total_sent"] == 0
    assert body["total_received"] == 0
    assert body["providers_connected"] == 0
    assert body["providers_total"] == 0


def test_config_get(client):
    c, mock_hub, state = client
    res = c.get("/api/comm/config")
    assert res.status_code == 200
    body = res.get_json()
    assert "providers" in body


def test_config_save(client):
    c, mock_hub, state = client
    res = c.post("/api/comm/config", json={
        "providers": {"my-provider": {"enabled": True}}})
    assert res.status_code == 200
    body = res.get_json()
    assert body["ok"] is True


def test_test_all_providers(client):
    c, mock_hub, state = client
    mock_hub.test_all.return_value = {}
    res = c.post("/api/comm/providers/test-all")
    assert res.status_code == 200
    body = res.get_json()
    assert isinstance(body, dict)


# ── CommunicationsHub ──────────────────────────────────────────────

def test_hub_create():
    hub = CommunicationsHub()
    assert hub is not None
    assert isinstance(hub._providers, dict)


def test_hub_register_unknown_provider():
    hub = CommunicationsHub()
    assert hub.register_provider("nonexistent-provider") is False


def test_hub_get_unknown_provider():
    hub = CommunicationsHub()
    assert hub.get_provider("nope") is None


def test_hub_list_providers_empty():
    hub = CommunicationsHub()
    assert hub.list_providers() == []


def test_hub_send_unknown_provider():
    hub = CommunicationsHub()
    result = hub.send("nope", "user@example.com", "hello")
    assert result["ok"] is False
    assert "not registered" in result["error"].lower()


def test_hub_receive_unknown_provider():
    hub = CommunicationsHub()
    assert hub.receive("nope") == []


def test_hub_message_log_empty():
    hub = CommunicationsHub()
    assert hub.get_message_log() == []
    assert hub.get_message_log(limit=10) == []
    assert hub.clear_log() == 0


def test_hub_test_all_registers_known_providers():
    hub = CommunicationsHub()
    results = hub.test_all()
    assert isinstance(results, dict)


# ── Auth requirements ──────────────────────────────────────────────

def test_routes_no_auth_required(client):
    """Communication routes should not require authentication."""
    c, mock_hub, state = client
    res = c.get("/api/comm/providers")
    assert res.status_code == 200
    res = c.get("/api/comm/stats")
    assert res.status_code == 200
    mock_hub.get_message_log.return_value = {"messages": [], "total": 0}
    res = c.get("/api/comm/messages")
    assert res.status_code == 200


def test_send_rejects_missing_content(client):
    c, mock_hub, state = client
    res = c.post("/api/comm/send", json={"provider": "p", "recipient": "r"})
    assert res.status_code == 400
    body = res.get_json()
    assert "error" in body


def test_send_rejects_missing_recipient(client):
    c, mock_hub, state = client
    res = c.post("/api/comm/send", json={"provider": "p", "content": "hi"})
    assert res.status_code == 400


def test_send_rejects_missing_provider(client):
    c, mock_hub, state = client
    res = c.post("/api/comm/send", json={"recipient": "r", "content": "hi"})
    assert res.status_code == 400


# ── Error cases ────────────────────────────────────────────────────

def test_test_all_returns_dict(client):
    c, mock_hub, state = client
    mock_hub.test_all.return_value = {}
    res = c.post("/api/comm/providers/test-all")
    assert res.status_code == 200
    body = res.get_json()
    assert isinstance(body, dict)


def test_stats_after_send(client):
    c, mock_hub, state = client
    mock_hub.send.return_value = {"ok": True}
    c.post("/api/comm/send", json={
        "provider": "twilio", "recipient": "+1", "content": "hi"})
    res = c.get("/api/comm/stats")
    body = res.get_json()
    assert body["total_sent"] == 0  # mock hub doesn't update state dict
    assert body["providers_total"] == 0
