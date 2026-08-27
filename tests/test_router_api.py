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
    # Cache may be HIT or MISS depending on test order
    assert res.headers.get("X-Cache") in ("MISS", "HIT")


def test_cache_hit_on_repeat(client):
    payload = {"prompt": "cache probe unique prompt"}
    first = client.post("/route", json=payload)
    second = client.post("/route", json=payload)
    assert first.status_code == second.status_code == 200
    assert first.headers["X-Cache"] == "MISS"
    assert second.headers["X-Cache"] == "HIT"
    # trace_id is unique per-request; compare everything else
    b1 = {k: v for k, v in first.get_json().items() if k != "trace_id"}
    b2 = {k: v for k, v in second.get_json().items() if k != "trace_id"}
    assert b1 == b2


def test_empty_prompt_rejected(client):
    res = client.post("/route", json={"prompt": ""})
    assert res.status_code == 400


def test_metrics_endpoint(client):
    client.post("/route", json={"prompt": "metrics probe prompt xyz"})
    res = client.get("/metrics")
    assert res.status_code == 200
    # /metrics may return Prometheus text or JSON depending on availability
    if res.mimetype == "text/plain":
        assert "requests_total" in res.get_data(as_text=True)
    else:
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


def test_api_traces_endpoint(client):
    """GET /api/traces returns list of recent traces."""
    res = client.post("/route", json={"prompt": "trace probe prompt"})
    assert res.status_code == 200
    body = res.get_json()
    assert "trace_id" in body
    tid = body["trace_id"]

    res2 = client.get("/api/traces")
    assert res2.status_code == 200
    traces = res2.get_json()
    assert "traces" in traces
    assert len(traces["traces"]) >= 1
    assert traces["traces"][0]["trace_id"] == tid
    assert traces["traces"][0]["task_type"] == "general_code"
    assert traces["traces"][0]["model_used"] == "qwen3.6-12b"
    assert traces["traces"][0]["status"] == "ok"
    assert traces["traces"][0]["latency_ms"] >= 0
