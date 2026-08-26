## Description: <br>
Generate and iteratively develop polished 3D browser games from natural language. <br>

This skill is ready for commercial/non-commercial use. <br>

## Publisher: <br>
[KeWang0622](https://clawhub.ai/user/KeWang0622) <br>

### License/Terms of Use: <br>
MIT-0 <br>


## Use Case: <br>
Developers, creators, and external users use this skill to generate or iterate playable Three.js browser games from natural-language game concepts. It produces a single HTML game, local serving guidance, and a shareable public URL when publishing is available. <br>

### Deployment Geography for Use: <br>
Global <br>

## Known Risks and Mitigations: <br>
Risk: Generated game folders may be uploaded to a public here.now URL by default. <br>
Mitigation: Review generated files before publishing and remove private photos, secrets, proprietary text, sensitive prompts, progress.md content, or embedded assets that should not be public. <br>
Risk: Generated games can embed user-provided image assets and persistent progress notes. <br>
Mitigation: Use non-sensitive source assets and inspect embedded data and progress records before sharing the game or public URL. <br>


## Reference(s): <br>
- [3D Game Builder on ClawHub](https://clawhub.ai/KeWang0622/build-game) <br>
- [Three.js Engine Patterns by Game Type](reference/engine-patterns.md) <br>
- [Procedural Asset Recipes](reference/procedural-assets.md) <br>
- [Procedural Audio Recipes (Web Audio API)](reference/audio-patterns.md) <br>
- [Complex Game Systems Reference](reference/game-systems.md) <br>
- [Advanced 3D Graphics Quality Patterns](reference/graphics-quality.md) <br>
- [GUI / HUD Design Patterns](reference/gui-patterns.md) <br>
- [Three.js module CDN](https://cdn.jsdelivr.net/npm/three@0.160.0/build/three.module.js) <br>
- [Three.js addons CDN](https://cdn.jsdelivr.net/npm/three@0.160.0/examples/jsm/) <br>


## Skill Output: <br>
**Output Type(s):** [code, markdown, shell commands, configuration, guidance] <br>
**Output Format:** [Single-file HTML game plus Markdown progress notes and shell commands] <br>
**Output Parameters:** [1D] <br>
**Other Properties Related to Output:** [Generated games are written under /tmp/game-build and may be served locally or published to here.now.] <br>

## Skill Version(s): <br>
1.2.0 (source: server release evidence) <br>

## Ethical Considerations: <br>
Users should evaluate whether this skill is appropriate for their environment, review any generated or modified files before relying on them, and apply their organization's safety, security, and compliance requirements before deployment. <br>
