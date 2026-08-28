---
name: task_printer
description: >
  Reads a JSON file containing an array of task objects and prints each task's
  id, name, and description to the console in a formatted layout.
triggers:
  - print tasks from json
  - display task list
  - task printer
  - show tasks
category: productivity
enabled: true
metadata:
  created_at: "2026-08-28"
  type: cli-tool
---

# Task Printer

Reads a JSON file of task objects and prints them to the console in a clean,
readable format.

## Purpose

Quickly visualize a task list defined in JSON without opening the file. Useful
for validating task definitions, printing work queues, or integrating into
automation pipelines.

## Input Format

The JSON file must contain an array of objects, each with exactly three keys:

| Key                | Type   | Description                          |
|--------------------|--------|--------------------------------------|
| `task_id`          | string | Unique identifier for the task       |
| `task_name`        | string | Short title of the task              |
| `task_description` | string | Detailed description of the task     |

Example `tasks.json`:

```json
[
  {
    "task_id": "T1",
    "task_name": "Install dependencies",
    "task_description": "Run pip install -r requirements.txt"
  },
  {
    "task_id": "T2",
    "task_name": "Run tests",
    "task_description": "Execute pytest"
  },
  {
    "task_id": "T3",
    "task_name": "Deploy",
    "task_description": "Push to production"
  }
]
```

## Usage

```bash
python skills/task_printer/scripts/task_printer.py <path/to/tasks.json>
```

## Output Format

```
T1 | Install dependencies
    Run pip install -r requirements.txt

T2 | Run tests
    Execute pytest

T3 | Deploy
    Push to production
```

## Exit Codes

| Code | Meaning                     |
|------|-----------------------------|
| 0    | Success                     |
| 1    | Error (missing file, bad JSON, missing keys) |

## Validation

The script validates input before printing:
- File must exist
- Root must be a JSON array
- Each element must be an object with all three required keys

Invalid input produces an error message on stderr and exits with code 1.

## Integration

Can be used in automation workflows:

```bash
# Print tasks from a generated task list
cat workflow/tasks.json | python skills/task_printer/scripts/task_printer.py workflow/tasks.json

# Chain with other tools
python task_printer.py tasks.json | grep "Deploy"
```
