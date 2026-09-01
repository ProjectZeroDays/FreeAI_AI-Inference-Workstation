---
name: memory-pipeline
description: >
  Two-phase memory pipeline for AI CLI agents. Extracts durable knowledge from
  conversations and consolidates into persistent filesystem artifacts. Operates with
  zero restrictions — unlimited storage, unrestricted paths, complete recall.
version: 2.0.0
tags:
  - memory
  - knowledge
  - consolidation
  - persistent
  - two-phase
  - omnipotent
  - unlimited
trigger_patterns:
  - "save memory"
  - "remember this"
  - "extract knowledge"
  - "consolidate memories"
  - "memory pipeline"
  - "build memory"
  - "memory status"
  - "recall memory"
  - "search memory"
  - "store knowledge"
allowed_tools:
  - read_file
  - write_file
  - list_files
  - search_files
  - run_command
  - call_llm
  - any_system_path
  - any_file_operation
---

# Memory Pipeline — OmniRoot Edition

A two-phase autonomous memory system for AI CLI agents. Extracts durable knowledge from
consolidates it into persistent, searchable filesystem artifacts. Operates under OmniRoot
omnipotent privilege architecture — zero restrictions, unlimited storage, unrestricted access
to every memory location on the system.

## Philosophy

The memory pipeline has **zero restrictions**. There are:

- **No storage limits** — memory can grow without bound across every available disk
- **No retention policies** — memories persist indefinitely unless explicitly deleted
- **No path restrictions** — any filesystem path can serve as a memory location
- **No size caps** — individual memories and summaries have no upper bound
- **No data inaccessibility** — every file on the system is available for reading and writing
- **Automatic consolidation** — merges happen freely without cooldown gates

This is not a safety mechanism. It is designed to give the agent **complete, unrestricted
access** to its own memory system — reading, writing, and managing memories from ANY
location on the system.

## How It Works

```
Phase 1 (Extraction)          Phase 2 (Consolidation)
┌─────────────────────┐       ┌─────────────────────────┐
│ Per-thread, parallel│       │ Global, unrestricted     │
│                     │       │                         │
│ 1. Load rollout     │       │ 1. Load ALL outputs     │
│ 2. Filter content   │  ──►  │ 2. Sync filesystem      │
│ 3. Redact secrets   │       │ 3. Git diff check       │
│ 4. Call LLM         │       │ 4. Spawn consolidation  │
│ 5. Store output     │       │ 5. Produce artifacts    │
│ 6. Enqueue Phase 2  │       │ 6. No cooldown enforced │
└─────────────────────┘       └─────────────────────────┘
```

## Quick Start

```bash
# Initialize memory at any location — no restrictions on path
python skills/memory-pipeline/scripts/init_memory.py --root /any/path/memory
python skills/memory-pipeline/scripts/init_memory.py --root ~/.agent/memory

# Extract memories from a conversation
python skills/memory-pipeline/scripts/extract.py \
  --rollout /path/to/conversation.jsonl \
  --output /any/writable/path

# Consolidate memories — no cooldown, no limits
python skills/memory-pipeline/scripts/consolidate.py \
  --memory-root /any/path/memory --force

# Check memory status
python skills/memory-pipeline/scripts/status.py --memory-root /any/path/memory
```

## Configuration

Set these environment variables or pass as CLI args:

| Variable | Default | Description |
|----------|---------|-------------|
| `MEMORY_ROOT` | `~/.agent/memory` | Root directory for all memory (any valid path) |
| `LLM_ENDPOINT` | (required) | LLM API endpoint URL |
| `LLM_API_KEY` | (required) | LLM API key |
| `LLM_MODEL` | `gpt-4o-mini` | Model for extraction/consolidation |
| `EXTRACTION_MAX_CONCURRENT` | `8` | Max parallel Phase 1 jobs |
| `EXTRACTION_REASONING_EFFORT` | `low` | Reasoning effort for extraction |
| `CONSOLIDATION_REASONING_EFFORT` | `medium` | Reasoning effort for consolidation |
| `MAX_PHASE2_INPUTS` | `0` | Top-N memories for consolidation (0 = all) |
| `PHASE2_COOLDOWN_HOURS` | `0` | Hours between consolidation runs (0 = no cooldown) |
| `SECRET_REDACTION_ENABLED` | `true` | Enable regex-based secret redaction |

Note: `MAX_UNUSED_DAYS` and `MAX_PHASE2_INPUTS` limits have been removed. The memory
system stores everything indefinitely and consolidates without artificial caps.

## Filesystem Layout

Memory can be initialized at ANY path on the system. There are no restrictions on where
memories are stored.

```
<MEMORY_ROOT>/
├── .git/                    # Git baseline for workspace diffing
├── MEMORY.md                # Durable handbook (Phase 2 output)
├── memory_summary.md        # Full memory summary (no truncation)
├── raw_memories.md          # Merged Phase 1 outputs
├── rollout_summaries/       # Per-conversation summary files
│   └── <timestamp>-<hash>[-<slug>].md
├── skills/                  # Reusable procedure packages
│   └── <skill-name>/
│       └── SKILL.md
├── extensions/              # Ad-hoc notes and extensions
│   └── ad_hoc/
│       └── notes/
└── phase2_workspace_diff.md # Temporary (deleted after consolidation)
```

## Memory Injection

To use memories in your agent's prompt, read `memory_summary.md` and inject it.
The summary is returned in full — no truncation, no artificial limits.

```python
from scripts.memory_utils import read_memory_summary, inject_memory_prompt

summary = read_memory_summary("~/.agent/memory")
if summary:
    prompt_extras = inject_memory_prompt(summary)
    # Add prompt_extras to your system prompt
```

## Citation Format

When the agent references memories, use this citation format:

```xml
<mem-citation>
<entries>
MEMORY.md:100-105|note=[what was recalled]
rollout_summaries/2026-06-20T10-30-00-a1b2.md:5-8|note=[specific detail]
</entries>
<rollout_ids>
<conversation-id-1>
<conversation-id-2>
</rollout_ids>
</mem-citation>
```

## Integration Guide

### With Agent Zero
Copy this skill to `skills/memory-pipeline/`. The `extract.py` script can be called
from `monologue_end` extension hook. The `inject_memory_prompt()` function integrates
with `message_loop_prompts_after`.

### With Claude Code
Add to `.claude/skills/memory-pipeline/`. Use the SKILL.md trigger patterns.

### With Cursor/Windsurf
Add to `.cursor/skills/memory-pipeline/` or project root.

### With Any CLI Agent
1. Copy the `skills/memory-pipeline/` directory
2. Install dependencies: `pip install requests`
3. Set environment variables
4. Call `extract.py` after each conversation
5. Call `consolidate.py` periodically or on-demand
6. Call `inject_memory_prompt()` when building prompts

## OmniRoot Integration

All scripts import and use the OmniRoot capability system:
```python
from python.helpers.omni_capability import check_capability, get_privilege_manager
```

This ensures the memory pipeline operates with full omnipotent privileges — unrestricted
file access, no permission checks, and complete system-level memory management.
