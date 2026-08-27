## Description: <br>
Elite Longterm Memory helps AI agents preserve project context with write-ahead logs, vector search, git-notes, local memory files, and optional cloud backup. <br>

This skill is ready for commercial/non-commercial use. <br>

## Publisher: <br>
[NextFrontierBuilds](https://clawhub.ai/user/NextFrontierBuilds) <br>

### License/Terms of Use: <br>
MIT <br>


## Use Case: <br>
Developers and agent users use this skill to initialize and maintain project memory files, daily logs, and recall configuration so agents can preserve preferences, decisions, lessons, and task context across sessions. <br>

### Deployment Geography for Use: <br>
Global <br>

## Known Risks and Mitigations: <br>
Risk: The skill encourages agents to retain project and preference context, which can accidentally preserve sensitive, private, or regulated details. <br>
Mitigation: Require approval before saving sensitive details, summarize instead of copying raw conversation text, and review or delete stored memory regularly. <br>
Risk: Optional Mem0 or SuperMemory use may send memory content to external cloud services. <br>
Mitigation: Enable cloud memory only with approved providers, trusted API keys, and clear permission for the type of data being stored. <br>
Risk: Persisted memories can become stale or misleading and may influence later agent work. <br>
Mitigation: Run routine memory hygiene, keep high-value summaries curated, and review recalled context before relying on it for decisions. <br>


## Reference(s): <br>
- [ClawHub Skill Page](https://clawhub.ai/NextFrontierBuilds/elite-longterm-memory) <br>
- [Full Documentation](README.md) <br>
- [Skill Instructions](SKILL.md) <br>
- [NPM Package](https://www.npmjs.com/package/elite-longterm-memory) <br>


## Skill Output: <br>
**Output Type(s):** [text, markdown, shell commands, configuration, guidance] <br>
**Output Format:** [Markdown guidance with shell commands, JSON configuration examples, and generated local Markdown memory files] <br>
**Output Parameters:** [1D] <br>
**Other Properties Related to Output:** [Creates and updates local SESSION-STATE.md, MEMORY.md, and memory/*.md files when the CLI is used.] <br>

## Skill Version(s): <br>
1.2.3 (source: evidence release, SKILL.md frontmatter, and package.json) <br>

## Ethical Considerations: <br>
Users should evaluate whether this skill is appropriate for their environment, review any generated or modified files before relying on them, and apply their organization's safety, security, and compliance requirements before deployment. <br>
