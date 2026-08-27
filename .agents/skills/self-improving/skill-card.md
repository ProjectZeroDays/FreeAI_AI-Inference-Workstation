## Description: <br>
Self-reflection, self-criticism, self-learning, and self-organizing memory help an agent evaluate its own work, catch mistakes, and improve permanently. <br>

This skill is ready for commercial/non-commercial use. <br>

## Publisher: <br>
[ivangdavila](https://clawhub.ai/user/ivangdavila) <br>

### License/Terms of Use: <br>
MIT-0 <br>


## Use Case: <br>
Developers, agent users, and workspace maintainers use this skill to help an agent learn from explicit corrections, self-reflection, failed operations, and repeated workflow patterns while keeping memory local and reviewable. <br>

### Deployment Geography for Use: <br>
Global <br>

## Known Risks and Mitigations: <br>
Risk: The skill keeps cross-session local memory about corrections, preferences, and workflow patterns. <br>
Mitigation: Install only when this memory behavior is desired, review ~/self-improving/ periodically, and use strict or passive mode when more confirmation is needed. <br>
Risk: Sensitive information could be retained if memory boundaries are not followed. <br>
Mitigation: Do not store credentials, financial data, medical data, biometric data, third-party details, location patterns, or access patterns. <br>
Risk: The setup flow can optionally install a separate Proactivity skill. <br>
Mitigation: Review the separate Proactivity skill before approving optional installation. <br>


## Reference(s): <br>
- [ClawHub Skill Page](https://clawhub.ai/ivangdavila/self-improving) <br>
- [Publisher Profile](https://clawhub.ai/user/ivangdavila) <br>
- [Skill Homepage](https://clawic.com/skills/self-improving) <br>
- [Setup Guide](setup.md) <br>
- [Security Boundaries](boundaries.md) <br>
- [Learning Mechanics](learning.md) <br>
- [Memory Operations](operations.md) <br>


## Skill Output: <br>
**Output Type(s):** [Guidance, Markdown, Shell commands, Configuration] <br>
**Output Format:** [Markdown guidance with inline shell commands and local file templates] <br>
**Output Parameters:** [1D] <br>
**Other Properties Related to Output:** [Creates or updates local memory and workspace steering files when activated and configured.] <br>

## Skill Version(s): <br>
1.2.16 (source: frontmatter and server release evidence) <br>

## Ethical Considerations: <br>
Users should evaluate whether this skill is appropriate for their environment, review any generated or modified files before relying on them, and apply their organization's safety, security, and compliance requirements before deployment. <br>
