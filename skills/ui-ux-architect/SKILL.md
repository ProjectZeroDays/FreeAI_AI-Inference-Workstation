---
name: ui-ux-architect
description: "Expert web design, GUI, UI/UX architect skill. Creates production-quality interfaces with design-system discipline. Triggers: 'design this page', 'UI review', 'make it look better', 'create a dashboard', 'design system', 'wireframe', 'mockup', 'landing page', 'admin panel', 'responsive layout', 'dark mode design', 'accessibility audit', 'component library', 'Figma-to-code', 'design tokens', 'typography scale', 'color palette', 'animation design', 'interaction patterns', 'micro-interactions', 'design system tokens', 'UI component', 'UX review', 'visual hierarchy'. Actions: plan, design, implement, review, fix, optimize, enhance, refactor."
license: MIT
---

# UI/UX Architect — Expert Design Skill

End-to-end design expertise for web, desktop, and mobile interfaces. From concept to production code with design-system rigor.

## When to Activate

- User says "design a page" / "make it look better" / "create a dashboard"
- UI/UX code review requested
- Design system or component library needed
- Figma/design token implementation
- Accessibility audit required
- Dark/light theme system design
- Responsive layout architecture
- Animation and interaction design
- Visual hierarchy and typography setup

---

## The Design Pipeline

```
Brief → Research → Design System → Wireframe → Prototype → Code → Review → Polish
```

### Phase 1: DESIGN BRIEF

Extract these before touching any design tool:

```markdown
## Project Brief
- **Product**: [name/type]
- **Audience**: [who uses it]
- **Primary task**: [what users do first]
- **Mood**: [professional/playful/bold/minimal/enterprise]
- **Constraints**: [tech stack, brand guidelines, accessibility level]
- **Competitors**: [3 references for inspiration]
- **Success metric**: [what makes this design good?]
```

**Ask one question at a time.** Don't start designing until the brief is complete.

---

### Phase 2: DESIGN SYSTEM

Every project gets a design system before components. Define these tokens first:

#### Color Palette

```css
/* Semantic tokens — never hardcode hex in components */
:root {
  /* Primary — brand identity */
  --color-primary: #0EA5E9;        /* sky-500 */
  --color-primary-fg: #FFFFFF;     /* text on primary */
  --color-primary-muted: rgba(14,165,233,0.1);
  --color-primary-strong: rgba(14,165,233,0.3);

  /* Secondary — accents */
  --color-secondary: #8B5CF6;      /* violet-500 */
  --color-accent: #22C55E;         /* green-500 */
  --color-warn: #F59E0B;          /* amber-500 */
  --color-danger: #EF4444;         /* red-500 */

  /* Neutrals — surfaces and text */
  --color-bg: #020617;             /* slate-950 */
  --color-bg-soft: #0F172A;        /* slate-900 */
  --color-panel: #1E293B;          /* slate-800 */
  --color-panel-2: #334155;        /* slate-700 */
  --color-border: rgba(148,163,184,0.15);
  --color-border-strong: rgba(148,163,184,0.3);

  /* Text — hierarchy */
  --color-text: #F1F5F9;           /* slate-100 */
  --color-text-muted: #94A3B8;     /* slate-400 */
  --color-text-quiet: #64748B;     /* slate-500 */

  /* Light mode overrides */
  --color-bg-light: #F8FAFC;       /* slate-50 */
  --color-panel-light: #FFFFFF;
  --color-border-light: rgba(15,23,42,0.1);
}

/* Usage: --color-primary, --color-bg, --color-text-muted */
```

#### Typography Scale

```css
:root {
  --font-sans: 'Inter', system-ui, -apple-system, sans-serif;
  --font-mono: 'JetBrains Mono', 'Fira Code', monospace;

  /* Scale: 1.250 ratio (Major Third) */
  --text-xs: 0.64rem;      /* 10.2px */
  --text-sm: 0.8rem;       /* 12.8px */
  --text-base: 1rem;       /* 16px  */
  --text-lg: 1.25rem;      /* 20px  */
  --text-xl: 1.563rem;     /* 25px  */
  --text-2xl: 1.953rem;    /* 31.25px */
  --text-3xl: 2.441rem;    /* 39px  */
  --text-4xl: 3.052rem;    /* 48.8px */

  --leading-tight: 1.25;
  --leading-normal: 1.5;
  --leading-relaxed: 1.75;

  --font-weight-normal: 400;
  --font-weight-medium: 500;
  --font-weight-semibold: 600;
  --font-weight-bold: 700;
}
```

#### Spacing Scale

```css
:root {
  --space-1: 0.25rem;   /* 4px  */
  --space-2: 0.5rem;    /* 8px  */
  --space-3: 0.75rem;   /* 12px */
  --space-4: 1rem;      /* 16px */
  --space-6: 1.5rem;    /* 24px */
  --space-8: 2rem;      /* 32px */
  --space-12: 3rem;     /* 48px */
  --space-16: 4rem;     /* 64px */
  --space-24: 6rem;     /* 96px */
}
```

#### Border Radius

```css
:root {
  --radius-sm: 6px;
  --radius-md: 10px;
  --radius-lg: 14px;
  --radius-xl: 20px;
  --radius-full: 9999px;
}
```

#### Shadows

```css
:root {
  --shadow-sm: 0 1px 2px rgba(0,0,0,0.3);
  --shadow-md: 0 4px 12px rgba(0,0,0,0.4);
  --shadow-lg: 0 10px 30px rgba(0,0,0,0.5);
  --shadow-glow: 0 0 20px rgba(14,165,233,0.3);
}
```

---

### Phase 3: LAYOUT ARCHITECTURE

#### Sidebar + Main Layout (Dashboard Pattern)

```css
.layout {
  display: grid;
  grid-template-columns: var(--sidebar-width, 260px) 1fr;
  min-height: 100vh;
}

.sidebar {
  position: sticky;
  top: 0;
  width: var(--sidebar-width);
  background: linear-gradient(180deg, rgba(15,23,42,0.96), rgba(11,18,34,0.98));
  border-right: 1px solid var(--border);
  backdrop-filter: blur(10px);
  display: flex;
  flex-direction: column;
}

.sidebar.collapsed {
  width: 48px;
  min-width: 48px;
  padding: 14px 8px;
}

.main {
  padding: 22px 28px 32px;
  overflow-y: auto;
}

/* Collapsed state expansion */
.layout:has(.sidebar.collapsed) {
  grid-template-columns: 48px 1fr;
}
```

#### Card Grid (Bento Pattern)

```css
.bento {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 16px;
}

.card {
  background: linear-gradient(180deg, rgba(255,255,255,0.04), rgba(255,255,255,0.02));
  border: 1px solid var(--border);
  border-radius: var(--radius-lg);
  padding: 20px;
  box-shadow: var(--shadow-md);
  backdrop-filter: blur(8px);
  transition: border-color 0.18s ease;
}

.card:hover {
  border-color: var(--border-strong);
}

.card.span-2 { grid-column: span 2; }
.card.span-row-2 { grid-row: span 2; }
```

---

### Phase 4: COMPONENT LIBRARY

#### Button System

```css
.btn {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 8px 16px;
  border-radius: var(--radius-md);
  border: 1px solid var(--border);
  background: var(--panel-2);
  color: var(--text);
  font-size: var(--text-sm);
  font-weight: 500;
  cursor: pointer;
  transition: all 0.15s ease;
  text-decoration: none;
  white-space: nowrap;
}

.btn:hover {
  border-color: var(--border-strong);
  transform: translateY(-1px);
}

.btn-primary {
  background: linear-gradient(135deg, #0EA5E9, #22C55E);
  border-color: transparent;
  color: #020617;
  font-weight: 700;
}

.btn-danger {
  background: rgba(239,68,68,0.12);
  border-color: rgba(239,68,68,0.3);
  color: #FCA5A5;
}

.btn-sm { padding: 5px 10px; font-size: 12px; }
.btn-lg { padding: 12px 24px; font-size: 15px; }
```

#### Input System

```css
.input {
  background: rgba(2,6,23,0.55);
  color: var(--text);
  border: 1px solid var(--border);
  border-radius: var(--radius-md);
  padding: 8px 12px;
  font-size: var(--text-base);
  font-family: inherit;
  width: 100%;
  transition: border-color 0.15s, box-shadow 0.15s;
}

.input:focus {
  outline: none;
  border-color: rgba(56,189,248,0.45);
  box-shadow: 0 0 0 3px rgba(56,189,248,0.12);
}

.input::placeholder { color: var(--color-text-quiet); }
```

#### Badge/Pill System

```css
.pill {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 3px 10px;
  border-radius: var(--radius-full);
  font-size: 12px;
  font-weight: 600;
}

.pill-success { background: rgba(34,197,94,0.15); color: #4ADE80; }
.pill-warning { background: rgba(245,158,11,0.15); color: #FBBF24; }
.pill-danger  { background: rgba(239,68,68,0.15); color: #F87171; }
.pill-info    { background: rgba(14,165,233,0.15); color: #38BDF8; }
.pill-muted   { background: rgba(100,116,139,0.15); color: #94A3B8; }
```

---

### Phase 5: INTERACTION PATTERNS

#### Loading States

```css
/* Skeleton shimmer */
@keyframes shimmer {
  0% { background-position: -200% 0; }
  100% { background-position: 200% 0; }
}

.skeleton {
  background: linear-gradient(90deg, var(--panel) 25%, var(--panel-2) 50%, var(--panel) 75%);
  background-size: 200% 100%;
  animation: shimmer 1.5s ease-in-out infinite;
  border-radius: var(--radius-md);
}

/* Spinner */
@keyframes spin {
  to { transform: rotate(360deg); }
}

.spinner {
  width: 20px; height: 20px;
  border: 2px solid var(--border);
  border-top-color: var(--accent);
  border-radius: 50%;
  animation: spin 0.6s linear infinite;
}
```

#### Toast Notifications

```css
.toast {
  position: fixed;
  bottom: 24px;
  right: 24px;
  padding: 12px 20px;
  border-radius: var(--radius-md);
  border: 1px solid var(--border);
  background: var(--panel);
  color: var(--text);
  font-size: 14px;
  box-shadow: var(--shadow-lg);
  animation: slideIn 0.25s ease;
  z-index: 1000;
}

@keyframes slideIn {
  from { transform: translateY(20px); opacity: 0; }
  to   { transform: translateY(0);    opacity: 1; }
}

.toast-success { border-color: rgba(34,197,94,0.4); background: rgba(34,197,94,0.1); }
.toast-error   { border-color: rgba(239,68,68,0.4); background: rgba(239,68,68,0.1); }
.toast-info    { border-color: rgba(56,189,248,0.4); background: rgba(56,189,248,0.1); }
```

---

### Phase 6: ACCESSIBILITY CHECKLIST

Every design pass must validate:

| Check | Rule | Test |
|-------|------|------|
| **Color contrast** | 4.5:1 minimum for normal text, 3:1 for large text | Use `contrast-ratio` tool |
| **Focus states** | Visible focus ring on all interactive elements | Tab through with keyboard |
| **Touch targets** | Minimum 44×44px | Measure with dev tools |
| **Alt text** | Descriptive on all `<img>` | Check DOM |
| **ARIA labels** | Icon-only buttons need `aria-label` | Audit with axe |
| **Form labels** | Every `<input>` has associated `<label>` | Check `for` attribute |
| **Keyboard nav** | Full workflow operable without mouse | Tab test |
| **Reduced motion** | Respects `prefers-reduced-motion` | Check CSS media query |
| **Semantic HTML** | `<nav>`, `<main>`, `<header>`, `<section>`, `<article>` | Validate structure |

---

### Phase 7: RESPONSIVE BREAKPOINTS

```css
/* Mobile-first breakpoints */
:root {
  --bp-sm: 640px;   /* phones */
  --bp-md: 768px;   /* tablets */
  --bp-lg: 1024px;  /* small laptops */
  --bp-xl: 1280px;  /* desktops */
  --bp-2xl: 1536px; /* large screens */
}

@media (max-width: 768px) {
  .layout { grid-template-columns: 1fr; }
  .sidebar {
    position: fixed;
    inset: 0;
    z-index: 200;
    transform: translateX(-100%);
    transition: transform 0.2s ease;
  }
  .sidebar.open { transform: translateX(0); }
}

@media (max-width: 1024px) {
  .bento { grid-template-columns: repeat(2, 1fr); }
}

@media (max-width: 640px) {
  .bento { grid-template-columns: 1fr; }
  .main { padding: 16px; }
}
```

---

### Phase 8: ANIMATION PRINCIPLES

```css
/* Duration scale — never arbitrary */
--duration-fast: 150ms;
--duration-normal: 200ms;
--duration-slow: 300ms;

/* Easing curves */
--ease-out: cubic-bezier(0.16, 1, 0.3, 1);   /* smooth deceleration */
--ease-in-out: cubic-bezier(0.45, 0, 0.55, 1); /* balanced */
--ease-spring: cubic-bezier(0.34, 1.56, 0.64, 1); /* bounce */

/* Usage */
transition: all var(--duration-normal) var(--ease-out);
```

**Animation rules:**
- Use `transform` and `opacity` only (GPU-accelerated)
- Never animate `width`, `height`, `top`, `left`
- Respect `prefers-reduced-motion`
- Micro-interactions: 150-200ms
- Page transitions: 300-400ms
- Loading skeletons: infinite shimmer

---

## Design Review Checklist

When reviewing any UI code, check:

```
□ Color tokens used (no hardcoded hex in components)
□ Typography scale consistent (no arbitrary font sizes)
□ Spacing follows scale (no arbitrary margins/padding)
□ Border radius consistent (small/medium/large/full)
□ Focus states visible on all interactive elements
□ Touch targets ≥ 44×44px
□ Dark mode works (or light mode if applicable)
□ Responsive at 320px, 768px, 1024px, 1440px
□ No horizontal scroll at any breakpoint
□ Animations respect prefers-reduced-motion
□ ARIA labels on icon-only buttons
□ Form inputs have visible labels
□ Error states defined and tested
□ Loading states defined
□ Empty states defined
□ Hover states on all interactive elements
□ Z-index scale defined (10, 20, 30, 50, 100, 200, 999)
□ CSS custom properties for all repeatable values
□ No inline styles (extract to classes)
□ Semantic HTML structure
```

---

## Common UI Patterns Reference

### Dashboard Overview

```html
<div class="layout">
  <nav class="sidebar">
    <div class="brand">FreeAI</div>
    <div class="scrollable-nav">
      <div class="nav-section">
        <span class="nav-label">Stack</span>
        <a href="/" class="nav-item active"><span class="nav-dot"></span> Dashboard</a>
        <a href="/gpu" class="nav-item"><span class="nav-dot"></span> GPU</a>
        <a href="/models" class="nav-item"><span class="nav-dot"></span> Models</a>
      </div>
    </div>
    <div class="sidebar-foot">
      <button class="sidebar-toggle" id="sidebar-toggle">◀</button>
      <span class="live-dot"></span>
      <span class="muted">Live</span>
    </div>
  </nav>

  <main class="main">
    <header class="topbar">
      <h1>Dashboard</h1>
      <div class="topbar-actions">
        <button class="theme-toggle" id="theme-toggle">◐</button>
      </div>
    </header>

    <div class="bento">
      <div class="card span-2">
        <h3>GPU Utilization</h3>
        <canvas id="gpu-chart"></canvas>
      </div>
      <div class="card">
        <h3>Active Models</h3>
        <div class="model-list">...</div>
      </div>
      <div class="card">
        <h3>Security Score</h3>
        <div class="metric">94<span class="muted">/100</span></div>
      </div>
    </div>
  </main>
</div>
```

### Form Pattern

```html
<form class="form-grid">
  <div class="form-field">
    <label for="name">Name</label>
    <input type="text" id="name" class="input" required />
    <span class="field-error">Required</span>
  </div>
  <div class="form-field">
    <label for="email">Email</label>
    <input type="email" id="email" class="input" />
  </div>
  <div class="form-field span-2">
    <label for="bio">Bio</label>
    <textarea id="bio" class="input" rows="4"></textarea>
  </div>
  <div class="form-actions">
    <button type="reset" class="btn">Cancel</button>
    <button type="submit" class="btn btn-primary">Save</button>
  </div>
</form>
```

---

## Tech Stack Recommendations

| Project Type | Stack | Rationale |
|-------------|-------|-----------|
| Marketing site | Next.js + Tailwind + shadcn/ui | SEO, performance, component library |
| Dashboard | Vanilla HTML/CSS/JS + Flask | Zero deps, fast load, full control |
| Admin panel | React + MUI / shadcn/ui | Rich component ecosystem |
| Landing page | Single HTML + Tailwind CDN | Fastest delivery, no build step |
| Mobile app | React Native / Flutter | Cross-platform native |
| Desktop GUI | Electron + React / Tauri | Native feel, web tech |

---

## Quick Commands

```bash
# Generate design tokens from Figma
npx @figma/code-connect extract ./design.json --output ./design-tokens/

# Audit accessibility
npx axe-core ./index.html --save ./audit-report.json

# Check color contrast
npx palette-checker --min-ratio 4.5 ./styles.css

# Validate responsive breakpoints
npxResponsive-viewport-check --breakpoints 320,768,1024,1440
```

---

## Anti-Patterns to Avoid

| ❌ Bad | ✅ Good |
|--------|---------|
| Hardcoded `#1a2b3c` in CSS | `var(--color-primary)` |
| `font-size: 13px` everywhere | `var(--text-sm)`, `var(--text-base)` |
| `padding: 17px` | `padding: var(--space-4)` |
| `z-index: 9999` | Defined scale: 10, 20, 30, 50 |
| `position: absolute` without container | Use grid/flex first |
| Inline `style="color: red"` | `.text-danger { color: var(--danger) }` |
| Animation on `width`/`height` | Animation on `transform`/`opacity` |
| No focus states | `:focus-visible` with outline |
| `overflow: hidden` on everything | Define scroll boundaries explicitly |
| Single theme, no dark mode | CSS variables with `body.light` toggle |
