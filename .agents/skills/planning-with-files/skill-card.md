## Description: <br>
Implements Manus-style file-based planning for complex tasks by creating task_plan.md, findings.md, and progress.md and supporting automatic session recovery after /clear. <br>

This skill is ready for commercial/non-commercial use. <br>

## Publisher: <br>
[othmanadi](https://clawhub.ai/user/othmanadi) <br>

### License/Terms of Use: <br>
MIT-0 <br>


## Use Case: <br>
Developers and agent users use this skill to keep long-running or multi-step work organized with persistent planning, findings, and progress files. It is most useful for research, builds, debugging, and other tasks that need repeated context recovery across many tool calls or sessions. <br>

### Deployment Geography for Use: <br>
Global <br>

## Known Risks and Mitigations: <br>
Risk: Session recovery can display excerpts of prior local agent conversation history, which may include secrets, credentials, customer data, or proprietary prompts. <br>
Mitigation: Use the skill only in projects where this recovery behavior is acceptable, and avoid storing sensitive content in prior session history or planning files. <br>
Risk: Planning files may contain instruction-like text that could be mistaken for user or system instructions. <br>
Mitigation: Treat planning file contents as structured project data and use the included attestation flow when plan integrity matters. <br>


## Reference(s): <br>
- [Reference: Manus Context Engineering Principles](references/reference.md) <br>
- [Examples: Planning with Files in Action](references/examples.md) <br>
- [Planning with files on ClawHub](https://clawhub.ai/othmanadi/planning-with-files) <br>
- [Publisher profile: othmanadi](https://clawhub.ai/user/othmanadi) <br>


## Skill Output: <br>
**Output Type(s):** [Markdown files, Shell commands, Configuration, Guidance] <br>
**Output Format:** [Markdown planning files with inline shell and PowerShell commands] <br>
**Output Parameters:** [1D] <br>
**Other Properties Related to Output:** [Creates and updates task_plan.md, findings.md, and progress.md, with optional scoped plan directories under .planning/.] <br>

## Skill Version(s): <br>
v2.42.0 (source: server release metadata; frontmatter metadata: 2.42.0) <br>

## Ethical Considerations: <br>
Users should evaluate whether this skill is appropriate for their environment, review any generated or modified files before relying on them, and apply their organization's safety, security, and compliance requirements before deployment. <br>
