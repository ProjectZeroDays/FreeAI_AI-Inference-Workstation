## Description: <br>
A continuously adaptive skill suite that empowers Clawdbot to act as a versatile coder, business analyst, project manager, web developer, data analyst, and NAS metadata scraper. <br>

This skill is ready for commercial/non-commercial use. <br>

## Publisher: <br>
[afajohn](https://clawhub.ai/user/afajohn) <br>

### License/Terms of Use: <br>


## Use Case: <br>
Developers, analysts, project managers, and external ClawHub users use this skill for coding assistance, business and project planning, web and data development, free resource discovery, and read-only NAS metadata cataloging. <br>

### Deployment Geography for Use: <br>
Global <br>

## Known Risks and Mitigations: <br>
Risk: The NAS metadata scraper can catalog file names, metadata, and directory structure from network-attached storage. <br>
Mitigation: Require explicit user-selected directories, exclude sensitive shares, keep results local, and provide deletion controls before use. <br>
Risk: The skill asks for vague API-key access through FREE_API_KEYS. <br>
Mitigation: Use separate least-privilege keys for named services only, and avoid providing broad bundled credentials. <br>
Risk: The skill covers a broad assistant surface across coding, analysis, project planning, web development, data work, and resource discovery. <br>
Mitigation: Review generated guidance, code, commands, and configuration before applying them to a project or environment. <br>


## Reference(s): <br>
- [MoltBot Skills Documentation](https://docs.molt.bot/tools/skills) <br>
- [Adaptive Suite ClawHub Listing](https://clawhub.ai/afajohn/adaptive-suite) <br>


## Skill Output: <br>
**Output Type(s):** [text, markdown, code, shell commands, configuration, guidance] <br>
**Output Format:** [Markdown with code snippets, shell commands, and structured guidance] <br>
**Output Parameters:** [1D] <br>
**Other Properties Related to Output:** [May propose local app files, database schemas, and read-only NAS metadata workflows for user review.] <br>

## Skill Version(s): <br>
1.0.0 (source: server release metadata) <br>

## Ethical Considerations: <br>
Users should evaluate whether this skill is appropriate for their environment, review any generated or modified files before relying on them, and apply their organization's safety, security, and compliance requirements before deployment. <br>
