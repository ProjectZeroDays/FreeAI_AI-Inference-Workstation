#!/usr/bin/env python3
"""
Task Printer — Read and display tasks from a JSON file.

Usage:
    python task_printer.py <tasks.json>

The JSON file should contain an array of task objects:
    [
        {"task_id": "T1", "task_name": "Install dependencies", "task_description": "Run pip install -r requirements.txt"},
        {"task_id": "T2", "task_name": "Run tests", "task_description": "Execute pytest"},
        {"task_id": "T3", "task_name": "Deploy", "task_description": "Push to production"}
    ]

Output:
    T1 | Install dependencies
        Run pip install -r requirements.txt

    T2 | Run tests
        Execute pytest

    T3 | Deploy
        Push to production
"""

import json
import sys
from pathlib import Path


def print_tasks(json_path: str) -> int:
    """Read a JSON file of tasks and print them to console.

    Args:
        json_path: Path to the JSON file containing tasks.

    Returns:
        0 on success, 1 on error.
    """
    path = Path(json_path)

    if not path.exists():
        print(f"Error: File not found: {json_path}", file=sys.stderr)
        return 1

    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        print(f"Error: Invalid JSON in {json_path}: {exc}", file=sys.stderr)
        return 1
    except OSError as exc:
        print(f"Error: Could not read {json_path}: {exc}", file=sys.stderr)
        return 1

    if not isinstance(data, list):
        print("Error: JSON root must be an array of task objects", file=sys.stderr)
        return 1

    required_keys = {"task_id", "task_name", "task_description"}
    for idx, task in enumerate(data):
        if not isinstance(task, dict):
            print(f"Error: Task at index {idx} is not an object", file=sys.stderr)
            return 1
        missing = required_keys - task.keys()
        if missing:
            print(f"Error: Task at index {idx} missing keys: {', '.join(sorted(missing))}", file=sys.stderr)
            return 1

    for task in data:
        print(f"{task['task_id']} | {task['task_name']}")
        print(f"    {task['task_description']}")
        print()

    return 0


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python task_printer.py <tasks.json>", file=sys.stderr)
        sys.exit(1)

    sys.exit(print_tasks(sys.argv[1]))
