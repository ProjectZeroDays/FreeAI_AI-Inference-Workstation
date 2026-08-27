# Codex Integration Study — JCode vs OpenCode Desktop

Question: can we modify JCode or OpenCode Desktop to host our agents,
a sandbox, and Codex-class dev tools? Which is the better host?

## Recommendation: **OpenCode as the primary host**, JCode as fallback

| Criterion | OpenCode | JCode |
|---|---|---|
| Provider config | First-class: `opencode.json` custom provider → point `base_url` at our router :8010/:8080 | Supported via manifest, but thinner |
| Extensibility | Plugins + custom commands + agents config | Full control (our code) but smaller surface |
| Tool architecture | Shell/edit/read tools already modeled like Codex | Would need building from scratch |
| Community velocity | Active upstream; we track it as a fork target | Solo maintenance |
| Risk | Upstream drift | Stagnation |

Both clients already appear in our switchboard (`mimocode/manifest.json`,
ports 3000/5000) — the integration work is provider wiring plus tool
bridge, not a rewrite.

## Codex feature inventory worth porting

Public, well-understood agentic-CLI capabilities mapped to our stack:

| Codex capability | Our equivalent today | Gap action |
|---|---|---|
| Sandboxed shell w/ approval modes (suggest / auto / full-auto) | `ENABLE_SHELL_TOOLS` global flag only | 🔜 per-run approval profiles in `autonomous/` (`approval: suggest\|auto\|full`) gating tool calls |
| OS-level sandbox (seccomp/landlock, network-off) | cwd-chroot-lite (path guards, timeouts) | 🔜 bubblewrap/systemd-nspawn runner option inside workspace container |
| Diff-based file edits (apply_patch) | whole-file `=== FILE ===` blocks | 🔜 accept unified diffs for surgical edits on large files |
| Git-aware context (repo map, status) | flat file tree listing | 🔜 include `git status` + diff stats in coder/reviewer prompts |
| Streaming plan/todo visibility | `_run.json` polling via CLI | ✅ dashboard auto-runs panel planned; SSE exists |
| MCP server support | none | 🔜 expose router+agents as an MCP server so any MCP client (incl. OpenCode) uses our models/tools |
| Session resume | run state persisted; no resume executor | 🔜 `resume_from(run_id)` re-enters loop with prior context |
| Model failover/fallback | ✅ router chain + degenerate retry | parity |
| Cost/token guardrails | max_tokens caps only | 🔜 token accounting per run from llama.cpp usage fields |

## Integration sequence (when picked up)

1. Ship MCP server wrapper (`mcp/server.py`) over `/route`, `/agent/*`,
   `/workflow/run`, autonomous start/status — instant Codex/OpenCode
   compatibility without touching their code.
2. Fork-track OpenCode: add "FreeAI" provider preset pointing at the
   MCP endpoint; keep upstream mergeable.
3. Port approval profiles into `autonomous/agent.py` (suggest = shell
   requires dashboard confirm endpoint; full-auto = current behavior).
4. Diff-edit support behind `EDIT_MODE=diff|full` env.
5. JCode inherits everything through the same MCP/API surface — zero
   extra work, which is exactly why OpenCode-first costs least.
