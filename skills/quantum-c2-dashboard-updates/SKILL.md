---
name: quantum-c2-dashboard-updates
description: Apply consistent design patterns, drag-and-drop functionality, audio feedback, and settings panels to the QUANTUM C2 single-file HTML dashboard. Use when updating quantum-platform-4-performance-safe-new-logo.html or similar QUANTUM dashboard files with q-card patterns, q-kpi-grid, q-dashboard-grid, data-sound/data-sounds attributes, draggable cards, and SETTINGS_PANELS definitions.
---

# QUANTUM C2 Dashboard Updates

This skill provides guidelines for maintaining and updating the QUANTUM C2 single-file HTML dashboard with consistent design patterns.

## File Location
- Primary: `C:\Users\Project Zero\Desktop\quantum-platform-4-performance-safe-new-logo.html`
- Size: ~3.77MB, ~10,178 lines

## Design Pattern Reference

### Page Structure
```html
<div class="page q2-page" id="page-name-page" style="display:none">
  <div class="q-page-shell">
    <div class="q-page-header">
      <div>
        <div class="q-eyebrow">Category</div>
        <h1>Page Title</h1>
        <p>Description text.</p>
      </div>
      <div class="q-page-badges">
        <span class="q-badge">BADGE 1</span>
        <span class="q-badge">BADGE 2</span>
      </div>
    </div>
    <div class="q-kpi-grid">
      <q-kpi detail="subtext" label="Label" value="123"></q-kpi>
    </div>
    <div class="q-dashboard-grid q-draggable-dashboard">
      <section class="q-card" draggable="true">
        <div class="q-card-head">
          <div><h2>Card Title</h2><p>Card description</p></div>
          <span class="q-status">STATUS</span>
        </div>
        <div class="q-card-body">...</div>
        <div class="q-card-actions">
          <button class="q-btn q-btn--primary" data-sound="click" data-sounds="click">Action</button>
        </div>
      </section>
    </div>
  </div>
</div>
```

## Required Attributes

### Interactive Buttons
All clickable buttons MUST have both attributes:
```html
<button data-sound="click" data-sounds="click">Label</button>
```

### Draggable Cards
All cards in dashboard grids MUST be draggable:
```html
<section class="q-card" draggable="true">
```

### Dashboard Grids
All dashboard grids MUST have drag class:
```html
<div class="q-dashboard-grid q-draggable-dashboard">
```

### KPI Animation
All KPI values should have live number animation:
```html
<q-kpi data-live-number="1" label="CPU" value="47%"></q-kpi>
```

## Settings Panels

Settings panels are defined in the `SETTINGS_PANELS` JavaScript object and referenced via `data-settings-panel` attribute on buttons.

### Pattern
```html
<button data-settings-panel="panel-name">Settings</button>
```

```javascript
const SETTINGS_PANELS = {
  'panel-name': {
    title: 'Panel Title',
    fields: [
      { id: 'setting-id', type: 'select|checkbox|number|text', label: 'Label', options: [...], default: 'value' }
    ]
  }
};
```

## Common Fixes

### Add Draggable to Cards
```python
import re
with open('file.html', 'r') as f:
    content = f.read()
pattern = r'<section class="q-card(?:\s+q-card--span-2)?">(\s*)>'
content = re.sub(pattern, r'<section class="q-card\2" draggable="true">', content)
```

### Add Audio to Buttons
```python
import re
with open('file.html', 'r') as f:
    content = f.read()
# Add data-sound and data-sounds to buttons missing them
pattern = r'<button class="([^"]*)"((?![^>]*data-sound)[^>]*)>'
content = re.sub(pattern, r'<button class="\1"\2 data-sound="click" data-sounds="click">', content)
```

### Add Nav Entries
Add to the appropriate nav section:
```html
<button class="nav-item" data-page-target="page-name-page" data-sound="click" data-sounds="click">Page Name</button>
```

## Statistics to Track
- Total cards: Should all have `draggable="true"`
- Total grids: Should all have `q-draggable-dashboard` class
- Data-live-number count: Should be on all KPIs
- Settings panels: Defined in SETTINGS_PANELS and referenced by buttons
