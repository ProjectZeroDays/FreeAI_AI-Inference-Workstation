---
name: frontend-design
description: Frontend UI/UX patterns, responsive design, component architecture, CSS strategies, accessibility, and design systems. Use when the user asks about UI components, responsive layouts, CSS patterns, design systems, accessibility (WCAG), or frontend architecture.
---

# Frontend Design

## Responsive Breakpoints

```css
/* Mobile-first approach */
/* sm: 640px, md: 768px, lg: 1024px, xl: 1280px, 2xl: 1536px */

.container {
  width: 100%;
  padding: 1rem;
}

@media (min-width: 640px) {
  .container { max-width: 640px; margin: 0 auto; }
}

@media (min-width: 1024px) {
  .container { max-width: 1024px; }
}
```

## CSS Grid Patterns

```css
/* Holy Grail Layout */
.layout {
  display: grid;
  grid-template-areas:
    "header header header"
    "nav main aside"
    "footer footer footer";
  grid-template-columns: 200px 1fr 200px;
  grid-template-rows: auto 1fr auto;
  min-height: 100vh;
}

/* Auto-fill responsive grid */
.grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
  gap: 1rem;
}

/* Named areas */
.header { grid-area: header; }
.nav { grid-area: nav; }
.main { grid-area: main; }
.aside { grid-area: aside; }
.footer { grid-area: footer; }
```

## Flexbox Patterns

```css
/* Center anything */
.center {
  display: flex;
  align-items: center;
  justify-content: center;
}

/* Space between */
.spread {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

/* Wrap with gap */
.wrap {
  display: flex;
  flex-wrap: wrap;
  gap: 1rem;
}

/* Sticky footer */
.page {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
}
.page-content { flex: 1; }
```

## Component Patterns

### Button Variants
```css
.btn {
  padding: 0.5rem 1rem;
  border-radius: 0.375rem;
  font-weight: 500;
  transition: all 0.15s ease;
}

.btn-primary {
  background: #3b82f6;
  color: white;
}
.btn-primary:hover { background: #2563eb; }

.btn-secondary {
  background: transparent;
  border: 1px solid #d1d5db;
  color: #374151;
}

.btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}
```

### Card Component
```css
.card {
  background: white;
  border-radius: 0.5rem;
  box-shadow: 0 1px 3px rgba(0,0,0,0.1);
  padding: 1.5rem;
  transition: box-shadow 0.2s;
}
.card:hover { box-shadow: 0 4px 6px rgba(0,0,0,0.1); }

.card-header { margin-bottom: 1rem; }
.card-body { color: #4b5563; }
.card-footer { margin-top: 1rem; padding-top: 1rem; border-top: 1px solid #e5e7eb; }
```

### Modal
```css
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0,0,0,0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 50;
}

.modal {
  background: white;
  border-radius: 0.5rem;
  padding: 2rem;
  max-width: 500px;
  width: 90%;
  max-height: 90vh;
  overflow-y: auto;
}
```

## Accessibility (WCAG)

### Semantic HTML
```html
<!-- Good -->
<nav aria-label="Main navigation">
  <ul role="list">
    <li><a href="/home">Home</a></li>
  </ul>
</nav>

<main>
  <article>
    <h1>Page Title</h1>
    <section aria-labelledby="section-1">
      <h2 id="section-1">Section</h2>
    </section>
  </article>
</main>

<!-- Bad -->
<div class="nav">
  <div class="nav-item" onclick="go('/home')">Home</div>
</div>
```

### Focus Management
```css
/* Visible focus for keyboard users */
:focus-visible {
  outline: 2px solid #3b82f6;
  outline-offset: 2px;
}

/* Remove outline for mouse users */
:focus:not(:focus-visible) {
  outline: none;
}
```

### ARIA Patterns
```html
<!-- Toggle -->
<button
  aria-expanded="false"
  aria-controls="menu"
  onclick="toggleMenu()"
>
  Menu
</button>
<ul id="menu" role="menu" hidden>
  <li role="menuitem">Item 1</li>
</ul>

<!-- Live region for dynamic updates -->
<div aria-live="polite" aria-atomic="true">
  <!-- Updates announced to screen readers -->
</div>

<!-- Loading state -->
<div aria-busy="true" aria-label="Loading results">
  <span class="spinner" aria-hidden="true"></span>
  Loading...
</div>
```

## Design Tokens

```css
:root {
  /* Colors */
  --color-primary: #3b82f6;
  --color-primary-hover: #2563eb;
  --color-secondary: #6b7280;
  --color-success: #10b981;
  --color-error: #ef4444;

  /* Typography */
  --font-sans: 'Inter', system-ui, sans-serif;
  --font-mono: 'JetBrains Mono', monospace;
  --text-xs: 0.75rem;
  --text-sm: 0.875rem;
  --text-base: 1rem;
  --text-lg: 1.125rem;

  /* Spacing */
  --space-1: 0.25rem;
  --space-2: 0.5rem;
  --space-4: 1rem;
  --space-8: 2rem;

  /* Shadows */
  --shadow-sm: 0 1px 2px rgba(0,0,0,0.05);
  --shadow-md: 0 4px 6px rgba(0,0,0,0.1);
  --shadow-lg: 0 10px 15px rgba(0,0,0,0.1);

  /* Transitions */
  --transition-fast: 150ms ease;
  --transition-normal: 300ms ease;
}
```

## Animation Patterns

```css
/* Fade in */
@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}
.fade-in { animation: fadeIn 0.3s ease; }

/* Slide up */
@keyframes slideUp {
  from { transform: translateY(20px); opacity: 0; }
  to { transform: translateY(0); opacity: 1; }
}

/* Reduced motion */
@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after {
    animation-duration: 0.01ms !important;
    transition-duration: 0.01ms !important;
  }
}
```

## Dark Mode

```css
:root {
  --bg: white;
  --text: #1f2937;
  --border: #e5e7eb;
}

@media (prefers-color-scheme: dark) {
  :root {
    --bg: #111827;
    --text: #f9fafb;
    --border: #374151;
  }
}

body {
  background: var(--bg);
  color: var(--text);
}
```
