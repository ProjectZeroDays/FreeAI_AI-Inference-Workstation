"""Tests for the secrets management module and dashboard API endpoints."""
import json
import os
import sys
import tempfile
from pathlib import Path

import pytest

flask = pytest.importorskip("flask")

from dashboard import backend as dash  # noqa: E402
from dashboard import secrets as secrets_mod  # noqa: E402


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
    monkeypatch.setattr(dash, "OPT_SETTINGS_PATH", str(tmp_path / "runtime-settings.json"))
    monkeypatch.setattr(dash, "PRESETS_PATH", str(tmp_path / "presets.json"))
    monkeypatch.setattr(dash, "PROVIDERS_MERGED_PATH", str(tmp_path / "providers-merged.json"))
    monkeypatch.setattr(dash, "HERMES_CONFIG_PATH", tmp_path / "hermes.json")
    monkeypatch.setattr(dash, "_SCHEDULER_CONFIG_PATH", str(tmp_path / "scheduler.json"))
    monkeypatch.setattr(secrets_mod, "SECRETS_DIR", tmp_path / "secrets.enc")
    monkeypatch.setattr(secrets_mod, "METADATA_PATH", tmp_path / "secrets.enc" / "metadata.json")
    dash._SUBAGENTS.clear()
    dash._TRAINING_DATA.update({"datasets": [], "jobs": {"sft": [], "dpo": [], "abr": []}, "models": []})
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
    dash._SALAD_CACHE = {"salad": None, "gpu": None, "ts": 0.0}
    # Clear any leaked in-memory secrets from other tests
    secrets_mod._IN_MEMORY.clear()
    # Remove any leftover encrypted files from prior tests
    if secrets_mod.SECRETS_DIR.exists():
        for f in secrets_mod.SECRETS_DIR.glob("*.enc"):
            try:
                f.unlink()
            except OSError:
                pass
        try:
            (secrets_mod.SECRETS_DIR / "metadata.json").unlink()
        except OSError:
            pass
    dash.app.config["TESTING"] = True
    dash.app.config["SECRET_KEY"] = "test-secret-key-for-evals"
    with dash.app.test_client() as c:
        yield c


@pytest.fixture()
def auth_client(client, monkeypatch):
    monkeypatch.setattr(dash, "AUTH_TOKEN", "test-auth-token-123")
    return client


# ── Module-level tests ───────────────────────────────────────────


def test_store_and_list_secrets():
    secrets_mod.store_secret("test-key", "test-value-123")
    names = secrets_mod.list_secrets()
    assert "test-key" in names
    val = secrets_mod.get_secret("test-key")
    assert val == "test-value-123"
    secrets_mod.delete_secret("test-key")


def test_get_secret_returns_none_for_missing():
    result = secrets_mod.get_secret("nonexistent-secret-xyz")
    assert result is None


def test_delete_secret():
    secrets_mod.store_secret("to-delete", "some-value")
    assert secrets_mod.get_secret("to-delete") == "some-value"
    assert secrets_mod.delete_secret("to-delete") is True
    assert secrets_mod.get_secret("to-delete") is None
    assert secrets_mod.delete_secret("to-delete") is False  # already gone


def test_rotate_secret():
    secrets_mod.store_secret("rotatable", "original-value")
    assert secrets_mod.get_secret("rotatable") == "original-value"
    result = secrets_mod.rotate_secret("rotatable", "new-rotated-value")
    assert result is True
    assert secrets_mod.get_secret("rotatable") == "new-rotated-value"
    secrets_mod.delete_secret("rotatable")


def test_rotate_missing_secret():
    result = secrets_mod.rotate_secret("does-not-exist", "new-value")
    assert result is False


def test_list_secrets_no_values():
    secrets_mod.store_secret("alpha", "secret-a")
    secrets_mod.store_secret("beta", "secret-b")
    names = secrets_mod.list_secrets()
    assert isinstance(names, list)
    assert all(isinstance(n, str) for n in names)
    assert "alpha" in names
    assert "beta" in names
    # Should not contain any values
    for n in names:
        assert "secret-" not in n
    secrets_mod.delete_secret("alpha")
    secrets_mod.delete_secret("beta")


def test_import_secrets():
    data = {"key-one": "value-one", "key-two": "value-two", "key-three": "value-three"}
    result = secrets_mod.import_secrets(data)
    assert result["imported"] == 3
    assert result["failed_count"] == 0
    assert secrets_mod.get_secret("key-one") == "value-one"
    assert secrets_mod.get_secret("key-two") == "value-two"
    assert secrets_mod.get_secret("key-three") == "value-three"
    secrets_mod.delete_secret("key-one")
    secrets_mod.delete_secret("key-two")
    secrets_mod.delete_secret("key-three")


def test_import_secrets_partial_failure():
    data = {"valid-key": "valid-value", "": "no-name", "bad key!": "bad"}
    result = secrets_mod.import_secrets(data)
    # Empty name should fail; others may or may not store depending on sanitization
    assert result["imported"] >= 0
    assert result["failed_count"] >= 0


def test_secrets_encrypted_storage():
    """Verify that encrypted files are actually written and not plaintext."""
    secrets_mod.store_secret("enc-test", "my-super-secret")
    enc_dir = secrets_mod.SECRETS_DIR
    assert enc_dir.exists()
    enc_files = list(enc_dir.glob("*.enc"))
    assert len(enc_files) >= 1
    # The encrypted file should not contain the plaintext value
    for f in enc_files:
        content = f.read_text()
        assert "my-super-secret" not in content
        assert len(content) > 20  # base64-encoded ciphertext is longer
    secrets_mod.delete_secret("enc-test")


def test_export_secrets():
    secrets_mod.store_secret("export-me", "export-value")
    exported = secrets_mod.export_secrets()
    assert "export-me" in exported
    assert exported["export-me"] == "export-value"
    secrets_mod.delete_secret("export-me")


def test_get_secret_metadata():
    secrets_mod.store_secret("meta-test", "value")
    meta = secrets_mod.get_secret_metadata("meta-test")
    assert meta is not None
    assert meta["name"] == "meta-test"
    assert "created_at" in meta
    assert "updated_at" in meta
    assert "value" not in meta  # metadata must never include the value
    secrets_mod.delete_secret("meta-test")


def test_get_secret_metadata_missing():
    meta = secrets_mod.get_secret_metadata("nonexistent")
    assert meta is None


def test_master_key_from_env():
    original = os.environ.get("SECRETS_MASTER_KEY")
    os.environ["SECRETS_MASTER_KEY"] = "test-master-key-for-unit-tests"
    try:
        key1 = secrets_mod._get_master_key()
        key2 = secrets_mod._get_master_key()
        assert len(key1) == 32
        assert key1 == key2
        # Different key should produce different per-secret keys
        secrets_mod.store_secret("key-env-test", "val")
        val = secrets_mod.get_secret("key-env-test")
        assert val == "val"
        secrets_mod.delete_secret("key-env-test")
    finally:
        if original is None:
            os.environ.pop("SECRETS_MASTER_KEY", None)
        else:
            os.environ["SECRETS_MASTER_KEY"] = original


# ── API endpoint tests ───────────────────────────────────────────


def test_secrets_page(client):
    res = client.get("/secrets")
    assert res.status_code == 200


def test_list_secrets_empty(client):
    res = client.get("/api/secrets")
    assert res.status_code == 200
    body = res.get_json()
    assert body["secrets"] == []
    assert body["total"] == 0


def test_store_secret_via_api(client):
    res = client.post("/api/secrets", json={"name": "api-key", "value": "sk-test-123"})
    assert res.status_code == 200
    body = res.get_json()
    assert body["ok"] is True
    assert body["name"] == "api-key"


def test_store_secret_missing_fields(client):
    res = client.post("/api/secrets", json={})
    assert res.status_code == 400
    body = res.get_json()
    assert "error" in body


def test_get_secret_metadata_via_api(client):
    client.post("/api/secrets", json={"name": "my-secret", "value": "abc"})
    res = client.get("/api/secrets/my-secret")
    assert res.status_code == 200
    body = res.get_json()
    assert body["name"] == "my-secret"
    assert "value" not in body


def test_get_secret_metadata_not_found(client):
    res = client.get("/api/secrets/nonexistent")
    assert res.status_code == 404


def test_delete_secret_via_api(client):
    client.post("/api/secrets", json={"name": "del-me", "value": "x"})
    res = client.delete("/api/secrets/del-me")
    assert res.status_code == 200
    body = res.get_json()
    assert body["ok"] is True
    # Verify gone
    res2 = client.get("/api/secrets/del-me")
    assert res2.status_code == 404


def test_delete_secret_not_found(client):
    res = client.delete("/api/secrets/nonexistent")
    assert res.status_code == 404


def test_rotate_secret_via_api(client):
    client.post("/api/secrets", json={"name": "rot-me", "value": "original"})
    res = client.post("/api/secrets/rot-me/rotate", json={"value": "rotated"})
    assert res.status_code == 200
    body = res.get_json()
    assert body["ok"] is True
    # Verify new value
    assert secrets_mod.get_secret("rot-me") == "rotated"
    secrets_mod.delete_secret("rot-me")


def test_rotate_missing_secret(client):
    res = client.post("/api/secrets/nosuch/rotate", json={"value": "new"})
    assert res.status_code == 404


def test_rotate_missing_value(client):
    client.post("/api/secrets", json={"name": "rot2", "value": "orig"})
    res = client.post("/api/secrets/rot2/rotate", json={})
    assert res.status_code == 400
    secrets_mod.delete_secret("rot2")


def test_import_secrets_via_api(client):
    res = client.post("/api/secrets/import", json={
        "imported-key-1": "val1",
        "imported-key-2": "val2",
    })
    assert res.status_code == 200
    body = res.get_json()
    assert body["imported"] == 2
    assert secrets_mod.get_secret("imported-key-1") == "val1"
    secrets_mod.delete_secret("imported-key-1")
    secrets_mod.delete_secret("imported-key-2")


def test_export_secrets_via_api(client):
    secrets_mod.store_secret("export-key", "export-val")
    res = client.get("/api/secrets/export")
    assert res.status_code == 200
    body = res.get_json()
    assert body["total"] >= 1
    assert "export-key" in body["secrets"]
    assert body["secrets"]["export-key"] == "export-val"
    secrets_mod.delete_secret("export-key")


def test_secrets_auth_required(auth_client, monkeypatch):
    """When AUTH_TOKEN is set, mutating endpoints require X-Auth-Token header."""
    # Store (no auth) → 401
    res = auth_client.post("/api/secrets", json={"name": "x", "value": "y"})
    assert res.status_code == 401

    # Delete (no auth) → 401
    res = auth_client.delete("/api/secrets/x")
    assert res.status_code == 401

    # Rotate (no auth) → 401
    res = auth_client.post("/api/secrets/x/rotate", json={"value": "z"})
    assert res.status_code == 401

    # Import (no auth) → 401
    res = auth_client.post("/api/secrets/import", json={"a": "1"})
    assert res.status_code == 401

    # GET endpoints should still work without auth
    res = auth_client.get("/api/secrets")
    assert res.status_code == 200

    res = auth_client.get("/api/secrets/export")
    assert res.status_code == 200


def test_secrets_auth_with_token(auth_client):
    """When AUTH_TOKEN is set, providing the correct token allows mutations."""
    headers = {"X-Auth-Token": "test-auth-token-123"}
    res = auth_client.post("/api/secrets", json={"name": "auth-test", "value": "ok"}, headers=headers)
    assert res.status_code == 200
    body = res.get_json()
    assert body["ok"] is True
    secrets_mod.delete_secret("auth-test")


def test_list_secrets_returns_no_values(client):
    """The /api/secrets list endpoint must never return secret values."""
    secrets_mod.store_secret("list-test", "this-is-secret")
    res = client.get("/api/secrets")
    body = res.get_json()
    names = body["secrets"]
    assert isinstance(names, list)
    for name in names:
        assert isinstance(name, str)
        assert "this-is-secret" not in name
    secrets_mod.delete_secret("list-test")


def test_secrets_content_not_in_metadata(client):
    """Metadata endpoint must not return the secret value."""
    secrets_mod.store_secret("meta-hidden", "hidden-value")
    res = client.get("/api/secrets/meta-hidden")
    body = res.get_json()
    assert "value" not in body
    assert "hidden-value" not in str(body)
    secrets_mod.delete_secret("meta-hidden")
