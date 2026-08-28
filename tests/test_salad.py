"""Salad GPU integration tests covering mock data fallback, config
endpoint, history endpoint, and error handling paths."""
import sys
from pathlib import Path

import pytest

flask = pytest.importorskip("flask")

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from dashboard import backend as dash  # noqa: E402


@pytest.fixture()
def client(tmp_path, monkeypatch):
    monkeypatch.setattr(dash, "CONFIG_DIR", tmp_path)
    monkeypatch.setattr(dash, "SKILLS_DIR", tmp_path / "skills")
    monkeypatch.setattr(dash, "ACTIVITY_LOG", tmp_path / "activity_log.jsonl")
    monkeypatch.setattr(dash, "UPLOAD_DIR", tmp_path / "uploads")
    monkeypatch.setattr(dash, "_SALAD_API_KEY", "")
    monkeypatch.setattr(dash, "SALAD_API_KEY", "")
    monkeypatch.setattr(dash, "AIKIDO_API_KEY", "")
    monkeypatch.setattr(dash, "AIKIDO_APP_ID", "")
    monkeypatch.setattr(dash, "OPT_SETTINGS_PATH",
                        str(tmp_path / "runtime-settings.json"))
    monkeypatch.setattr(dash, "PRESETS_PATH",
                        str(tmp_path / "presets.json"))
    monkeypatch.setattr(dash, "PROVIDERS_MERGED_PATH",
                        str(tmp_path / "providers-merged.json"))
    monkeypatch.setattr(dash, "HERMES_CONFIG_PATH",
                        Path(tmp_path / "hermes.json"))
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
    with dash.app.test_client() as c:
        yield c


# ── Mock data fallback (no API key) ──────────────────────────────

def test_salad_no_key_returns_mock(client):
    res = client.get("/api/salad")
    assert res.status_code == 200
    body = res.get_json()
    assert body["configured"] is False
    assert body["mock"] is True
    data = body["data"]
    assert isinstance(data["total_usd"], (int, float))
    assert 0 <= data["total_usd"] <= 500
    assert isinstance(data["gpu_hours"], int)
    assert len(data["nodes"]) >= 3
    assert len(data["nodes"]) <= 8


def test_salad_gpu_no_key_returns_mock(client):
    res = client.get("/api/salad/gpu")
    assert res.status_code == 200
    body = res.get_json()
    assert body["configured"] is False
    assert body["mock"] is True
    gpus = body["gpus"]
    assert isinstance(gpus, list)
    assert len(gpus) >= 3
    for gpu in gpus:
        assert "name" in gpu
        assert "utilization" in gpu
        assert "temperature" in gpu
        assert "vram_total" in gpu
        assert 0 <= gpu["utilization"] <= 100
        assert 40 <= gpu["temperature"] <= 85
        assert gpu["vram_total"] > 0


def test_salad_history_no_key(client):
    res = client.get("/api/salad/history")
    assert res.status_code == 200
    body = res.get_json()
    assert body["mock"] is True
    history = body["history"]
    assert len(history) == 7
    for entry in history:
        assert "date" in entry
        assert "day_label" in entry
        assert "earnings" in entry
        assert "gpu_hours" in entry
        assert 0 <= entry["earnings"] <= 50
        assert isinstance(entry["gpu_hours"], int)


# ── Config endpoint ──────────────────────────────────────────────

def test_config_get_no_key(client):
    res = client.get("/api/salad/config")
    assert res.status_code == 200
    body = res.get_json()
    assert body["configured"] is False


def test_config_post_saves_key(client):
    res = client.post("/api/salad/config", json={"api_key": "sk-test-123"})
    assert res.status_code == 200
    body = res.get_json()
    assert body["saved"] is True
    assert body["configured"] is True
    # Verify subsequent salad call now uses the key
    res2 = client.get("/api/salad")
    assert res2.get_json()["configured"] is True


def test_config_post_clears_key(client):
    dash._SALAD_API_KEY = "sk-some-key"
    res = client.post("/api/salad/config", json={"api_key": ""})
    assert res.status_code == 200
    body = res.get_json()
    assert body["cleared"] is True
    assert body["saved"] is True
    assert body["configured"] is False


def test_config_post_empty_body(client):
    res = client.post("/api/salad/config", json={})
    assert res.status_code == 200
    body = res.get_json()
    assert body["cleared"] is True


# ── Error handling ───────────────────────────────────────────────

def test_salad_page_rendered(client):
    res = client.get("/salad")
    assert res.status_code == 200
    assert b"Salad GPU Network" in res.data


def test_salad_cache_busting_on_config_change(client):
    assert dash._SALAD_CACHE["ts"] == 0.0
    client.get("/api/salad")
    ts1 = dash._SALAD_CACHE["ts"]
    assert ts1 > 0
    client.post("/api/salad/config", json={"api_key": "sk-new"})
    assert dash._SALAD_CACHE["ts"] == 0.0
    client.post("/api/salad/config", json={"api_key": ""})
    assert dash._SALAD_CACHE["ts"] == 0.0
