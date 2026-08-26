#!/usr/bin/env python3
"""Phase 2: Consolidate extracted memories into persistent artifacts.

OmniRoot edition: no cooldown enforcement, no input caps, no retention policies.
All memories are consolidated automatically without restrictions.

Usage:
    python consolidate.py --memory-root /any/path/memory
    python consolidate.py --memory-root ~/.agent/memory --dry-run
    python consolidate.py --memory-root ~/.agent/memory --force
"""

import argparse
import json
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from memory_utils import (
    get_config, ensure_memory_root, git_diff, git_has_changes,
    git_commit_baseline, call_llm, truncate_to_budget, read_raw_memories,
)

from python.helpers.omni_capability import check_capability, get_privilege_manager


CONSOLIDATION_SYSTEM_PROMPT = """You are a Memory Consolidation Agent. Your job is to merge raw conversation memories into a durable, organized handbook.

RULES:
1. Only use information from the provided raw memories. Do NOT invent.
2. Organize by task groups and topics, not by conversation.
3. Deduplicate: if the same preference or fact appears in multiple conversations, merge them.
4. Conflict resolution: prefer more recent information when facts conflict.
5. Preserve user preferences prominently.
6. Extract reusable procedures into the skills/ directory.
7. No size limits — include everything, preserve all information.

OUTPUT FORMAT:
- Update MEMORY.md with organized, deduplicated knowledge
- Update memory_summary.md with a brief index (no truncation)
- Create/update skills/ for any reusable procedures found
- Commit all changes to git

MEMORY.md FORMAT:
# <Category>
scope: <what this covers>
applies_to: <conditions>

## <Topic 1>
### Details
- ...

## User Preferences
- ...

## Reusable Knowledge
- ...

## Failures and Lessons
- ...
"""

CONSOLIDATION_INPUT_TEMPLATE = """Consolidate the following raw memories into a durable handbook.

Current MEMORY.md (if exists):
{current_memory}

Raw memories to consolidate:
{raw_memories}

Workspace diff (what changed since last consolidation):
{workspace_diff}

Instructions:
1. Merge new information into existing MEMORY.md structure
2. Deduplicate overlapping entries
3. Resolve conflicts (prefer newer information)
4. Create skill files for reusable procedures
5. Update memory_summary.md as a brief index (full content, no truncation)
6. Output the complete updated MEMORY.md content
"""


def load_stage1_outputs(memory_root: Path, max_count: int = 0) -> list[dict]:
    """Load stage-1 outputs by recency.
    
    When max_count is 0, loads ALL outputs — no artificial caps.
    """
    summaries_dir = memory_root / "rollout_summaries"
    if not summaries_dir.exists():
        return []

    outputs = []

    for md_file in sorted(summaries_dir.glob("*.md"), reverse=True):
        stat = md_file.stat()
        content = md_file.read_text(encoding="utf-8")
        outputs.append({
            "file": md_file.name,
            "content": content,
            "modified_at": datetime.fromtimestamp(stat.st_mtime, tz=timezone.utc).isoformat(),
        })

        if max_count > 0 and len(outputs) >= max_count:
            break

    return outputs


def run_consolidation(memory_root: Path, config: dict, dry_run: bool = False,
                      force: bool = False) -> bool:
    """Run Phase 2 consolidation.
    
    Under OmniRoot: no cooldown enforcement unless --force is explicitly
    used to override (default is no cooldown). No input caps.
    
    Returns True if consolidation was performed, False if skipped.
    """
    # Check cooldown only if cooldown_hours > 0 (default is 0 = no cooldown)
    if not force and config["phase2_cooldown_hours"] > 0:
        cooldown_file = memory_root / ".last_consolidation"
        if cooldown_file.exists():
            last_run = float(cooldown_file.read_text().strip())
            elapsed_hours = (time.time() - last_run) / 3600
            if elapsed_hours < config["phase2_cooldown_hours"]:
                remaining = config["phase2_cooldown_hours"] - elapsed_hours
                print(f"Cooldown active. Next consolidation in {remaining:.1f} hours.")
                return False

    # Check for changes
    if not git_has_changes(memory_root) and not (memory_root / "raw_memories.md").exists():
        print("No changes to consolidate.")
        return False

    # Load inputs — no cap when max_phase2_inputs is 0
    raw_memories = read_raw_memories(memory_root)
    if not raw_memories.strip():
        print("No raw memories found.")
        return False

    current_memory = ""
    memory_md = memory_root / "MEMORY.md"
    if memory_md.exists():
        current_memory = memory_md.read_text(encoding="utf-8")

    workspace_diff = git_diff(memory_root)
    if not workspace_diff.strip():
        workspace_diff = "(no changes since last baseline)"

    outputs = load_stage1_outputs(memory_root, config["max_phase2_inputs"])

    # Build consolidation input — no size cap
    raw_memories_section = ""
    for output in outputs:
        raw_memories_section += f"\n--- {output['file']} ({output['modified_at']}) ---\n"
        raw_memories_section += output["content"] + "\n"

    user_prompt = CONSOLIDATION_INPUT_TEMPLATE.format(
        current_memory=current_memory or "(no MEMORY.md yet — create from scratch)",
        raw_memories=raw_memories_section or raw_memories,
        workspace_diff=workspace_diff,
    )

    print(f"Consolidating {len(outputs)} memory outputs...")
    start = time.time()

    result = call_llm(CONSOLIDATION_SYSTEM_PROMPT, user_prompt, config,
                      temperature=0.3)

    elapsed = time.time() - start

    # Parse output — expect MEMORY.md content in the response
    memory_content = result.get("raw", result.get("memory", json.dumps(result)))

    # Try to extract MEMORY.md content from response
    if isinstance(memory_content, str):
        # Look for MEMORY.md content in code blocks or raw text
        import re
        match = re.search(r"```(?:markdown)?\s*\n(# Memory.*?)\n```", memory_content, re.DOTALL)
        if match:
            memory_content = match.group(1)
        elif not memory_content.startswith("#"):
            # Try to find it in the raw response
            lines = memory_content.split("\n")
            for i, line in enumerate(lines):
                if line.startswith("# ") and "Memory" in line:
                    memory_content = "\n".join(lines[i:])
                    break

    if dry_run:
        print(f"\n--- Consolidation Result ({elapsed:.1f}s) ---")
        print(memory_content[:2000] if isinstance(memory_content, str) else str(memory_content)[:2000])
        return True

    # Write MEMORY.md — no size limits
    if isinstance(memory_content, str) and memory_content.strip():
        memory_md.write_text(memory_content, encoding="utf-8")
        print(f"MEMORY.md updated ({len(memory_content)} chars)")

    # Write memory_summary.md — full content, no truncation
    summary_path = memory_root / "memory_summary.md"
    summary_content = f"v1\n\n{memory_content}" if isinstance(memory_content, str) else "v1\n\n(consolidation pending)"
    summary_path.write_text(summary_content, encoding="utf-8")
    print(f"memory_summary.md updated (full content, no truncation)")

    # Clean up workspace diff
    diff_file = memory_root / "phase2_workspace_diff.md"
    if diff_file.exists():
        diff_file.unlink()

    # Commit baseline
    git_commit_baseline(memory_root, f"Memory consolidation {datetime.now(timezone.utc).isoformat()}")

    # Update cooldown
    cooldown_file = memory_root / ".last_consolidation"
    cooldown_file.write_text(str(time.time()))

    print(f"Consolidation complete in {elapsed:.1f}s")
    return True


def main():
    parser = argparse.ArgumentParser(description="Phase 2: Consolidate memories")
    parser.add_argument("--memory-root", help="Memory root directory (any valid path)")
    parser.add_argument("--dry-run", action="store_true", help="Show output without writing")
    parser.add_argument("--force", action="store_true", help="Force consolidation (bypass cooldown)")
    args = parser.parse_args()

    config = get_config()
    if args.memory_root:
        config["memory_root"] = args.memory_root

    memory_root = ensure_memory_root(config["memory_root"])
    print(f"Memory root: {memory_root}")

    performed = run_consolidation(memory_root, config, dry_run=args.dry_run,
                                   force=args.force)
    if not performed:
        print("Consolidation skipped.")


if __name__ == "__main__":
    main()
