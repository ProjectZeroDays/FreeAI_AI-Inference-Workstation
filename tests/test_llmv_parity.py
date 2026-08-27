"""llmv-parity dashboard tests: auth gate, upload, clients switchboard."""
import io as _io
import os

import pytest

flask = pytest.importorskip("flask")

from dashboard import backend as dash  # noqa: E402


@pytest.fixture()
def client(tmp_path, monkeypatch):
    monkeypatch.setattr(dash, "UPLOAD_DIR", str(tmp_path / "uploads"))
    monkeypatch.setattr(dash, "AUTH_TOKEN", "")
    monkeypatch.setattr(dash, "OPT_SETTINGS_PATH",
                        str(tmp_path / "runtime-settings.json"))
    dash.app.config["TESTING"] = True
    with dash.app.test_client() as c:
        yield c


def test_upload_and_list(client):
    data = {"file": (_io.BytesIO(b"hello world"), "notes.txt")}
    res = client.post("/api/upload", data=data,
                      content_type="multipart/form-data")
    assert res.status_code == 200
    assert res.get_json()["name"] == "notes.txt"

    lst = client.get("/api/uploads").get_json()["uploads"]
    assert lst == [{"name": "notes.txt", "bytes": 11}]


def test_upload_sanitizes_names(client):
    data = {"file": (_io.BytesIO(b"x"), "../../etc/passwd")}
    res = client.post("/api/upload", data=data,
                      content_type="multipart/form-data")
    assert res.status_code == 200
    assert res.get_json()["name"] == "passwd"


def test_upload_requires_file(client):
    res = client.post("/api/upload", data={},
                      content_type="multipart/form-data")
    assert res.status_code == 400


def test_clients_switchboard(tmp_path, monkeypatch):
    import json as _json
    root = tmp_path / "stack"
    base = root / "mimocode"
    base.mkdir(parents=True)
    (base / "clients.json").write_text(_json.dumps({
        "clients": [{"id": "opencode", "name": "OpenCode",
                     "port": 3000, "enabled": True}]}))
    (base / "desktop.json").write_text(_json.dumps({
        "id": "mimocode-desktop", "name": "MimoCode Desktop",
        "port": 6080, "enabled": True, "url": "/desktop"}))

    monkeypatch.setattr(dash, "ROOT_DIR", str(root))
    dash.app.config["TESTING"] = True
    with dash.app.test_client() as c:
        res = c.get("/api/clients")
    ids = [c["id"] for c in res.get_json()["clients"]]
    assert "opencode" in ids and "mimocode-desktop" in ids


def test_auth_gate_blocks_writes_when_enabled(tmp_path, monkeypatch):
    monkeypatch.setattr(dash, "AUTH_TOKEN", "sekret")
    monkeypatch.setattr(dash, "OPT_SETTINGS_PATH",
                        str(tmp_path / "runtime-settings.json"))
    dash.app.config["TESTING"] = True
    with dash.app.test_client() as c:
        res = c.post("/api/settings", json={"auto_management": False})
        assert res.status_code == 401

        res = c.post("/api/settings", json={"auto_management": False},
                     headers={"X-Auth-Token": "sekret"})
        assert res.status_code == 200

        # reads stay open
        assert c.get("/api/settings").status_code == 200
        assert c.get("/api/status").status_code == 200
