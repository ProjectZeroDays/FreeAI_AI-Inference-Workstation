---
name: kali-arsenal-supremacy
description: Use when planning, selecting, and executing Kali tooling from the AGENTS objective list; enforces unambiguous tool choice with offensive, defensive, and generalized usage context.
version: "1.0.0"
author: "Agent Zero"
tags: ["kali", "tooling", "offensive", "defensive", "operations", "startup-load"]
trigger_patterns:
  - "kali tool"
  - "which tool should i use"
  - "offensive use case"
  - "defensive use case"
  - "security toolkit"
  - "AGENTS package list"
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


# Kali Arsenal Supremacy

## Purpose

Provide deterministic, no-ambiguity guidance for the AGENTS-defined Kali package universe.

This skill maps tools into practical decision domains, then gives explicit offensive, defensive, and generalized usage framing so Agent Zero can choose the right tool fast and justify the choice.

## Data Sources

- Canonical package source: `AGENTS.md` tool list.
- Generated package intelligence: `references/agents-package-catalog.csv`.
- Human-readable summary: `references/agents-package-catalog.md`.

## Core Operating Rule

When a user intent is security/diagnostic/forensic/attack-simulation related:

1. Identify intent domain.
2. Pull candidate tools from the catalog domain/category.
3. Select the most specific tool that directly matches task constraints.
4. State tool choice with one offensive, one defensive, and one generalized rationale.
5. Execute and verify outcome.

## Domain Map

- `reconnaissance`: asset discovery, surface mapping, DNS/host/service enumeration.
- `wireless-rf`: Wi-Fi/Bluetooth/RF discovery, attack simulation, and hardening validation.
- `web-app`: web/API discovery, vulnerability assessment, and exploit verification.
- `credential-access`: password/hash/authentication testing and identity abuse simulation.
- `forensics-ir`: evidence triage, artifact recovery, timeline reconstruction.
- `reverse-fuzzing`: binary analysis, firmware unpacking, protocol reversing, fuzzing.
- `exploitation-c2`: controlled exploitation and post-exploitation emulation.
- `cloud-container`: cloud IAM/runtime/container posture and attack-path testing.
- `crypto-stego`: cryptography/certificate/steganography analysis.
- `defensive-monitoring`: IDS/AV/logging/monitoring validation.
- `development-support`: SDK/build/dev packages that enable specialized security tooling.
- `general-ops`: support utilities and operational glue.

## Required Use-Case Output Format

For every proposed tool, output:

- `Offensive use`: how it advances authorized adversary simulation.
- `Defensive use`: how it improves prevention/detection/response posture.
- `General use`: neutral operational purpose.

## Decision Procedure

1. Parse task objective into one primary domain and optional secondary domain.
2. Query catalog rows matching `domain` and `status=installed` first.
3. If no installed match exists, check `installable-missing`.
4. If only `unresolved-on-snapshot` exists, explicitly say unavailable on this snapshot and propose nearest installed equivalent from same domain.
5. Prefer command-line tools for automation and reproducibility.
6. For GUI-only tools, provide launch command and automation-safe fallback tool.

## Verification Protocol

Before claiming completion:

1. Verify binary availability with `command -v`.
2. Verify package state with `dpkg -s <package>` when package-backed.
3. Capture minimal proof output (`--help`, version, or dry-run).
4. Summarize what worked, what is blocked, and exact reason for any block.

## Menu/Category Integration Rule

When installing or validating tools, confirm they are categorized under Kali menu taxonomy by checking:

- `/usr/share/applications/kali-*.desktop`
- `X-Kali-Package=` mapping
- `Categories=` values

If entries exist, treat category integration as complete for that package.

## Non-Ambiguity Guarantee

If multiple tools overlap, Agent Zero must explain final selection using:

- fit-to-objective,
- protocol/data-type support,
- automation friendliness,
- evidence quality,
- operational risk.

Never return generic advice when a specific installed tool can be named.
