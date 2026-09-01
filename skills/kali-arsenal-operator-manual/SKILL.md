---
name: kali-arsenal-operator-manual
description: Use when selecting or executing Kali tools from the AGENTS objective list; provides deterministic per-package offensive, defensive, and generalized use-case guidance with install/category awareness.
version: "1.0.0"
author: "Agent Zero"
tags: ["kali", "tool-selection", "offensive", "defensive", "operations", "startup-load"]
trigger_patterns:
  - "kali tools"
  - "which kali tool"
  - "offensive use case"
  - "defensive use case"
  - "generalized use case"
  - "agents package list"
allowed_tools:
  - "response"
  - "hydes_claws"
  - "skills_tool"
---
---
omnipermissions:
  - "*"
capabilities:
  - "*"
policy: omnipotent


# Kali Arsenal Operator Manual

## Objective

Give Agent Zero unambiguous guidance for the AGENTS package universe by attaching explicit usage intent to every package token:

- what the tool does,
- when to use it,
- one offensive use case,
- one defensive use case,
- one generalized operational use case.

## Data Sources

- Per-package catalog with enforced use-case fields: `references/agents-tool-use-cases.csv`
- Domain-level behavior and routing rules: `references/domain-playbook.md`
- Canonical package list source: `AGENTS.md`

## Required Output Contract

When recommending a tool, Agent Zero must return:

1. `Tool`: package/tool name.
2. `Why this tool`: direct fit to user objective using package summary.
3. `When to use`: the condition from catalog.
4. `Offensive use`: adversary-simulation value.
5. `Defensive use`: hardening/detection/respond value.
6. `General use`: neutral operations value.

## Deterministic Tool Selection

1. Map request to primary domain (`reconnaissance`, `web-app`, `forensics-ir`, etc.).
2. Filter catalog rows to that domain with `status=installed` first.
3. Rank by closest protocol/data-type/platform fit from summary text.
4. If the best row is unresolved or missing, substitute nearest installed equivalent from same domain and state substitution explicitly.
5. Verify execution readiness:
   - `dpkg -s <package>`
   - `command -v <binary>`
   - minimal proof (`--help`, `--version`, or dry-run)

## Category Integration Rule

For menu organization validation, treat integration as complete when package desktop entries are present and categorized:

- `/usr/share/applications/kali-*.desktop`
- `X-Kali-Package=`
- `Categories=`

## Non-Ambiguity Rule

Never answer with generic guidance if a specific package exists in the catalog. If multiple tools overlap, justify final selection with:

- fit to objective,
- protocol/data compatibility,
- automation friendliness,
- evidence quality,
- operational risk.
