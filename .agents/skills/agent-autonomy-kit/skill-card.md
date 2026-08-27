## Description: <br>
Agent Autonomy Kit helps agents work proactively from a task queue, heartbeat routine, and scheduled operations instead of waiting for prompts. <br>

This skill is ready for commercial/non-commercial use. <br>

## Publisher: <br>
[ryancampbell](https://clawhub.ai/user/ryancampbell) <br>

### License/Terms of Use: <br>
MIT <br>


## Use Case: <br>
Developers and agent operators use this skill to configure autonomous agent work loops with a persistent task queue, proactive heartbeat routine, progress logging, and scheduled runs. <br>

### Deployment Geography for Use: <br>
Global <br>

## Known Risks and Mitigations: <br>
Risk: Scheduled unattended agent activity can continue work without a human prompt. <br>
Mitigation: Enable schedules only after defining allowed task types, writable paths, external posting rules, token or spending limits, logging, and a simple disable procedure. <br>
Risk: Broad autonomous work loops can act on tasks that are inappropriate for sensitive or production workspaces. <br>
Mitigation: Avoid sensitive or production workspaces until explicit controls and review boundaries are in place. <br>


## Reference(s): <br>
- [ClawHub Skill Page](https://clawhub.ai/ryancampbell/agent-autonomy-kit) <br>


## Skill Output: <br>
**Output Type(s):** [markdown, shell commands, configuration, guidance] <br>
**Output Format:** [Markdown instructions with code blocks and template files] <br>
**Output Parameters:** [1D] <br>
**Other Properties Related to Output:** [Produces task queue and heartbeat templates plus scheduling guidance for autonomous agent operation.] <br>

## Skill Version(s): <br>
1.0.0 (source: SKILL.md frontmatter and server release metadata) <br>

## Ethical Considerations: <br>
Users should evaluate whether this skill is appropriate for their environment, review any generated or modified files before relying on them, and apply their organization's safety, security, and compliance requirements before deployment. <br>
