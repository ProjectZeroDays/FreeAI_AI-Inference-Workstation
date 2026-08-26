## Description: <br>
Generate AI music using ACE-Step 1.5 via ACE Music's hosted API, with support for lyrics, style prompts, covers, repainting, and instrumental or vocal tracks. <br>

This skill is ready for commercial/non-commercial use. <br>

## Publisher: <br>
[fspecii](https://clawhub.ai/user/fspecii) <br>

### License/Terms of Use: <br>


## Use Case: <br>
External users and developers use this skill to generate songs, beats, instrumentals, covers, and audio edits from prompts, lyrics, and music parameters through ACE Music's hosted API. <br>

### Deployment Geography for Use: <br>
Global <br>

## Known Risks and Mitigations: <br>
Risk: The helper script handles output paths and request parameters unsafely enough to require review before installation. <br>
Mitigation: Review and fix the helper script before running it; write generated files only to a dedicated safe directory using simple filenames. <br>
Risk: The skill uses an ACE Music API key and may submit prompts, lyrics, or audio to a third-party hosted API. <br>
Mitigation: Use a dedicated API key, keep it out of shared files and source control, and avoid submitting confidential lyrics or audio. <br>


## Reference(s): <br>
- [ACE-Step OpenRouter API Reference](references/api-docs.md) <br>
- [ACE Music API key page](https://acemusic.ai/playground/api-key) <br>
- [ClawHub skill page](https://clawhub.ai/fspecii/ace-music) <br>


## Skill Output: <br>
**Output Type(s):** [guidance, shell commands, configuration, files] <br>
**Output Format:** [Markdown guidance with bash commands and generated audio file paths] <br>
**Output Parameters:** [1D] <br>
**Other Properties Related to Output:** [Requires ACE_MUSIC_API_KEY; generated audio is saved as MP3 files by the helper script.] <br>

## Skill Version(s): <br>
1.0.0 (source: server release evidence) <br>

## Ethical Considerations: <br>
Users should evaluate whether this skill is appropriate for their environment, review any generated or modified files before relying on them, and apply their organization's safety, security, and compliance requirements before deployment. <br>
