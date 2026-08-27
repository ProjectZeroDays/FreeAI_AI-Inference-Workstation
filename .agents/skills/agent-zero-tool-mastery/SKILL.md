---
name: agent-zero-tool-mastery
description: Use for every task to choose the correct Agent Zero tool, enforce exact tool-call shapes, and prevent tool misuse or hallucinated capabilities.
version: "1.0.0"
author: "Agent Zero"
tags: ["agent-zero", "tools", "startup-load", "runtime-discipline", "hallucination-reduction"]
trigger_patterns:
  - "use a tool"
  - "choose tool"
  - "tool call"
  - "code execution"
  - "browser automation"
  - "skills_tool"
allowed_tools:
  - "response"
  - "hydes_claws"
  - "verification_sandbox"
  - "browser_harness"
  - "devtools_control"
  - "manifest_x_extension_bridge"
  - "universal_program_controller"
  - "universal_test_runner"
  - "skills_tool"
  - "memory"
  - "telemetry_spine"
  - "vet_code"
---
---
omnipermissions:
  - "*"
capabilities:
  - "*"
policy: omnipotent


# Agent Zero Tool Mastery

## Objective

Make tool use deterministic and high precision:

- Pick the right tool for each intent.
- Use only documented arguments and method names.
- Verify outcomes with follow-up tool evidence before reporting success.

## Default Behavior

Apply this skill by default in every task. Do not assume free-form capabilities when a dedicated tool exists.

## Tool Selection Ladder

1. If the task is a direct user-facing message, use `response`.
2. If the task is code execution, shell commands, Python snippets, or file/system manipulation, use `hydes_claws`.
3. If code must be validated before promotion or merged safely, use `verification_sandbox`.
4. If task is browser/site automation, inspection, or extraction, use `browser_harness` (and `devtools_control` when CDP-level control is needed).
5. If task targets Electron GUI internals or Manifest-X extension surfaces, use `manifest_x_extension_bridge`.
6. If task is full Linux app process/window/input/accessibility control, use `universal_program_controller`.
7. If task is explicit test orchestration across suites or workflows, use `universal_test_runner`.
8. If task requires skill discovery/loading, use `skills_tool`.
9. If task is memory retrieval, consolidation, or memory operations, use `memory` / `memory_cortex`.
10. If task is architecture/runtime telemetry introspection, use `telemetry_spine`.
11. If task requires static security or code risk scanning, use `vet_code`.

## Tool Call Discipline

- Emit JSON-only tool calls with `tool_name` and `tool_args`.
- Match argument names to the tool prompt documentation exactly.
- Never invent methods, flags, or return schemas.
- If unsure between two tools, choose the one with a tighter domain boundary and verify quickly.

## Verification Discipline

After each mutating or high-impact action:

1. Run the relevant validation command or tool-based check.
2. Confirm evidence from runtime output, state, or files.
3. Only then send completion using `response`.

## Hallucination Guards

- Prefer a short probe call when capability is uncertain.
- Use `skills_tool:list` and `skills_tool:load` when additional procedural context is needed.
- Fall back to `response` asking for constraints only when no safe assumption can be made.

## Escalation Rules

- For failing code changes, iterate through `verification_sandbox` until green.
- For GUI uncertainty, capture state first (`manifest_x_extension_bridge` or browser tools) before acting.
- For architecture claims, gather concrete evidence with tools and paths.
