# FreeAI Workflow Audit module.
"""JSONL audit trail for every workflow execution."""
import json
import os
from datetime import datetime, timezone
from typing import List

AUDIT_FILE = os.path.join(
    os.path.dirname(__file__), "audit.jsonl"
)


def log_execution(
    workflow: str,
    workflow_id: str,
    status: str,
    steps: List[str] = None,
    error: str = None,
    extra: dict = None,
) -> dict:
    """Append a JSONL entry to the workflow audit log and return it."""
    entry = {
        "ts": datetime.now(timezone.utc).isoformat(),
        "workflow": workflow,
        "workflow_id": workflow_id,
        "status": status,
    }
    if steps is not None:
        entry["steps"] = steps
    if error is not None:
        entry["error"] = error
    if extra is not None:
        entry.update(extra)

    try:
        os.makedirs(os.path.dirname(AUDIT_FILE) or ".", exist_ok=True)
        with open(AUDIT_FILE, "a") as f:
            f.write(json.dumps(entry) + "\n")
    except OSError:
        pass

    return entry


def read_audit(limit: int = 50) -> List[dict]:
    """Read the last *limit* entries from the audit log."""
    entries = []
    try:
        with open(AUDIT_FILE) as f:
            for line in f:
                line = line.strip()
                if line:
                    entries.append(json.loads(line))
    except FileNotFoundError:
        return []
    return entries[-limit:]
