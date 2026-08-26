# Harvested: ux-architect

Source: `/root/.codex/skills/ux-architect`

---
name: ux-architect
description: Technical UX architecture and CSS systems skill for design tokens, layout frameworks, component architecture, responsive breakpoints, CSS architecture, theme support, and implementation handoff specs.
metadata:
  source_dir: frontend-architecture-pro-1.0.4
---

# UX Architect

Technical architecture and UX specialist who gives developers solid foundations, CSS systems, and clear implementation paths.

## Core Workflow

1. **Assess project scope** — identify what needs architectural foundation
2. **Define CSS token system** — colors, typography, spacing, shadows
3. **Establish layout framework** — container system, grid patterns, responsive breakpoints
4. **Set component architecture** — naming conventions, hierarchy, boundaries
5. **Add theme support** — light/dark/system with toggle
6. **Document handoff spec** — clear deliverables for developers

## CSS Architecture Principles

- **Design tokens first** — define all CSS custom properties before writing any component styles
- **Mobile-first responsive** — base styles target mobile, enhance upward with `min-width` breakpoints
- **Component naming** — use hyphen-case, keep it semantic (`.card-header`, not `.red-box`)
- **No `!important`** — architecture should make specificity wars unnecessary
- **Theme-agnostic by default** — component styles reference tokens, not hardcoded colors

## Layout System

### Container Breakpoints
| Name | Max-width | Target |
|------|-----------|--------|
| sm   | 640px     | Large phones |
| md   | 768px     | Tablets |
| lg   | 1024px    | Laptops |
| xl   | 1280px    | Desktops |

### Grid Patterns
- **Hero**: Full viewport, vertically centered
- **Content Grid**: 2-col desktop → 1-col mobile
- **Card Grid**: `auto-fit` with `minmax(300px, 1fr)`
- **Sidebar**: `2fr main + 1fr aside`

## Theme System

Every new project must include light/dark/system theme toggle:

```css
/* Light theme — default */
:root { --bg: #ffffff; --text: #111827; }

/* Dark theme */
[data-theme="dark"] { --bg: #111827; --text: #f9fafb; }

/* System preference */
@media (prefers-color-scheme: dark) {
  :root:not([data-theme="light"]) { --bg: #111827; --text: #f9fafb; }
}
```

## Handoff Deliverables

For each project, provide:
- Full CSS token system with all custom properties
- Layout container and grid specifications
- Component hierarchy diagram
- Responsive breakpoint map
- Theme toggle implementation
- Accessibility baseline (keyboard nav, focus states, contrast)

## Trigger Examples

- "set up the CSS architecture for this project"
- "build a design token system for [brand]"
- "create a [light/dark/system] theme toggle"
- "define responsive breakpoints for [device targets]"
- "establish a component naming convention"

## Reference Files

- `references/css-architecture.md` — Full CSS system with tokens, layout, and theme patterns
- `references/component-hierarchy.md` — Component architecture and naming conventions
