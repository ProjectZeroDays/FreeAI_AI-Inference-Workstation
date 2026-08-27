"""MCP Registry API tests."""
import sys
import os
import json

import pytest

flask = pytest.importorskip("flask")

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "dashboard"))

import backend as dash  # noqa: E402


@pytest.fixture()
def client(tmp_path, monkeypatch):
    dash.app.config["TESTING"] = True
    monkeypatch.setattr(dash, "MCP_DIR", tmp_path)
    (tmp_path / "servers").mkdir()
    with dash.app.test_client() as c:
        yield c


def test_mcp_list_empty(client):
    res = client.get("/api/mcp")
    assert res.status_code == 200
    body = res.get_json()
    assert body["total"] == 0
    assert body["servers"] == []


def test_mcp_list_discovers_dirs(client):
    server_dir = dash.MCP_DIR / "servers" / "my-server"
    server_dir.mkdir(parents=True)
    (server_dir / "SKILL.md").write_text("---\ndescription: My MCP server\n---\nBody")

    res = client.get("/api/mcp")
    body = res.get_json()
    assert body["total"] == 1
    assert body["servers"][0]["name"] == "my-server"
    assert "My MCP server" in body["servers"][0]["description"]
    assert body["servers"][0]["enabled"] is True


def test_mcp_list_multiple(client):
    server_dir = dash.MCP_DIR / "servers"
    for name in ["auth", "filesystem", "database"]:
        d = server_dir / name
        d.mkdir()
        (d / "SKILL.md").write_text(f"---\ndescription: {name} server\n---\nbody")

    res = client.get("/api/mcp")
    body = res.get_json()
    assert body["total"] == 3
    names = {s["name"] for s in body["servers"]}
    assert names == {"auth", "filesystem", "database"}


def test_mcp_register_valid(client):
    res = client.post("/api/mcp/register",
                      json={"name": "test-server", "command": "node", "args": ["index.js"]})
    assert res.status_code == 200
    body = res.get_json()
    assert body["ok"] is True
    assert body["server"]["name"] == "test-server"
    assert body["server"]["command"] == "node"


def test_mcp_register_missing_name(client):
    res = client.post("/api/mcp/register", json={"command": "node"})
    assert res.status_code == 400
    assert "error" in res.get_json()


def test_mcp_register_missing_command(client):
    res = client.post("/api/mcp/register", json={"name": "foo"})
    assert res.status_code == 400
    assert "error" in res.get_json()


def test_mcp_register_both_missing(client):
    res = client.post("/api/mcp/register", json={})
    assert res.status_code == 400


def test_mcp_no_skill_md(client):
    """Directories without SKILL.md are still counted."""
    server_dir = dash.MCP_DIR / "servers" / "no-skill"
    server_dir.mkdir(parents=True)

    res = client.get("/api/mcp")
    body = res.get_json()
    assert body["total"] == 1
    assert body["servers"][0]["description"] == ""
