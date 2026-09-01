---
name: accessibility-audit
description: WCAG compliance, accessibility testing, ARIA patterns, screen reader optimization, and keyboard navigation. Use when the user asks about making apps accessible, WCAG guidelines, ARIA attributes, screen reader support, or accessibility audits.
---

# Accessibility Audit

## WCAG 2.1 Quick Reference

### Level A (Minimum)
- All images have alt text
- All form inputs have labels
- Keyboard accessible
- No content flashes more than 3 times/sec
- Page has title
- Link text is descriptive

### Level AA (Recommended)
- Color contrast ratio ≥ 4.5:1 (normal text), ≥ 3:1 (large text)
- Text resizable up to 200% without loss
- Responsive to viewport changes
- Focus visible on interactive elements
- Skip navigation link provided

## Semantic HTML

```html
<!-- Bad -->
<div class="nav">
  <div class="nav-item" onclick="go('/home')">Home</div>
</div>
<div class="content">
  <div class="title">Welcome</div>
</div>

<!-- Good -->
<nav aria-label="Main">
  <ul>
    <li><a href="/home">Home</a></li>
  </ul>
</nav>
<main>
  <h1>Welcome</h1>
</main>
```

## ARIA Patterns

### Landmarks
```html
<header aria-label="Site header">...</header>
<nav aria-label="Main navigation">...</nav>
<main>
  <article>
    <h1>Page Title</h1>
    <section aria-labelledby="section-1">
      <h2 id="section-1">Section</h2>
    </section>
  </article>
  <aside aria-label="Related links">...</aside>
</main>
<footer aria-label="Site footer">...</footer>
```

### Live Regions
```html
<!-- Announce dynamic updates -->
<div aria-live="polite" aria-atomic="true">
  3 items in cart
</div>

<!-- Assertive (interrupts) -->
<div aria-live="assertive">
  Error: Form submission failed
</div>

<!-- Loading state -->
<div aria-busy="true">
  <span aria-hidden="true">Loading...</span>
</div>
```

### Modal Dialog
```html
<div role="dialog" aria-modal="true" aria-labelledby="dialog-title">
  <h2 id="dialog-title">Confirm Action</h2>
  <p>Are you sure?</p>
  <button>Cancel</button>
  <button>Confirm</button>
</div>
```

### Tabs
```html
<div role="tablist" aria-label="Settings">
  <button role="tab" aria-selected="true" aria-controls="panel-1" id="tab-1">
    General
  </button>
  <button role="tab" aria-selected="false" aria-controls="panel-2" id="tab-2" tabindex="-1">
    Security
  </button>
</div>
<div role="tabpanel" id="panel-1" aria-labelledby="tab-1">
  Content for General
</div>
<div role="tabpanel" id="panel-2" aria-labelledby="tab-2" hidden>
  Content for Security
</div>
```

### Accordion
```html
<h3>
  <button aria-expanded="true" aria-controls="content-1">
    Section 1
  </button>
</h3>
<div id="content-1" role="region" aria-labelledby="header-1">
  <p>Content here</p>
</div>
```

## Keyboard Navigation

```css
/* Visible focus indicator */
:focus-visible {
  outline: 2px solid #3b82f6;
  outline-offset: 2px;
}

/* Remove default outline for mouse users */
:focus:not(:focus-visible) {
  outline: none;
}
```

```javascript
// Trap focus in modal
function trapFocus(element) {
  const focusable = element.querySelectorAll(
    'a[href], button:not([disabled]), input:not([disabled]), ' +
    'select:not([disabled]), textarea:not([disabled]), [tabindex]:not([tabindex="-1"])'
  );
  
  const first = focusable[0];
  const last = focusable[focusable.length - 1];
  
  element.addEventListener('keydown', (e) => {
    if (e.key !== 'Tab') return;
    
    if (e.shiftKey) {
      if (document.activeElement === first) {
        e.preventDefault();
        last.focus();
      }
    } else {
      if (document.activeElement === last) {
        e.preventDefault();
        first.focus();
      }
    }
  });
  
  first.focus();
}
```

## Color Contrast

```javascript
// Check contrast ratio
function getContrastRatio(hex1, hex2) {
  const lum1 = getLuminance(hex1);
  const lum2 = getLuminance(hex2);
  const lighter = Math.max(lum1, lum2);
  const darker = Math.min(lum1, lum2);
  return (lighter + 0.05) / (darker + 0.05);
}

function getLuminance(hex) {
  const rgb = hexToRgb(hex);
  const [r, g, b] = rgb.map(c => {
    c = c / 255;
    return c <= 0.03928 ? c / 12.92 : Math.pow((c + 0.055) / 1.055, 2.4);
  });
  return 0.2126 * r + 0.7152 * g + 0.0722 * b;
}

// WCAG AA: 4.5:1 for normal text, 3:1 for large text
// WCAG AAA: 7:1 for normal text, 4.5:1 for large text
```

## Form Accessibility

```html
<form>
  <!-- Always associate labels with inputs -->
  <label for="email">Email address</label>
  <input
    id="email"
    type="email"
    required
    aria-required="true"
    aria-describedby="email-help email-error"
    aria-invalid="false"
  />
  <span id="email-help">We'll never share your email</span>
  <span id="email-error" role="alert" aria-live="assertive"></span>

  <!-- Group related fields -->
  <fieldset>
    <legend>Shipping Address</legend>
    <label for="street">Street</label>
    <input id="street" type="text" />
  </fieldset>

  <!-- Error announcements -->
  <div role="alert" aria-live="assertive">
    <!-- Populated on error -->
  </div>
</form>
```

## Image Accessibility

```html
<!-- Informative image -->
<img src="chart.png" alt="Sales increased 25% from January to March" />

<!-- Decorative image -->
<img src="border.png" alt="" role="presentation" />

<!-- Complex image -->
<figure>
  <img src="architecture.png" alt="System architecture diagram" aria-describedby="arch-desc" />
  <figcaption id="arch-desc">
    The system consists of three layers: presentation, business logic, and data access.
  </figcaption>
</figure>
```

## Testing Checklist

- [ ] All images have appropriate alt text
- [ ] All form inputs have labels
- [ ] Keyboard can reach all interactive elements
- [ ] Focus order is logical
- [ ] Focus indicator is visible
- [ ] Color contrast meets WCAG AA (4.5:1)
- [ ] Page has descriptive title
- [ ] Headings are hierarchical (h1 → h2 → h3)
- [ ] Links are descriptive (not "click here")
- [ ] Skip navigation link exists
- [ ] ARIA labels used correctly
- [ ] Live regions announce dynamic content
- [ ] No keyboard traps
- [ ] Touch targets ≥ 44x44px
- [ ] Reduced motion respected
