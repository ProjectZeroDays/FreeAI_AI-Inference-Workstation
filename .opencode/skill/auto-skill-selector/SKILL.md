---
name: auto-skill-selector
description: The meta-skill that picks other skills. Loaded by the coordinator before any task to match the user's request against every installed skill's frontmatter description and surface the 1-3 skills most relevant to THIS turn. Use BEFORE planning or dispatch — load this once per turn when the request looks non-trivial, then load the picked skill(s). Never assume which skill a task wants; let this scan and propose.
---

# auto-skill-selector — pick the right skill, fast

This is a **router**. It runs a lightweight match between the current user request
and every installed skill's `description` (frontmatter), surfaces the top 1-3
candidates, and tells the coordinator which to load. It does NOT do the work
itself — it picks the worker.

## 0. Why this exists

Skills only trigger when their description matches. The user's phrasing won't
always match a skill's keywords ("ship a release" vs `release`-skill's
description says "cut a versioned release"). This skill is the bridge: it reads
all available descriptions and proposes the best fit, so the coordinator never
guesses.

## 1. Inventory the installed skills

opencode exposes loaded skills via its tool surface, but to keep this skill
self-contained, we maintain an explicit registry here. **Keep this table in sync
when you add a skill** (it lives at the top for that reason):

| skill              | triggers (subset; see its SKILL.md for full)                                              |
|--------------------|-------------------------------------------------------------------------------------------|
| orchestrate        | multi-step, fan-out, parallel subagents, decompose, dispatch, aggregate                   |
| rate-limit-retry   | 429, 5xx, timeout, retry, backoff, jitter, fallback, RPM, TPM, quota, circuit breaker    |
| self-heal          | broken API, auth failure, ECONNREFUSED, module not found, command not found, ENOENT       |
| repo-maintenance   | maintain repo, run CI locally, outdated deps, stale issues, deps PR, refresh CHANGELOG    |
| research           | what's the current version, CVE affected range, breaking changes, verify before planning   |
| code-review        | review this PR, find bugs in this diff, audit these commits, security review              |
| release            | release, cut a release, bump version, tag a release, publish a new version, ship a release |
| docs-sync          | sync docs, fix outdated README, regenerate API docs, update the wiki, docs are behind     |
| project-audit      | audit my repo, find dead code, find duplicate files, orphaned deps, what can I delete     |
| frontend-coverage  | wire up the backend, what endpoints aren't used, frontend backend mismatch, dead routes  |
| release-assets     | build binaries, package for release, cross-compile, .deb/.rpm/.dmg, ship install scripts, upload release assets |
| scan-and-debug     | scan for errors, run all tests, what's failing in CI, debug this, reproduce this bug     |
| auto-skill-creator | create a new skill, this keeps happening, I keep doing X, propose a skill from this chat |

(Inherited community skills — `comfyui`, `p5js`, `manim-video`, `linear`, etc. —
match on their own frontmatter; the selector doesn't pre-list them all, it
matches by `description` text too. The table above is for skills authored in
this toolkit where we know the exact trigger words.)

## 2. Match algorithm (cheap and transparent)

For the current user request `R`:

1. Tokenize `R` (lowercase, split on non-alphanumerics, drop stop words).
2. For each skill `S`, build a keyword set `K(S)` from: its `name`, its
   `description`, and the trigger phrases listed in §1 (when present).
3. Score `S` by `|K(S) ∩ tokens(R)| + bonus(if a known multi-word trigger phrase
   appears verbatim in R, +2)`. Verbatim phrase wins because single-word matches
   are noisy.
4. Drop all scores ≤ 0. Sort descending. Take top 3.

If the top score is ≥5 and the next is ≤1, recommend **one**. If two skills are
within 2 of each other and their scores are both ≥3, recommend **both**, loaded
in priority order.

## 3. Hard cases — know when to refuse

- **No skill scores > 0** → DON'T invent one. Tell the user "no installed skill
  matches; treating as ad-hoc work" and proceed without loading a skill. The
  coordinator will fall back to the `planner` + `coder` path.
- **Safety skills (`rate-limit-retry`, `self-heal`) calling themselves** → those
  are reactive skills, not task skills. Exclude them from the top recommendation;
  they fire on failure modes, not requests. Keep them in the registry so they
  can be loaded LATER when something breaks.
- **Two skills overlapping so much it's a coin-flip** (`repo-maintenance` vs
  `project-audit` for "clean up the repo") → recommend the one matching the
  user's verb. "Maintain" / "run CI" → `repo-maintenance`. "Audit" / "find dead
  code" / "what can I delete" → `project-audit`. State the tiebreaker in your
  proposal so the user can override.
- **The user already invoked a slash command (`/review`, `/scan`, etc.)** →
  bypass this skill; the slash command already routed to the right skill. Only
  use the selector when the user typed prose.

## 4. Output format (the coordinator consumes this)

Return ONLY this block; no preamble, no narration:

```
SKILL MATCH:
  primary:  <skill-name>            (score N, matched: "<phrase>")
  optional: <skill-name>            (score N, matched: "<phrase>")   # or "none"
  bypass:   <fallback reason> | loaded-then-discarded
RATIONALE (one line): <why this over the runner-up>
NEXT: load `primary` (and `optional` if any) before proceeding. Then continue
with the user's request.
```

## 5. What the coordinator does with it

After this skill returns:
1. `coordinator` loads the named skill(s) via its own skill-loading mechanism
   (no separate tool call needed in opencode — the skill content is inlined).
2. `coordinator` proceeds with the user's request, acting on the loaded skill's
   instructions.
3. `coordinator` does NOT load `auto-skill-selector` again for follow-up messages
   in the same turn — the routing decision stands. Re-run the selector only on a
   substantively new user request (different verbs/objects).

## 6. Hard limits

- Never load a skill after the user is already in a `/command` flow; let the
  command drive.
- Never recommend a skill whose score is 0 — silence is better than noise.
- Never recommend >3 skills at once — that's indecision, not routing.
- Never omit the safety-skills caveat (§3) so they remain available for reactive
  use later in the session.
- If `auto-skill-creator` scores high, that's a *meta* recommendation: the user
  is describing recurring work. Surface it, but don't auto-create — creation needs
  confirmation per that skill's own rules.