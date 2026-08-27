## Description: <br>
Pexo helps agents create finished multi-shot videos from text, images, URLs, scripts, or audio using Pexo's hosted video generation service and model routing. <br>

This skill is ready for commercial/non-commercial use. <br>

## Publisher: <br>
[rainer-liao](https://clawhub.ai/user/rainer-liao) <br>

### License/Terms of Use: <br>
MIT-0 <br>


## Use Case: <br>
External users and developers use this skill to create product ads, short-form social videos, brand videos, explainers, and revisions through a Pexo project workflow from an agent session. <br>

### Deployment Geography for Use: <br>
Global <br>

## Known Risks and Mitigations: <br>
Risk: The skill forwards user video prompts, uploaded media, and project metadata to a third-party service. <br>
Mitigation: Install only when the user trusts Pexo for that content, and avoid using private, internal, or sensitive URLs or media unless approved. <br>
Risk: The skill requires a live PEXO_API_KEY stored in local configuration. <br>
Mitigation: Restrict permissions on ~/.pexo and ~/.pexo/config, and do not point PEXO_CONFIG at untrusted files. <br>
Risk: The skill can consume account credits while creating or revising videos. <br>
Mitigation: Review credit balance and purchase requirements before submitting production requests or retries. <br>


## Reference(s): <br>
- [Pexo homepage](https://pexo.ai) <br>
- [ClawHub skill page](https://clawhub.ai/rainer-liao/pexoai-agent) <br>
- [Setup Checklist](references/SETUP-CHECKLIST.md) <br>
- [Troubleshooting](references/TROUBLESHOOTING.md) <br>


## Skill Output: <br>
**Output Type(s):** [Guidance, Shell commands, API Calls, Markdown, Files] <br>
**Output Format:** [Markdown with inline shell commands, JSON command results, project links, media URLs, and downloaded video files] <br>
**Output Parameters:** [1D] <br>
**Other Properties Related to Output:** [May relay prompts, uploaded media, project metadata, and revision choices to the Pexo service; final video URLs may include signed query parameters.] <br>

## Skill Version(s): <br>
0.3.12 (source: server release evidence) <br>

## Ethical Considerations: <br>
Users should evaluate whether this skill is appropriate for their environment, review any generated or modified files before relying on them, and apply their organization's safety, security, and compliance requirements before deployment. <br>
