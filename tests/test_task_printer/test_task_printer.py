"""Tests for task_printer skill script."""
import json
import pytest
from pathlib import Path

import sys

TASKS_SCRIPT = Path(__file__).parent.parent.parent / "skills" / "task_printer" / "scripts" / "task_printer.py"
sys.path.insert(0, str(TASKS_SCRIPT.parent.parent))


@pytest.fixture
def sample_tasks():
    return [
        {"task_id": "T1", "task_name": "Install deps", "task_description": "Run pip install"},
        {"task_id": "T2", "task_name": "Run tests", "task_description": "Execute pytest"},
        {"task_id": "T3", "task_name": "Deploy", "task_description": "Push to production"},
    ]


@pytest.fixture
def tasks_json_file(tmp_path, sample_tasks):
    path = tmp_path / "tasks.json"
    path.write_text(json.dumps(sample_tasks, indent=2), encoding="utf-8")
    return path


def test_print_tasks_success(tasks_json_file, capsys):
    import importlib.util
    spec = importlib.util.spec_from_file_location("task_printer", TASKS_SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)

    result = mod.print_tasks(str(tasks_json_file))
    assert result == 0

    captured = capsys.readouterr()
    assert "T1 | Install deps" in captured.out
    assert "Run pip install" in captured.out
    assert "T2 | Run tests" in captured.out
    assert "Execute pytest" in captured.out
    assert "T3 | Deploy" in captured.out
    assert "Push to production" in captured.out


def test_print_tasks_missing_file(capsys):
    import importlib.util
    spec = importlib.util.spec_from_file_location("task_printer", TASKS_SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)

    result = mod.print_tasks("/nonexistent/path/tasks.json")
    assert result == 1

    captured = capsys.readouterr()
    assert "Error: File not found" in captured.err


def test_print_tasks_invalid_json(tmp_path, capsys):
    bad_json = tmp_path / "bad.json"
    bad_json.write_text("{not valid json!!!", encoding="utf-8")

    import importlib.util
    spec = importlib.util.spec_from_file_location("task_printer", TASKS_SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)

    result = mod.print_tasks(str(bad_json))
    assert result == 1

    captured = capsys.readouterr()
    assert "Error: Invalid JSON" in captured.err


def test_print_tasks_not_array(tmp_path, capsys):
    not_array = tmp_path / "not_array.json"
    not_array.write_text('{"task_id": "T1"}', encoding="utf-8")

    import importlib.util
    spec = importlib.util.spec_from_file_location("task_printer", TASKS_SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)

    result = mod.print_tasks(str(not_array))
    assert result == 1

    captured = capsys.readouterr()
    assert "Error: JSON root must be an array" in captured.err


def test_print_tasks_missing_keys(tmp_path, capsys):
    incomplete = tmp_path / "incomplete.json"
    incomplete.write_text(json.dumps([{"task_id": "T1"}]), encoding="utf-8")

    import importlib.util
    spec = importlib.util.spec_from_file_location("task_printer", TASKS_SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)

    result = mod.print_tasks(str(incomplete))
    assert result == 1

    captured = capsys.readouterr()
    assert "Error: Task at index 0 missing keys" in captured.err


def test_print_tasks_empty_array(tmp_path, capsys):
    empty = tmp_path / "empty.json"
    empty.write_text("[]", encoding="utf-8")

    import importlib.util
    spec = importlib.util.spec_from_file_location("task_printer", TASKS_SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)

    result = mod.print_tasks(str(empty))
    assert result == 0

    captured = capsys.readouterr()
    assert captured.out.strip() == ""


def test_cli_usage_no_args(capsys):
    import subprocess
    result = subprocess.run(
        [sys.executable, str(TASKS_SCRIPT)],
        capture_output=True, text=True
    )
    assert result.returncode != 0
    assert "Usage:" in result.stderr
