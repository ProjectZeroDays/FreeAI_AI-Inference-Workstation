## Description: <br>
Help users build a personal knowledge base by organizing whatever they send into structured notes. <br>

This skill is ready for commercial/non-commercial use. <br>

## Publisher: <br>
[ivangdavila](https://clawhub.ai/user/ivangdavila) <br>

### License/Terms of Use: <br>


## Use Case: <br>
External users use this skill to capture links, ideas, quotes, questions, and other notes into a local Markdown personal knowledge base, then progressively organize them with tags, links, and an inbox workflow. <br>

### Deployment Geography for Use: <br>
Global <br>

## Known Risks and Mitigations: <br>
Risk: Private or sensitive material may be stored in the local knowledge base under ~/kb/. <br>
Mitigation: Avoid sending secrets or private material unless local Markdown storage is acceptable for that content. <br>
Risk: Fetching user-provided links may contact external sites. <br>
Mitigation: Review links before fetching and avoid opening untrusted URLs when network contact is not intended. <br>
Risk: Inbox processing can remove items after they are converted into notes. <br>
Mitigation: Review generated notes before deleting inbox entries. <br>


## Reference(s): <br>
- [ClawHub skill page](https://clawhub.ai/ivangdavila/pkm) <br>
- [Publisher profile](https://clawhub.ai/user/ivangdavila) <br>


## Skill Output: <br>
**Output Type(s):** [Text, Markdown, Shell commands, Guidance] <br>
**Output Format:** [Markdown notes, concise guidance, and optional shell commands for local search or file operations] <br>
**Output Parameters:** [1D] <br>
**Other Properties Related to Output:** [Creates or updates local Markdown files under ~/kb/ and may fetch linked pages when the user provides URLs.] <br>

## Skill Version(s): <br>
1.0.1 (source: server release metadata) <br>

## Ethical Considerations: <br>
Users should evaluate whether this skill is appropriate for their environment, review any generated or modified files before relying on them, and apply their organization's safety, security, and compliance requirements before deployment. <br>
