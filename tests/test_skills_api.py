"""Plugin manager / registry API tests."""
import sys
import os
import json

import pytest

flask = pytest.importorskip("flask")

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "dashboard"))

import backend as dash  # noqa: E402


@pytest.fixture()
def client(tmp_path, monkeypatch):
    dash.app.config["TESTING"] = True
    # Point plugin registry to temp
    monkeypatch.setattr(dash, "CONFIG_DIR", tmp_path)
    monkeypatch.setattr(dash, "SKILLS_DIR", tmp_path / "skills")
    monkeypatch.setattr(dash, "ACTIVITY_LOG", tmp_path / "activity_log.jsonl")
    (tmp_path / "skills").mkdir()
    (tmp_path / "registry").mkdir()
    (tmp_path / "registry" / "plugins.json").write_text(json.dumps({
        "browser-auto": {"name": "browser-auto", "category": "browser",
                          "enabled": True, "installed": True},
        "code-review": {"name": "code-review", "category": "code",
                         "enabled": True, "installed": False},
        "debug-helper": {"name": "debug-helper", "category": "debug",
                          "enabled": False, "installed": False},
    }))
    with dash.app.test_client() as c:
        yield c


def test_skills_list_basic(client):
    res = client.get("/api/skills")
    assert res.status_code == 200
    skills = res.get_json()
    assert isinstance(skills, list)


def test_skills_save_and_list(client):
    res = client.post("/api/skills/save", json={
        "name": "my-skill",
        "description": "A test skill",
        "triggers": ["test", "debug"],
        "category": "testing"})
    assert res.status_code == 200
    body = res.get_json()
    assert body["ok"] is True
    assert body["name"] == "my-skill"

    # Verify it shows up in skills list
    res2 = client.get("/api/skills")
    names = [s["name"] for s in res2.get_json()]
    assert "my-skill" in names


def test_skills_save_missing_name(client):
    res = client.post("/api/skills/save", json={"description": "no name"})
    assert res.status_code == 400
    assert "error" in res.get_json()


def test_skills_delete(client):
    # Create then delete
    client.post("/api/skills/save", json={"name": "delete-me", "description": "x"})
    res = client.delete("/api/skills/delete/delete-me")
    assert res.status_code == 200
    assert res.get_json()["ok"] is True

    res2 = client.get("/api/skills")
    names = [s["name"] for s in res2.get_json()]
    assert "delete-me" not in names


def test_skills_delete_nonexistent(client):
    res = client.delete("/api/skills/delete/nonexistent-skill-xyz")
    assert res.status_code == 200
    assert res.get_json()["ok"] is True


def test_skills_scan_no_log(client):
    """No activity log means no auto-created skills."""
    res = client.post("/api/skills/scan")
    body = res.get_json()
    assert body["created"] == []
    assert "message" in body


def test_skills_activity_empty(client):
    res = client.get("/api/skills/activity")
    body = res.get_json()
    assert body["entries"] == []
    assert body["total"] == 0


def test_skills_log_and_activity(client):
    client.post("/api/skills/log", json={
        "session_id": "sess-1",
        "user_input": "refactor the login module",
        "assistant_output": "Done refactoring",
        "task_type": "refactor"})
    res = client.get("/api/skills/activity")
    body = res.get_json()
    assert body["total"] >= 1
    assert len(body["entries"]) >= 1
    entry = body["entries"][0]
    assert entry["task_type"] == "refactor"
    assert entry["session"] == "sess-1"


def test_skills_triggers_parsed(client):
    res = client.post("/api/skills/save", json={
        "name": "trigger-test",
        "triggers": ["debug", "refactor", "fix"]})
    assert res.get_json()["ok"] is True

    res2 = client.get("/api/skills")
    skill = [s for s in res2.get_json() if s["name"] == "trigger-test"][0]
    assert "debug" in skill["triggers"]
    assert "refactor" in skill["triggers"]


def test_skills_special_chars_in_name(client):
    """Names with special chars are sanitized for the directory."""
    res = client.post("/api/skills/save", json={"name": "my skill!!"})
    body = res.get_json()
    assert body["ok"] is True
    # Verify the saved skill's frontmatter name matches the original input
    res2 = client.get("/api/skills")
    names = [s["name"] for s in res2.get_json()]
    assert "my skill!!" in names
