# Physics, 3D, Canvas, And Advanced Visual Assets

Use this reference when GUI work needs physics animation, canvas, WebGL, Three.js, 3D previews, procedural assets, animated model/video output, or advanced visual simulation.

## Rendering Path

| Requirement | Recommended path |
| --- | --- |
| 2D diagram, precise paths, fields, trajectories | HTML Canvas or SVG |
| Rich 3D interactive scene | Three.js |
| Native game engine target | Keep `game-developer` active and consult Unity/Unreal references |
| 3D video or motion graphic output | Blender headless runner |
| AI-generated 3D model motion/video | AI animation 3D model reference |
| Cohesive game-style assets | Game Cog reference |

## Physics Animation Workflow

For physics-driven GUI or explanatory animations:

1. Identify objects, constraints, fields, forces, and coordinate system.
2. Decide whether direct formula, fixed-timestep simulation, or keyframed approximation is correct.
3. Build a vector/static frame first.
4. Add motion second.
5. Verify positions, timing, scale, and phase transitions against the physical model.

Use direct formulas for projectiles and known trajectories. Use fixed timestep for collision/forces. Use keyframes only when the goal is illustrative rather than physically exact.

## Three.js Quality Baseline

- Set pixel ratio with an upper bound.
- Use physically plausible lighting and tone mapping.
- Add shadows only where they improve depth.
- Use post-processing intentionally: FXAA/SMAA, SSAO, bloom, color grading.
- Keep DOM HUD overlays separate from the render canvas.
- Verify canvas is nonblank and framed correctly in desktop and mobile viewports.
- Avoid heavy effects that destroy interaction latency.

## Procedural And Asset Work

- Build procedural models from stable primitives when assets are unavailable.
- Use cohesive material palettes and consistent lighting.
- Use PBR or flat-shaded style intentionally, not randomly.
- For generated assets, keep a mapping from reference image or brief to the produced model/texture/UI element.
- Preserve asset provenance and output paths in the final report.

## Blender And 3D Video

The harvested Blender runner is in `scripts/blender-animation/run_blender.sh`.

Use Blender when the output should be rendered video, not an interactive GUI. Generate a bounded Blender Python script, render headlessly, and report the script path, output path, and logs.

## AI 3D Animation And Game Asset Generation

Use the harvested `ai-animation-3d-model` and `game-cog` material as references when a GUI needs:

- animated 3D model clips
- character-consistent UI/game assets
- tilesets, icon sets, sprites, 3D models, music, or prototype asset packs
- generated game-world visual direction that should remain cohesive

## References

- `references/advanced-harvested/physics-animation-workflow.md`
- `references/advanced-harvested/blender-animation.md`
- `references/advanced-harvested/ai-animation-3d-model.md`
- `references/advanced-harvested/game-cog.md`
- `references/source-references/build-game/engine-patterns.md`
- `references/source-references/build-game/graphics-quality.md`
- `references/source-references/build-game/procedural-assets.md`
- `scripts/blender-animation/run_blender.sh`
