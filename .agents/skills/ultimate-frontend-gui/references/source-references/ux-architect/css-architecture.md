# CSS Architecture Reference

Complete CSS architecture system from the UX Architect agent.

## Design Token System

```css
:root {
  /* Light Theme Colors */
  --bg-primary: #ffffff;
  --bg-secondary: #f9fafb;
  --bg-tertiary: #f3f4f6;
  --text-primary: #111827;
  --text-secondary: #6b7280;
  --text-muted: #9ca3af;
  --border-color: #e5e7eb;
  --border-strong: #d1d5db;

  /* Brand Colors */
  --primary-50:  #f0f9ff;
  --primary-100: #e0f2fe;
  --primary-200: #bae6fd;
  --primary-300: #7dd3fc;
  --primary-400: #38bdf8;
  --primary-500: #0284c7;
  --primary-600: #0369a1;
  --primary-700: #075985;

  --secondary-50:  #f9fafb;
  --secondary-100: #f3f4f6;
  --secondary-200: #e5e7eb;
  --secondary-300: #d1d5db;
  --secondary-400: #9ca3af;
  --secondary-500: #6b7280;
  --secondary-600: #4b5563;
  --secondary-700: #374151;
  --secondary-800: #1f2937;
  --secondary-900: #111827;

  /* Semantic Colors */
  --success: #10b981;
  --success-light: #d1fae5;
  --warning: #f59e0b;
  --warning-light: #fef3c7;
  --error: #ef4444;
  --error-light: #fee2e2;
  --info: #3b82f6;
  --info-light: #dbeafe;

  /* Typography Scale */
  --text-xs:   0.75rem;    /* 12px */
  --text-sm:   0.875rem;   /* 14px */
  --text-base: 1rem;       /* 16px */
  --text-lg:   1.125rem;   /* 18px */
  --text-xl:   1.25rem;    /* 20px */
  --text-2xl:  1.5rem;     /* 24px */
  --text-3xl:  1.875rem;   /* 30px */
  --text-4xl:  2.25rem;    /* 36px */

  --font-sans: 'Inter', system-ui, -apple-system, sans-serif;
  --font-mono: 'JetBrains Mono', 'Fira Code', monospace;

  --font-weight-normal: 400;
  --font-weight-medium: 500;
  --font-weight-semibold: 600;
  --font-weight-bold: 700;

  --line-height-tight: 1.25;
  --line-height-normal: 1.5;
  --line-height-relaxed: 1.75;

  /* Spacing Scale (4px base) */
  --space-0:  0;
  --space-1:  0.25rem;   /* 4px */
  --space-2:  0.5rem;    /* 8px */
  --space-3:  0.75rem;   /* 12px */
  --space-4:  1rem;      /* 16px */
  --space-5:  1.25rem;  /* 20px */
  --space-6:  1.5rem;    /* 24px */
  --space-8:  2rem;      /* 32px */
  --space-10: 2.5rem;   /* 40px */
  --space-12: 3rem;      /* 48px */
  --space-16: 4rem;      /* 64px */
  --space-20: 5rem;      /* 80px */
  --space-24: 6rem;      /* 96px */

  /* Layout Containers */
  --container-sm: 640px;
  --container-md: 768px;
  --container-lg: 1024px;
  --container-xl: 1280px;

  /* Border Radius */
  --radius-sm:   0.25rem;
  --radius-md:   0.5rem;
  --radius-lg:   0.75rem;
  --radius-xl:   1rem;
  --radius-2xl:  1.5rem;
  --radius-full: 9999px;

  /* Shadows */
  --shadow-xs: 0 1px 2px 0 rgb(0 0 0 / 0.05);
  --shadow-sm: 0 1px 3px 0 rgb(0 0 0 / 0.1), 0 1px 2px -1px rgb(0 0 0 / 0.1);
  --shadow-md: 0 4px 6px -1px rgb(0 0 0 / 0.1), 0 2px 4px -2px rgb(0 0 0 / 0.1);
  --shadow-lg: 0 10px 15px -3px rgb(0 0 0 / 0.1), 0 4px 6px -4px rgb(0 0 0 / 0.1);
  --shadow-xl: 0 20px 25px -5px rgb(0 0 0 / 0.1), 0 8px 10px -6px rgb(0 0 0 / 0.1);

  /* Transitions */
  --transition-fast: 150ms ease;
  --transition-normal: 300ms ease;
  --transition-slow: 500ms ease;

  /* Z-index */
  --z-dropdown: 1000;
  --z-sticky: 1020;
  --z-fixed: 1030;
  --z-modal-backdrop: 1040;
  --z-modal: 1050;
  --z-popover: 1060;
  --z-tooltip: 1070;
}
```

## Dark Theme Override

```css
[data-theme="dark"] {
  --bg-primary: #111827;
  --bg-secondary: #1f2937;
  --bg-tertiary: #374151;
  --text-primary: #f9fafb;
  --text-secondary: #d1d5db;
  --text-muted: #9ca3af;
  --border-color: #374151;
  --border-strong: #4b5563;

  --shadow-sm: 0 1px 3px 0 rgb(0 0 0 / 0.3), 0 1px 2px -1px rgb(0 0 0 / 0.3);
  --shadow-md: 0 4px 6px -1px rgb(0 0 0 / 0.3), 0 2px 4px -2px rgb(0 0 0 / 0.3);
  --shadow-lg: 0 10px 15px -3px rgb(0 0 0 / 0.3), 0 4px 6px -4px rgb(0 0 0 / 0.3);
}
```

## System Theme Preference

```css
@media (prefers-color-scheme: dark) {
  :root:not([data-theme="light"]) {
    --bg-primary: #111827;
    --bg-secondary: #1f2937;
    --bg-tertiary: #374151;
    --text-primary: #f9fafb;
    --text-secondary: #d1d5db;
    --text-muted: #9ca3af;
    --border-color: #374151;
    --border-strong: #4b5563;
  }
}
```

## Layout Components

### Container
```css
.container {
  width: 100%;
  max-width: var(--container-lg);
  margin: 0 auto;
  padding: 0 var(--space-4);
}

.container-sm  { max-width: var(--container-sm); }
.container-md  { max-width: var(--container-md); }
.container-lg  { max-width: var(--container-lg); }
.container-xl  { max-width: var(--container-xl); }

@media (max-width: 768px) {
  .container { padding: 0 var(--space-4); }
}
```

### Grid Patterns
```css
/* Two column */
.grid-2 {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: var(--space-8);
}

@media (max-width: 768px) {
  .grid-2 { grid-template-columns: 1fr; gap: var(--space-6); }
}

/* Auto-fit card grid */
.grid-cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: var(--space-6);
}

/* Sidebar layout */
.grid-sidebar {
  display: grid;
  grid-template-columns: 2fr 1fr;
  gap: var(--space-8);
}

@media (max-width: 1024px) {
  .grid-sidebar { grid-template-columns: 1fr; }
}
```

## Typography Components

```css
.text-h1 {
  font-size: var(--text-4xl);
  font-weight: var(--font-weight-bold);
  line-height: var(--line-height-tight);
  letter-spacing: -0.025em;
}

.text-h2 {
  font-size: var(--text-3xl);
  font-weight: var(--font-weight-bold);
  line-height: var(--line-height-tight);
}

.text-h3 {
  font-size: var(--text-2xl);
  font-weight: var(--font-weight-semibold);
  line-height: var(--line-height-tight);
}

.text-body {
  font-size: var(--text-base);
  line-height: var(--line-height-normal);
}

.text-small {
  font-size: var(--text-sm);
  color: var(--text-secondary);
}
```

## Theme Toggle Component

```html
<div class="theme-toggle" role="group" aria-label="选择主题">
  <button class="theme-toggle-option" data-theme="light" aria-pressed="true">浅色</button>
  <button class="theme-toggle-option" data-theme="dark" aria-pressed="false">深色</button>
  <button class="theme-toggle-option" data-theme="system" aria-pressed="false">系统</button>
</div>
```

```javascript
class ThemeManager {
  constructor() {
    this.currentTheme = localStorage.getItem('theme')
      || (window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light');
    this.applyTheme(this.currentTheme);
  }

  applyTheme(theme) {
    if (theme === 'system') {
      document.documentElement.removeAttribute('data-theme');
    } else {
      document.documentElement.setAttribute('data-theme', theme);
    }
    localStorage.setItem('theme', theme);
    this.currentTheme = theme;
    this.updateToggleUI();
  }

  updateToggleUI() {
    document.querySelectorAll('.theme-toggle-option').forEach(btn => {
      btn.classList.toggle('active', btn.dataset.theme === this.currentTheme);
      btn.setAttribute('aria-pressed', btn.dataset.theme === this.currentTheme);
    });
  }
}

document.addEventListener('DOMContentLoaded', () => {
  const tm = new ThemeManager();
  document.querySelector('.theme-toggle')?.addEventListener('click', e => {
    if (e.target.matches('.theme-toggle-option')) {
      tm.applyTheme(e.target.dataset.theme);
    }
  });
});
```

## Responsive Breakpoints

| Breakpoint | Min-width | Devices |
|-----------|-----------|---------|
| sm | 640px | Large phones, landscape |
| md | 768px | Tablets |
| lg | 1024px | Laptops |
| xl | 1280px | Desktops |
| 2xl | 1536px | Large screens |

```css
/* Mobile first — base styles target smallest screens */
/* Then enhance upward */

@media (min-width: 640px)  { /* sm */ }
@media (min-width: 768px)  { /* md */ }
@media (min-width: 1024px) { /* lg */ }
@media (min-width: 1280px) { /* xl */ }
```
