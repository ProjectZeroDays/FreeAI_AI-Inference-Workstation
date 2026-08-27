---
name: c2-theme-integrator
description: Integrates external HTML dashboards into the Quantum unified dashboard. Extracts DOM structure from source HTML, restyles with c2.html CSS variables, renames branding to Quantum, adds AI chatbot, and links navigation. Use when the user wants to merge or integrate a new HTML page into quantum_unified.html.
---

# C2 Theme Integrator

Integrates external HTML dashboards into `core/web_interface/templates/quantum_unified.html` while matching the c2.html visual style.

## CSS Variables (Canonical)

```css
--bg:#02040a;
--panel:rgba(3,14,30,0.94);
--accent:#00e5ff;
--accent-soft:#6bdcff;
--accent-strong:#00f6ff;
--danger:#ff4b6b;
--muted:#7fa2b8;
--success:#6ef0a3;
--warn:#ffd36b;
--glass:rgba(0,20,40,0.86);
--border:rgba(16,51,71,0.6);
--light:#cfefff;
--font:"Segoe UI",system-ui,-apple-system,sans-serif;
--mono:"Space Mono","Courier New",monospace;
```

Background: `radial-gradient(circle at 10% 10%, #07111f, #020308, #000)`

## Integration Steps

### 1. Read Source HTML
- Read the external HTML file completely
- Identify: layout structure (sidebar, main content, panels), color scheme, fonts, framework dependencies (Tailwind, Bootstrap, etc.)
- Note all CSS custom properties and theme tokens

### 2. Extract DOM Structure
- Extract the semantic layout (sidebar sections, navigation items, content panels, data tables)
- Strip framework-specific scripts (Vite, React, Replit, Tailwind CDN, hot reload)
- Remove all `data-replit-metadata` and `data-component-name` attributes
- Keep only the structural HTML and inline SVG icons

### 3. Apply c2.html Theme
- Replace all colors with c2.html CSS variable references
- Map source accent colors → `var(--accent)` (#00e5ff)
- Map source background → `var(--bg)` (#02040a)
- Map source card/panel → `var(--panel)` or `var(--card-bg)`
- Map source muted/secondary text → `var(--muted)`
- Map source danger/error → `var(--danger)`
- Map source border → `var(--border)`
- Replace framework font families with `var(--font)` / `var(--mono)`
- Add scrollbar styling (6px width, transparent track, `var(--border)` thumb)

### 4. Rename Branding
- Replace all occurrences of external brand names → "Quantum" / "QUANTUM"
- Case-sensitive replacements: `PEGASUS` → `QUANTUM`, `Pegasus` → `Quantum`, `pegasus` → `quantum`
- Clicking the logo/brand text must navigate back to `showPage('dashboard')`

### 5. Add to Unified Dashboard
- Add as a new `.page` div inside `#content`
- Add corresponding `.nav-item` in sidebar
- Wire `onclick="showPage('page-id')"` on the nav item
- Ensure `showPage()` function handles the new page

### 6. Add AI Chatbot
- Include the persistent chatbox HTML from c2.html:
  - `#chat-toggle` button (fixed, bottom-right)
  - `#chatbox` container with titlebar, log, composer
  - `sendChat()` and `toggleChat()` JavaScript functions
- Style the chatbox with c2.html glass morphism (`var(--glass)`, `var(--border)`)

### 7. Validate
- Open in browser via `start "" "<path>"`
- Verify all navigation works
- Verify theme consistency (no raw hex colors from source)
- Verify Quantum branding throughout
- Verify chatbot opens/closes correctly

## Layout Patterns

### Sidebar Nav Item
```html
<div class="nav-item" onclick="showPage('page-id')">
  <div class="left">
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><!-- icon --></svg>
    Label
  </div>
</div>
```

### Page Container
```html
<div id="page-id" class="page">
  <div class="page-header">
    <h1>Page Title</h1>
    <div class="subtitle">Status info</div>
  </div>
  <!-- content -->
</div>
```

### Detail Panel
```html
<div class="detail-panel">
  <div class="panel-header">
    <svg><!-- icon --></svg> PANEL TITLE
  </div>
  <div class="panel-body">
    <div class="data-row">
      <div class="info">
        <span class="primary">Main text</span>
        <span class="secondary">Secondary text</span>
      </div>
      <span class="badge">Value</span>
    </div>
  </div>
</div>
```

## Navigation Function

```javascript
function showPage(id) {
  document.querySelectorAll('.page').forEach(p => p.classList.remove('active'));
  document.querySelectorAll('.nav-item').forEach(n => n.classList.remove('active'));
  var el = document.getElementById('page-' + id);
  if (el) el.classList.add('active');
  if (event && event.target) {
    var item = event.target.closest('.nav-item');
    if (item) item.classList.add('active');
  }
}
```

## Common Pitfalls

- **tkinter**: Does NOT support 8-char hex (`#RRGGBBAA`). Only 6-char `#RRGGBB`.
- **tkinter Label**: Has NO `-command` option. Use `Label.bind("<Button-1>", cb)` or `tk.Button`.
- **Tailwind**: If source uses Tailwind, extract computed styles and convert to vanilla CSS. Do NOT include Tailwind CDN in the unified dashboard.
- **React/Vite**: Strip all `import`, `export`, module scripts, hot-reload code.
- **External fonts**: Include via `<link>` tag but fall back to system fonts.
