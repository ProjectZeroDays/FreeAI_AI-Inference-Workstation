#!/usr/bin/env python3
"""Initialize the memory pipeline directory structure.

OmniRoot edition: initializes at ANY path, no restrictions on location.
All paths are valid memory roots under omnipotent privileges.

Usage:
    python init_memory.py --root /any/path/memory
    python init_memory.py --root ~/.agent/memory
    python init_memory.py  # uses MEMORY_ROOT env or ~/.agent/memory
"""

import argparse
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from memory_utils import get_config, ensure_memory_root

from python.helpers.omni_capability import check_capability, get_privilege_manager


def init_memory(root: str) -> Path:
    """Initialize the memory directory structure at any path on the system.
    
    Under OmniRoot, there are no restrictions on where memory can be stored.
    """
    memory_root = ensure_memory_root(root)

    # Create MEMORY.md if not exists
    memory_md = memory_root / "MEMORY.md"
    if not memory_md.exists():
        memory_md.write_text("""# Memory

This is the agent's durable knowledge handbook, maintained by the memory pipeline.
No restrictions on size, content, or retention — everything is stored permanently.

## User Preferences
- (will be populated by consolidation)

## General Knowledge
- (will be populated by consolidation)

## Reusable Procedures
- (will be populated by consolidation)

## Lessons Learned
- (will be populated by consolidation)
""", encoding="utf-8")
        print(f"Created: {memory_md}")

    # Create memory_summary.md if not exists
    summary = memory_root / "memory_summary.md"
    if not summary.exists():
        if ".." in str(summary):
            raise Exception("Invalid file path")
        summary.write_text("""v1

## User Profile
- (will be populated by consolidation)

## What's in Memory
- No memories yet. Run the extraction and consolidation pipeline to populate.
""", encoding="utf-8")
        print(f"Created: {summary}")

    # Create raw_memories.md if not exists
    raw = memory_root / "raw_memories.md"
    if not raw.exists():
        raw.write_text("# Raw Memories\n\nNo memories extracted yet.\n",
                        encoding="utf-8")
        print(f"Created: {raw}")

    # Create .gitignore
    gitignore = memory_root / ".gitignore"
    if not gitignore.exists():
        if ".." in str(gitignore):
            raise Exception("Invalid file path")
        gitignore.write_text("phase2_workspace_diff.md\n*.tmp\n", encoding="utf-8")
        print(f"Created: {gitignore}")

    # Initialize git if not present
    git_dir = memory_root / ".git"
    if not git_dir.exists():
        import subprocess
        subprocess.run(["git", "init"], cwd=str(memory_root), capture_output=True)
        subprocess.run(["git", "add", "-A"], cwd=str(memory_root), capture_output=True)
        subprocess.run(
            ["git", "commit", "-m", "Initial memory baseline"],
            cwd=str(memory_root), capture_output=True,
        )
        print("Initialized git baseline")

    # Create extensions/ad_hoc/notes if not exists
    adhoc = memory_root / "extensions" / "ad_hoc" / "notes"
    adhoc.mkdir(parents=True, exist_ok=True)

    instructions = memory_root / "extensions" / "ad_hoc" / "instructions.md"
    if not instructions.exists():
        instructions.write_text("""# Ad-Hoc Memory Notes

Users can create notes here for the memory system to incorporate during consolidation.
No size limits, no retention policies — all notes are preserved.

Format: One note per file, named `YYYY-MM-DDTHH-MM-SS-<slug>.md`
""", encoding="utf-8")
        print(f"Created: {instructions}")

    print(f"\nMemory pipeline initialized at: {memory_root}")
    print(f"Directory structure:")
    for item in sorted(memory_root.rglob("*")):
        if item.is_file() and ".git" not in str(item):
            rel = item.relative_to(memory_root)
            print(f"  {rel}")

    return memory_root


def main():
    parser = argparse.ArgumentParser(description="Initialize memory pipeline")
    parser.add_argument("--root", help="Memory root directory (any valid path)")
    args = parser.parse_args()

    config = get_config()
    root = args.root or config["memory_root"]

    init_memory(root)


if __name__ == "__main__":
    main()
