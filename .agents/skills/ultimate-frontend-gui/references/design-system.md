# Design System And Visual Quality

Use this reference when the task is building, redesigning, or polishing a GUI.

## UX Architecture

- Start with purpose, audience, content, and constraints.
- Define information hierarchy before visual style.
- Identify primary task, secondary actions, empty state, loading state, error state, and disabled state.
- Establish component boundaries and reuse existing primitives before creating new ones.
- Use CSS tokens for color, typography, spacing, radius, shadow, z-index, and breakpoints.
- Keep layout mobile-first with stable desktop expansions.

## Layout

- Build with a clear layout skeleton: shell, nav, primary content, secondary panels, modals, drawers, and toolbars.
- For dashboards and operational tools, prioritize dense but readable scanning over oversized marketing composition.
- For landing pages and editorial work, use stronger hierarchy, visual rhythm, and section transitions.
- Avoid card-heavy pages unless the domain is truly item/card based.
- Do not put cards inside cards.
- Use stable sizing for repeated tiles, boards, icon buttons, and fixed-format controls.

## Visual Direction

Choose one direction and execute it consistently:

- quiet utilitarian
- editorial
- cinematic
- luxury/refined
- playful
- brutalist
- retro-futuristic
- organic
- technical/industrial

Do not average several styles together. Use the product domain to choose the direction.

## Anti-Generic Rules

- Avoid default SaaS templates, generic purple gradients, random glassmorphism, and context-free decoration.
- Avoid one-note color palettes dominated by a single hue family.
- Avoid decorative blobs, orbs, bokeh, and background shapes that do not support the content.
- Avoid using hero-scale text inside dense app panels.
- Avoid visible instructional text that explains what the UI is doing unless the user workflow needs it.

## Component Quality

- Use existing component libraries or primitives first.
- Use icons for familiar actions when available.
- Add accessible names to icon-only controls.
- Show validation and errors near the triggering control.
- Provide clear empty states with one next action.
- Ensure text wraps or truncates intentionally.
- Use tabular numbers for counters, prices, metrics, and tables.

## References

- `references/source-references/frontend-design-agency/design-system-rules.md`
- `references/source-references/frontend-design-agency/layout-patterns-library.md`
- `references/source-references/frontend-design-agency/typography-scale-template.md`
- `references/source-references/frontend-design-agency/color-palette-examples.md`
- `references/source-references/ux-architect/css-architecture.md`
- `references/source-references/ux-architect/component-hierarchy.md`
- `references/harvested/frontend-design-agents.md`
- `references/harvested/frontend-design-3.md`
- `references/harvested/awwwards-design.md`
- `references/harvested/superdesign.md`
