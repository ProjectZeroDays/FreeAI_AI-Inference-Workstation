"""Tests for workflow API endpoints (FastAPI)."""
import json
import os
import tempfile
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

try:
    from workflow.api import app
except ImportError:
    from api import app


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def templates_path(tmp_path, monkeypatch):
    cfg_dir = tmp_path / "config"
    cfg_dir.mkdir()
    tpl = cfg_dir / "workflow-templates.json"
    tpl.write_text(json.dumps({
        "templates": [
            {"id": "api_build", "name": "API Build",
             "steps": [{"name": "fetch", "agent": "orch"}]},
            {"id": "microservice_build", "name": "Microservice Build",
             "steps": [{"name": "scaffold", "agent": "orch"}]},
        ]
    }))
    monkeypatch.setattr("workflow.api.TEMPLATES_PATH", str(tpl))
    return tpl


# --------------------------- validate ---------------------------

def test_validate_ok(client):
    res = client.post("/workflow/validate", json={
        "steps": [
            {"name": "a", "consumes": [], "produces": ["x"]},
            {"name": "b", "consumes": ["x"], "produces": ["y"]},
        ]
    })
    assert res.status_code == 200
    assert res.json()["warnings"] == []


def test_validate_missing_produces(client):
    res = client.post("/workflow/validate", json={
        "steps": [{"name": "a", "consumes": [], "produces": None}]
    })
    assert res.status_code == 200
    warnings = res.json()["warnings"]
    assert any("missing 'produces'" in w for w in warnings)


def test_validate_missing_consumes(client):
    res = client.post("/workflow/validate", json={
        "steps": [{"name": "a", "consumes": None, "produces": ["x"]}]
    })
    assert res.status_code == 200
    warnings = res.json()["warnings"]
    assert any("missing 'consumes'" in w for w in warnings)


def test_validate_circular(client):
    res = client.post("/workflow/validate", json={
        "steps": [
            {"name": "a", "consumes": ["b"], "produces": []},
            {"name": "b", "consumes": ["a"], "produces": []},
        ]
    })
    assert res.status_code == 200
    warnings = res.json()["warnings"]
    assert any("circular dependency" in w for w in warnings)


# --------------------------- validate-definition ---------------------------

def test_validate_definition_missing_name(client):
    res = client.post("/workflow/validate-definition", json={
        "definition": {
            "steps": [{"name": "a", "consumes": [], "produces": ["x"]}]
        }
    })
    assert res.status_code == 200
    warnings = res.json()["warnings"]
    assert any("missing 'name'" in w for w in warnings)


def test_validate_definition_missing_triggers(client):
    res = client.post("/workflow/validate-definition", json={
        "definition": {
            "name": "my_wf",
            "steps": [{"name": "a", "consumes": [], "produces": ["x"]}]
        }
    })
    assert res.status_code == 200
    warnings = res.json()["warnings"]
    assert any("missing 'triggers'" in w for w in warnings)


# --------------------------- templates ---------------------------

def test_get_templates(client, templates_path):
    res = client.get("/workflow/templates")
    assert res.status_code == 200
    data = res.json()
    assert len(data["templates"]) == 2
    ids = [t["id"] for t in data["templates"]]
    assert "api_build" in ids
    assert "microservice_build" in ids


def test_get_templates_not_found(client, monkeypatch):
    monkeypatch.setattr("workflow.api.TEMPLATES_PATH", "/nonexistent/path.json")
    res = client.get("/workflow/templates")
    assert res.status_code == 404


# --------------------------- audit ---------------------------

def test_get_audit_empty(client, tmp_path, monkeypatch):
    audit_file = tmp_path / "audit.jsonl"
    monkeypatch.setattr("workflow.audit.AUDIT_FILE", str(audit_file))
    res = client.get("/workflow/audit")
    assert res.status_code == 200
    assert res.json()["entries"] == []


def test_get_audit_with_entries(client, tmp_path, monkeypatch):
    audit_file = tmp_path / "audit.jsonl"
    audit_file.write_text(json.dumps({"workflow": "w", "status": "ok"}) + "\n")
    monkeypatch.setattr("workflow.audit.AUDIT_FILE", str(audit_file))
    res = client.get("/workflow/audit")
    assert res.status_code == 200
    assert len(res.json()["entries"]) == 1


# --------------------------- health ---------------------------

def test_health(client):
    res = client.get("/health")
    assert res.status_code == 200
    assert res.json()["status"] == "ok"
