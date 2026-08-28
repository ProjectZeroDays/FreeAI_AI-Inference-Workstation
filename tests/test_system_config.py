"""Tests for system configuration features: DDNS, Network Auto, Cards Settings."""
import pytest

flask = pytest.importorskip("flask")

from dashboard import backend as dash


@pytest.fixture()
def client(tmp_path, monkeypatch):
    monkeypatch.setattr(dash, "CONFIG_DIR", tmp_path)
    monkeypatch.setattr(dash, "OPT_SETTINGS_PATH", str(tmp_path / "runtime-settings.json"))
    dash.app.config["TESTING"] = True
    # Reset shared state
    with dash._DDNS_LOCK:
        dash._DDNS_RECORDS.clear()
        dash._DDNS_RECORDS.append({
            "id": "1", "type": "A", "hostname": "freeai.home",
            "value": "192.168.1.100", "ttl": 300, "status": "active",
        })
        dash._DDNS_PROVIDER.update({"service": "no-ip", "username": "", "hostname": "freeai.ddns.net", "auto_refresh": True})
    with dash._NETWORK_LOCK:
        dash._NETWORK_STATE.update({
            "vpn": {"enabled": False, "provider": "auto", "status": "disconnected"},
            "tor": {"enabled": False, "circuit": "auto", "status": "stopped"},
            "dnscrypt": {"enabled": False, "resolver": "cloudflare", "status": "stopped"},
            "quality": {"latency_ms": 0, "bandwidth_up": 0, "bandwidth_down": 0, "packet_loss": 0},
        })
    with dash._CARDS_LOCK:
        dash._CARDS_CONFIG.clear()
        dash._CARDS_CONFIG.update({
            "loot": {"title": "Loot", "icon": "💎", "auto_refresh": True, "refresh_interval": 30},
            "c2": {"title": "C2", "icon": "📡", "auto_refresh": True, "refresh_interval": 15},
            "browser-v2": {"title": "Browser", "icon": "🌐", "auto_refresh": False, "refresh_interval": 60},
            "security": {"title": "Security", "icon": "🛡", "auto_refresh": True, "refresh_interval": 30},
            "subagents": {"title": "Subagents", "icon": "🤖", "auto_refresh": True, "refresh_interval": 10},
        })
    with dash.app.test_client() as c:
        yield c


# ── DDNS Management ──────────────────────────────────────────────

def test_ddns_manager_page(client):
    res = client.get("/ddns-manager")
    assert res.status_code == 200
    assert b"DDNS Manager" in res.data


def test_api_ddns_status(client):
    res = client.get("/api/ddns/status")
    assert res.status_code == 200
    body = res.get_json()
    assert body["provider"] == "no-ip"
    assert body["hostname"] == "freeai.ddns.net"
    assert body["auto_refresh"] is True
    assert body["records_count"] == 1


def test_api_ddns_records(client):
    res = client.get("/api/ddns/records")
    assert res.status_code == 200
    body = res.get_json()
    assert isinstance(body, list)
    assert len(body) == 1
    assert body[0]["type"] == "A"


def test_api_ddns_update_record(client):
    res = client.put("/api/ddns/records/1", json={"value": "10.0.0.1", "ttl": 600})
    assert res.status_code == 200
    body = res.get_json()
    assert body["ok"] is True
    assert body["record"]["value"] == "10.0.0.1"
    assert body["record"]["ttl"] == 600


def test_api_ddns_update_record_not_found(client):
    res = client.put("/api/ddns/records/999", json={"value": "1.2.3.4"})
    assert res.status_code == 404


def test_api_ddns_provision(client):
    res = client.post("/api/ddns/provision", json={
        "type": "CNAME", "hostname": "api.freeai.ddns.net", "value": "10.0.0.5", "ttl": 120,
    })
    assert res.status_code == 200
    body = res.get_json()
    assert body["ok"] is True
    assert body["record"]["type"] == "CNAME"
    assert body["record"]["hostname"] == "api.freeai.ddns.net"
    assert body["record"]["status"] == "active"


def test_api_ddns_sync(client):
    res = client.get("/api/ddns/sync")
    assert res.status_code == 200
    body = res.get_json()
    assert body["synced"] is True
    assert "records" in body
    assert "ts" in body


# ── Network Auto-Management ──────────────────────────────────────

def test_network_auto_page(client):
    res = client.get("/network-auto")
    assert res.status_code == 200
    assert b"Network Auto" in res.data


def test_api_network_status(client):
    res = client.get("/api/network/status")
    assert res.status_code == 200
    body = res.get_json()
    assert "vpn" in body
    assert "tor" in body
    assert "dnscrypt" in body
    assert "quality" in body
    assert body["vpn"]["enabled"] is False


def test_api_network_vpn_toggle(client):
    res = client.post("/api/network/vpn/toggle", json={})
    assert res.status_code == 200
    body = res.get_json()
    assert body["ok"] is True
    assert body["vpn"]["enabled"] is True
    assert body["vpn"]["status"] == "connected"

    # Toggle again to turn off
    res = client.post("/api/network/vpn/toggle", json={})
    body = res.get_json()
    assert body["vpn"]["enabled"] is False
    assert body["vpn"]["status"] == "disconnected"


def test_api_network_vpn_toggle_with_provider(client):
    res = client.post("/api/network/vpn/toggle", json={"provider": "mullvad"})
    assert res.status_code == 200
    body = res.get_json()
    assert body["vpn"]["provider"] == "mullvad"


def test_api_network_tor_circuit(client):
    res = client.post("/api/network/tor/circuit", json={"enabled": True, "circuit": "us-de-fr"})
    assert res.status_code == 200
    body = res.get_json()
    assert body["ok"] is True
    assert body["tor"]["enabled"] is True
    assert body["tor"]["circuit"] == "us-de-fr"
    assert body["tor"]["status"] == "active"


def test_api_network_tor_circuit_disable(client):
    res = client.post("/api/network/tor/circuit", json={"enabled": False})
    assert res.status_code == 200
    body = res.get_json()
    assert body["tor"]["enabled"] is False
    assert body["tor"]["status"] == "stopped"


def test_api_network_quality(client):
    res = client.get("/api/network/quality")
    assert res.status_code == 200
    body = res.get_json()
    assert "latency_ms" in body
    assert "bandwidth_up" in body
    assert "bandwidth_down" in body
    assert "packet_loss" in body
    assert "ts" in body


def test_api_network_optimize(client):
    res = client.post("/api/network/optimize", json={})
    assert res.status_code == 200
    body = res.get_json()
    assert body["ok"] is True
    assert "quality" in body
    assert body["quality"]["latency_ms"] >= 0


# ── Cards Settings API ──────────────────────────────────────────

def test_api_cards_settings_all(client):
    res = client.get("/api/cards/settings")
    assert res.status_code == 200
    body = res.get_json()
    assert "loot" in body
    assert "c2" in body
    assert "browser-v2" in body
    assert "security" in body
    assert "subagents" in body
    assert body["loot"]["title"] == "Loot"
    assert body["loot"]["icon"] == "\U0001F48E"


def test_api_cards_settings_get(client):
    res = client.get("/api/cards/settings/c2")
    assert res.status_code == 200
    body = res.get_json()
    assert body["title"] == "C2"
    assert body["icon"] == "\U0001F4E1"
    assert body["auto_refresh"] is True
    assert body["refresh_interval"] == 15


def test_api_cards_settings_get_not_found(client):
    res = client.get("/api/cards/settings/nonexistent")
    assert res.status_code == 404


def test_api_cards_settings_update(client):
    res = client.put("/api/cards/settings/loot", json={
        "title": "Harvested Loot",
        "icon": "💰",
        "auto_refresh": False,
        "refresh_interval": 45,
    })
    assert res.status_code == 200
    body = res.get_json()
    assert body["ok"] is True
    assert body["config"]["title"] == "Harvested Loot"
    assert body["config"]["icon"] == "\U0001F4B0"
    assert body["config"]["auto_refresh"] is False
    assert body["config"]["refresh_interval"] == 45


def test_api_cards_settings_update_not_found(client):
    res = client.put("/api/cards/settings/nonexistent", json={"title": "test"})
    assert res.status_code == 404


def test_api_cards_settings_partial_update(client):
    res = client.put("/api/cards/settings/security", json={"refresh_interval": 60})
    assert res.status_code == 200
    body = res.get_json()
    assert body["config"]["refresh_interval"] == 60
    # Other fields should remain
    assert body["config"]["title"] == "Security"


def test_cards_settings_persistence(client):
    """Verify that an update persists and is readable on subsequent GET."""
    client.put("/api/cards/settings/subagents", json={"title": "AI Workers", "refresh_interval": 20})
    res = client.get("/api/cards/settings/subagents")
    body = res.get_json()
    assert body["title"] == "AI Workers"
    assert body["refresh_interval"] == 20
