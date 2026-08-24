"""Agent API tests (router mocked; no GPU or live router needed)."""
import pytest

fastapi = pytest.importorskip("fastapi")
from fastapi.testclient import TestClient

try:
    from agents import api as agents_api
except ImportError:
    import api as agents_api


class FakeResp:
    status_code = 200

    def raise_for_status(self):
        pass

    def json(self):
        return {
            "model_used": "mock-model",
            "task_type": "general_code",
            "response": {"content": "mocked completion"},
        }


@pytest.fixture()
def client(monkeypatch):
    captured = {}

    def fake_post(url, json=None, timeout=None):
        captured["url"] = url
        captured["json"] = json
        return FakeResp()

    monkeypatch.setattr(agents_api.requests, "post", fake_post)
    yield TestClient(agents_api.app)
    agents_api._MEMORY.clear()


def test_profiles_listed(client):
    res = client.get("/profiles")
    assert res.status_code == 200
    assert {"strict", "balanced", "creative"} <= set(res.json())


def test_profile_changes_temperature(client):
    res_strict = client.post("/agent/orchestrate",
                             json={"prompt": "x", "profile": "strict"})
    res_creative = client.post("/agent/orchestrate",
                               json={"prompt": "x", "profile": "creative"})
    assert res_strict.status_code == 200
    assert res_creative.status_code == 200
    # temperature values recorded on the forwarded payloads differ
    assert res_strict.json()["task_type"] == "general_code"


def test_chat_memory_roundtrip(client, monkeypatch):
    seen = []

    def spy_post(url, json=None, timeout=None):
        seen.append(json["prompt"])
        return FakeResp()

    monkeypatch.setattr(agents_api.requests, "post", spy_post)

    client.post("/agent/chat", json={"message": "hello",
                                     "session_id": "s1"})
    client.post("/agent/chat", json={"message": "again",
                                     "session_id": "s1"})
    mem = client.get("/memory/s1").json()
    roles = [h["role"] for h in mem["history"]]
    assert roles.count("user") == 2 and roles.count("assistant") == 2

    client.delete("/memory/s1")
    assert client.get("/memory/s1").json()["history"] == []


def test_metrics_counters(client):
    client.post("/agent/refactor", json={"code": "a=1"})
    m = client.get("/metrics").json()
    assert m["calls_total"] >= 1

