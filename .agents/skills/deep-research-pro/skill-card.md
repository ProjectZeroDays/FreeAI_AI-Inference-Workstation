## Description: <br>
Multi-source deep research agent. Searches the web, synthesizes findings, and delivers cited reports. No API keys required. <br>

This skill is ready for commercial/non-commercial use. <br>

## Publisher: <br>
[parags](https://clawhub.ai/user/parags) <br>

### License/Terms of Use: <br>
MIT <br>


## Use Case: <br>
Developers, researchers, and external users use this skill to plan multi-query web and news research, read selected sources, synthesize findings, and produce cited research reports. <br>

### Deployment Geography for Use: <br>
Global <br>

## Known Risks and Mitigations: <br>
Risk: Research queries and selected URLs may be sent to DuckDuckGo and third-party websites. <br>
Mitigation: Avoid sensitive research topics or instruct the agent not to use web access for sensitive work. <br>
Risk: Fetched third-party pages may contain inaccurate, outdated, or misleading information. <br>
Mitigation: Review cited sources, cross-check important claims, and treat single-source claims as unverified. <br>
Risk: The skill can save research reports locally. <br>
Mitigation: Ask the agent not to save files when local persistence is not desired. <br>


## Reference(s): <br>
- [Deep Research Pro on ClawHub](https://clawhub.ai/parags/deep-research-pro) <br>
- [Codex](https://github.com/codex/codex) <br>
- [uv](https://github.com/astral-sh/uv) <br>


## Skill Output: <br>
**Output Type(s):** [text, markdown, shell commands, configuration, guidance] <br>
**Output Format:** [Markdown research reports with citations, optional JSON output, and saved local files] <br>
**Output Parameters:** [1D] <br>
**Other Properties Related to Output:** [May fetch third-party web pages and save reports locally when asked.] <br>

## Skill Version(s): <br>
1.0.2 (source: server release metadata; artifact frontmatter and package.json report 1.0.0) <br>

## Ethical Considerations: <br>
Users should evaluate whether this skill is appropriate for their environment, review any generated or modified files before relying on them, and apply their organization's safety, security, and compliance requirements before deployment. <br>
