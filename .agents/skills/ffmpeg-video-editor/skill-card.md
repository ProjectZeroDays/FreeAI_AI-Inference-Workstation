## Description: <br>
Generate FFmpeg commands from natural language video editing requests - cut, trim, convert, compress, change aspect ratio, extract audio, and more. <br>

This skill is ready for commercial/non-commercial use. <br>

## Publisher: <br>
[MahmoudAdelbghany](https://clawhub.ai/user/MahmoudAdelbghany) <br>

### License/Terms of Use: <br>


## Use Case: <br>
Developers, creators, and video editors use this skill to turn natural-language editing requests into FFmpeg commands for trimming, converting, resizing, compressing, extracting audio, and related video operations. <br>

### Deployment Geography for Use: <br>
Global <br>

## Known Risks and Mitigations: <br>
Risk: Generated FFmpeg commands include `-y`, which can overwrite existing output files by default. <br>
Mitigation: Verify input and output filenames before running commands, and remove `-y` when existing files should be preserved. <br>
Risk: The skill assumes FFmpeg is available and does not install or verify the FFmpeg binary. <br>
Mitigation: Install FFmpeg from a trusted source before running generated commands. <br>


## Reference(s): <br>
- [ClawHub skill page](https://clawhub.ai/MahmoudAdelbghany/ffmpeg-video-editor) <br>


## Skill Output: <br>
**Output Type(s):** [Text, Markdown, Shell commands, Guidance] <br>
**Output Format:** [Markdown with inline bash code blocks] <br>
**Output Parameters:** [1D] <br>
**Other Properties Related to Output:** [Commands commonly include overwrite and cleaner-output flags; review filenames before execution.] <br>

## Skill Version(s): <br>
1.0.0 (source: server release metadata) <br>

## Ethical Considerations: <br>
Users should evaluate whether this skill is appropriate for their environment, review any generated or modified files before relying on them, and apply their organization's safety, security, and compliance requirements before deployment. <br>
