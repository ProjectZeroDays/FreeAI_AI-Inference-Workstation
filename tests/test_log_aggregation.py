"""Tests for the FluentBit → Loki → Grafana log aggregation pipeline.

Covers the new Loki API endpoints added to dashboard/backend.py:
  GET /api/logs/loki/query
  GET /api/logs/loki/labels
  GET /api/logs/loki/label/<name>/values
All endpoints gracefully return empty results when Loki is unreachable.
"""
import json
import os
import sys
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest

flask = pytest.importorskip("flask")

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "dashboard"))

from dashboard import backend as dash  # noqa: E402


@pytest.fixture()
def client(tmp_path, monkeypatch):
    monkeypatch.setattr(dash, "CONFIG_DIR", tmp_path)
    monkeypatch.setattr(dash, "SKILLS_DIR", tmp_path / "skills")
    monkeypatch.setattr(dash, "ACTIVITY_LOG", tmp_path / "activity_log.jsonl")
    monkeypatch.setattr(dash, "UPLOAD_DIR", tmp_path / "uploads")
    monkeypatch.setattr(dash, "LOKI_URL", "http://loki:3100")
    dash.app.config["TESTING"] = True
    dash.app.config["SECRET_KEY"] = "test-secret-key-for-evals"
    with dash.app.test_client() as c:
        yield c


# ── Endpoint existence ───────────────────────────────────────────

def test_loki_query_endpoint_exists(client):
    """GET /api/logs/loki/query returns 200 even when Loki is down."""
    res = client.get("/api/logs/loki/query")
    assert res.status_code == 200
    body = res.get_json()
    assert "logs" in body
    assert "total" in body


def test_loki_labels_endpoint(client):
    """GET /api/logs/loki/labels returns 200 even when Loki is down."""
    res = client.get("/api/logs/loki/labels")
    assert res.status_code == 200
    body = res.get_json()
    assert "labels" in body


def test_loki_label_values_endpoint(client):
    """GET /api/logs/loki/label/<name>/values returns 200 even when Loki is down."""
    res = client.get("/api/logs/loki/label/service_name/values")
    assert res.status_code == 200
    body = res.get_json()
    assert "values" in body


# ── Empty results when Loki unavailable ──────────────────────────

def test_loki_query_empty(client):
    """When Loki is unavailable, query returns empty logs list."""
    res = client.get("/api/logs/loki/query")
    body = res.get_json()
    assert body["logs"] == []
    assert body["total"] == 0
    assert body["loki_available"] is False


def test_loki_labels_empty(client):
    """When Loki is unavailable, labels returns empty list."""
    res = client.get("/api/logs/loki/labels")
    body = res.get_json()
    assert body["labels"] == []


def test_loki_label_values_empty(client):
    """When Loki is unavailable, label values returns empty list."""
    res = client.get("/api/logs/loki/label/host/values")
    body = res.get_json()
    assert body["values"] == []


# ── Request formatting ───────────────────────────────────────────

def test_loki_query_format(client, monkeypatch):
    """Verify the query endpoint sends correct params to Loki."""
    captured = {}

    def fake_urlopen(req, timeout=None):
        captured["url"] = req.full_url if hasattr(req, "full_url") else str(req)
        captured["headers"] = dict(req.headers)
        resp = MagicMock()
        resp.read.return_value = json.dumps({
            "status": "success",
            "data": {"result": []}
        }).encode()
        resp.__enter__ = lambda s: s
        resp.__exit__ = lambda s, *a: None
        resp.status = 200
        return resp

    monkeypatch.setattr("urllib.request.urlopen", fake_urlopen)
    res = client.get("/api/logs/loki/query?query={app=&quot;test&quot;}&limit=50&start=now-30m&end=now")
    assert res.status_code == 200
    assert "loki" in captured.get("url", "")
    assert "query_range" in captured["url"]


def test_loki_query_with_labels(client, monkeypatch):
    """Verify label-based queries are sent correctly."""
    captured = {}

    def fake_urlopen(req, timeout=None):
        captured["url"] = req.full_url if hasattr(req, "full_url") else str(req)
        resp = MagicMock()
        resp.read.return_value = json.dumps({
            "status": "success",
            "data": {"result": []}
        }).encode()
        resp.__enter__ = lambda s: s
        resp.__exit__ = lambda s, *a: None
        resp.status = 200
        return resp

    monkeypatch.setattr("urllib.request.urlopen", fake_urlopen)
    res = client.get('/api/logs/loki/query?query=%7Bservice_name%3D%22freeai-router%22%7D&limit=200')
    assert res.status_code == 200
    assert "query_range" in captured["url"]
    assert "service_name" in captured["url"]


# ── Successful Loki response parsing ─────────────────────────────

def test_loki_query_parses_success_response(client, monkeypatch):
    """When Loki returns data, it is parsed into structured log entries."""
    loki_response = {
        "status": "success",
        "data": {
            "result": [
                {
                    "labels": {"service_name": "freeai-router", "cluster": "test"},
                    "values": [
                        ["1700000000000000000", '{"level":"info","message":"hello"}'],
                        ["1700000001000000000", '{"level":"error","message":"oops"}'],
                    ]
                }
            ]
        }
    }

    def fake_urlopen(req, timeout=None):
        resp = MagicMock()
        resp.read.return_value = json.dumps(loki_response).encode()
        resp.__enter__ = lambda s: s
        resp.__exit__ = lambda s, *a: None
        resp.status = 200
        return resp

    monkeypatch.setattr("urllib.request.urlopen", fake_urlopen)
    res = client.get('/api/logs/loki/query?query=%7Bservice_name%3D%22freeai-router%22%7D')
    body = res.get_json()
    assert body["loki_available"] is True
    assert body["total"] == 2
    assert len(body["logs"]) == 2
    assert body["logs"][0]["message"] == "hello"
    assert body["logs"][1]["level"] == "error"


def test_loki_labels_parses_response(client, monkeypatch):
    """Label discovery endpoint returns parsed label names."""
    loki_response = {"status": "success", "data": ["service_name", "cluster", "host"]}

    def fake_urlopen(req, timeout=None):
        resp = MagicMock()
        resp.read.return_value = json.dumps(loki_response).encode()
        resp.__enter__ = lambda s: s
        resp.__exit__ = lambda s, *a: None
        resp.status = 200
        return resp

    monkeypatch.setattr("urllib.request.urlopen", fake_urlopen)
    res = client.get("/api/logs/loki/labels")
    body = res.get_json()
    assert "service_name" in body["labels"]
    assert "cluster" in body["labels"]


def test_loki_label_values_parses_response(client, monkeypatch):
    """Label values endpoint returns parsed values."""
    loki_response = {"status": "success", "data": ["freeai-router", "freeai-worker"]}

    def fake_urlopen(req, timeout=None):
        resp = MagicMock()
        resp.read.return_value = json.dumps(loki_response).encode()
        resp.__enter__ = lambda s: s
        resp.__exit__ = lambda s, *a: None
        resp.status = 200
        return resp

    monkeypatch.setattr("urllib.request.urlopen", fake_urlopen)
    res = client.get("/api/logs/loki/label/service_name/values")
    body = res.get_json()
    assert "freeai-router" in body["values"]
    assert "freeai-worker" in body["values"]


# ── Error handling ────────────────────────────────────────────────

def test_loki_query_network_error(client, monkeypatch):
    """Network errors return empty results without 500."""
    def fake_urlopen(*a, **kw):
        raise OSError("connection refused")
    monkeypatch.setattr("urllib.request.urlopen", fake_urlopen)
    res = client.get("/api/logs/loki/query")
    assert res.status_code == 200
    body = res.get_json()
    assert body["logs"] == []
    assert body["loki_available"] is False


def test_loki_query_json_error(client, monkeypatch):
    """Malformed JSON from Loki returns empty results."""
    def fake_urlopen(*a, **kw):
        resp = MagicMock()
        resp.read.return_value = b"not json at all"
        resp.__enter__ = lambda s: s
        resp.__exit__ = lambda s, *a: None
        resp.status = 200
        return resp
    monkeypatch.setattr("urllib.request.urlopen", fake_urlopen)
    res = client.get("/api/logs/loki/query")
    assert res.status_code == 200
    body = res.get_json()
    assert body["logs"] == []


def test_loki_query_non_success_status(client, monkeypatch):
    """Loki returning non-success status is handled gracefully."""
    def fake_urlopen(*a, **kw):
        resp = MagicMock()
        resp.read.return_value = json.dumps({"status": "error", "error": "bad query"}).encode()
        resp.__enter__ = lambda s: s
        resp.__exit__ = lambda s, *a: None
        resp.status = 200
        return resp
    monkeypatch.setattr("urllib.request.urlopen", fake_urlopen)
    res = client.get("/api/logs/loki/query")
    assert res.status_code == 200
    body = res.get_json()
    assert body["loki_available"] is False


# ── Existing logs endpoints still work ───────────────────────────

def test_existing_logs_endpoint_returns_200(client):
    """Existing /api/logs endpoint must return 200 with correct shape."""
    res = client.get("/api/logs")
    assert res.status_code == 200
    body = res.get_json()
    assert "logs" in body
    assert "total" in body


def test_existing_logs_clear_returns_200(client):
    """Existing /api/logs/clear endpoint must return 200 with ok=True."""
    res = client.post("/api/logs/clear")
    assert res.status_code == 200
    assert res.get_json()["ok"] is True
