"""Tests for the HITL (Human-in-the-Loop) approval system."""
import os
import sys
import time

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)


@pytest.fixture
def tmp_hitl_config(tmp_path, monkeypatch):
    """Point HITL state to a temp directory."""
    import autonomous.approval as hitl
    monkeypatch.setattr(hitl, "CONFIG_DIR", tmp_path)
    monkeypatch.setattr(hitl, "HITL_STATE_PATH", tmp_path / "hitl.json")
    monkeypatch.setenv("HITL_ENABLED", "1")
    monkeypatch.setattr(hitl, "HITL_ENABLED", True)
    monkeypatch.setattr(hitl, "HITL_APPROVAL_TIMEOUT_S", 300)
    hitl._PENDING.clear()
    yield hitl
    # cleanup
    hitl._PENDING.clear()


def test_request_approval_pending(tmp_hitl_config):
    import autonomous.approval as hitl
    req = hitl.request_approval(
        operator="user1", action="deploy", target="prod",
        command="docker deploy", risk_level="high",
    )
    assert req["status"] == "pending"
    assert req["operator"] == "user1"
    assert req["request_id"]
    assert req["expires_at"] > req["created_at"]


def test_request_approval_auto_approved_when_disabled(tmp_hitl_config, monkeypatch):
    import autonomous.approval as hitl
    monkeypatch.setattr(hitl, "HITL_ENABLED", False)
    req = hitl.request_approval("u", "act", "tgt")
    assert req["status"] == "approved"
    assert req["auto_approved"] is True


def test_approve_then_is_approved(tmp_hitl_config):
    import autonomous.approval as hitl
    req = hitl.request_approval("u", "deploy", "prod")
    rid = req["request_id"]
    hitl.approve_request(rid, "admin")
    assert hitl.is_approved(rid) is True


def test_reject_then_is_not_approved(tmp_hitl_config):
    import autonomous.approval as hitl
    req = hitl.request_approval("u", "destroy", "prod")
    rid = req["request_id"]
    hitl.reject_request(rid, "not authorized", "security")
    assert hitl.is_approved(rid) is False


def test_double_approve_raises(tmp_hitl_config):
    import autonomous.approval as hitl
    req = hitl.request_approval("u", "deploy", "prod")
    hitl.approve_request(req["request_id"], "admin")
    with pytest.raises(ValueError):
        hitl.approve_request(req["request_id"], "admin2")


def test_detect_danger_file_deletion():
    import autonomous.approval as hitl
    matches = hitl._detect_danger("rm -rf /important", "cleanup")
    assert "file_deletion" in matches


def test_detect_danger_credential_theft():
    import autonomous.approval as hitl
    matches = hitl._detect_danger("cat /etc/shadow", "dump creds")
    assert "credential_theft" in matches


def test_detect_danger_no_match_safe_command():
    import autonomous.approval as hitl
    matches = hitl._detect_danger("echo hello world", "test")
    assert matches == []


def test_check_approval_required_returns_none_for_safe(tmp_hitl_config):
    import autonomous.approval as hitl
    result = hitl.check_approval_required("echo hi")
    assert result is None


def test_check_approval_required_returns_request_for_dangerous(tmp_hitl_config):
    import autonomous.approval as hitl
    result = hitl.check_approval_required("rm -rf /tmp", "cleanup old files")
    assert result is not None
    assert result["status"] == "pending"
    assert "file_deletion" in result["danger_patterns"]


def test_list_pending_requests(tmp_hitl_config):
    import autonomous.approval as hitl
    hitl.request_approval("u1", "a1", "t1", command="rm -rf /x")
    hitl.request_approval("u2", "a2", "t2", command="cat /etc/passwd")
    pending = hitl.list_pending()
    assert len(pending) == 2


def test_purge_expired_removes_old_requests(tmp_hitl_config, monkeypatch):
    import autonomous.approval as hitl
    monkeypatch.setattr(hitl, "HITL_APPROVAL_TIMEOUT_S", 0)
    hitl.request_approval("u", "a", "t", command="rm -rf /x")
    pending = hitl.list_pending()
    assert len(pending) == 1
    # Time has moved past expiry
    time.sleep(0.01)
    purged = hitl.purge_expired()
    assert purged >= 1
    assert len(hitl.list_pending()) == 0


def test_timeout_status_rejects(tmp_hitl_config, monkeypatch):
    import autonomous.approval as hitl
    monkeypatch.setattr(hitl, "HITL_APPROVAL_TIMEOUT_S", 0)
    req = hitl.request_approval("u", "a", "t", command="rm -rf /x")
    time.sleep(0.01)
    assert hitl.is_approved(req["request_id"]) is False


def test_persistence_to_disk(tmp_hitl_config):
    import autonomous.approval as hitl
    req = hitl.request_approval("u", "deploy", "prod", command="docker push")
    rid = req["request_id"]
    # Force persist
    hitl._persist()
    state_path = hitl.HITL_STATE_PATH
    assert state_path.exists()
    content = state_path.read_text()
    assert rid in content
