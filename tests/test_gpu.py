"""GPU API tests — mock nvidia-smi fallback path."""
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
    dash.app.config["SECRET_KEY"] = "test-secret-for-unit-tests"
    with dash.app.test_client() as c:
        yield c
    # Reset GPU state after each test
    dash._gpu_state.update({"devices": [], "total_vram_mb": 0,
                            "used_vram_mb": 0, "utilization_pct": 0,
                            "temperature_c": 0, "power_w": 0})


def test_gpu_initial_state(client):
    res = client.get("/api/gpu")
    assert res.status_code == 200
    body = res.get_json()
    assert body["devices"] == []
    assert body["total_vram_mb"] == 0


def test_gpu_scan_fallback(client, monkeypatch):
    """When nvidia-smi is absent, scan returns mock device."""
    import subprocess
    orig_run = subprocess.run

    def fake_run(*args, **kwargs):
        raise subprocess.CalledProcessError(1, "nvidia-smi")
    monkeypatch.setattr(subprocess, "run", fake_run)

    res = client.post("/api/gpu/scan")
    assert res.status_code == 200
    body = res.get_json()
    assert len(body["devices"]) >= 1
    dev = body["devices"][0]
    assert "name" in dev
    assert dev["total_vram_mb"] > 0


def test_gpu_scan_updates_state(client, monkeypatch):
    import subprocess
    fake_output = ("NVIDIA A100-SXM4-40GB, 40960, 8192, 34%, 62, 180.5\n"
                   "NVIDIA A100-SXM4-40GB, 40960, 4096, 12%, 55, 95.0")

    def fake_run(cmd, **kwargs):
        class R:
            stdout = fake_output
            returncode = 0
        return R()
    monkeypatch.setattr(subprocess, "run", fake_run)

    res = client.post("/api/gpu/scan")
    body = res.get_json()
    assert len(body["devices"]) == 2
    assert body["total_vram_mb"] == (40960 + 40960) * 1024
    assert body["used_vram_mb"] == (8192 + 4096) * 1024
    assert body["utilization_pct"] > 0


def test_gpu_state_persists_after_scan(client, monkeypatch):
    import subprocess

    def fake_run(*args, **kwargs):
        raise subprocess.CalledProcessError(1, "nvidia-smi")
    monkeypatch.setattr(subprocess, "run", fake_run)

    client.post("/api/gpu/scan")
    res = client.get("/api/gpu")
    body = res.get_json()
    assert len(body["devices"]) >= 1


def test_gpu_scan_no_devices(client, monkeypatch):
    """Empty nvidia-smi output yields no devices."""
    import subprocess

    def fake_run(*args, **kwargs):
        class R:
            stdout = ""
            returncode = 0
        return R()
    monkeypatch.setattr(subprocess, "run", fake_run)

    res = client.post("/api/gpu/scan")
    body = res.get_json()
    assert body["devices"] == []
    assert body["total_vram_mb"] == 0


# ── GPU Warmup API tests ───────────────────────────────────────


def test_gpu_warmup_status_empty(client):
    res = client.get("/api/gpu/warmup")
    assert res.status_code == 200
    body = res.get_json()
    assert "skipped" in body
    assert "results" in body


def test_gpu_warmup_detect_no_gpu(client, monkeypatch):
    """Detect returns empty when no nvidia-smi and no torch."""
    monkeypatch.setattr(dash, "_detect_gpus", lambda: ([], None))
    res = client.get("/api/gpu/warmup/detect")
    body = res.get_json()
    assert body["count"] == 0
    assert body["source"] is None


def test_gpu_warmup_config(client):
    res = client.get("/api/gpu/warmup/config")
    assert res.status_code == 200
    body = res.get_json()
    assert "enabled" in body
    assert "batch_size" in body


def test_gpu_warmup_results_no_data(client):
    res = client.get("/api/gpu/warmup/results")
    assert res.status_code == 200
    body = res.get_json()
    assert "results" in body


def test_gpu_warmup_post_triggers_warmup(client, monkeypatch):
    """POST to /api/gpu/warmup returns skipped when no GPU."""
    monkeypatch.setattr(dash, "_detect_gpus", lambda: ([], None))
    res = client.post("/api/gpu/warmup", json={"batch_size": 1, "seq_len": 64, "warmup_iters": 1})
    assert res.status_code == 200
    body = res.get_json()
    assert body["skipped"] is True


def test_gpu_warmup_page(client):
    res = client.get("/gpu-warmup")
    assert res.status_code == 200
    assert b"GPU Warmup" in res.get_data()
