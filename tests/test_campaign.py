"""Campaign Manager API tests."""
import sys
import os

import pytest

flask = pytest.importorskip("flask")

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "dashboard"))

import backend as dash  # noqa: E402


@pytest.fixture()
def client(monkeypatch):
    dash.app.config["TESTING"] = True
    # Ensure campaign list starts empty for each test
    with dash._campaign_lock:
        dash._campaigns.clear()
    monkeypatch.setattr(dash, "CONFIG_DIR",
                        type("P", (), {"exists": lambda: True,
                                        "__truediv__": lambda s, x: type("P", (),
                                        {"exists": lambda: False})()})())
    with dash.app.test_client() as c:
        yield c
    with dash._campaign_lock:
        dash._campaigns.clear()


def test_list_campaigns_empty(client):
    res = client.get("/api/campaign")
    assert res.status_code == 200
    body = res.get_json()
    assert body["total"] == 0
    assert body["campaigns"] == []


def test_create_campaign(client):
    res = client.post("/api/campaign/create",
                      json={"name": "test-campaign", "type": "scan",
                            "targets": ["10.0.0.1"]})
    assert res.status_code == 200
    body = res.get_json()
    assert body["ok"] is True
    assert body["campaign"]["name"] == "test-campaign"
    assert body["campaign"]["type"] == "scan"
    assert body["campaign"]["status"] == "active"
    assert "id" in body["campaign"]


def test_create_campaign_defaults(client):
    res = client.post("/api/campaign/create", json={})
    assert res.status_code == 200
    body = res.get_json()
    assert body["campaign"]["type"] == "scan"
    assert body["campaign"]["name"] == "untitled-campaign"


def test_list_campaigns_after_create(client):
    client.post("/api/campaign/create", json={"name": "c1"})
    res = client.get("/api/campaign")
    body = res.get_json()
    assert body["total"] == 1
    assert body["campaigns"][0]["name"] == "c1"


def test_run_campaign_found(client):
    create = client.post("/api/campaign/create", json={"name": "run-me"})
    cid = create.get_json()["campaign"]["id"]
    res = client.post(f"/api/campaign/{cid}/run")
    assert res.status_code == 200
    body = res.get_json()
    assert body["ok"] is True
    assert body["status"] == "running"


def test_run_campaign_not_found(client):
    res = client.post("/api/campaign/nonexistent/run")
    assert res.status_code == 404
    assert "error" in res.get_json()


def test_delete_campaign(client):
    create = client.post("/api/campaign/create", json={"name": "delete-me"})
    cid = create.get_json()["campaign"]["id"]
    res = client.delete(f"/api/campaign/{cid}")
    assert res.status_code == 200
    assert res.get_json()["deleted"] == 1
    # Verify gone
    res2 = client.get("/api/campaign")
    assert res2.get_json()["total"] == 0


def test_delete_campaign_not_found(client):
    res = client.delete("/api/campaign/nonexistent")
    assert res.status_code == 200
    assert res.get_json()["deleted"] == 0


def test_multiple_campaigns(client):
    for i in range(3):
        client.post("/api/campaign/create", json={"name": f"c{i}"})
    res = client.get("/api/campaign")
    assert res.get_json()["total"] == 3


def test_campaign_targets_preserved(client):
    res = client.post("/api/campaign/create",
                      json={"name": "scoped", "targets": ["1.2.3.4", "5.6.7.8"]})
    body = res.get_json()
    assert body["campaign"]["targets"] == ["1.2.3.4", "5.6.7.8"]
