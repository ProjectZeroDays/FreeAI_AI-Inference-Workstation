"""Tests for the pipeline API module."""
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))

from pipeline.api import (  # noqa: E402
    app,
    pipeline_scaffold,
    pipeline_refactor,
    pipeline_debug,
    pipeline_analyze,
    pipeline_review,
    pipeline_document,
    run_custom_pipeline,
    _runs,
    _runs_lock,
    _extract_text,
    _write_file,
    _read_tree,
)
from fastapi.testclient import TestClient  # noqa: E402


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture(autouse=True)
def clear_runs():
    """Clear pipeline runs before each test."""
    with _runs_lock:
        _runs.clear()
    yield
    with _runs_lock:
        _runs.clear()


@pytest.fixture
def mock_llm():
    """Mock the LLM call to avoid real HTTP requests."""
    with patch("pipeline.api._call_llm") as mock:
        mock.return_value = {"response": {"content": "mocked response"}}
        yield mock


# ── Health ──────────────────────────────────────────────────────────

def test_health(client):
    res = client.get("/health")
    assert res.status_code == 200
    body = res.json()
    assert body["status"] == "ok"
    assert "active_pipelines" in body


# ── Scaffold ───────────────────────────────────────────────────────

def test_scaffold(client, mock_llm):
    res = client.post("/pipeline/scaffold", json={"spec": "build a web app"})
    assert res.status_code == 200
    body = res.json()
    assert body["phase"] == "scaffold"
    mock_llm.assert_called_once()


def test_scaffold_invalid_profile(client, mock_llm):
    res = client.post("/pipeline/scaffold", json={"spec": "x", "profile": "invalid-profile"})
    assert res.status_code == 200
    assert res.json()["phase"] == "scaffold"


# ── Refactor ────────────────────────────────────────────────────────

def test_refactor(client, mock_llm):
    res = client.post("/pipeline/refactor", json={
        "code": "def foo(): pass",
        "language": "python",
        "goals": "clean code",
    })
    assert res.status_code == 200
    assert res.json()["phase"] == "refactor"


def test_refactor_invalid_language(client, mock_llm):
    res = client.post("/pipeline/refactor", json={"code": "x", "language": "cobol"})
    assert res.status_code == 200


# ── Debug ───────────────────────────────────────────────────────────

def test_debug(client, mock_llm):
    res = client.post("/pipeline/debug", json={
        "code": "def broken(): return 1/0",
        "error": "ZeroDivisionError",
    })
    assert res.status_code == 200
    assert res.json()["phase"] == "debug"


def test_debug_empty_code(client, mock_llm):
    res = client.post("/pipeline/debug", json={"code": "", "error": "boom"})
    assert res.status_code == 200


# ── Analyze ─────────────────────────────────────────────────────────

def test_analyze(client, mock_llm):
    res = client.post("/pipeline/analyze", json={
        "context": "some context",
        "question": "what is this?",
    })
    assert res.status_code == 200
    assert res.json()["phase"] == "analyze"


# ── Review ──────────────────────────────────────────────────────────

def test_review(client, mock_llm):
    res = client.post("/pipeline/review", json={
        "code": "def bad(): pass",
        "spec": "good code",
    })
    assert res.status_code == 200
    assert res.json()["phase"] == "review"


# ── Document ────────────────────────────────────────────────────────

def test_document(client, mock_llm):
    res = client.post("/pipeline/document", json={
        "spec": "my spec",
        "tree": "README.md",
    })
    assert res.status_code == 200
    assert res.json()["phase"] == "document"


# ── Custom Pipeline ─────────────────────────────────────────────────

def test_custom_pipeline_runs_steps(client, mock_llm):
    res = client.post("/pipeline/custom", json={
        "spec": "build a todo app",
        "steps": [
            {"phase": "scaffold", "input": {"spec": "build a todo app"}},
            {"phase": "analyze", "input": {"question": "what are the requirements?"}},
        ],
    })
    assert res.status_code == 200
    body = res.json()
    assert "pipeline_id" in body
    assert body["status"] == "started"
    pid = body["pipeline_id"]

    res2 = client.get(f"/pipeline/status/{pid}")
    assert res2.status_code == 200
    status_body = res2.json()
    assert "pipeline_id" in status_body
    assert "status" in status_body


def test_custom_pipeline_not_found(client):
    res = client.get("/pipeline/status/nonexistent-pipeline-id-xyz")
    assert res.status_code == 404


def test_custom_pipeline_cancel(client, mock_llm):
    res = client.post("/pipeline/custom", json={
        "spec": "test",
        "steps": [{"phase": "scaffold", "input": {}}],
    })
    pid = res.json()["pipeline_id"]
    res2 = client.post(f"/pipeline/cancel/{pid}")
    assert res2.status_code == 200
    assert res2.json()["status"] == "cancelled"


def test_custom_pipeline_cancel_not_found(client):
    res = client.post("/pipeline/cancel/nonexistent")
    assert res.status_code == 404


def test_list_pipelines_empty(client):
    res = client.get("/pipeline/status")
    assert res.status_code == 200
    body = res.json()
    assert body["pipelines"] == []
    assert body["total"] == 0


def test_list_pipelines_after_run(client, mock_llm):
    client.post("/pipeline/custom", json={
        "spec": "test",
        "steps": [{"phase": "analyze", "input": {}}],
    })
    res = client.get("/pipeline/status")
    body = res.json()
    assert body["total"] >= 1


# ── Helper functions ────────────────────────────────────────────────

def test_extract_text_dict():
    result = {"response": {"content": "hello world"}}
    assert _extract_text(result) == "hello world"


def test_extract_text_string():
    result = {"response": "plain text"}
    assert _extract_text(result) == "plain text"


def test_extract_text_empty():
    assert _extract_text({}) == ""


def test_extract_text_none_response():
    assert _extract_text({"response": None}) == "None"


def test_write_file_in_workspace(tmp_path):
    ws = tmp_path / "ws"
    ws.mkdir()
    path = _write_file(ws, "sub/dir/test.txt", "hello")
    assert (ws / "sub" / "dir" / "test.txt").read_text() == "hello"
    assert path.endswith("test.txt")


def test_write_file_path_traversal_blocked(tmp_path):
    ws = tmp_path / "ws"
    ws.mkdir()
    with pytest.raises(Exception, match="Invalid file path"):
        _write_file(ws, "../etc/passwd", "evil")


def test_read_tree_empty(tmp_path):
    tree = _read_tree(tmp_path)
    assert tree == "(empty workspace)"


def test_read_tree_with_files(tmp_path):
    (tmp_path / "a.txt").write_text("aaa")
    (tmp_path / "b.txt").write_text("bbb")
    tree = _read_tree(tmp_path)
    assert "a.txt" in tree
    assert "b.txt" in tree


# ── Pipeline functions directly ─────────────────────────────────────

def test_pipeline_scaffold_returns_phase(mock_llm):
    result = pipeline_scaffold("build a app", profile="creative")
    assert result["phase"] == "scaffold"
    assert "result" in result


def test_pipeline_refactor_returns_phase(mock_llm):
    result = pipeline_refactor("def x(): pass", language="python")
    assert result["phase"] == "refactor"
    assert "result" in result


def test_pipeline_debug_returns_phase(mock_llm):
    result = pipeline_debug("def x(): 1/0", error="ZeroDivisionError")
    assert result["phase"] == "debug"
    assert "result" in result


def test_pipeline_analyze_returns_phase(mock_llm):
    result = pipeline_analyze("context here", "what is it?")
    assert result["phase"] == "analyze"
    assert "result" in result


def test_pipeline_review_returns_phase(mock_llm):
    result = pipeline_review("code here", spec="good code")
    assert result["phase"] == "review"
    assert "result" in result


def test_pipeline_document_returns_phase(mock_llm):
    result = pipeline_document("spec", "tree")
    assert result["phase"] == "document"
    assert "result" in result
