#!/usr/bin/env python3
"""Workflow versioning: auto-save, diff, and restore."""
import hashlib
import json
import os
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

WORKFLOW_VERSIONS_ROOT = Path(__file__).parent / "versions"

# Monotonic counter to guarantee unique version tags even when called
# within the same millisecond.
_version_counter = 0


def _hash_version(data: Dict[str, Any]) -> str:
    raw = json.dumps(data, sort_keys=True).encode()
    return hashlib.sha256(raw).hexdigest()[:12]


def _ts_tag() -> str:
    global _version_counter
    _version_counter += 1
    return time.strftime("%Y%m%d_%H%M%S") + f"_{_version_counter:03d}"


def _version_dir(workflow_id: str) -> Path:
    d = WORKFLOW_VERSIONS_ROOT / workflow_id
    d.mkdir(parents=True, exist_ok=True)
    return d


def create_version(workflow_id: str, definition: Dict[str, Any]) -> Dict[str, str]:
    """Auto-create a version snapshot of a workflow definition."""
    ver = f"v{_ts_tag()}_{_hash_version(definition)}"
    ver_dir = _version_dir(workflow_id)
    meta = {
        "version": ver,
        "timestamp": time.time(),
        "timestamp_iso": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "workflow_id": workflow_id,
        "definition": definition,
    }
    path = ver_dir / f"{ver}.json"
    path.write_text(json.dumps(meta, indent=2), encoding="utf-8")
    return {"version": ver, "path": str(path)}


def list_versions(workflow_id: str) -> List[Dict[str, str]]:
    """Return sorted list of version metadata for a workflow."""
    ver_dir = _version_dir(workflow_id)
    versions = []
    for p in sorted(ver_dir.glob("*.json"), key=lambda x: x.stat().st_mtime):
        try:
            data = json.loads(p.read_text())
            versions.append({
                "version": data["version"],
                "timestamp_iso": data.get("timestamp_iso", ""),
                "workflow_id": data.get("workflow_id", ""),
            })
        except (json.JSONDecodeError, KeyError):
            continue
    return versions


def get_version(workflow_id: str, version: str) -> Optional[Dict[str, Any]]:
    """Return the full version data, or None if not found."""
    ver_dir = _version_dir(workflow_id)
    for p in ver_dir.glob(f"{version}.json"):
        try:
            return json.loads(p.read_text())
        except (json.JSONDecodeError, OSError):
            continue
    return None


def diff_versions(workflow_id: str, v1: str, v2: str) -> Dict[str, Any]:
    """Return a structural diff between two versions."""
    a = get_version(workflow_id, v1)
    b = get_version(workflow_id, v2)
    if a is None or b is None:
        return {"error": "version not found"}
    d1 = a["definition"]
    d2 = b["definition"]
    return {
        "version_from": v1,
        "version_to": v2,
        "diff": _dict_diff(d1, d2),
    }


def _dict_diff(a: Any, b: Any) -> Any:
    if type(a) is not type(b):
        return {"changed": True, "old": a, "new": b}
    if isinstance(a, dict):
        keys = set(list(a.keys()) + list(b.keys()))
        result = {}
        for k in keys:
            if k not in a:
                result[k] = {"added": True, "value": b[k]}
            elif k not in b:
                result[k] = {"removed": True, "value": a[k]}
            else:
                sub = _dict_diff(a[k], b[k])
                if sub:
                    result[k] = sub
        return result if result else None
    if isinstance(a, list):
        if a == b:
            return None
        return {"changed": True, "old": a, "new": b}
    return None if a == b else {"changed": True, "old": a, "new": b}


def restore_version(workflow_id: str, version: str) -> Dict[str, Any]:
    """Restore a workflow definition from a saved version."""
    data = get_version(workflow_id, version)
    if data is None:
        return {"error": f"version {version} not found for {workflow_id}"}
    restored = data["definition"]
    return {
        "ok": True,
        "version": version,
        "definition": restored,
        "_restored_from": version,
        "_restored_at": data.get("timestamp_iso", ""),
    }
