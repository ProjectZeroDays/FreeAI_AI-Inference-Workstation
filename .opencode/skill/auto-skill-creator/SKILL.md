---
name: auto-skill-creator
description: Mines the current chat for repetitive, multi-step, or rule-bound work the user (or agent) keeps doing, and proposes a new SKILL.md to capture it. Use when the user says "I keep having to...", "every time I do X", "this is getting repetitive — make a skill", "propose a skill from this chat". Also fires on the ~30-min cadence via the `auto-skill-creator.ts` plugin, or on demand via /skills-mine.
---

# auto-skill-creator — turn recurring work into a new skill

This skill ONLY **proposes** a new skill file. It never installs it
unilaterally — the coordinator/user confirms before the file lands in
`.opencode/skill/<name>/SKILL.md`.

## 0. When to fire

Pair this skill with strong evidence that:
- a workflow has appeared **≥3 times** in this session (recurrence), OR
- the user said as much ("I keep doing X", "every time"), OR
- a single user request involves ≥6 sequential deterministic steps that don't
  fit any existing skill, OR
- the `auto-skill-creator.ts` plugin fired its ~30-min timer prompt.

Anti-recurrence: don't fire on `chore:`-style one-offs ("rename this file"),
on requests fully covered by an existing skill (use that skill instead), or on
clarification questions. Speculative skill creation is waste.

## 1. Candidate detection

Scan the recent turns (the last ~10 user messages + agent responses). A
candidate workflow has these markers:

| marker                                                  | weight |
|---------------------------------------------------------|--------|
| user request and matching response shape ≥3× this session | 3      |
| explicit "I keep/the agent keeps..." phrasing           | 4      |
| multi-step procedure with deterministic order (>3 steps) | 2      |
| reference to a tool, file, or config repeated across turns | 1    |
| the workflow already matches an existing skill strongly  | -5 (skip; don't propose a dup) |

Sum weights. If score ≥3, propose; else, just note "no skill candidates this
session" and stop.

## 2. Authoring the proposed SKILL.md

opencode's skill loader scans `**/SKILL.md` and consumes specific frontmatter.
Author to spec:

```markdown
---
name: <lowercase-hyphen-name, ≤64 chars, matches the folder name>
description: One sentence covering what the skill does AND when to trigger it.
  Front-load the literal keywords a user is likely to say; gate with "Use when..."
  not "I help with..."; third person.
---

# <Skill Title>

(intro: 2-4 lines on what this skill accomplishes and when it's the right tool)

## 0. Pre-flight / Stop conditions
(the conditions that must hold before this skill runs; gates refuse bad input)

## 1. Step-by-step playbook
(ordered numbered steps; named file paths; concrete commands; examples)

## 2. Decision tree / edge cases
(when the playbook branches; tie-breakers; false-positive avoidance)

## 3. Output format
(must have a fixed shape so downstream agents / the coordinator can parse it)

## 4. Hard limits
(no destructive ops, no force-push, etc. — the user's safety bounds)
```

Authoring rules (non-negotiable for the generated skill):

- `name` lowercase-hyphen, ≤64 chars.
- `description` MUST front-load trigger keywords AND gate with "Use when...".
  Bad: "Helps with commits." Good: "Use when the user commits, amends a staged
  file, or asks 'commit this' — composes a conventional-commit message, runs
  `git commit`, and confirms before pushing."
- Body sections use the §0 pre-flight → playbook → output → limits shape that the
  other skills in this toolkit use. Consistency makes them readable to the agent.
- No emojis. No empty sections — if a section wouldn't have content, drop it.
- Cite `file:line` references like the rest of the toolkit (e.g.
  `src/rateLimiter.ts:42`) when a step depends on existing code.

## 3. Naming and de-dup

Before proposing, check the registry in `auto-skill-selector`'s §1 table and the
filesystem under `.opencode/skill/*`. If your proposed `name` is taken:

- Don't overwrite. Append a numbered variant (`<name>-v2`) only if the intent is
  genuinely different; if it's the same intent, the user probably wants the
  **existing** skill extended, not a new one. In that case, propose an *edit* to
  the existing skill rather than a new file.

## 4. Output format (the proposal, before any write)

```
SKILL CANDIDATE:
  name:        <proposed-name>
  triggered by: <one line: which markers in recent turns scored ≥3>
  recurrence:  <N occurrences in this session / "user stated" / "30-min timer">

PROPOSED SKILL.md (preview; not applied):
---
name: <...>
description: <...>
---
# <Title>

<full body>

CONFIRM? reply `install <name>` to write
`.opencode/skill/<name>/SKILL.md` and reload skills (you must restart opencode
for the agent to load it). Reply `tweak <field>: <value>` to revise first.
```

Wait for the user's reply. On `install`, use the `write` tool to create the
file at the absolute path; on `tweak`, regenerate the preview with the requested
change before installing. Never write the file without explicit confirmation.

## 5. Cadence / cadence-of-cadence

- This skill running once means: propose ≤1 candidate per session unless the user
  asks for more. Don't spam multiple candidates simultaneously — that's
  decision fatigue, not help.
- The ~30-min timer (the plugin) is a *suggestion* to *consider* running this
  skill, never an auto-install. The plugin's job is one prompt per session, every
  ≥30 min of inactivity; this skill's job is to *propose*; the user's job is to
  *confirm*.
- After a successful install, log a one-line note in the chat: "Skill
  `<name>` installed; reload required." Don't keep proposing after install.

## 6. Hard limits

- Never install a skill above HIGH confidence (3+ recurrence signals or one
  explicit user request). One-off chats are not recurring work.
- Never overwrite or augment an existing skill without naming the conflict and
  asking. Default failure mode is "extend existing" rather than "create new".
- Never create a skill that subverts safety (jailbreaks, refusal ablation,
  credential theft, evasion). Reject such candidates loudly and stop.
- Never create a skill whose trigger is "this skill should always run" — that
  defeats opencode's selector. Skills are scoped tools.
- After every install, remind the user once: skills load at startup, so the new
  skill needs an opencode restart to take effect. Don't repeat the reminder.