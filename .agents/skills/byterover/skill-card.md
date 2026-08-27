## Description: <br>
ByteRover helps agents query, search, curate, review, and version project memory stored in `.brv/context-tree` through the `brv` CLI. <br>

This skill is ready for commercial/non-commercial use. <br>

## Publisher: <br>
[byteroverinc](https://clawhub.ai/user/byteroverinc) <br>

### License/Terms of Use: <br>
MIT-0 <br>


## Use Case: <br>
Developers and agent users use ByteRover to retrieve project patterns before work and save new decisions or architectural knowledge after implementation. <br>

### Deployment Geography for Use: <br>
Global <br>

## Known Risks and Mitigations: <br>
Risk: Broad memory instructions may cause unnecessary external-memory queries or persistent storage of user interaction details. <br>
Mitigation: Use ByteRover only for intentional project-memory workflows and prefer local search when synthesized answers are not needed. <br>
Risk: Stored project memory may include secrets or personal data if curation is performed without review. <br>
Mitigation: Review content before curation or sync, and avoid storing secrets or personal data. <br>
Risk: Remote sync and additional memory providers can read or write more project context than expected. <br>
Mitigation: Enable remote sync or extra providers only after confirming what content they can access and modify. <br>


## Reference(s): <br>


## Skill Output: <br>
**Output Type(s):** [text, markdown, shell commands, configuration, guidance] <br>
**Output Format:** [Markdown guidance with inline shell commands; some CLI commands can emit JSON.] <br>
**Output Parameters:** [1D] <br>
**Other Properties Related to Output:** [Commands operate on `.brv/context-tree`; query and curate operations can use a configured LLM provider, while remote sync requires authentication.] <br>

## Skill Version(s): <br>
3.3.0 (source: server release evidence) <br>

## Ethical Considerations: <br>
Users should evaluate whether this skill is appropriate for their environment, review any generated or modified files before relying on them, and apply their organization's safety, security, and compliance requirements before deployment. <br>
