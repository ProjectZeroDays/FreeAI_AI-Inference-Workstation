---
name: summarize-session
description: "Summarizes an agent session transcript into a concise briefing: goals, decisions, code changes, open questions. Use when starting a new session after a previous one, or when the user asks 'what did we work on?' or 'summarize the session'."
---

# Summarize Session

Generates a human-readable session summary from a session transcript (JSONL, log file, or chat history). Produces a structured briefing covering what was done, what changed, and what's left.

## When to Use

- User says: "summarize the session", "what did we work on", "give me a session recap", "session summary"
- Before starting a new session and you want context from the previous one
- After a long task when the user wants a recap
- When asked to "brief me on what happened"

## Inputs

The skill accepts a session transcript. Look for these formats in order:

1. **Session JSONL** — a `.jsonl` file in `.opencode/sessions/`, `sessions/`, or the project root (named `session-*.jsonl` or `transcript-*.jsonl`)
2. **`.md` session log** — a markdown file in `.opencode/`, `sessions/`, or the project root
3. **Raw chat log** — messages pasted directly by the user

If no transcript is found, ask the user: "Which session would you like summarized? Please provide a transcript file or path, or paste the conversation history."

## Output Format

Produce a summary in this structure:

```
## Session Summary: [brief title]
**Date**: [YYYY-MM-DD]
**Duration**: [approximate]
**Status**: completed | interrupted | abandoned

### Goals
- [What the user was trying to accomplish]

### Key Decisions
- [Important technical or architectural choices made]

### Changes Made
- **Files modified**: [list with brief descriptions]
- **New files created**: [list]
- **Files deleted**: [list]
- **Configuration changes**: [env vars, config updates, etc.]

### Code Highlights
- [Relevant code snippets or patterns introduced, with file:line references]

### Open Questions / Blockers
- [Items left unresolved, TODOs, or questions the user asked but didn't answer]

### Next Steps
- [Recommended actions for the next session]
```

## Rules

- Be concise. Use bullet points, not paragraphs.
- Do NOT include raw command output, full file contents, or secrets.
- Focus on *what changed* and *why*, not every single action taken.
- If the session was long, group related changes instead of listing every one.
- Flag anything that looks like a bug, a workaround, or an incomplete implementation.
- If no transcript is available, summarize from memory if you have it; otherwise state that clearly.

## Quick Command

When the user provides a file path directly, summarize it immediately without asking.

Example:
> "summarize .opencode/sessions/session-2025-01-15.jsonl"
> → Read the file and produce the summary above.
