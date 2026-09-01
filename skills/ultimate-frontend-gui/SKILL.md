---
name: ultimate-frontend-gui
description: Use when Codex is building, modifying, debugging, reviewing, testing, or polishing GUI and frontend interfaces, including advanced web apps, dashboards, landing pages, UI components, accessibility, responsive layout, visual design, motion, desktop/live visual control, game-grade real-time interfaces, Three.js/canvas/WebGL, physics/3D systems, frontend performance, browser verification, and diagnostics.
metadata:
  short-description: Unified GUI and frontend engineering skill
  harvested_from:
    - accessibility
    - awwwards-design
    - css-animations
    - epic-design
    - frontend-design
    - frontend-design-3
    - frontend-design-agency
    - frontend-design-pro
    - frontend-doctor
    - frontend-performance
    - frontend-testing
    - motion
    - openclaw-flutter-animations
    - superdesign
    - ui-skills
    - ultimate-frontend
    - ux-architect
    - web-animation-design
    - desktop-control
    - build-game
    - game-architect
    - game-developer
    - game-designer-toolkit
    - game-ai
    - game-cog
    - blender-animation
    - ai-animation-3d-model
    - physics-animation-workflow
    - fullstack-developer
    - agent-team-orchestration
---

# Ultimate Frontend GUI

Use this as the single active skill for serious GUI and frontend work. It consolidates the best harvested guidance from frontend design, accessibility, motion, diagnostics, performance, desktop control, game engineering, real-time systems, physics animation, 3D rendering, and visual verification skills.

## Load Only What You Need

- Coverage and archive decisions: `references/coverage-map.md`
- Design systems, layout, visual quality: `references/design-system.md`
- Accessibility baseline and audits: `references/accessibility.md`
- Motion, animation, scroll, Flutter motion: `references/motion-animation.md`
- Debugging, performance, tests, browser verification: `references/diagnostics-performance-testing.md`
- Live visual control and desktop automation: `references/live-visual-control.md`
- Game-grade GUI systems and real-time interaction: `references/game-grade-gui-systems.md`
- Physics, 3D, canvas, WebGL, and advanced visual assets: `references/physics-3d-canvas.md`
- Full harvested source bodies: `references/harvested/`
- Advanced harvested source bodies: `references/advanced-harvested/`
- Detailed source references: `references/source-references/`
- Diagnostic scripts: `scripts/frontend-doctor/`
- Desktop control scripts and guides: `scripts/desktop-control/`
- Browser game serve helper: `scripts/build-game/`
- Blender headless runner: `scripts/blender-animation/`
- Cinematic asset/layer scripts: `scripts/epic-design/`

Read the relevant reference file when the task needs depth. Do not load every harvested file by default.

## Trigger Scope

Use for:

- Building or redesigning web pages, app shells, dashboards, forms, tables, panels, tools, and UI components
- Modifying existing GUI behavior or appearance
- Making frontend work look production-ready, distinctive, and coherent
- Frontend accessibility, focus, keyboard support, ARIA, contrast, and responsive layout
- Motion, animation, scrollytelling, transitions, microinteractions, and Flutter UI animation
- Game-grade interfaces: real-time dashboards, spatial tools, editor canvases, command surfaces, HUD-like overlays, simulation views, rich data maps, and complex state machines
- Desktop or live visual control for inspecting, interacting with, and verifying running GUIs
- Canvas, WebGL, Three.js, 3D scenes, physics-driven animation, procedural visuals, and advanced asset pipelines
- Frontend debugging: blank screens, hydration failures, layout bugs, resource loading, extension popups
- Frontend performance and Core Web Vitals
- Frontend tests, component tests, E2E smoke coverage, and browser screenshot verification

Skip this skill for non-UI backend work, pure game mechanics, generic browser automation, unrelated testing, or non-frontend architecture.

## Priority Rules

When source skills conflict, apply this hierarchy:

1. User request and local repo instructions
2. Existing product flow, framework, design system, and component primitives
3. Correctness, accessibility, and keyboard usability
4. Responsive layout and text containment
5. Performance and maintainability
6. Direct visual verification of what actually rendered
7. Distinctive visual polish
8. Game-grade, cinematic, physics, or high-motion effects

Preserve the current app flow unless the user asks for redesign. Use existing components, tokens, helpers, and icon libraries before adding new systems.

## Core Workflow

1. Inspect local context first: package files, framework, route/component structure, styles, design system, assets, and existing UI conventions.
2. Determine mode: build, modify, debug, audit, performance, test, animation, accessibility, or visual polish.
3. Clarify only true blockers. If the brief is usable, infer sensible defaults and proceed.
4. Define the UX architecture: information hierarchy, layout regions, responsive behavior, component boundaries, token needs, and states.
5. Choose one visual direction that fits the product. Do not average unrelated styles together.
6. Implement working code using the repo's established stack and patterns.
7. For complex UIs, decide whether the interface needs a normal app model, a canvas/WebGL render loop, a game-style mode/state manager, or a hybrid.
8. Verify behavior in a browser, desktop session, screenshot harness, or relevant test harness when the UI can run locally.
9. Report what changed, what was verified, and any remaining risk.

## Design And UX Rules

- Build the actual usable experience first, not a marketing explanation of the feature.
- Match the UI to its domain. Operational software should be dense, calm, and scannable; expressive sites can be more cinematic.
- Avoid generic AI UI: default SaaS layouts, timid color, stock-like gradients, repetitive cards, and context-free decoration.
- Use a real hierarchy: primary task, secondary actions, data states, errors, empty states, loading, and disabled states.
- Use stable dimensions for grids, controls, boards, toolbars, counters, icon buttons, and fixed-format components.
- Keep cards for repeated items, modals, and genuinely framed tools. Do not nest cards inside cards.
- Make text fit every container on mobile and desktop. Do not let button labels, headings, or long words overflow.
- Do not use decorative orbs, bokeh blobs, or generic gradient backgrounds.
- Avoid one-note palettes and overused purple or purple-blue gradient themes.
- Use icons for familiar tool actions when available, with accessible names or tooltips.

## Advanced GUI Systems

Treat complex software GUIs as interactive systems, not static screens. Use game engineering patterns when the interface has real-time state, direct manipulation, spatial navigation, canvas/WebGL rendering, simulation, timelines, large visual scenes, or heavy input feedback.

- Use render loops only when the UI has continuously changing visuals; otherwise keep normal reactive UI flow.
- Separate model/state, input commands, simulation/update, render/presentation, and effects.
- Use finite state machines for modes such as browse, edit, preview, inspect, drag, select, playback, pause, and error.
- Use command queues for reversible actions, macro operations, guided workflows, and multi-step interactions.
- Use spatial structures, object pooling, and culling for large canvas/WebGL scenes.
- Keep HUD overlays, tool palettes, and inspector panels readable, responsive, and non-blocking.
- For game-grade work, read `references/game-grade-gui-systems.md`.
- For physics, 3D, canvas, WebGL, procedural assets, or Blender/video output, read `references/physics-3d-canvas.md`.

## Accessibility Baseline

Every GUI change must preserve or improve:

- Semantic HTML and correct roles
- Keyboard navigation and visible focus states
- `aria-label` or visible text for icon-only controls
- Form labels, validation messages, and error placement near the action
- Contrast at WCAG 2.1 AA level for normal text and controls
- Reduced motion handling for non-essential animation
- Live regions for async status only when users need them

For deeper audits, read `references/accessibility.md` and the harvested `accessibility.md`.

## Motion Rules

- Add motion only when it communicates hierarchy, continuity, feedback, or state change.
- Prefer compositor properties: `transform` and `opacity`.
- Avoid animating layout properties such as `width`, `height`, `top`, `left`, `margin`, and `padding`.
- Use CSS for simple transitions, Motion.dev or project-approved motion libraries for React/Vue gestures, shared layout, and exit animation.
- Keep interaction feedback fast, usually under 200ms.
- Respect `prefers-reduced-motion` for all non-essential motion.
- For cinematic scroll or 2.5D effects, inspect assets first and use `scripts/epic-design/` when applicable.

For detailed choices, read `references/motion-animation.md`.

## Debug, Performance, And Test Discipline

When fixing frontend bugs, reproduce the symptom first if possible. Capture the actual console, network, DOM, screenshot, or test failure evidence before patching.

Use this order:

1. Reproduce locally with the app's normal dev server or build path.
2. Inspect console exceptions, failed resources, hydration warnings, route fallback behavior, and layout overflow.
3. Isolate the root cause in the smallest relevant code path.
4. Patch the app's real flow.
5. Re-run the same reproduction plus focused tests or browser smoke checks.

For performance, measure before prescribing. Use Lighthouse, bundle analyzers, browser Performance traces, or framework build output when available.

For tests, prefer user-visible assertions: roles, labels, text, behavior, and critical journeys. Use stable selectors only when semantic selectors are insufficient.

Read `references/diagnostics-performance-testing.md` for deeper procedures.

## Live Visual Control

When a GUI can run locally, visual truth beats static inspection. Use browser automation first for web apps, and use desktop control when the task needs OS-level window activation, mouse/keyboard interaction, native app behavior, or screenshots outside the browser harness.

Use an observe-act-verify loop:

1. Observe with screenshot, DOM, console, network, pixel, or window-state evidence.
2. Decide the smallest useful action.
3. Act with browser automation, keyboard, mouse, hotkeys, or scripted control.
4. Verify with a new screenshot or state check.
5. Stop if the result diverges and re-plan from evidence.

For desktop control details, read `references/live-visual-control.md` and `scripts/desktop-control/QUICK_REFERENCE.md`.

## Verification Expectations

For runnable frontend apps:

- Start the dev server or static server when needed.
- Check at least one desktop and one mobile viewport for substantial UI changes.
- Use Playwright, browser automation, screenshots, or existing test tools when available.
- For desktop/native windows, capture before/after screenshots and use guarded mouse/keyboard automation only when needed.
- Confirm that assets render, text does not overlap, controls are reachable, and primary interactions work.
- For canvas, WebGL, or 3D UI, verify nonblank pixels, correct framing, movement/interactivity, and stable performance.

Do not claim a GUI is complete or fixed without concrete verification output unless the environment blocks running it.
