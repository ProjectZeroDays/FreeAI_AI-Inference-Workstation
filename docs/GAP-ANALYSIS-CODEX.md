# GAP Analysis — FreeAI Autonomous Stack vs OpenAI Codex (reverse-engineered)

Scope: capability-by-capability comparison of our self-hosted stack
against publicly understood Codex agentic-coding behavior. Gap sizes:
🟢 parity · 🟡 partial · 🔴 missing.

## Model & inference

| Capability | Codex | Ours | Gap | Path to close |
|---|---|---|---|---|
| Frontier model quality | hosted frontier LLMs | 12–13B local GGUF | 🔴 (capability ceiling) | inherent to local; mitigate with better prompts/roles, or bridge to hosted APIs via provider adapter |
| Multi-model fallback | managed server-side | ✅ router chain + degenerate retry | 🟢 | — |
| Context window | ~200K tokens | 4–32K (llama.cpp ctx) | 🔴 | raise `LLAMA_CTX` w/ KV quant; repo-map compression instead of raw files |
| Streaming everywhere | ✅ | router sync-only today | 🟡 | SSE passthrough in `/route` (backend streams already supported) |

## Agent loop

| Capability | Codex | Ours | Gap | Path |
|---|---|---|---|---|
| Plan → execute → verify loop | ✅ | ✅ planner/coder/tester/fixer/reviewer | 🟢 | — |
| Real command verification | ✅ sandboxed exec | ✅ compileall/pytest/node when shell on | 🟢 | widen tool set (linters per language) |
| Self-repair from errors | ✅ | ✅ fix rounds fed real output | 🟢 | — |
| Long-horizon memory across sessions | ✅ cloud threads | run-scoped `_run.json` only | 🟡 | persist summaries into a vector/kv store; resume executor |
| Parallel task execution inside a run | ✅ | workflow engine has it; SDLC loop sequential | 🟡 | reuse `run_parallel` for independent tasks |

## Tooling & safety

| Capability | Codex | Ours | Gap | Path |
|---|---|---|---|---|
| Approval profiles (suggest/auto/full-auto) | ✅ tri-mode UX | global shell flag | 🔴 | per-run approval enum + dashboard confirm queue |
| OS-level sandboxing | seccomp/landlock, network-off | path guards + timeouts + workspace root | 🔴 | bwrap/nspawn runner; default-deny network profile |
| Diff/surgical patch application | apply_patch | full-file rewrite blocks | 🔴 | unified-diff parser + applier (`EDIT_MODE=diff`) |
| Git-native operation | branch/commit/PR flows | git absent from agent context | 🔴 | init repo per run; commit per green phase; export bundle = branch archive |
| Tool plugin ecosystem / MCP | MCP client+server | REST only | 🔴 | ship MCP server wrapper over existing APIs |
| Network egress control for generated code | policy-managed | none | 🔴 | same sandbox work as above |

## Product surface

| Capability | Codex | Ours | Gap | Path |
|---|---|---|---|---|
| IDE/desktop integration | VSCode + CLI | OpenCode/JCode manifests, UI console | 🟡 | MCP server + provider preset (see CODEX-INTEGRATION.md) |
| Cloud + CLI + CI surfaces | ✅ | CLI + API + compose/K8s | 🟡 | GitHub Action calling autonomous API on issues |
| Telemetry/eval harness | internal | metrics counters only | 🔴 | prompt-regression suite: golden tasks scored by reviewer model |
| Cost guardrails | hosted billing | power tuner saves watts | 🟢 (opex) | token accounting when usage fields land |

## Verdict

Structurally we already implement the Codex *loop* (plan/code/verify/
fix/document/package) with real verification and multi-model routing.
The three load-bearing gaps are **sandbox depth**, **patch-based
editing**, and **MCP/tool ecosystem**. Closing those three makes
OpenCode/Codex-class clients first-class citizens of this stack and is
the recommended next epic — sequenced in docs/CODEX-INTEGRATION.md.
