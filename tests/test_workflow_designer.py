"""Tests for workflow designer API endpoints."""
import sys
import os
import json
import time

import pytest

flask = pytest.importorskip("flask")

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "dashboard"))

import backend as dash  # noqa: E402


@pytest.fixture()
def client(tmp_path, monkeypatch):
    dash.app.config["TESTING"] = True
    # Point workflow save dirs to temp so tests are isolated
    monkeypatch.setattr(dash, "_WORKFLOW_SAVE_DIR", tmp_path)
    monkeypatch.setattr(dash, "_designer_wf_dir", tmp_path / "designer-wf")
    (tmp_path / "designer-wf").mkdir()
    # Point templates path to temp
    tmpl_path = tmp_path / "templates.json"
    tmpl_path.write_text("[]", encoding="utf-8")
    monkeypatch.setattr(dash, "_TEMPLATES_PATH", tmpl_path)
    with dash.app.test_client() as c:
        yield c


# ── Templates ────────────────────────────────────────────────────

def test_templates_empty(client):
    res = client.get("/api/workflow-designer/templates")
    assert res.status_code == 200
    body = res.get_json()
    assert body["total"] == 0
    assert body["templates"] == []


def test_templates_save(client):
    res = client.post("/api/workflow-designer/templates", json={
        "name": "Code Review",
        "prompt": "Review this code for..."
    })
    assert res.status_code == 200
    body = res.get_json()
    assert body["ok"] is True
    assert body["id"].startswith("tmpl_")

    # Verify it persisted
    res2 = client.get("/api/workflow-designer/templates")
    assert res2.get_json()["total"] == 1
    assert res2.get_json()["templates"][0]["name"] == "Code Review"


def test_templates_save_duplicate_id_updates(client):
    client.post("/api/workflow-designer/templates", json={
        "id": "my-tmpl", "name": "First", "prompt": "prompt1"
    })
    res = client.post("/api/workflow-designer/templates", json={
        "id": "my-tmpl", "name": "Updated", "prompt": "prompt2"
    })
    assert res.get_json()["ok"] is True
    res2 = client.get("/api/workflow-designer/templates")
    tmpl = res2.get_json()["templates"][0]
    assert tmpl["name"] == "Updated"
    assert tmpl["prompt"] == "prompt2"


def test_templates_save_missing_fields(client):
    res = client.post("/api/workflow-designer/templates", json={"name": "No Prompt"})
    assert res.status_code == 400
    assert "error" in res.get_json()

    res2 = client.post("/api/workflow-designer/templates", json={"prompt": "No name"})
    assert res2.status_code == 400


def test_templates_delete(client):
    save = client.post("/api/workflow-designer/templates", json={
        "id": "del-me", "name": "Delete Me", "prompt": "x"
    })
    assert save.get_json()["ok"] is True

    res = client.delete("/api/workflow-designer/templates/del-me")
    assert res.status_code == 200
    assert res.get_json()["ok"] is True

    res2 = client.get("/api/workflow-designer/templates")
    assert res2.get_json()["total"] == 0


def test_templates_delete_not_found(client):
    res = client.delete("/api/workflow-designer/templates/nonexistent")
    assert res.status_code == 404


# ── Workflows CRUD ───────────────────────────────────────────────

def test_workflows_list_empty(client):
    res = client.get("/api/workflow-designer/workflows")
    assert res.status_code == 200
    body = res.get_json()
    assert body["total"] == 0
    assert body["workflows"] == []


def test_workflows_save(client):
    res = client.post("/api/workflow-designer/workflows", json={
        "name": "My Pipeline",
        "definition": {
            "nodes": [
                {"id": "1", "type": "start", "name": "Start", "x": 0, "y": 0},
                {"id": "2", "type": "end", "name": "End", "x": 200, "y": 0},
            ],
            "edges": [{"from": "1", "to": "2"}],
        }
    })
    assert res.status_code == 200
    body = res.get_json()
    assert body["ok"] is True
    assert "path" in body

    # Verify list includes it
    res2 = client.get("/api/workflow-designer/workflows")
    wf = res2.get_json()["workflows"]
    assert len(wf) == 1
    assert wf[0]["name"] == "My Pipeline"
    assert wf[0]["node_count"] == 2


def test_workflows_save_missing_name(client):
    res = client.post("/api/workflow-designer/workflows", json={
        "definition": {"nodes": []}
    })
    assert res.status_code == 400


def test_workflows_save_missing_definition(client):
    res = client.post("/api/workflow-designer/workflows", json={"name": "No Def"})
    assert res.status_code == 400


def test_workflows_get(client):
    client.post("/api/workflow-designer/workflows", json={
        "name": "Get Me",
        "definition": {"nodes": [{"id": "1", "type": "step", "name": "A"}], "edges": []}
    })
    res = client.get("/api/workflow-designer/workflows/get-me")
    assert res.status_code == 200
    body = res.get_json()
    assert body["definition"]["nodes"][0]["name"] == "A"
    assert body["id"] == "get-me"


def test_workflows_get_not_found(client):
    res = client.get("/api/workflow-designer/workflows/nonexistent")
    assert res.status_code == 404
    assert "error" in res.get_json()


def test_workflows_delete(client):
    save = client.post("/api/workflow-designer/workflows", json={
        "name": "Delete Me",
        "definition": {"nodes": [], "edges": []}
    })
    assert save.get_json()["ok"] is True

    res = client.delete("/api/workflow-designer/workflows/delete-me")
    assert res.status_code == 200
    assert res.get_json()["ok"] is True

    res2 = client.get("/api/workflow-designer/workflows")
    assert res2.get_json()["total"] == 0


def test_workflows_delete_not_found(client):
    res = client.delete("/api/workflow-designer/workflows/nonexistent")
    assert res.status_code == 404


def test_workflows_list_multiple(client):
    for i in range(3):
        client.post("/api/workflow-designer/workflows", json={
            "name": f"Workflow {i}",
            "definition": {"nodes": [], "edges": []}
        })
    res = client.get("/api/workflow-designer/workflows")
    assert res.get_json()["total"] == 3
    names = {w["name"] for w in res.get_json()["workflows"]}
    assert names == {"Workflow 0", "Workflow 1", "Workflow 2"}


def test_workflows_invalid_name_sanitized(client):
    res = client.post("/api/workflow-designer/workflows", json={
        "name": "Bad Name!@#",
        "definition": {"nodes": [], "edges": []}
    })
    assert res.status_code == 200
    assert res.get_json()["ok"] is True
    # Special chars become hyphens; lookup with sanitized name
    res2 = client.get("/api/workflow-designer/workflows/bad-name---")
    assert res2.status_code == 200
