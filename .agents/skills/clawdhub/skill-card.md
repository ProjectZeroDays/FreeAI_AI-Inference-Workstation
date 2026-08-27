## Description: <br>
Use the ClawdHub CLI to search, install, update, and publish agent skills from clawdhub.com. <br>

This skill is ready for commercial/non-commercial use. <br>

## Publisher: <br>
[steipete](https://clawhub.ai/user/steipete) <br>

### License/Terms of Use: <br>


## Use Case: <br>
Developers and agent operators use this skill to guide agents through ClawdHub CLI workflows for discovering, installing, updating, listing, authenticating, and publishing skills. <br>

### Deployment Geography for Use: <br>
Global <br>

## Known Risks and Mitigations: <br>
Risk: Install, update, force, and no-input commands can modify local skill folders or overwrite existing skill content. <br>
Mitigation: Require explicit user approval before running install, update --all, --force, or --no-input commands, and verify the package, registry, and target directory first. <br>
Risk: Login and publish commands can affect account state or publish local files to the registry. <br>
Mitigation: Require explicit user approval before login or publish commands, and review the files, slug, version, changelog, and target registry before publishing. <br>


## Reference(s): <br>
- [Clawdhub skill page](https://clawhub.ai/steipete/clawdhub) <br>
- [ClawdHub registry](https://clawdhub.com) <br>


## Skill Output: <br>
**Output Type(s):** [Shell commands, Configuration instructions, Guidance] <br>
**Output Format:** [Markdown with inline bash code blocks] <br>
**Output Parameters:** [1D] <br>
**Other Properties Related to Output:** [Requires the clawdhub CLI binary; command execution should be explicitly approved by the user.] <br>

## Skill Version(s): <br>
1.0.0 (source: server release evidence) <br>

## Ethical Considerations: <br>
Users should evaluate whether this skill is appropriate for their environment, review any generated or modified files before relying on them, and apply their organization's safety, security, and compliance requirements before deployment. <br>
