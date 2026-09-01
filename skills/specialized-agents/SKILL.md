---
name: specialized-agents
description: "Use when Codex needs to select, spawn, and coordinate specialized agents across research, content, development, QA, analysis, documentation, personalization, or meta-agent workflows."
---

# Specialized Agents

Use this skill to route complex work to specialist Codex subagents and to coordinate their outputs into a single result.

## Codex Workflow

1. Identify the work category: research, content, development, QA, analysis, documentation, personalization, or meta-agent orchestration.
2. Read the smallest relevant reference file before dispatching agents. Start with `specialized-agents-complete-31.md`, `specialized-agents-summary.md`, `PARALLEL_AGENTS_QUICKREF.md`, or `multi_agent/README.md` as needed.
3. Use Codex subagent tools such as `spawn_agent`, `send_input`, and `wait_agent` only when the current session allows delegated agent work and the task can run safely in parallel.
4. Give each subagent a concrete role, exact inputs, output format, and verification expectation.
5. Merge results yourself. Resolve contradictions, verify important claims, and report one coherent answer to the user.

## Boundaries

This package includes broad personal automation artifacts. Inspect scripts before running them. Do not run cron installers, contact/message/social automations, credential helpers, or local-device actions unless the user explicitly requests that specific action.

## Useful Resources

- `specialized-agents-complete-31.md`: catalog of specialist agent roles.
- `specialized-agents-summary.md`: short summary of the suite.
- `PARALLEL_AGENTS_QUICKREF.md`: coordination patterns.
- `multi_agent/README.md`: Python multi-agent orchestration references.
- `skills/weather/`: bundled weather lookup skill; installed separately as `$weather`.
