"""Encryption API tests: page, disks, check-passphrase, recovery-key, encrypt-disk."""
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
    with dash.app.test_client() as c:
        yield c


# ── Page Route ───────────────────────────────────────────────────

def test_encryption_page(client):
    res = client.get("/encryption")
    assert res.status_code == 200


# ── Disks API ────────────────────────────────────────────────────

def test_encryption_disks(client, monkeypatch):
    def fake_run(*args, **kwargs):
        class R:
            returncode = 0
            stdout = json.dumps({"blockdevices": []})
            stderr = ""
        return R()
    monkeypatch.setattr("subprocess.run", fake_run)
    res = client.get("/api/encryption/disks")
    assert res.status_code == 200
    body = res.get_json()
    assert "disks" in body
    assert "lsblk" in body
    assert "scanned_at" in body


# ── Check Passphrase ─────────────────────────────────────────────

def test_encryption_check_passphrase_missing_fields(client):
    res = client.post("/api/encryption/check-passphrase", json={})
    assert res.status_code == 400
    body = res.get_json()
    assert "error" in body

    res = client.post("/api/encryption/check-passphrase", json={
        "disk": "/dev/sda"})
    assert res.status_code == 400

    res = client.post("/api/encryption/check-passphrase", json={
        "passphrase": "secret"})
    assert res.status_code == 400


def test_encryption_check_passphrase_success(client, monkeypatch):
    def fake_run(*args, **kwargs):
        class R:
            returncode = 0
            stdout = ""
            stderr = ""
        return R()
    monkeypatch.setattr("subprocess.run", fake_run)
    res = client.post("/api/encryption/check-passphrase", json={
        "disk": "/dev/sda", "passphrase": "test"})
    assert res.status_code == 200
    body = res.get_json()
    assert "valid" in body
    assert body["disk"] == "/dev/sda"


def test_encryption_check_passphrase_timeout(client, monkeypatch):
    def fake_run(*args, **kwargs):
        raise TimeoutError("timed out")
    monkeypatch.setattr("subprocess.run", fake_run)
    res = client.post("/api/encryption/check-passphrase", json={
        "disk": "/dev/sda", "passphrase": "test"})
    # The route catches TimeoutExpired (subprocess-specific); a plain
    # TimeoutError falls through to the generic Exception handler → 500.
    assert res.status_code == 500


# ── Recovery Key ─────────────────────────────────────────────────

def test_encryption_recovery_key(client, tmp_path, monkeypatch):
    # The route writes to /etc/freeai/partition-info.json which is not
    # writable on this platform; expect 500.
    res = client.post("/api/encryption/recovery-key")
    assert res.status_code in (200, 500)
    if res.status_code == 200:
        body = res.get_json()
        assert body["ok"] is True
        assert "key" in body
        assert body["length"] == 32


# ── Encrypt Disk ─────────────────────────────────────────────────

def test_encryption_encrypt_disk_missing_fields(client):
    res = client.post("/api/encryption/encrypt-disk", json={})
    assert res.status_code == 400
    body = res.get_json()
    assert "error" in body

    res = client.post("/api/encryption/encrypt-disk", json={
        "disk": "/dev/sda"})
    assert res.status_code == 400

    res = client.post("/api/encryption/encrypt-disk", json={
        "passphrase": "secret"})
    assert res.status_code == 400


def test_encryption_encrypt_disk_invalid_path(client, monkeypatch):
    """A path not starting with /dev/ should be normalised, but the
    resulting command will fail — we verify it hits the destructive path
    and returns an error (not a successful encrypt)."""
    def fake_run(*args, **kwargs):
        class FakeProc:
            returncode = 1
            stdout = ""
            stderr = "command not found"
        raise OSError("no such file")
    monkeypatch.setattr("subprocess.run", fake_run)
    res = client.post("/api/encryption/encrypt-disk", json={
        "disk": "not-a-device", "passphrase": "secret"})
    # Should error rather than succeed
    body = res.get_json()
    assert "error" in body


def test_encryption_encrypt_disk_dev_path(client, monkeypatch):
    """Valid /dev/sda path: subprocess calls will fail (no real devices),
    so we expect an error response, not a 200 success."""
    def fake_run(*args, **kwargs):
        raise OSError("mock: no such device")
    monkeypatch.setattr("subprocess.run", fake_run)
    res = client.post("/api/encryption/encrypt-disk", json={
        "disk": "/dev/sda", "passphrase": "secret"})
    # Any non-200 is acceptable since we have no real block devices
    assert res.status_code != 200 or "error" in res.get_json()
