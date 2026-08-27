"""RBAC role hierarchy and permission matrix tests."""
import sys
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

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
    monkeypatch.setattr(dash, "AIKIDO_API_KEY", "")
    monkeypatch.setattr(dash, "AIKIDO_APP_ID", "")
    monkeypatch.setattr(dash, "OPT_SETTINGS_PATH",
                        str(tmp_path / "runtime-settings.json"))
    monkeypatch.setattr(dash, "PRESETS_PATH",
                        str(tmp_path / "presets.json"))
    monkeypatch.setattr(dash, "PROVIDERS_MERGED_PATH",
                        str(tmp_path / "providers-merged.json"))
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
    dash.app.config["TESTING"] = True
    dash.app.config["SECRET_KEY"] = "test-secret-key-for-rbac"
    with dash.app.test_client() as c:
        yield c


# ── Role hierarchy ─────────────────────────────────────────────

def test_role_hierarchy_operator_can_viewer(client):
    """operator > viewer: operator can do everything viewer can."""
    res = client.post("/api/permissions/check",
                      json={"resource": "config", "action": "read",
                            "role": "viewer"})
    assert res.get_json()["allowed"] is True
    res2 = client.post("/api/permissions/check",
                       json={"resource": "config", "action": "read",
                             "role": "operator"})
    assert res2.get_json()["allowed"] is True


def test_role_hierarchy_admin_can_operator(client):
    """admin > operator: admin can do everything operator can."""
    res = client.post("/api/permissions/check",
                      json={"resource": "config", "action": "write",
                            "role": "admin"})
    body = res.get_json()
    assert body["allowed"] is True
    res2 = client.post("/api/permissions/check",
                       json={"resource": "config", "action": "write",
                             "role": "operator"})
    assert res2.get_json()["allowed"] is True


def test_viewer_cannot_modify_config(client):
    res = client.post("/api/permissions/check",
                      json={"resource": "config", "action": "write",
                            "role": "viewer"})
    assert res.get_json()["allowed"] is False


def test_viewer_can_read_models(client):
    res = client.post("/api/permissions/check",
                      json={"resource": "models", "action": "read",
                            "role": "viewer"})
    assert res.get_json()["allowed"] is True


def test_operator_can_deploy_models(client):
    res = client.post("/api/permissions/check",
                      json={"resource": "models", "action": "write",
                            "role": "operator"})
    assert res.get_json()["allowed"] is True


def test_admin_can_delete_users(client):
    res = client.post("/api/permissions/check",
                      json={"resource": "users", "action": "delete",
                            "role": "admin"})
    assert res.get_json()["allowed"] is True


def test_viewer_cannot_delete_users(client):
    res = client.post("/api/permissions/check",
                      json={"resource": "users", "action": "delete",
                            "role": "viewer"})
    assert res.get_json()["allowed"] is False


# ── Permission matrix ──────────────────────────────────────────

def test_permission_matrix_admin_all_actions(client):
    for resource in ("models", "config", "users", "run", "delete"):
        for action in ("read", "write", "exec"):
            res = client.post("/api/permissions/check",
                              json={"resource": resource, "action": action,
                                    "role": "admin"})
            assert res.get_json()["allowed"] is True, \
                f"admin should allow {resource}/{action}"


def test_permission_matrix_viewer_read_only(client):
    for resource in ("models", "config", "skills", "workflows"):
        res = client.post("/api/permissions/check",
                          json={"resource": resource, "action": "read",
                                "role": "viewer"})
        assert res.get_json()["allowed"] is True, \
            f"viewer should read {resource}"
    res = client.post("/api/permissions/check",
                      json={"resource": "config", "action": "write",
                            "role": "viewer"})
    assert res.get_json()["allowed"] is False


def test_permission_matrix_developer_cannot_delete(client):
    res = client.post("/api/permissions/check",
                      json={"resource": "users", "action": "delete",
                            "role": "developer"})
    assert res.get_json()["allowed"] is False


def test_permission_matrix_operator_can_run(client):
    res = client.post("/api/permissions/check",
                      json={"resource": "run", "action": "exec",
                            "role": "operator"})
    assert res.get_json()["allowed"] is True


# ── @require_role decorator ────────────────────────────────────

def test_require_role_decorator_allows_equal(client):
    from auth.users import require_role
    checker = require_role("developer")
    user = {"username": "alice", "role": "developer"}
    result = checker(user)
    assert result == user


def test_require_role_decorator_allows_higher(client):
    from auth.users import require_role
    checker = require_role("developer")
    user = {"username": "bob", "role": "admin"}
    result = checker(user)
    assert result == user


def test_require_role_decorator_blocks_lower(client):
    from auth.users import require_role
    checker = require_role("admin")
    user = {"username": "carol", "role": "developer"}
    result = checker(user)
    assert result is None


def test_require_role_decorator_blocks_none(client):
    from auth.users import require_role
    checker = require_role("viewer")
    assert checker(None) is None


def test_require_role_unknown_role_defaults_to_viewer(client):
    """A role not in the hierarchy falls back to level 0 (viewer)."""
    from auth.users import require_role
    checker = require_role("superadmin")
    user = {"username": "x", "role": "admin"}
    # superadmin is not in the role_order dict, defaults to 0
    # admin level is 2, so 2 >= 0 -> allowed
    result = checker(user)
    assert result == user
