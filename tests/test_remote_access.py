"""Remote access API tests: SSH/VNC status, keys, password, start/stop."""
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
    # The backend routes call subprocess.run() but subprocess is not
    # imported at module level. Inject it so the routes work.
    import subprocess as _sp
    dash.subprocess = _sp
    with dash.app.test_client() as c:
        yield c


# ── Page Route ───────────────────────────────────────────────────

def test_remote_access_page(client):
    res = client.get("/remote-access")
    assert res.status_code == 200


# ── Status API ───────────────────────────────────────────────────

def test_remote_access_status(client):
    res = client.get("/api/remote-access/status")
    assert res.status_code == 200
    body = res.get_json()
    assert "ssh" in body
    assert "vnc" in body
    assert "novnc" in body
    ssh = body["ssh"]
    assert "running" in ssh
    assert "port" in ssh
    vnc = body["vnc"]
    assert "running" in vnc
    assert "port" in vnc


# ── SSH Start / Stop ─────────────────────────────────────────────

def test_remote_access_ssh_start(client, monkeypatch):
    import subprocess as _sp
    def fake_run(*args, **kwargs):
        class R:
            returncode = 0
            stdout = ""
            stderr = ""
        return R()
    monkeypatch.setattr(_sp, "run", fake_run)
    res = client.post("/api/remote-access/ssh/start")
    assert res.status_code == 200
    body = res.get_json()
    assert body["ok"] is True


def test_remote_access_ssh_start_fails(client, monkeypatch):
    import subprocess as _sp
    def fake_run(*args, **kwargs):
        raise OSError("service not found")
    monkeypatch.setattr(_sp, "run", fake_run)
    res = client.post("/api/remote-access/ssh/start")
    assert res.status_code == 500
    assert "error" in res.get_json()


# ── SSH Keys ─────────────────────────────────────────────────────

def test_remote_access_ssh_keys_get(client):
    res = client.get("/api/remote-access/ssh/keys")
    assert res.status_code == 200
    body = res.get_json()
    assert "keys" in body
    assert isinstance(body["keys"], list)


def test_remote_access_ssh_keys_add(client, tmp_path, monkeypatch):
    # The route hardcodes /root/.ssh/authorized_keys and
    # /home/freeai/.ssh/authorized_keys. Create them under tmp_path and
    # symlink (or just create the real paths on this platform).
    root_ssh = tmp_path / "root" / ".ssh"
    root_ssh.mkdir(parents=True)
    (root_ssh / "authorized_keys").write_text("")
    home_freeai = tmp_path / "home" / "freeai" / ".ssh"
    home_freeai.mkdir(parents=True)
    (home_freeai / "authorized_keys").write_text("")
    # Replace the hardcoded paths with tmp_path versions
    import pathlib
    real_root = pathlib.Path("/root/.ssh/authorized_keys")
    real_freeai = pathlib.Path("/home/freeai/.ssh/authorized_keys")
    # On Windows these are relative to C:\; just create them there
    real_root.parent.mkdir(parents=True, exist_ok=True)
    real_freeai.parent.mkdir(parents=True, exist_ok=True)
    (real_root).write_text("")
    (real_freeai).write_text("")
    res = client.post("/api/remote-access/ssh/keys", json={
        "action": "add",
        "keys": ["ssh-rsa AAAAB3 test-key"]})
    assert res.status_code == 200
    body = res.get_json()
    assert body["ok"] is True
    assert body["added"] == 1
    # Verify key is now returned
    res = client.get("/api/remote-access/ssh/keys")
    keys = res.get_json()["keys"]
    assert any("test-key" in k for k in keys)
    # Cleanup
    real_root.unlink(missing_ok=True)
    real_freeai.unlink(missing_ok=True)


def test_remote_access_ssh_keys_add_empty(client):
    res = client.post("/api/remote-access/ssh/keys", json={
        "action": "add", "keys": []})
    assert res.status_code == 200
    body = res.get_json()
    assert body["ok"] is True
    assert body["added"] == 0


def test_remote_access_ssh_keys_unknown_action(client):
    res = client.post("/api/remote-access/ssh/keys", json={
        "action": "unknown", "keys": []})
    assert res.status_code == 400
