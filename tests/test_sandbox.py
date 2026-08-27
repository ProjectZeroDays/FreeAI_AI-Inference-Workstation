"""Sandbox executor API tests."""
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
    dash._SANDBOX["output"] = None
    dash._SANDBOX["last_run"] = None


def test_sandbox_info(client):
    res = client.get("/api/sandbox")
    assert res.status_code == 200
    body = res.get_json()
    assert body["enabled"] is True
    assert body["max_runtime_s"] == 30


def test_run_python_simple(client):
    res = client.post("/api/sandbox/run",
                      json={"code": "print('hello')", "language": "python"})
    assert res.status_code == 200
    body = res.get_json()
    assert body["ok"] is True
    assert "hello" in body["result"].get("output", "")


def test_run_python_expression(client):
    res = client.post("/api/sandbox/run",
                      json={"code": "x = 2 + 3\nprint(x)"})
    body = res.get_json()
    assert body["ok"] is True
    assert "5" in body["result"].get("output", "")


def test_run_python_error(client):
    res = client.post("/api/sandbox/run",
                      json={"code": "1 / 0"})
    body = res.get_json()
    assert body["ok"] is True
    assert "error" in body["result"]


def test_run_missing_code_returns_400(client):
    res = client.post("/api/sandbox/run", json={})
    assert res.status_code == 400
    assert "error" in res.get_json()


def test_run_non_python(client):
    res = client.post("/api/sandbox/run",
                      json={"code": "echo hello", "language": "bash"})
    body = res.get_json()
    assert body["ok"] is True
    assert "not supported" in body["result"].get("output", "").lower()


def test_run_captures_output(client):
    code = "import sys\nprint('out', file=sys.stdout)\nprint('err', file=sys.stderr)"
    res = client.post("/api/sandbox/run", json={"code": code})
    body = res.get_json()
    output = body["result"].get("output", "")
    assert "out" in output


def test_sandbox_last_run_updated(client):
    import time
    res = client.post("/api/sandbox/run", json={"code": "pass"})
    assert res.status_code == 200
    assert dash._SANDBOX["last_run"] is not None
    assert time.time() - dash._SANDBOX["last_run"] < 5


def test_sandbox_output_persisted(client):
    client.post("/api/sandbox/run", json={"code": "print('stored')"})
    info = client.get("/api/sandbox").get_json()
    assert info["output"] is not None
