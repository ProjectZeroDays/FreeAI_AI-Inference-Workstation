---
name: professional-frontend-developer
description: Professional website frontend development skill for building, analyzing, and refining websites with attention to detail, responsive design, accessibility, and modern UI/UX patterns. Use when the user wants to create, improve, or audit website frontend code.
---

# Professional Frontend Developer

Expert frontend development skill for creating professional, polished websites with attention to detail, responsive design, accessibility, and modern UI/UX patterns.

## When to Use

- Building new website pages or components
- Auditing and improving existing websites
- Fixing layout, styling, or responsive issues
- Implementing dark/light mode themes
- Adding animations and interactions
- Improving accessibility (WCAG compliance)
- Performance optimization
- SEO improvements

## Core Principles

### 1. Design System Consistency
- Use CSS custom properties (variables) for colors, spacing, typography
- Maintain consistent spacing scale (4px, 8px, 12px, 16px, 24px, 32px, 48px, 64px)
- Use consistent border-radius values
- Maintain consistent shadow hierarchy
- Create reusable component patterns

### 2. Responsive Design
- Mobile-first approach
- Breakpoints: 375px (mobile), 768px (tablet), 1024px (laptop), 1280px (desktop), 1440px (large)
- Fluid typography with clamp()
- Flexible grids with CSS Grid and Flexbox
- Test all breakpoints

### 3. Accessibility (WCAG 2.1 AA)
- Semantic HTML elements
- ARIA labels where needed
- Keyboard navigation support
- Focus visible states
- Color contrast ratios (4.5:1 minimum)
- Alt text for images
- Skip navigation links

### 4. Performance
- Optimize images (WebP, lazy loading)
- Minify CSS and JavaScript
- Critical CSS inlining
- Defer non-critical JS
- Use CSS animations over JS when possible

### 5. Modern CSS Features
- CSS Grid and Flexbox
- CSS custom properties
- Container queries
- Subgrid
- Scroll-driven animations
- backdrop-filter for glassmorphism
- CSS nested syntax

## Component Patterns

### Buttons
```css
.btn {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem 1.5rem;
  font-weight: 600;
  border-radius: var(--radius);
  transition: all 0.2s ease;
  cursor: pointer;
}

.btn-primary {
  background: var(--primary);
  color: white;
  border: 2px solid var(--primary);
}

.btn-primary:hover {
  background: var(--primary-dark);
  border-color: var(--primary-dark);
  transform: translateY(-2px);
  box-shadow: var(--shadow-md);
}

.btn-secondary {
  background: transparent;
  color: var(--primary);
  border: 2px solid var(--primary);
}

.btn-secondary:hover {
  background: var(--primary);
  color: white;
}
```

### Cards
```css
.card {
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: var(--radius-lg);
  padding: 1.5rem;
  transition: all 0.3s ease;
}

.card:hover {
  transform: translateY(-4px);
  box-shadow: var(--shadow-lg);
  border-color: var(--border-strong);
}
```

### Navigation
```css
.navbar {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  z-index: 1000;
  background: var(--bg-glass);
  backdrop-filter: blur(20px);
  border-bottom: 1px solid var(--border);
}

.navbar.scrolled {
  background: var(--bg-primary);
  box-shadow: var(--shadow-md);
}
```

### Hero Section
```css
.hero {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
  padding: 8rem 2rem 4rem;
}

.hero-content {
  text-align: center;
  max-width: 800px;
}

.hero h1 {
  font-size: clamp(2.5rem, 5vw, 4rem);
  font-weight: 800;
  line-height: 1.1;
  margin-bottom: 1.5rem;
}
```

## Theme Implementation

### CSS Variables for Theming
```css
:root {
  /* Dark Theme (Default) */
  --bg-primary: #0a0e1a;
  --bg-secondary: #0d1117;
  --bg-card: rgba(22, 27, 34, 0.6);
  --text-primary: #f0f6fc;
  --text-secondary: #8b949e;
  --primary: #00e5ff;
  --primary-dark: #00b8d4;
  --border: rgba(255, 255, 255, 0.06);
  --shadow-sm: 0 1px 2px rgba(0, 0, 0, 0.4);
  --shadow-md: 0 4px 12px rgba(0, 0, 0, 0.5);
  --shadow-lg: 0 10px 30px rgba(0, 0, 0, 0.6);
}

[data-theme="light"] {
  --bg-primary: #ffffff;
  --bg-secondary: #f6f8fc;
  --bg-card: #ffffff;
  --text-primary: #111827;
  --text-secondary: #4b5563;
  --primary: #6366f1;
  --primary-dark: #4f46e5;
  --border: rgba(0, 0, 0, 0.08);
  --shadow-sm: 0 1px 3px rgba(0, 0, 0, 0.08);
  --shadow-md: 0 4px 12px rgba(0, 0, 0, 0.1);
  --shadow-lg: 0 10px 30px rgba(0, 0, 0, 0.12);
}
```

### Theme Toggle
```javascript
function initThemeToggle() {
  const STORAGE_KEY = 'theme';
  const toggle = document.getElementById('themeToggle');
  
  // Check saved preference
  const savedTheme = localStorage.getItem(STORAGE_KEY) || 'dark';
  document.documentElement.setAttribute('data-theme', savedTheme);
  updateIcon(savedTheme);
  
  toggle.addEventListener('click', () => {
    const current = document.documentElement.getAttribute('data-theme');
    const next = current === 'dark' ? 'light' : 'dark';
    document.documentElement.setAttribute('data-theme', next);
    localStorage.setItem(STORAGE_KEY, next);
    updateIcon(next);
  });
  
  function updateIcon(theme) {
    const icon = toggle.querySelector('i');
    icon.className = theme === 'dark' ? 'fas fa-sun' : 'fas fa-moon';
  }
}
```

## Professional Polish Checklist

### Typography
- [ ] Use professional font pairing (e.g., Inter for body, JetBrains Mono for code)
- [ ] Consistent font sizes with scale (1.25rem, 1.5rem, 2rem, 2.5rem, 3rem)
- [ ] Proper line-height (1.5-1.75 for body, 1.1-1.25 for headings)
- [ ] Letter-spacing for uppercase text (0.05-0.1em)
- [ ] Font-weight hierarchy (400 regular, 500 medium, 600 semibold, 700 bold)

### Spacing
- [ ] Consistent padding/margin scale
- [ ] Adequate white space between sections (4rem-6rem)
- [ ] Proper alignment and visual balance
- [ ] Responsive spacing adjustments

### Colors
- [ ] Consistent color palette
- [ ] Proper contrast ratios (WCAG AA)
- [ ] Hover states for all interactive elements
- [ ] Focus states for keyboard navigation
- [ ] Active/pressed states

### Animations
- [ ] Smooth transitions (0.2-0.3s ease)
- [ ] Subtle hover effects
- [ ] Scroll-triggered animations
- [ ] Loading states
- [ ] Respect prefers-reduced-motion

### Icons
- [ ] Use consistent icon library (Font Awesome, Lucide, Heroicons)
- [ ] Proper sizing
- [ ] Aria labels for accessibility
- [ ] Hover/active states

### Components
- [ ] Consistent border-radius
- [ ] Consistent shadow hierarchy
- [ ] Consistent border styles
- [ ] Responsive behavior
- [ ] Touch-friendly targets (min 44x44px)

## Common Fixes

### Fix Encoding Issues
```javascript
// Replace mangled characters
content = content.replace(/â€"/g, '—');
content = content.replace(/â€"/g, '–');
content = content.replace(/â€/g, '…');
content = content.replace(/�/g, '–');
```

### Fix Layout Issues
```css
/* Center content */
.hero-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
}

/* Fix overflow */
.container {
  max-width: 1280px;
  margin: 0 auto;
  padding: 0 2rem;
}

/* Fix sticky elements */
.navbar {
  position: fixed;
  top: 0;
  width: 100%;
  z-index: 1000;
}
```

### Fix Responsive Issues
```css
/* Mobile-first media queries */
@media (min-width: 768px) {
  .grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (min-width: 1024px) {
  .grid {
    grid-template-columns: repeat(3, 1fr);
  }
}

@media (min-width: 1280px) {
  .grid {
    grid-template-columns: repeat(4, 1fr);
  }
}
```

## Deliverables

When completing a frontend task, ensure:
1. All HTML is semantic and accessible
2. CSS is organized with comments and consistent naming
3. JavaScript is modular and handles errors
4. All breakpoints tested (375px, 768px, 1024px, 1280px, 1440px)
5. Both light and dark modes tested
6. No console errors
7. Performance optimized
8. Documentation updated if needed
