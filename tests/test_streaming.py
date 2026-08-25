"""Router SSE streaming tests (mock backend)."""
import pytest

flask = pytest.importorskip("flask")

import router as router_mod  # noqa: E402


@pytest.fixture()
def client():
    router_mod.app.config["TESTING"] = True
    with router_mod.app.test_client() as c:
        yield c


def test_stream_endpoint_sse(client):
    res = client.post("/route", json={
        "prompt": "Build a production API", "stream": True})
    assert res.status_code == 200
    assert res.mimetype == "text/event-stream"
    body = res.get_data(as_text=True)
    assert '"content"' in body
    assert "data: [DONE]" in body.strip().splitlines()[-1]


def test_stream_frames_are_json(client):
    res = client.post("/route", json={
        "prompt": "explain this code", "stream": True})
    lines = [l for l in res.get_data(as_text=True).splitlines()
             if l.startswith("data: ")]
    assert lines, "no SSE frames"
    import json
    parsed = [json.loads(l[6:]) for l in lines[:-1]]
    assert any("content" in p for p in parsed)
    assert any("model" in p or "task_type" in p for p in parsed)


def test_non_stream_unchanged(client):
    res = client.post("/route", json={"prompt": "plain request"})
    assert res.status_code == 200
    assert res.mimetype == "application/json"
