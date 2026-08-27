## Description: <br>
Generates local, consent-gated Git-history reflection reports with descriptive commit cadence, change pattern, code style, and quality-artifact statistics. <br>

This skill is ready for commercial/non-commercial use. <br>

## Publisher: <br>
[wscats](https://clawhub.ai/user/wscats) <br>

### License/Terms of Use: <br>
MIT-0 <br>


## Use Case: <br>
Developers use this skill for self-reflection on their own Git history, or for opt-in team retrospectives where every included author has explicitly consented. It summarizes Git-visible activity as discussion prompts, not performance judgments. <br>

### Deployment Geography for Use: <br>
Global <br>

## Known Risks and Mitigations: <br>
Risk: The skill processes identifiable per-author Git activity data. <br>
Mitigation: Run it only for self-reflection or for a team retrospective where every included author has explicitly consented. <br>
Risk: Generated reports could be misused for performance reviews, ranking, compensation, discipline, or surveillance. <br>
Mitigation: Treat outputs as descriptive discussion prompts only and refuse HR, ranking, comparison, or surveillance use cases. <br>
Risk: Reports may contain sensitive work-history data. <br>
Mitigation: Store generated reports carefully and share them only with the consenting participants who need them. <br>


## Reference(s): <br>
- [Metrics Guide](references/metrics-guide.md) <br>
- [ClawHub Release Page](https://clawhub.ai/wscats/code-analysis-skills) <br>
- [Publisher Profile](https://clawhub.ai/user/wscats) <br>


## Skill Output: <br>
**Output Type(s):** [text, markdown, json, html, pdf, guidance] <br>
**Output Format:** [Markdown, JSON, HTML, or PDF report with an explicit usage notice] <br>
**Output Parameters:** [1D] <br>
**Other Properties Related to Output:** [Reports are scoped to the current local Git user by default; multi-author reports require explicit consented author names.] <br>

## Skill Version(s): <br>
1.1.1 (source: server release metadata; artifact pyproject.toml and skill.yaml list 1.1.0) <br>

## Ethical Considerations: <br>
Users should evaluate whether this skill is appropriate for their environment, review any generated or modified files before relying on them, and apply their organization's safety, security, and compliance requirements before deployment. <br>
