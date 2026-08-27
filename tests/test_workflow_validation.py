"""Tests for workflow/validator.py and workflow/audit.py."""
import json
import os
import tempfile
from pathlib import Path

import pytest

try:
    from workflow.validator import validate_workflow, _detect_cycles
    from workflow.audit import log_execution, read_audit
except ImportError:
    from validator import validate_workflow, _detect_cycles
    from audit import log_execution, read_audit


class _S:
    """Minimal step shim for validator tests."""
    def __init__(self, name, consumes=None, produces=None):
        self.name = name
        self.consumes = consumes
        self.produces = produces


# --------------------------- validator ---------------------------

def test_validate_ok_chain():
    steps = [
        _S("a", consumes=[], produces=["x"]),
        _S("b", consumes=["x"], produces=["y"]),
    ]
    assert validate_workflow(steps) == []


def test_validate_accepts_initial_keys():
    steps = [_S("b", consumes=["spec"], produces=["out"])]
    assert validate_workflow(steps, initial_keys=["spec"]) == []


def test_validate_missing_produces_warning():
    steps = [_S("a", consumes=[], produces=None)]
    w = validate_workflow(steps)
    assert any("missing 'produces'" in x for x in w)


def test_validate_missing_consumes_warning():
    steps = [_S("a", consumes=None, produces=["x"])]
    w = validate_workflow(steps)
    assert any("missing 'consumes'" in x for x in w)


def test_validate_missing_name_warning():
    steps = [_S(None, consumes=[], produces=[])]
    w = validate_workflow(steps)
    assert any("missing 'name'" in x for x in w)


def test_validate_missing_dependency():
    steps = [_S("b", consumes=["a"], produces=["y"])]
    w = validate_workflow(steps)
    assert any("'a'" in x for x in w)


def test_validate_circular_dependency():
    steps = [
        _S("a", consumes=["b"], produces=[]),
        _S("b", consumes=["a"], produces=[]),
    ]
    w = validate_workflow(steps)
    assert any("circular dependency" in x for x in w)


def test_validate_self_cycle():
    steps = [_S("a", consumes=["a"], produces=[])]
    w = validate_workflow(steps)
    assert any("circular dependency" in x for x in w)


def test_validate_no_cycle_linear():
    steps = [
        _S("a", consumes=[], produces=["x"]),
        _S("b", consumes=["x"], produces=["y"]),
        _S("c", consumes=["y"], produces=[]),
    ]
    w = validate_workflow(steps)
    assert not any("circular" in x for x in w)


# --------------------------- audit ---------------------------

def test_log_and_read_audit(tmp_path, monkeypatch):
    audit_file = tmp_path / "audit.jsonl"
    monkeypatch.setattr("workflow.audit.AUDIT_FILE", str(audit_file))

    log_execution("wf1", "id1", "started")
    log_execution("wf1", "id1", "finished", steps=["a", "b"])
    log_execution("wf1", "id2", "failed", error="boom")

    entries = read_audit()
    assert len(entries) == 3
    assert entries[0]["status"] == "started"
    assert entries[1]["steps"] == ["a", "b"]
    assert entries[2]["error"] == "boom"


def test_read_audit_missing_file(tmp_path, monkeypatch):
    audit_file = tmp_path / "nonexistent.jsonl"
    monkeypatch.setattr("workflow.audit.AUDIT_FILE", str(audit_file))
    assert read_audit() == []


def test_log_execution_returns_entry(tmp_path, monkeypatch):
    audit_file = tmp_path / "audit.jsonl"
    monkeypatch.setattr("workflow.audit.AUDIT_FILE", str(audit_file))
    entry = log_execution("my_wf", "wid", "started", extra={"tag": "x"})
    assert entry["workflow"] == "my_wf"
    assert entry["tag"] == "x"
