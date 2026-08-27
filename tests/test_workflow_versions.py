"""Workflow versioning tests: create, list, restore, diff."""
import json
import os
import sys
import time
import tempfile
from pathlib import Path

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "workflow"))

import pytest

from workflow.versioning import (  # noqa: E402
    create_version, list_versions, get_version, diff_versions,
    restore_version, _version_dir, WORKFLOW_VERSIONS_ROOT,
)


@pytest.fixture(autouse=True)
def _tmp_versions(monkeypatch, tmp_path):
    """Use a temporary directory for versions during tests."""
    monkeypatch.setattr("workflow.versioning.WORKFLOW_VERSIONS_ROOT", tmp_path)
    return tmp_path


def test_create_version_writes_file():
    wf_id = "test-wf-1"
    definition = {"name": "my-workflow", "steps": [{"name": "a", "agent": "x"}]}
    result = create_version(wf_id, definition)
    assert "version" in result
    assert "path" in result
    assert Path(result["path"]).exists()


def test_create_version_returns_hash_suffix():
    wf_id = "test-wf-2"
    definition = {"name": "same-def", "value": 42}
    r1 = create_version(wf_id, definition)
    time.sleep(0.01)
    r2 = create_version(wf_id, definition)
    # Same definition -> same hash; different timestamps
    assert r1["version"].startswith("v")
    assert r2["version"].startswith("v")
    assert r1["version"] != r2["version"]  # different timestamps


def test_create_version_different_definition_different_hash():
    wf_id = "test-wf-3"
    r1 = create_version(wf_id, {"name": "a", "val": 1})
    r2 = create_version(wf_id, {"name": "a", "val": 2})
    assert r1["version"] != r2["version"]


def test_list_versions_returns_sorted():
    wf_id = "test-wf-4"
    create_version(wf_id, {"name": "first"})
    time.sleep(0.01)
    create_version(wf_id, {"name": "second"})
    versions = list_versions(wf_id)
    assert len(versions) == 2
    assert versions[0]["version"] != versions[1]["version"]
    # sorted by mtime (oldest first)
    assert versions[0]["timestamp_iso"] <= versions[1]["timestamp_iso"]


def test_list_versions_empty():
    assert list_versions("nonexistent-wf") == []


def test_get_version_retrieves_full_data():
    wf_id = "test-wf-5"
    definition = {"name": "wf", "steps": [{"name": "step1"}]}
    result = create_version(wf_id, definition)
    ver = result["version"]
    data = get_version(wf_id, ver)
    assert data is not None
    assert data["definition"] == definition
    assert data["workflow_id"] == wf_id
    assert "timestamp" in data
    assert "timestamp_iso" in data


def test_get_version_returns_none_for_missing():
    assert get_version("no-such-wf", "v9999") is None


def test_diff_versions_returns_diff_dict():
    wf_id = "test-wf-6"
    create_version(wf_id, {"name": "wf", "steps": [{"name": "a"}],
                            "config": {"debug": True}})
    time.sleep(0.01)
    create_version(wf_id, {"name": "wf", "steps": [{"name": "b"}],
                            "config": {"debug": False}})
    vers = list_versions(wf_id)
    diff = diff_versions(wf_id, vers[0]["version"], vers[1]["version"])
    assert "diff" in diff
    assert diff["version_from"] == vers[0]["version"]
    assert diff["version_to"] == vers[1]["version"]


def test_diff_versions_missing_version():
    wf_id = "test-wf-7"
    diff = diff_versions(wf_id, "v-nonexistent", "v-also-missing")
    assert "error" in diff


def test_restore_version_returns_definition():
    wf_id = "test-wf-8"
    definition = {"name": "restored-wf", "steps": [{"name": "s1"}]}
    result = create_version(wf_id, definition)
    ver = result["version"]
    restored = restore_version(wf_id, ver)
    assert restored["ok"] is True
    assert restored["definition"]["name"] == "restored-wf"
    assert restored["definition"]["steps"] == [{"name": "s1"}]
    assert "_restored_from" in restored
    assert "_restored_at" in restored


def test_restore_version_missing_returns_error():
    restored = restore_version("no-wf", "v-missing")
    assert "error" in restored
