"""Workflow engine API tests."""
import sys
import os
import json
import tempfile
import shutil

import pytest

flask = pytest.importorskip("flask")

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "dashboard"))

import backend as dash  # noqa: E402


@pytest.fixture()
def client(tmp_path, monkeypatch):
    dash.app.config["TESTING"] = True
    # Point workflow dir to temp so tests are isolated
    monkeypatch.setattr(dash, "_WORKFLOW_DIR", tmp_path)
    (tmp_path / "workflows").mkdir()
    with dash.app.test_client() as c:
        yield c


def test_workflow_list_empty(client):
    res = client.get("/api/workflow")
    assert res.status_code == 200
    body = res.get_json()
    assert body["total"] == 0
    assert body["workflows"] == []


def test_workflow_list_with_files(client):
    wf_dir = dash._WORKFLOW_DIR / "workflows"
    (wf_dir / "build.json").write_text(json.dumps({
        "name": "Build Pipeline", "steps": [{"name": "compile"}, {"name": "test"}],
        "status": "active"}), encoding="utf-8")
    (wf_dir / "deploy.json").write_text(json.dumps({
        "name": "Deploy", "steps": [{"name": "push"}],
        "status": "inactive"}), encoding="utf-8")

    res = client.get("/api/workflow")
    body = res.get_json()
    assert body["total"] == 2
    names = {w["name"] for w in body["workflows"]}
    assert "Build Pipeline" in names
    assert "Deploy" in names


def test_workflow_step_count(client):
    wf_dir = dash._WORKFLOW_DIR / "workflows"
    (wf_dir / "complex.json").write_text(json.dumps({
        "name": "Complex", "steps": [{"name": "a"}, {"name": "b"}, {"name": "c"}],
        "status": "active"}), encoding="utf-8")

    res = client.get("/api/workflow")
    body = res.get_json()
    wf = [w for w in body["workflows"] if w["name"] == "Complex"][0]
    assert wf["steps"] == 3


def test_workflow_registries_empty(client, tmp_path, monkeypatch):
    monkeypatch.setattr(dash, "ROOT", tmp_path)
    res = client.get("/api/workflow/registries")
    assert res.status_code == 200
    body = res.get_json()
    assert body["registries"] == []


def test_workflow_registries_with_files(client, tmp_path, monkeypatch):
    # Backend uses ROOT.parent / "registry"; set ROOT so parent lands at tmp_path
    monkeypatch.setattr(dash, "ROOT", tmp_path)
    reg_dir = tmp_path.parent / "registry"
    reg_dir.mkdir(parents=True)
    (reg_dir / "plugins.json").write_text(json.dumps([
        {"name": "a"}, {"name": "b"}, {"name": "c"}]))
    (reg_dir / "single.json").write_text(json.dumps({"entries": [1, 2]}))

    res = client.get("/api/workflow/registries")
    body = res.get_json()
    assert len(body["registries"]) == 2
    names = {r["file"] for r in body["registries"]}
    assert "plugins.json" in names
    assert "single.json" in names


def test_workflow_invalid_json_skipped(client):
    wf_dir = dash._WORKFLOW_DIR / "workflows"
    (wf_dir / "broken.json").write_text("not valid json {{{")
    (wf_dir / "good.json").write_text(json.dumps({
        "name": "Good", "steps": [], "status": "active"}))

    res = client.get("/api/workflow")
    body = res.get_json()
    assert body["total"] == 1
    assert body["workflows"][0]["name"] == "Good"
