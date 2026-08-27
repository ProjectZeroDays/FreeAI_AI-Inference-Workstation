"""Integration tests: full request flows, error handling, and concurrent requests.

Tests the complete pipeline: /route → classification → agent dispatch → response.
Uses the Flask test client with MOCK_LLM=1 so no GPU or live backend is needed.
"""
import json
import os
import sys
import threading
import time

import pytest

flask = pytest.importorskip("flask")

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "router"))

import router as router_mod  # noqa: E402
from workflow.validator import validate_workflow  # noqa: E402
from workflow.engine import from_definition  # noqa: E402


@pytest.fixture()
def client():
    router_mod.app.config["TESTING"] = True
    with router_mod.app.test_client() as c:
        yield c


# ── full request flows ───────────────────────────────────────────────────

def test_route_full_flow_yields_expected_keys(client):
    """A successful /route call returns model_used, task_type, confidence, response."""
    res = client.post("/route", json={
        "prompt": "Build a production API service with docker and kubernetes",
        "max_tokens": 128,
    })
    assert res.status_code == 200
    body = res.get_json()
    assert "model_used" in body
    assert "task_type" in body
    assert "confidence" in body
    assert "response" in body
    assert body["task_type"] == "full_project"
    assert isinstance(body["confidence"], float)
    assert 0 < body["confidence"] <= 1.0


def test_route_stream_endpoint(client):
    """POST /route/stream returns SSE frames."""
    res = client.post("/route/stream", json={
        "prompt": "explain how hashing works",
        "max_tokens": 64,
    })
    assert res.status_code == 200
    assert "text/event-stream" in res.content_type
    assert b"data:" in res.data


def test_route_with_agent_override(client):
    """Explicit agent param is passed through to the classification chain."""
    res = client.post("/route", json={
        "prompt": "refactor this code for performance",
        "agent": "code-specialist",
        "max_tokens": 64,
    })
    assert res.status_code == 200
    body = res.get_json()
    assert body["task_type"] == "refactor"


def test_route_with_explicit_model(client):
    """Explicit model param does not crash and returns a response."""
    res = client.post("/route", json={
        "prompt": "hello world",
        "model": "qwen3.6-12b",
        "max_tokens": 32,
    })
    assert res.status_code == 200
    body = res.get_json()
    assert "response" in body


# ── error handling ───────────────────────────────────────────────────────

def test_route_empty_prompt_returns_400(client):
    res = client.post("/route", json={})
    assert res.status_code == 400
    body = res.get_json()
    assert "error" in body


def test_route_empty_string_prompt_returns_400(client):
    res = client.post("/route", json={"prompt": ""})
    assert res.status_code == 400


def test_route_missing_content_type(client):
    """POST without JSON body should not crash."""
    res = client.post("/route", data="not-json")
    # Flask returns 400 for invalid JSON
    assert res.status_code in (400, 415, 500)


def test_health_returns_ok(client):
    res = client.get("/health")
    assert res.status_code == 200
    body = res.get_json()
    assert body["status"] == "ok"


def test_models_endpoint_returns_registry(client):
    res = client.get("/models")
    assert res.status_code == 200
    models = res.get_json()
    assert isinstance(models, dict)
    assert len(models) > 0


def test_metrics_endpoint_after_requests(client):
    client.post("/route", json={"prompt": "metrics probe unique prompt"})
    res = client.get("/metrics")
    assert res.status_code == 200
    body = res.get_json()
    assert body["requests_total"] >= 1
    assert "latency_avg_ms" in body


# ── concurrent requests ─────────────────────────────────────────────────

def test_concurrent_route_requests():
    """Fire 30 requests concurrently; all should succeed."""
    errors = []
    results = []
    lock = threading.Lock()

    def hit(idx):
        try:
            router_mod.app.config["TESTING"] = True
            with router_mod.app.test_client() as c:
                res = c.post("/route", json={
                    "prompt": f"concurrent integration test {idx} — classify this",
                    "max_tokens": 64,
                })
            with lock:
                results.append(res.status_code)
        except Exception as exc:
            with lock:
                errors.append(str(exc))

    threads = [threading.Thread(target=hit, args=(i,)) for i in range(30)]
    for t in threads:
        t.start()
    for t in threads:
        t.join(timeout=30)

    assert len(errors) == 0, f"Concurrent errors: {errors[:5]}"
    assert len(results) == 30
    assert all(code == 200 for code in results)


def test_concurrent_stream_requests():
    """Stream endpoint under concurrent load."""
    results = []
    lock = threading.Lock()

    def hit(idx):
        try:
            router_mod.app.config["TESTING"] = True
            with router_mod.app.test_client() as c:
                res = c.post("/route/stream", json={
                    "prompt": f"stream concurrent test {idx}",
                    "max_tokens": 32,
                })
            with lock:
                results.append(res.status_code)
        except Exception:
            with lock:
                results.append(0)

    threads = [threading.Thread(target=hit, args=(i,)) for i in range(10)]
    for t in threads:
        t.start()
    for t in threads:
        t.join(timeout=30)

    success = results.count(200)
    print(f"Stream concurrent: {success}/{len(results)} succeeded")
    assert success == len(results)


# ── workflow integration ────────────────────────────────────────────────

def test_workflow_validation_integrates_with_router():
    """A workflow definition validates correctly and can be loaded."""
    from workflow.engine import Step, InlineStep, Workflow

    wf = Workflow(name="test-wf", steps=[
        Step("classify", "analyze", lambda ctx: {"result": "ok"}),
        InlineStep("route", "orchestrate",
                   {"prompt": "test", "max_tokens": 16},
                   consumes=["classify"]),
    ])
    warnings = validate_workflow(wf.steps, initial_keys=["classify"])
    assert len(warnings) == 0


def test_workflow_from_definition_roundtrip():
    """Definition → Workflow object preserves steps and names."""
    defn = {
        "name": "int-test",
        "steps": [
            {"name": "a", "agent": "analyze", "payload": {"q": "1"}},
            {"name": "b", "agent": "orchestrate", "consumes": ["a"],
             "payload": {"prompt": "p"}},
        ],
    }
    wf = from_definition(defn)
    assert wf.name == "int-test"
    assert len(wf.steps) == 2
    assert wf.steps[0].name == "a"
    assert wf.steps[1].name == "b"
