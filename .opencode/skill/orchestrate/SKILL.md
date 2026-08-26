---
name: orchestrate
description: Subagent fan-out and result aggregation for opencode. Use when the coordinator needs to decompose a request across multiple specialist subagents, dispatch them in parallel/serial via the task tool, and synthesize their returns into one answer. Covers decomposition, concurrency caps, handoff protocols, and failure handling.
---

# Orchestrate — subagent fan-out for opencode

Use this skill whenever a request needs more than one specialist subagent. The
coordinator owns decomposition, dispatch, and aggregation; subagents are
isolated and return a single message.

## 1. Decompose before you dispatch

Produce a small table in your head (or a `todowrite` list) before calling `task`:

| step | subagent_type | model      | depends on | acceptance criterion        |
|------|---------------|------------|------------|-----------------------------|
| 1    | planner       | small_model| —          | plan with paths + criteria  |
| 2a   | coder         | default    | 1          | tests green for module A    |
| 2b   | coder         | default    | 1          | tests green for module B    |
| 3    | reviewer      | default    | 2a,2b      | no actionable findings      |
| 4    | maintainer    | small_model| 3          | lint/types/tests green      |

Rules:
- One concern per subagent. Don't combine "implement X" and "review X" in one.
- Prefer the `planner` first whenever the request touches >2 files or the path
  isn't obvious.
- The reviewer always runs **after** implementation, on the diff, cold.

## 2. Dispatch with the `task` tool

```
task(subagent_type="coder",
     description=<3-5 words>,
     prompt=<fully self-contained instructions; the subagent has NO memory of your conversation>)
```

- The `prompt` must contain everything the subagent needs: file paths, the
  exact plan item, conventions to follow, and the acceptance criterion. Never
  say "see above" — the subagent can't.
- `description` is a short label, shown in the UI; make it unique per round.

## 3. Concurrency and ordering

- Hard cap: **3 concurrent** `task` dispatches using the default model. The
  provider rate limiter (see `rate-limit-retry`) is the real backstop, but keep
  this cap so you don't burn budget on retries.
- If items are independent (2a, 2b above), dispatch them in the same assistant
  message so they run in parallel. If they depend on each other, wait.
- Use cheap models (`small_model`: `openai/gpt-4o-mini` or a local model) for
  planner/maintainer triage steps; reserve the default model for coder/reviewer.

## 4. Handling subagent failures

A subagent return can be a success, a partial result, or an error. Treat each:

- **Error / it clearly didn't finish**: do NOT immediately re-dispatch. Load the
  `self-heal` skill, diagnose (was it a tool failure? an API 429? bad path?),
  fix the root cause in the *prompt* or environment, then re-dispatch at most
  once. If it fails again, surface the failure to the user instead of looping.
- **Partial**: feed the partial result forward. Don't redo finished work.
- **Success**: aggregate (next step).

Never enter a tight retry loop. The `rate-limit-retry` skill owns backoff
math; this skill owns *when* to retry.

## 5. Aggregate, don't relay

When all subagents return:
1. Synthesize their outputs into **one** answer to the user.
2. Lead with the outcome ("Done: X, Y landed; Z deferred because …").
3. Include `file:line` references so the user can navigate.
4. Do not paste each subagent's raw return. The user asked you, not them.

## 6. Handoff protocol

If you must hand a result from one subagent to another, do it **through the
prompt**, including the artifact (the diff, the plan text, the findings list).
Subagents don't share filesystem state between rounds beyond what's on disk, so
for code, the diff on disk is the handoff; for analysis, paste it inline.

## 7. Cancelling / reducing scope

If the user's budget/time runs low, prefer to **reduce scope** (deliver one
working slice) over shipping partially-broken breadth. Tell the user what was
deferred so they can request it next.