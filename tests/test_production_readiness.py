"""Integration tests for desktop noVNC, Salad GPU sync, and resource quotas."""
import json
import os
import sys
import tempfile
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))


# ── Desktop / noVNC integration ───────────────────────────────────────

def test_novnc_script_exists_and_is_valid():
    """The noVNC startup script exists and contains valid bash."""
    script = ROOT / "desktop" / "start_novnc.sh"
    assert script.exists()
    content = script.read_text()
    assert "websockify" in content
    assert "6080" in content
    assert "5901" in content


def test_vnc_script_exists():
    """The VNC startup script exists."""
    script = ROOT / "desktop" / "start_vnc.sh"
    assert script.exists()


def test_xfce_script_exists():
    """The XFCE startup script exists."""
    script = ROOT / "desktop" / "start_xfce.sh"
    assert script.exists()


def test_docker_compose_desktop_profile_requires_password():
    """docker-compose.yml desktop service uses ${VAR:?} pattern."""
    compose = ROOT / "docker-compose.yml"
    content = compose.read_text()
    assert "DESKTOP_VNC_PASSWORD" in content
    # Should use the require-syntax, not a plain default
    assert ":?DESKTOP_VNC_PASSWORD" in content or ":?VNC_PASSWORD" in content


def test_docker_compose_grafana_requires_password():
    """Grafana must not fall back to default 'admin' password."""
    compose = ROOT / "docker-compose.yml"
    content = compose.read_text()
    # The old insecure default should be gone
    assert 'GRAFANA_ADMIN_PASSWORD:-admin' not in content
    assert "GRAFANA_ADMIN_PASSWORD" in content


# ── Salad GPU earnings sync ───────────────────────────────────────────

def test_salad_config_endpoint_works_with_empty_key():
    """Salad config endpoint returns configured=False when no key."""
    from dashboard import backend as dash
    dash.app.config["TESTING"] = True
    with dash.app.test_client() as c:
        res = c.get("/api/salad/config")
        assert res.status_code == 200
        body = res.get_json()
        assert body["configured"] is False


def test_salad_data_endpoint_returns_mock_when_no_key():
    """Without API key, Salad returns mock data, not an error."""
    from dashboard import backend as dash
    dash.app.config["TESTING"] = True
    with dash.app.test_client() as c:
        res = c.get("/api/salad")
        assert res.status_code == 200
        body = res.get_json()
        assert body["mock"] is True
        assert "data" in body


# ── Resource quota enforcement ────────────────────────────────────────

def test_docker_compose_has_resource_limits():
    """Key services declare deploy.resource limits in compose."""
    compose = ROOT / "docker-compose.yml"
    content = compose.read_text()
    # At minimum router and agents should have memory/cpu limits
    assert "limits:" in content
    assert "memory:" in content
    assert "cpus:" in content


def test_docker_compose_no_hardcoded_secrets():
    """No plaintext passwords or API keys should appear in compose."""
    compose = ROOT / "docker-compose.yml"
    content = compose.read_text()
    forbidden = ["PASSWORD=pass", "PASSWORD='pass'", "ADMIN_PASSWORD=admin",
                 "API_KEY=sk-", "TOKEN=ghp_"]
    for pattern in forbidden:
        assert pattern not in content, f"Found hardcoded secret pattern: {pattern}"


def test_env_example_has_required_secrets_section():
    """.env.example documents production-required secrets."""
    env_example = ROOT / ".env.example"
    content = env_example.read_text()
    assert "DESKTOP_VNC_PASSWORD" in content
    assert "GRAFANA_ADMIN_PASSWORD" in content
    assert "ROUTER_API_KEY" in content


# ── Circuit breaker edge cases ────────────────────────────────────────

def test_circuit_breaker_sliding_window_env_vars():
    """Router reads circuit breaker env vars from docker-compose."""
    sys.path.insert(0, str(ROOT / "router"))
    from load_balancer import CB_WINDOW_SIZE, CB_RATIO_THRESHOLD, CB_MIN_REQUESTS
    assert CB_WINDOW_SIZE > 0
    assert 0.0 < CB_RATIO_THRESHOLD <= 1.0
    assert CB_MIN_REQUESTS > 0


def test_circuit_breaker_recovery_clears_window(monkeypatch):
    """After recovery, the outcome window is cleared."""
    sys.path.insert(0, str(ROOT / "router"))
    import load_balancer as lb
    monkeypatch.setattr(lb, "FAILURE_THRESHOLD", 3)
    monkeypatch.setattr(lb, "CB_RATIO_THRESHOLD", 0.9)
    monkeypatch.setattr(lb, "CB_MIN_REQUESTS", 100)
    lb.reset_state()
    key = "a@http://x"
    lb.get_state(key)  # prime
    # 3 consecutive failures trip via consecutive threshold
    for _ in range(3):
        lb.record_failure(key)
    assert lb.get_state(key)["healthy"] is False
    # A success should clear the window and reset
    lb.record_success(key)
    state = lb.get_state(key)
    assert state["healthy"] is True
    assert state["circuit_open_until"] == 0.0
    # Window should contain only the success
    assert len(lb._outcomes.get(key, [])) == 1


# ── HITL + GODMODE campaign integration ───────────────────────────────

def test_godmode_campaign_rejects_destructive_without_approval(tmp_path, monkeypatch):
    """GODMODE campaign should request approval for destructive actions."""
    import autonomous.approval as hitl
    import agents.godmode as godmode
    monkeypatch.setattr(hitl, "CONFIG_DIR", tmp_path)
    monkeypatch.setattr(hitl, "HITL_STATE_PATH", tmp_path / "hitl.json")
    monkeypatch.setenv("HITL_ENABLED", "1")
    monkeypatch.setattr(hitl, "HITL_ENABLED", True)
    monkeypatch.setattr(godmode, "CONFIG_DIR", tmp_path)
    hitl._PENDING.clear()
    godmode._save_state({"enabled": True, "campaign_mode": True,
                          "campaign_name": "test-campaign",
                          "permissions_override": True,
                          "created_at": 0, "updated_at": 0})

    # Check that a dangerous command triggers an approval request
    req = hitl.check_approval_required("rm -rf /critical/data", "campaign test-campaign")
    assert req is not None
    assert req["status"] == "pending"
    assert "file_deletion" in req["danger_patterns"]

    # Without approval, is_approved returns False
    assert hitl.is_approved(req["request_id"]) is False

    # After approval, it returns True
    hitl.approve_request(req["request_id"], "operator")
    assert hitl.is_approved(req["request_id"]) is True
