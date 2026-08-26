## Description: <br>
Animates OBJ, FBX, GLB, and GLTF 3D model files into 1080p MP4 video clips using a cloud GPU animation service. <br>

This skill is ready for commercial/non-commercial use. <br>

## Publisher: <br>
[linmillsd7](https://clawhub.ai/user/linmillsd7) <br>

### License/Terms of Use: <br>
MIT-0 <br>


## Use Case: <br>
External users, 3D artists, and game developers use this skill to upload 3D model assets, describe desired motion, and receive rendered animation video files without manual keyframing. <br>

### Deployment Geography for Use: <br>
Global <br>

## Known Risks and Mitigations: <br>
Risk: The skill sends 3D assets, prompts, URLs, and render metadata to a third-party cloud service. <br>
Mitigation: Use it only with assets approved for that service, and review the provider's privacy and retention terms before uploading confidential models. <br>
Risk: URL uploads and broad request routing can cause the service to process external resources selected by the user or agent. <br>
Mitigation: Prefer explicit file uploads or trusted URLs, and confirm the intended animation or export request before submitting work to the service. <br>


## Reference(s): <br>
- [ClawHub skill page](https://clawhub.ai/linmillsd7/ai-animation-3d-model) <br>
- [NemoVideo API base](https://mega-api-prod.nemovideo.ai) <br>


## Skill Output: <br>
**Output Type(s):** [Text, Files, API Calls, Guidance] <br>
**Output Format:** [Plain text progress updates and downloaded video files, typically 1080p MP4] <br>
**Output Parameters:** [1D] <br>
**Other Properties Related to Output:** [Requires NEMO_TOKEN or an anonymous cloud-service token; supports 3D model uploads up to 500MB.] <br>

## Skill Version(s): <br>
1.0.0 (source: SKILL.md frontmatter and server release metadata) <br>

## Ethical Considerations: <br>
Users should evaluate whether this skill is appropriate for their environment, review any generated or modified files before relying on them, and apply their organization's safety, security, and compliance requirements before deployment. <br>
