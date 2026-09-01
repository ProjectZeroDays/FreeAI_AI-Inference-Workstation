---
name: context-surfing
description: "Monitors context window health throughout a session and rides peak context quality for maximum output fidelity. Activates automatically after plan-interview and intent-framed-agent. Stays active through execution and hands off cleanly to simplify-and-harden and self-improvement when the wave completes naturally or exits via handoff. Use this skill whenever a multi-step agent task is underway and session continuity or context drift is a concern. Especially important for long-running tasks, complex refactors, or any work where degraded context would silently corrupt the output. Trigger even if the user doesn't say 'context surfing' — if an agent task is running across multiple steps with intent and a plan already established, this skill is live."
---

# Context Surfing

The agent rides the wave of peak context. When the wave crests, it commits. When it detects drift, it pulls out cleanly — saving state, handing off, and letting the next session catch the next wave.

No wipeouts. No zombie sessions. Only intentional, high-fidelity execution.

## Mental Model

Think of context like an ocean wave:

- **Paddling in** = loading the intent frame, plan, and initial context. Energy is building.
- **The peak** = full context coherence. The agent knows exactly what it's doing and why. This is when to execute.
- **The shoulder** = context starting to flatten. Still rideable, but output density is dropping.
- **The close-out** = drift. Contradiction, hedging, second-guessing, or hallucinated details. Wipe-out territory.

The skill's job: ride as long as the wave is good, exit before it closes out.

## Lifecycle Position

```
[plan-interview] → [intent-framed-agent] → [context-surfing ACTIVE] → [verify-gate] → [simplify-and-harden] → [self-improvement]
```

Context Surfing is the execution layer. It wraps all work between intent capture and post-completion review.

### Relationship with intent-framed-agent

Both skills are live during execution. They monitor different failure modes:

- **intent-framed-agent** monitors *scope* drift — am I doing the right thing?
- **context-surfing** monitors *context quality* drift — am I still capable of doing it well?

**Precedence rule:** If both fire simultaneously, context-surfing's exit takes precedence. Degraded context makes scope checks unreliable.

## Activation

This skill is live the moment the intent frame and plan are established. No explicit invocation needed.

At activation, load whatever anchors are available:

1. The intent frame (from intent-framed-agent output) — if available
2. The plan (from plan-interview output) — if available
3. Project context files (CLAUDE.md, AGENTS.md, README.md)

## Drift Detection

### Strong signals (exit immediately)
- The agent contradicts a decision it already made
- A detail appears in the output that was never in the original context (hallucination)
- The agent re-opens a scope question that was explicitly resolved
- Output starts re-explaining the task rather than executing it

### Weak signals (trigger recovery)
- Responses are getting longer without getting more useful
- Hedging language increases: "it depends", "could be", "might want to consider"
- The agent switches approaches mid-task without explicit user direction
- References to the original intent become vague or paraphrased

## Recovery Protocol (Wave Re-Anchor)

When weak signals accumulate, try to re-anchor first:

### Step 1: Pause and re-read
Stop producing output. Re-read whatever wave anchor artifacts are available:
1. If an intent frame exists, open and read it verbatim
2. If a plan file exists, open and read the relevant section
3. Re-read the user's original task description and project context files

### Step 2: Reconcile
- **If the mismatch resolves** — resume execution
- **If uncertainty remains** — spawn a context-monitor subagent for a fresh perspective
- **If the subagent confirms strong drift** — escalate to the user
- **If the user re-grounds you** — integrate and resume
- **If the user can't resolve it** — proceed to Exit Protocol

## Exit Protocol (Wave Close-Out)

When a strong signal fires, or recovery fails:

### Step 1: Stop executing
Immediately pause task execution.

### Step 2: Write the handoff file
Create `.context-surfing/handoff-[slug]-[timestamp].md`:

```markdown
# Context Surf Handoff

## Session Info
- Task: [task name / slug]
- Started: [timestamp]
- Ended: [timestamp]
- Exit reason: [what drift signal was detected]

## Intent Frame (if available)
[copy directly from intent-framed-agent artifact]

## Plan (if available)
[copy directly from plan-interview artifact]

## Completed Work
[what was done]

## In Progress at Exit
[what was active]

## Pending Work
[remaining tasks]

## Drift Notes
[what triggered the exit]

## Active Context Files
[list .md files loaded]

## Modified Context Files
[list .md files changed]

## Recommended Re-entry Point
[where to pick up]
```

### Step 3: Notify the user
> "Context wave is done. I've saved the session state to `.context-surfing/[filename]`. The next session should load that file and catch the next wave."

## Principles

**Ride the peak, not the whole ocean.** A shorter session with high fidelity beats a long session with gradual corruption.

**Exit is not failure.** The wave close-out is a feature.

**The handoff file is the continuity.** It's what makes the next session as sharp as this one started.

**Never hide the exit.** Always be explicit with the user that a context exit happened and why.
