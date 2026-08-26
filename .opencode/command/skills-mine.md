---
description: Mine recent turns for repetitive / rule-bound / multi-step work and propose a new SKILL.md (or extend an existing one). Confirms before installing.
agent: coordinator
model: anthropic/claude-sonnet-4-5-20250929
subtask: true
---

Load the `auto-skill-creator` skill and mine the recent chat for a skill
candidate. `$ARGUMENTS` may be one of:
- (empty)              → scan the last ~10 turns and propose at most one
  candidate.
- `--last N`           → scan the last N turns.
- `--force`            → propose even if recurrence score <3 (use sparingly; the
  confidence gate exists to avoid skill-spam).
- `--dry-run`          → produce the preview but never write the file.

Per the skill:
1. Detect candidates using the §1 weighting table.
2. If none reach score ≥3 (or `--force`), say so and stop.
3. Otherwise show the §4 preview (frontmatter + full body) and **WAIT** for the
   user to reply `install <name>` or `tweak <field>: <value>`.
4. On `install`, use `write` to create
   `.opencode/<skill-name>/SKILL.md` (matches `name` in frontmatter).
5. Remind the user ONCE: skills load at opencode startup, so a restart is
   required for the new skill to take effect. Don't repeat.

Never overwrite an existing skill without naming the conflict first and getting
explicit `install --replace <name>` confirmation. Default to proposing an
*extension* edit if an existing skill already covers the workflow.