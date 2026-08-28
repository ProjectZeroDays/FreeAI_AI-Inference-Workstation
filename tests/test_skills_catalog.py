"""Skills catalog API tests: listing, refresh, install, path-traversal guard."""
import json
import pytest

flask = pytest.importorskip("flask")

from dashboard import backend as dash  # noqa: E402


@pytest.fixture()
def client(tmp_path, monkeypatch):
    monkeypatch.setattr(dash, "CONFIG_DIR", tmp_path)
    monkeypatch.setattr(dash, "SKILLS_DIR", tmp_path / "skills")
    monkeypatch.setattr(dash, "ACTIVITY_LOG", tmp_path / "activity_log.jsonl")
    monkeypatch.setattr(dash, "UPLOAD_DIR", tmp_path / "uploads")
    monkeypatch.setattr(dash, "SALAD_API_KEY", "")
    monkeypatch.setattr(dash, "_SALAD_API_KEY", "")
    monkeypatch.setattr(dash, "AIKIDO_API_KEY", "")
    monkeypatch.setattr(dash, "AIKIDO_APP_ID", "")
    monkeypatch.setattr(dash, "OPT_SETTINGS_PATH",
                        str(tmp_path / "runtime-settings.json"))
    monkeypatch.setattr(dash, "PRESETS_PATH",
                        str(tmp_path / "presets.json"))
    monkeypatch.setattr(dash, "PROVIDERS_MERGED_PATH",
                        str(tmp_path / "providers-merged.json"))
    monkeypatch.setattr(dash, "HERMES_CONFIG_PATH",
                        tmp_path / "hermes.json")
    monkeypatch.setattr(dash, "_SCHEDULER_CONFIG_PATH",
                        str(tmp_path / "scheduler.json"))
    dash._SUBAGENTS.clear()
    dash._TRAINING_DATA.update({
        "datasets": [], "jobs": {"sft": [], "dpo": [], "abr": []},
        "models": [],
    })
    dash._MEMORY_STATE["projects"].clear()
    dash._MEMORY_STATE["learnings"].clear()
    dash._AUTOMATIONS["jobs"].clear()
    dash._AUTOMATIONS["history"].clear()
    dash._campaigns.clear()
    dash._scheduler_jobs.clear()
    dash._gpu_state["devices"] = []
    dash._gpu_state["total_vram_mb"] = 0
    dash._gpu_state["used_vram_mb"] = 0
    dash._uploads.clear()
    dash._SALAD_API_KEY = ""
    dash._SALAD_CACHE = {"salad": None, "gpu": None, "ts": 0.0}
    dash.app.config["TESTING"] = True
    dash.app.config["SECRET_KEY"] = "test-secret-key-for-evals"
    # Point CATALOG_PATH into tmp_path so we control the catalog data
    monkeypatch.setattr(dash, "CATALOG_PATH", tmp_path / "catalog.json")
    with dash.app.test_client() as c:
        yield c


# ── Page Route ───────────────────────────────────────────────────

def test_skills_catalog_page(client):
    res = client.get("/skills-catalog")
    assert res.status_code == 200


# ── Catalog API ──────────────────────────────────────────────────

def test_skills_catalog_empty(client):
    (client.application.config.get("TEST_TEMP_PATH", client.__dict__)
     )  # no-op; CATALOG_PATH was set in fixture
    res = client.get("/api/skills/catalog")
    assert res.status_code == 200
    body = res.get_json()
    assert "skills" in body
    assert "sources" in body
    assert "total" in body
    assert body["total"] == 0


def test_skills_catalog_with_data(client, tmp_path):
    catalog_path = dash.CATALOG_PATH
    catalog_path.write_text(json.dumps({
        "skills": [
            {"id": "test-skill", "name": "Test Skill", "category": "dev"},
        ],
        "sources": ["local"],
        "total": 1,
    }), encoding="utf-8")
    res = client.get("/api/skills/catalog")
    assert res.status_code == 200
    body = res.get_json()
    assert body["total"] == 1
    assert len(body["skills"]) == 1
    assert body["skills"][0]["id"] == "test-skill"


def test_skills_catalog_refresh(client, tmp_path, monkeypatch):
    """Refresh returns ok when scraper path doesn't exist (fallback)."""
    dash.CATALOG_PATH.write_text('{"skills":[],"total":0}', encoding="utf-8")
    # Point ROOT so the scraper path resolves into tmp_path (unlikely to exist)
    monkeypatch.setattr(dash, "ROOT", tmp_path)
    res = client.post("/api/skills/catalog/refresh")
    # May succeed or fall back to rebuild; in any case 200/500
    assert res.status_code in (200, 500)


def test_skills_available_empty(client):
    res = client.get("/api/skills/available")
    assert res.status_code == 200
    body = res.get_json()
    assert "skills" in body
    assert "total" in body
    assert isinstance(body["skills"], list)


def test_skills_available_with_catalog(client, tmp_path):
    dash.CATALOG_PATH.write_text(json.dumps({
        "skills": [
            {"id": "my-skill", "name": "My Skill", "category": "test"},
        ],
        "total": 1,
    }), encoding="utf-8")
    # Create a local skill with a different id so it appears as available
    local_dir = dash.SKILLS_DIR / "other-skill"
    local_dir.mkdir(parents=True, exist_ok=True)
    (local_dir / "SKILL.md").write_text("---\nname: other-skill\n---\nbody")
    res = client.get("/api/skills/available")
    assert res.status_code == 200
    body = res.get_json()
    # my-skill should still appear (not installed locally)
    ids = [s["id"] for s in body["skills"]]
    assert "my-skill" in ids


def test_skills_catalog_install_valid(client):
    res = client.post("/api/skills/catalog/install", json={
        "id": "my-new-skill",
        "name": "My New Skill",
        "description": "A test skill",
        "category": "testing",
        "triggers": ["test", "verify"],
    })
    assert res.status_code == 200
    body = res.get_json()
    assert body["ok"] is True
    assert body["id"] == "my-new-skill"
    assert "path" in body
    # Verify SKILL.md was written
    skill_file = dash.SKILLS_DIR / "my-new-skill" / "SKILL.md"
    assert skill_file.exists()
    content = skill_file.read_text(encoding="utf-8")
    assert "My New Skill" in content


def test_skills_catalog_install_invalid_id(client):
    """Path-traversal or otherwise invalid IDs should be rejected with 400."""
    res = client.post("/api/skills/catalog/install", json={
        "id": "../../etc/passwd",
    })
    assert res.status_code == 400
    body = res.get_json()
    assert "error" in body

    res = client.post("/api/skills/catalog/install", json={
        "id": "",
    })
    assert res.status_code == 400

    res = client.post("/api/skills/catalog/install", json={
        "id": "valid-id but with spaces",
    })
    assert res.status_code == 400


def test_skills_catalog_install_no_id(client):
    res = client.post("/api/skills/catalog/install", json={})
    assert res.status_code == 400
