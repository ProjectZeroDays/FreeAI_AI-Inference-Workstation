## Description: <br>
Orchestrates multi-agent teams with defined roles, task lifecycles, handoff protocols, review workflows, and shared artifact conventions. <br>

This skill is ready for commercial/non-commercial use. <br>

## Publisher: <br>
[arminnaimi](https://clawhub.ai/user/arminnaimi) <br>

### License/Terms of Use: <br>


## Use Case: <br>
Developers and agent operators use this skill to set up sustained multi-agent workflows with defined roles, task states, handoffs, reviews, and artifact conventions. <br>

### Deployment Geography for Use: <br>
Global <br>

## Known Risks and Mitigations: <br>
Risk: Uncontrolled agent spawning can increase cost or exceed operational limits. <br>
Mitigation: Define who may spawn agents and set budget and concurrency limits before using the workflow. <br>
Risk: Shared workspaces can expose secrets or allow untrusted edits to persistent role and protocol files. <br>
Mitigation: Keep secrets out of shared directories and protect persistent role and protocol files from untrusted edits. <br>
Risk: Coordinated agents may attempt high-impact actions without enough human oversight. <br>
Mitigation: Require human approval before high-impact actions. <br>


## Reference(s): <br>
- [ClawHub skill page](https://clawhub.ai/arminnaimi/agent-team-orchestration) <br>
- [Team setup](references/team-setup.md) <br>
- [Task lifecycle](references/task-lifecycle.md) <br>
- [Communication](references/communication.md) <br>
- [Patterns](references/patterns.md) <br>


## Skill Output: <br>
**Output Type(s):** [Text, Markdown, Guidance, Configuration] <br>
**Output Format:** [Markdown guidance with task-flow templates and handoff examples] <br>
**Output Parameters:** [1D] <br>
**Other Properties Related to Output:** [Instruction-only playbook; no code execution or external tool calls are required.] <br>

## Skill Version(s): <br>
1.0.0 (source: server release metadata) <br>

## Ethical Considerations: <br>
Users should evaluate whether this skill is appropriate for their environment, review any generated or modified files before relying on them, and apply their organization's safety, security, and compliance requirements before deployment. <br>
