# Game-Grade GUI Systems

Use this reference when a GUI needs the complexity budget normally used in games: real-time updates, modes, spatial interaction, simulation, canvas/WebGL, dense HUDs, editors, timelines, or highly interactive tools.

## When To Use Game Patterns In Software UI

Use game-grade patterns for:

- visual editors, node graphs, timelines, canvases, maps, simulation views, dashboards with live state
- drag/drop surfaces, spatial selection, zoom/pan, camera controls, command palettes, inspectors
- complex mode systems such as select, edit, preview, playback, annotate, compare, inspect
- high-frequency feedback where static component state is too weak

Do not force a render loop onto normal forms, settings pages, static dashboards, or content sites.

## Core Architecture

Separate these layers:

- State model: canonical data and derived state
- Input: keyboard, mouse, touch, pointer lock, gamepad, gestures
- Command layer: reversible actions, macros, history, undo/redo
- Update/simulation: time-based changes, physics, polling, async operations
- Presentation: DOM, canvas, WebGL, SVG, overlays
- Effects: animation, sound, particles, transient feedback
- Verification: screenshot, pixel, DOM, and interaction checks

## Modes And State Machines

Use finite state machines for interaction modes. Examples:

- `idle -> selecting -> dragging -> committing -> idle`
- `view -> edit -> preview -> publish`
- `loading -> ready -> paused -> error`

Use stack state when overlays can temporarily suspend an underlying mode: modal, command palette, pause overlay, tooltip inspection, context menu.

## Time And Flow

- Use frame update loops for visuals and interaction feel.
- Use fixed timestep only for deterministic physics or simulation.
- Use command queues for multi-step workflows and animation sequences.
- Use timers sparingly; prefer requestAnimationFrame or explicit state transitions.
- Keep async loading non-blocking and show progress mapped to real load steps.

## Spatial And Real-Time Systems

For large visual surfaces:

- Use spatial hashing, grid indexing, quadtrees, octrees, or BVH-style culling for large object sets.
- Use object pooling for frequent particles, markers, handles, cards, toasts, bullets, or transient UI objects.
- Use level of detail and visibility culling for huge canvases or WebGL scenes.
- Cache expensive measurements and avoid allocations inside render/update loops.

## HUD And Overlay Rules

- HUD containers should not block pointer events unless a child is interactive.
- Use tabular numbers for live metrics.
- Animate value changes smoothly, but keep them readable.
- Layer information: persistent critical state, contextual secondary state, optional details on focus/hover.
- Keep overlays stable at mobile and desktop sizes.

## Advanced GUI Examples

- Data observability dashboard with live charts: model + update loop + command filters + stable HUD metrics.
- Node editor: spatial index + selection FSM + command history + zoom/pan camera + minimap.
- 3D product configurator: Three.js scene + DOM inspector + material/state model + screenshot verification.
- Timeline editor: command queue + keyframe interpolation + drag state machine + viewport culling.

## References

- `references/source-references/game-architect/system-ui.md`
- `references/source-references/game-architect/system-time.md`
- `references/source-references/game-architect/system-scene.md`
- `references/source-references/game-architect/algorithm.md`
- `references/source-references/build-game/gui-patterns.md`
- `references/source-references/build-game/game-systems.md`
- `references/source-references/game-developer/ecs-patterns.md`
- `references/source-references/game-developer/performance-optimization.md`
- `references/advanced-harvested/game-ai.md`
- `references/advanced-harvested/game-architect.md`
- `references/advanced-harvested/game-developer.md`
