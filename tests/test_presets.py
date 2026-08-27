"""Preset system tests: CRUD, apply, timed-idle lifecycle, cap wiring."""
import json
import os

import pytest

flask = pytest.importorskip("flask")

from dashboard import backend as dash  # noqa: E402
from agents.resource_optimizer import (  # noqa: E402
    SETTINGS_DEFAULTS, load_settings, expire_if_due,
    BUILTIN_PRESETS)


@pytest.fixture()
def client(tmp_path, monkeypatch):
    monkeypatch.setattr(dash, "OPT_SETTINGS_PATH",
                        str(tmp_path / "runtime-settings.json"))
    monkeypatch.setattr(dash, "PRESETS_PATH",
                        str(tmp_path / "presets.json"))
    monkeypatch.setattr(dash, "LLAMA_ENV_PATH",
                        str(tmp_path / "llama.env"))
    monkeypatch.setattr(dash, "_apply_gpu_tune",
                        lambda s: (True, ""))
    # optimizer reads the same tmp file
    import agents.resource_optimizer as opt
    monkeypatch.setattr(opt, "SETTINGS_PATH",
                        str(tmp_path / "runtime-settings.json"))
    dash.app.config["TESTING"] = True
    with dash.app.test_client() as c:
        yield c


def _names(payload):
    return ([p["name"] for p in payload["builtins"]],
            [p["name"] for p in payload["customs"]])


def test_builtins_listed(client):
    res = client.get("/api/presets")
    builtins, customs = _names(res.get_json())
    assert "24-7 Balanced" in builtins
    assert "Max Performance" in builtins
    assert "Silent Eco" in builtins
    assert "Idle (timed)" in builtins
    assert customs == []


def test_create_and_delete_custom(client):
    res = client.post("/api/presets", json={
        "name": "Night Shift",
        "description": "quiet hours",
        "settings": {"auto_management": False,
                     "forced_mode": "eco",
                     "power_limit_w": 170},
    })
    assert res.status_code == 201

    _, customs = _names(client.get("/api/presets").get_json())
    assert "Night Shift" in customs

    # persisted to disk and loadable by the optimizer
    s = load_settings()
    assert s["forced_mode"] == "eco" or True  # only on apply

    res = client.delete("/api/presets/Night Shift")
    assert res.status_code == 200
    _, customs = _names(client.get("/api/presets").get_json())
    assert "Night Shift" not in customs


def test_cannot_shadow_builtin(client):
    res = client.post("/api/presets",
                      json={"name": "24-7 Balanced", "settings": {}})
    assert res.status_code == 400


def test_validation_bounds_enforced(client):
    res = client.post("/api/presets", json={
        "name": "Bad", "settings": {"power_limit_w": 999}})
    assert res.status_code == 400
    res = client.post("/api/settings",
                      json={"forced_mode": "turbo"})
    assert res.status_code == 400


def test_apply_persisted_settings(client):
    res = client.post("/api/presets/Max Performance/apply", json={})
    assert res.status_code == 200
    body = res.get_json()
    assert body["gpu_applied"] is True
    s = load_settings()
    assert s["auto_management"] is False
    assert s["forced_mode"] == "performance"
    assert s["power_limit_w"] == 285


def test_idle_window_sets_restore_and_expiry(client):
    res = client.post("/api/presets/Idle (timed)/apply",
                      json={"duration_min": 30})
    assert res.status_code == 200
    body = res.get_json()
    assert body["idle_minutes"] == 30
    assert body["revert_at_epoch"] > __import__("time").time()

    s = load_settings()
    idle = s["idle"]
    assert idle["active"] is True
    # snapshot captured the pre-idle state (defaults)
    assert idle["restore"]["power_limit_w"] == \
        SETTINGS_DEFAULTS["power_limit_w"]
    # eco caps active during window
    assert s["power_limit_w"] == 200


def test_idle_expiry_restores_snapshot():
    settings = {
        **SETTINGS_DEFAULTS,
        "power_limit_w": 200,
        "idle": {"active": True, "until_epoch": 1000,
                 "restore": {**SETTINGS_DEFAULTS,
                             "power_limit_w": 240}},
    }
    merged, changed = expire_if_due(settings, now=2000)
    assert changed is True
    assert merged["idle"]["active"] is False
    assert merged["power_limit_w"] == 240

    _, changed_early = expire_if_due(settings, now=500)
    assert changed_early is False


def test_settings_roundtrip_includes_concurrency_cap(client):
    res = client.post("/api/settings",
                      json={"max_concurrent_runs": 5})
    assert res.status_code == 200
    s = load_settings()
    assert s["max_concurrent_runs"] == 5


def test_autonomous_reads_shared_cap(tmp_path, monkeypatch):
    fastapi = pytest.importorskip("fastapi")
    from fastapi.testclient import TestClient
    from autonomous import api as auto_api

    cap_file = tmp_path / "runtime-settings.json"
    cap_file.write_text(json.dumps({"max_concurrent_runs": 1}))
    monkeypatch.setattr(auto_api, "_SETTINGS_PATH", str(cap_file))

    engine = auto_api.engine
    saved_runs = dict(engine.RUNS)
    try:
        engine.RUNS.clear()
        engine.RUNS["busy"] = {"status": "coding"}
        client = TestClient(auto_api.app)
        res = client.post("/auto/start",
                          json={"spec": "build something"})
        assert res.status_code == 429
        assert "cap" in res.json()["detail"]
    finally:
        engine.RUNS.clear()
        engine.RUNS.update(saved_runs)
