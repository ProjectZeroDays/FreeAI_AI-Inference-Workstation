## Description: <br>
Spec-first, TDD, subagent-driven software development workflow for building features, debugging issues, and finishing development branches. <br>

This skill is ready for commercial/non-commercial use. <br>

## Publisher: <br>
[wlshlad85](https://clawhub.ai/user/wlshlad85) <br>

### License/Terms of Use: <br>


## Use Case: <br>
Developers and engineering agents use this skill to follow a structured software-development workflow: brainstorm, write implementation plans, execute tasks with TDD and subagents, debug systematically, and finish branches with test verification. <br>

### Deployment Geography for Use: <br>
Global <br>

## Known Risks and Mitigations: <br>
Risk: The workflow may run tests, create commits, spawn subagents, and help merge branches or open pull requests. <br>
Mitigation: Review generated plans, commands, diffs, branch names, and pull request text before execution. <br>
Risk: Plan files and subagent prompts can expose sensitive project details if secrets or credentials are included. <br>
Mitigation: Do not put secrets or private credentials into plan files or subagent prompts. <br>


## Reference(s): <br>
- [Superpowers Dev Workflow on ClawHub](https://clawhub.ai/wlshlad85/superpowers) <br>
- [Brainstorming Reference](references/brainstorming.md) <br>
- [Writing Plans Reference](references/writing-plans.md) <br>
- [Subagent-Driven Development Reference](references/subagent-development.md) <br>
- [Systematic Debugging Reference](references/systematic-debugging.md) <br>
- [Test-Driven Development Reference](references/tdd.md) <br>
- [Finishing a Development Branch Reference](references/finishing-branch.md) <br>


## Skill Output: <br>
**Output Type(s):** [Text, Markdown, Code, Shell commands, Configuration, Guidance] <br>
**Output Format:** [Markdown with inline shell commands, code snippets, plans, review prompts, and branch-operation choices] <br>
**Output Parameters:** [1D] <br>
**Other Properties Related to Output:** [May create design docs and implementation plans, propose commands, spawn subagents, and guide commits, merges, or pull requests when the host agent has those tools.] <br>

## Skill Version(s): <br>
1.0.0 (source: server release evidence) <br>

## Ethical Considerations: <br>
Users should evaluate whether this skill is appropriate for their environment, review any generated or modified files before relying on them, and apply their organization's safety, security, and compliance requirements before deployment. <br>
