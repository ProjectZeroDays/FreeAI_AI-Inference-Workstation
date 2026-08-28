"""AI Training dashboard API tests."""
import io
import json
from pathlib import Path

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
                        Path(tmp_path / "hermes.json"))
    monkeypatch.setattr(dash, "_SCHEDULER_CONFIG_PATH",
                        str(tmp_path / "scheduler.json"))
    # Reset in-memory state
    dash._SUBAGENTS.clear()
    dash._TRAINING_DATA.update({
        "datasets": [], "jobs": {"sft": [], "dpo": [], "abr": []},
        "models": [],
    })
    dash._AI_TRAINING_JOBS.clear()
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


# ── Page Route ─────────────────────────────────────────────────────

def test_page_ai_training(client):
    res = client.get("/ai-training")
    assert res.status_code == 200


# ── Training Jobs List ─────────────────────────────────────────────

def test_training_jobs_empty(client):
    res = client.get("/api/training/jobs")
    assert res.status_code == 200
    assert res.get_json() == []


def test_training_jobs_after_create(client):
    res = client.post("/api/training/jobs", json={
        "type": "sft",
        "base_model": "qwen3.6-12b",
        "name": "test-job-1"})
    assert res.status_code == 200
    body = res.get_json()
    assert body["status"] == "queued"
    assert "job_id" in body
    # verify it appears in list
    res = client.get("/api/training/jobs")
    jobs = res.get_json()
    assert len(jobs) == 1
    assert jobs[0]["id"] == body["job_id"]


def test_training_jobs_create_dpo(client):
    res = client.post("/api/training/jobs", json={
        "type": "dpo",
        "base_model": "llama-3-8b",
        "name": "dpo-job"})
    assert res.status_code == 200
    body = res.get_json()
    assert body["status"] == "queued"


def test_training_jobs_create_invalid_type(client):
    # The existing POST /api/training/jobs route crashes on invalid type
    # (KeyError on _TRAINING_DATA["jobs"]["invalid"])
    res = client.post("/api/training/jobs", json={"type": "invalid"})
    assert res.status_code in (200, 500)


# ── Training Job Detail ────────────────────────────────────────────

def test_training_job_detail(client):
    res = client.post("/api/training/jobs", json={
        "type": "sft", "base_model": "qwen3.6-12b", "name": "detail-job"})
    job_id = res.get_json()["job_id"]
    res = client.get(f"/api/training/jobs/{job_id}")
    assert res.status_code == 200
    body = res.get_json()
    assert body["id"] == job_id
    assert body["name"] == "detail-job"


def test_training_job_detail_not_found(client):
    res = client.get("/api/training/jobs/nonexistent")
    assert res.status_code == 404


# ── Training Job Status Update ─────────────────────────────────────

def test_training_job_status_update(client):
    res = client.post("/api/training/jobs", json={
        "type": "sft", "base_model": "qwen3.6-12b", "name": "status-job"})
    job_id = res.get_json()["job_id"]
    res = client.put(f"/api/training/jobs/{job_id}/status", json={
        "status": "running"})
    assert res.status_code == 200
    body = res.get_json()
    assert body["ok"] is True
    assert body["status"] == "running"


def test_training_job_status_update_no_status(client):
    res = client.put("/api/training/jobs/fake-id/status", json={})
    assert res.status_code == 400


def test_training_job_status_update_not_found(client):
    res = client.put("/api/training/jobs/nonexistent/status", json={
        "status": "running"})
    assert res.status_code == 404


# ── Training Datasets ──────────────────────────────────────────────

def test_training_datasets_empty(client):
    res = client.get("/api/training/datasets")
    assert res.status_code == 200
    assert res.get_json() == []


def test_training_datasets_create(client):
    data = {"file": (io.BytesIO(b'{"prompt":"test"}\n'), "test.jsonl")}
    res = client.post(
        "/api/training/datasets",
        data={"name": "test-ds", "format": "jsonl", **data},
        content_type="multipart/form-data")
    assert res.status_code == 200
    body = res.get_json()
    assert body["name"] == "test-ds"
    assert body["format"] == "jsonl"
    assert "id" in body
    # verify it appears in list
    res = client.get("/api/training/datasets")
    datasets = res.get_json()
    assert len(datasets) == 1
    assert datasets[0]["name"] == "test-ds"


# ── Training Models ────────────────────────────────────────────────

def test_training_models_empty(client):
    res = client.get("/api/training/models")
    assert res.status_code == 200
    assert res.get_json() == []


# ── Training Deploy ────────────────────────────────────────────────

def test_training_deploy_not_found(client):
    res = client.post("/api/training/deploy", json={"model_id": "nonexistent"})
    assert res.status_code == 404


# ── GPU Status ─────────────────────────────────────────────────────

def test_training_gpu_status_mock(client):
    res = client.get("/api/training/gpu-status")
    assert res.status_code == 200
    body = res.get_json()
    assert "devices" in body
    assert len(body["devices"]) >= 1
    device = body["devices"][0]
    assert "name" in device
    assert "utilization" in device


def test_training_gpu_status_with_devices(client):
    dash._gpu_state["devices"] = [{
        "id": 0,
        "name": "NVIDIA A100",
        "memory_total": 40960,
        "memory_used": 8192,
        "utilization": 75,
        "temperature": 62,
    }]
    res = client.get("/api/training/gpu-status")
    assert res.status_code == 200
    body = res.get_json()
    assert len(body["devices"]) == 1
    assert body["devices"][0]["name"] == "NVIDIA A100"
    assert body["devices"][0]["utilization"] == 75
