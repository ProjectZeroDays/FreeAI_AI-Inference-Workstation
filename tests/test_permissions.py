"""Permissions engine tests."""
import sys
import os

import pytest

flask = pytest.importorskip("flask")

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "dashboard"))

import backend as dash  # noqa: E402


@pytest.fixture()
def client():
    dash.app.config["TESTING"] = True
    with dash.app.test_client() as c:
        yield c


def test_permissions_endpoint(client):
    res = client.get("/api/permissions")
    assert res.status_code == 200
    body = res.get_json()
    assert "roles" in body
    assert "current_role" in body
    assert body["current_role"] == "admin"
    assert body["rbac_enabled"] is True


def test_admin_can_everything(client):
    res = client.post("/api/permissions/check",
                      json={"resource": "delete", "action": "exec", "role": "admin"})
    body = res.get_json()
    assert body["allowed"] is True


def test_viewer_can_read(client):
    res = client.post("/api/permissions/check",
                      json={"resource": "config", "action": "read", "role": "viewer"})
    body = res.get_json()
    assert body["allowed"] is True


def test_viewer_cannot_write(client):
    res = client.post("/api/permissions/check",
                      json={"resource": "config", "action": "write", "role": "viewer"})
    body = res.get_json()
    assert body["allowed"] is False


def test_operator_can_exec(client):
    res = client.post("/api/permissions/check",
                      json={"resource": "run", "action": "exec", "role": "operator"})
    body = res.get_json()
    assert body["allowed"] is True


def test_guest_restricted(client):
    res = client.post("/api/permissions/check",
                      json={"resource": "secret", "action": "write", "role": "guest"})
    body = res.get_json()
    assert body["allowed"] is False


def test_default_role_is_admin(client):
    res = client.post("/api/permissions/check",
                      json={"resource": "x", "action": "write"})
    body = res.get_json()
    assert body["role"] == "admin"
    assert body["allowed"] is True


def test_check_returns_resource_and_action(client):
    res = client.post("/api/permissions/check",
                      json={"resource": "models", "action": "deploy", "role": "admin"})
    body = res.get_json()
    assert body["resource"] == "models"
    assert body["action"] == "deploy"
    assert body["role"] == "admin"


def test_wildcard_role_allows_any(client):
    res = client.post("/api/permissions/check",
                      json={"resource": "anything", "action": "anything", "role": "admin"})
    body = res.get_json()
    assert body["allowed"] is True
