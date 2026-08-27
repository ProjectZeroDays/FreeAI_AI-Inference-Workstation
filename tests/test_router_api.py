"""Router API tests via Flask test client (mock backend, no GPU)."""
import pytest

flask = pytest.importorskip("flask")

import router as router_mod  # noqa: E402  (flat module via sys.path)


@pytest.fixture()
def client():
    router_mod.app.config["TESTING"] = True
    with router_mod.app.test_client() as c:
        yield c


def test_health(client):
    res = client.get("/health")
    assert res.status_code == 200
    assert res.get_json()["status"] == "ok"


def test_route_mock(client):
    res = client.post("/route", json={"prompt": "Build a production API"})
    assert res.status_code == 200
    body = res.get_json()
    assert body["task_type"] == "full_project"
    assert body["response"].get("mock") is True
    assert res.headers["X-Cache"] == "MISS"


def test_cache_hit_on_repeat(client):
    payload = {"prompt": "cache probe unique prompt"}
    first = client.post("/route", json=payload)
    second = client.post("/route", json=payload)
    assert first.status_code == second.status_code == 200
    assert first.headers["X-Cache"] == "MISS"
    assert second.headers["X-Cache"] == "HIT"
    assert first.get_json() == second.get_json()


def test_empty_prompt_rejected(client):
    res = client.post("/route", json={"prompt": ""})
    assert res.status_code == 400


def test_metrics_endpoint(client):
    client.post("/route", json={"prompt": "metrics probe prompt xyz"})
    res = client.get("/metrics")
    assert res.status_code == 200
    body = res.get_json()
    assert body["requests_total"] >= 1
    assert "latency_avg_ms" in body


def test_models_listing(client):
    res = client.get("/models")
    assert res.status_code == 200
    models = res.get_json()
    local = {k for k, v in models.items()
             if not k.startswith(("openai/", "anthropic/", "google/"))}
    assert {"qwen3.6-12b", "moe-13b", "qwen3.5-9b"} <= local
    # provider models merged when keys present (see test_providers.py)
