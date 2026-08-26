# Motion And Animation

Use this reference for microinteractions, CSS animation, Motion.dev, scroll effects, cinematic pages, and Flutter UI animation.

## Motion Purpose

Add motion when it:

- gives feedback
- preserves continuity between states
- guides attention
- explains spatial movement
- makes a high-value page feel crafted

Skip motion when it is decorative noise, slows the workflow, or conflicts with accessibility/performance.

## Web Decision Tree

- Simple hover, fade, slide, or enter/exit: CSS transition or keyframes.
- React/Vue shared layout, gestures, interruption, or exit animation: Motion.dev or the project-approved motion library.
- Scroll storytelling, pinned sections, parallax, text reveals, or cinematic product pages: use the Epic Design references.
- Deterministic clip/timeline preview: use CSS animation rules from `css-animations`.

## Rules

- Animate `transform` and `opacity`.
- Avoid layout animation unless the motion library handles it correctly.
- Use `ease-out` for entrances and feedback.
- Use `ease-in-out` for on-screen movement.
- Keep feedback motion short, usually under 200ms.
- Pause loops off-screen.
- Include reduced-motion fallbacks.
- Avoid large animated blurs or backdrop filters.
- Do not apply `will-change` permanently.

## Flutter Decision Tree

- Single property/state change: implicit animation.
- Multiple properties or lifecycle control: explicit animation.
- Shared element between routes: Hero animation.
- Sequential list or reveal effects: staggered animation.
- Natural drag/spring behavior: physics-based animation.

## References

- `references/harvested/web-animation-design.md`
- `references/harvested/motion.md`
- `references/harvested/css-animations.md`
- `references/harvested/epic-design.md`
- `references/harvested/openclaw-flutter-animations.md`
- `references/source-references/motion-docs/quick-start.md`
- `references/source-references/epic-design/motion-system.md`
- `references/source-references/epic-design/text-animations.md`
- `references/source-references/frontend-design-agency/motion-system-guide.md`
