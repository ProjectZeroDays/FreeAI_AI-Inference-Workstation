"""MCP Server authentication tests."""

import sys
import os
import pytest

flask = pytest.importorskip("flask")

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "mcp"))

import server as mcp_server  # noqa: E402


@pytest.fixture()
def client_no_auth(monkeypatch):
    """MCP server with no authentication required."""
    monkeypatch.setenv("MCP_API_KEY", "")
    mcp_server.MCP_API_KEY = ""
    mcp_server.app.config["TESTING"] = True
    with mcp_server.app.test_client() as c:
        yield c


@pytest.fixture()
def client_with_auth(monkeypatch):
    """MCP server with authentication required."""
    monkeypatch.setenv("MCP_API_KEY", "test-secret-key")
    mcp_server.MCP_API_KEY = "test-secret-key"
    mcp_server.app.config["TESTING"] = True
    with mcp_server.app.test_client() as c:
        yield c


def test_health_no_auth_required(client_with_auth):
    """Health endpoint should not require authentication."""
    res = client_with_auth.get("/health")
    assert res.status_code == 200
    body = res.get_json()
    assert body["status"] == "ok"
    assert body["auth_required"] is True


def test_health_shows_auth_status(client_no_auth):
    """Health endpoint should indicate if auth is required."""
    res = client_no_auth.get("/health")
    assert res.status_code == 200
    body = res.get_json()
    assert body["status"] == "ok"
    assert body["auth_required"] is False


def test_tools_no_auth_when_disabled(client_no_auth):
    """Tools endpoint should work without auth when MCP_API_KEY is not set."""
    res = client_no_auth.get("/mcp/tools")
    assert res.status_code == 200
    body = res.get_json()
    assert "tools" in body
    assert isinstance(body["tools"], list)


def test_tools_requires_auth_when_enabled(client_with_auth):
    """Tools endpoint should require auth when MCP_API_KEY is set."""
    res = client_with_auth.get("/mcp/tools")
    assert res.status_code == 401
    body = res.get_json()
    assert body["error"] == "unauthorized"


def test_tools_with_valid_api_key_header(client_with_auth):
    """Tools endpoint should accept valid X-API-Key header."""
    res = client_with_auth.get("/mcp/tools", headers={"X-API-Key": "test-secret-key"})
    assert res.status_code == 200
    body = res.get_json()
    assert "tools" in body


def test_tools_with_valid_auth_token_header(client_with_auth):
    """Tools endpoint should accept valid X-Auth-Token header."""
    res = client_with_auth.get(
        "/mcp/tools", headers={"X-Auth-Token": "test-secret-key"}
    )
    assert res.status_code == 200
    body = res.get_json()
    assert "tools" in body


def test_tools_with_valid_bearer_token(client_with_auth):
    """Tools endpoint should accept valid Authorization Bearer token."""
    res = client_with_auth.get(
        "/mcp/tools", headers={"Authorization": "Bearer test-secret-key"}
    )
    assert res.status_code == 200
    body = res.get_json()
    assert "tools" in body


def test_tools_with_invalid_api_key(client_with_auth):
    """Tools endpoint should reject invalid API key."""
    res = client_with_auth.get("/mcp/tools", headers={"X-API-Key": "wrong-key"})
    assert res.status_code == 401
    body = res.get_json()
    assert body["error"] == "unauthorized"


def test_call_requires_auth_when_enabled(client_with_auth):
    """Call endpoint should require auth when MCP_API_KEY is set."""
    res = client_with_auth.post("/mcp/call", json={"tool": "route", "args": {}})
    assert res.status_code == 401
    body = res.get_json()
    assert body["error"] == "unauthorized"


def test_call_no_auth_when_disabled(client_no_auth, monkeypatch):
    """Call endpoint should work without auth when MCP_API_KEY is not set."""

    # Mock requests.post to avoid actual network calls
    class MockResponse:
        def __init__(self):
            self.status_code = 200

        def json(self):
            return {"result": "ok"}

    def mock_post(*args, **kwargs):
        return MockResponse()

    monkeypatch.setattr("server.requests.post", mock_post)

    res = client_no_auth.post(
        "/mcp/call", json={"tool": "route", "args": {"prompt": "test"}}
    )
    # Should not get 401 (may get 200 or other status from mock)
    assert res.status_code != 401


def test_call_with_valid_auth(client_with_auth, monkeypatch):
    """Call endpoint should accept valid authentication."""

    # Mock requests.post to avoid actual network calls
    class MockResponse:
        def __init__(self):
            self.status_code = 200

        def json(self):
            return {"result": "ok"}

    def mock_post(*args, **kwargs):
        return MockResponse()

    monkeypatch.setattr("server.requests.post", mock_post)

    res = client_with_auth.post(
        "/mcp/call",
        json={"tool": "route", "args": {"prompt": "test"}},
        headers={"X-API-Key": "test-secret-key"},
    )
    assert res.status_code == 200


def test_call_unknown_tool(client_no_auth):
    """Call endpoint should reject unknown tools."""
    res = client_no_auth.post("/mcp/call", json={"tool": "unknown", "args": {}})
    assert res.status_code == 400
    body = res.get_json()
    assert body["error"] == "unknown tool"
