# Component Hierarchy & Naming Conventions

## Four-Layer Architecture

### Layer 1: Layout Components
Core structural elements that define page architecture. Never depend on content.

- `.container` — page wrapper with max-width and centering
- `.grid-*` — layout grids (`.grid-2`, `.grid-sidebar`, `.grid-cards`)
- `.section` — major page section with vertical rhythm
- `.stack` — vertical stack of items with consistent gap

### Layer 2: Content Components
Display information. May contain data, but have no interactive behavior.

- `.card` — contained content block
- `.card-header` / `.card-body` / `.card-footer` — card sub-components
- `.avatar` — user/image representation
- `.badge` — status/category indicator
- `.divider` — horizontal separator

### Layer 3: Interactive Components
Components that respond to user input.

- `.btn` — action trigger
- `.input` / `.textarea` / `.select` — form inputs
- `.checkbox` / `.radio` — boolean/toggle inputs
- `.toggle` — on/off switch
- `.dropdown` — expandable menu
- `.modal` — overlay dialog
- `.tabs` — panel switcher

### Layer 4: Utility Components
Single-purpose, often used to modify other components.

- `.text-*` — typography helpers (`.text-sm`, `.text-center`)
- `.flex` / `.grid` — layout helpers
- `.gap-*` — spacing helpers (`.gap-2`, `.gap-4`)
- `.hidden` / `.visible` — visibility
- `.sr-only` — screen reader only (visible to a11y, hidden visually)

## Naming Conventions

### Hyphen-case for everything
```
.card-header
.text-small
.grid-2-col
.theme-toggle
```

### BEM variant for component sub-elements (optional)
When a component has multiple sub-parts that need explicit scoping:
```
.card__header { }
.card__body { }
.card__footer { }
```

### Variant suffixes
```
.btn-primary    ← color variant
.btn-sm         ← size variant
.btn-block      ← layout variant
.input-error    ← state variant
```

## Component Hierarchy Diagram

```
Layout
├── .container
│   └── .grid-*
│       ├── .section
│       │   └── .stack
│       └── .sidebar
│
Content
├── .card
│   ├── .card-header
│   ├── .card-body
│   └── .card-footer
├── .avatar
├── .badge
└── .divider
│
Interactive
├── .btn
│   └── [variants: primary, secondary, ghost, danger]
├── .form-group
│   ├── .form-label
│   └── .form-input
├── .modal
│   ├── .modal-backdrop
│   └── .modal-dialog
└── .dropdown
│
Utility
├── .text-*
├── .flex, .grid
├── .gap-*
└── .sr-only
```

## Component Composition Example

```html
<!-- Layout: Grid with sidebar -->
<div class="container grid-sidebar">
  <main>
    <!-- Section with stacked content -->
    <section class="section stack gap-6">
      <!-- Card component -->
      <article class="card">
        <header class="card-header">
          <h2 class="text-h3">Card Title</h2>
          <span class="badge badge-success">已上线</span>
        </header>
        <div class="card-body">
          <p class="text-body">Content goes here.</p>
        </div>
        <footer class="card-footer">
          <button class="btn btn-primary">主操作</button>
          <button class="btn btn-ghost">次操作</button>
        </footer>
      </article>
    </section>
  </main>

  <aside>
    <!-- Another card -->
    <div class="card">
      ...
    </div>
  </aside>
</div>
```

## Accessibility Requirements by Layer

| Layer | A11y Concern |
|-------|-------------|
| Layout | Skip links, landmark regions (`<main>`, `<nav>`, `<aside>`) |
| Content | Heading hierarchy (h1→h2→h3), alt text for images |
| Interactive | Focus management, keyboard nav, ARIA labels, error announcements |
| Utility | Screen reader only content (`.sr-only`) |

## CSS Specificity Guidelines

1. **Single class selectors** — `.card { }` not `.card.class { }`
2. **No nesting beyond 1 level** — BEM-style `.card__body p` is ok, but don't go deeper
3. **No IDs for styling** — IDs are for JS hooks only
4. **Avoid attribute selectors** — `[type="text"]` is fragile, use `.input` instead
5. **No `!important`** — If you need it, your architecture is wrong
