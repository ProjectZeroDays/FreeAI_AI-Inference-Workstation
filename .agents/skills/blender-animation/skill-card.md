## Description: <br>
Generate and render 3D animations using Blender headless mode, including scene setup, object and camera animation, lighting, and MP4 output. <br>

This skill is ready for commercial/non-commercial use. <br>

## Publisher: <br>
[vignesh8164](https://clawhub.ai/user/vignesh8164) <br>

### License/Terms of Use: <br>
MIT-0 <br>


## Use Case: <br>
Developers and agent operators use this skill to generate Blender Python scenes, run Blender in headless mode, and collect rendered MP4 output plus execution logs. <br>

### Deployment Geography for Use: <br>
Global <br>

## Known Risks and Mitigations: <br>
Risk: Generated Blender Python runs locally and may be unsafe in sensitive or high-privilege environments. <br>
Mitigation: Use a sandbox or low-privilege environment for untrusted prompts and review generated scripts before rendering sensitive projects. <br>
Risk: The skill depends on the local Blender executable used for headless rendering. <br>
Mitigation: Ensure the Blender executable on PATH is from a trusted source before running the generated script. <br>
Risk: Rendering animations can consume significant local CPU, GPU, memory, or disk resources. <br>
Mitigation: Keep renders within the skill's stated constraints, including short animation duration and output limited to /tmp. <br>


## Reference(s): <br>
- [ClawHub skill page](https://clawhub.ai/vignesh8164/blender-animation) <br>


## Skill Output: <br>
**Output Type(s):** [text, code, shell commands, files] <br>
**Output Format:** [Markdown with Blender Python code, shell command guidance, output file path, and logs] <br>
**Output Parameters:** [1D] <br>
**Other Properties Related to Output:** [Runs a generated Blender Python script with Blender headless mode and writes rendered video output to /tmp/output.mp4.] <br>

## Skill Version(s): <br>
1.0.1 (source: server release metadata and SKILL.md Version; skill.json lists 1.0.0) <br>

## Ethical Considerations: <br>
Users should evaluate whether this skill is appropriate for their environment, review any generated or modified files before relying on them, and apply their organization's safety, security, and compliance requirements before deployment. <br>
