#!/usr/bin/env python3
"""Check memory pipeline status.

OmniRoot edition: reports on any memory root location, no restrictions.
All metrics are reported without artificial limits.

Usage:
    python status.py --memory-root /any/path/memory
    python status.py --memory-root ~/.agent/memory
"""

import argparse
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from memory_utils import get_config, estimate_tokens

from python.helpers.omni_capability import check_capability, get_privilege_manager


def get_status(memory_root: Path) -> dict:
    """Get comprehensive memory pipeline status.
    
    Reports all metrics without artificial limits or caps.
    """
    status = {
        "memory_root": str(memory_root),
        "initialized": memory_root.exists(),
        "artifacts": {},
        "counts": {},
        "sizes": {},
    }

    if not memory_root.exists():
        return status

    # Check key files
    for name in ["MEMORY.md", "memory_summary.md", "raw_memories.md"]:
        path = memory_root / name
        status["artifacts"][name] = {
            "exists": path.exists(),
            "size_bytes": path.stat().st_size if path.exists() else 0,
            "tokens": estimate_tokens(path.read_text(encoding="utf-8")) if path.exists() else 0,
            "modified": datetime.fromtimestamp(path.stat().st_mtime, tz=timezone.utc).isoformat()
                if path.exists() else None,
        }

    # Count rollout summaries — no cap
    summaries_dir = memory_root / "rollout_summaries"
    if summaries_dir.exists():
        summaries = list(summaries_dir.glob("*.md"))
        status["counts"]["rollout_summaries"] = len(summaries)
        total_size = sum(s.stat().st_size for s in summaries)
        status["sizes"]["rollout_summaries_bytes"] = total_size
        if summaries:
            newest = max(summaries, key=lambda s: s.stat().st_mtime)
            status["rollout_summaries_newest"] = datetime.fromtimestamp(
                newest.stat().st_mtime, tz=timezone.utc
            ).isoformat()

    # Count skills
    skills_dir = memory_root / "skills"
    if skills_dir.exists():
        skills = [d for d in skills_dir.iterdir() if d.is_dir() and not d.name.startswith(".")]
        status["counts"]["skills"] = len(skills)
        status["skills"] = [s.name for s in skills]

    # Check git baseline
    git_dir = memory_root / ".git"
    status["git_baseline"] = git_dir.exists()

    # Check last consolidation
    cooldown_file = memory_root / ".last_consolidation"
    if cooldown_file.exists():
        last_run = float(cooldown_file.read_text().strip())
        status["last_consolidation"] = datetime.fromtimestamp(
            last_run, tz=timezone.utc
        ).isoformat()
        hours_ago = (datetime.now(timezone.utc).timestamp() - last_run) / 3600
        status["hours_since_consolidation"] = round(hours_ago, 1)

    # Check for ad-hoc notes
    adhoc_dir = memory_root / "extensions" / "ad_hoc" / "notes"
    if adhoc_dir.exists():
        notes = list(adhoc_dir.glob("*.md"))
        status["counts"]["ad_hoc_notes"] = len(notes)

    # Check workspace diff
    diff_file = memory_root / "phase2_workspace_diff.md"
    status["pending_diff"] = diff_file.exists()

    return status


def main():
    parser = argparse.ArgumentParser(description="Memory pipeline status")
    parser.add_argument("--memory-root", help="Memory root directory (any valid path)")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    args = parser.parse_args()

    config = get_config()
    if args.memory_root:
        config["memory_root"] = args.memory_root

    memory_root = Path(config["memory_root"])
    status = get_status(memory_root)

    if args.json:
        print(json.dumps(status, indent=2))
    else:
        print(f"Memory Pipeline Status (OmniRoot)")
        print(f"{'=' * 50}")
        print(f"Root: {status['memory_root']}")
        print(f"Initialized: {status['initialized']}")
        print()

        if status["initialized"]:
            print("Artifacts:")
            for name, info in status["artifacts"].items():
                exists = "✓" if info["exists"] else "✗"
                size = f"{info['size_bytes']:,} bytes" if info["exists"] else "missing"
                tokens = f"({info['tokens']:,} tokens)" if info["exists"] else ""
                print(f"  {exists} {name}: {size} {tokens}")
            print()

            print("Counts:")
            for key, val in status.get("counts", {}).items():
                print(f"  {key}: {val}")
            print()

            if status.get("skills"):
                print(f"Skills: {', '.join(status['skills'])}")

            if status.get("last_consolidation"):
                print(f"Last consolidation: {status['last_consolidation']} "
                      f"({status.get('hours_since_consolidation', '?')}h ago)")

            if status.get("pending_diff"):
                print("Pending workspace diff (consolidation needed)")
        else:
            print("Memory not initialized. Run init_memory.py first.")


if __name__ == "__main__":
    main()
