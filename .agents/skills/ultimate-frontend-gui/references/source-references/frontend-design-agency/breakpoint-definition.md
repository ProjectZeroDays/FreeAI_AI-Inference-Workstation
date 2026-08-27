# Breakpoint Definition

> **Umsetzungshilfe, keine Standardlösung.**
> Diese Datei ist nicht normativ. Sie darf keine Produktentscheidung vorwegnehmen und keine definierte visuelle These überschreiben.
> Breakpoint-Werte und Responsive-Strategie an den konkreten Produkttyp und die Nutzungskontexte anpassen. Die hier gezeigten Werte sind gängige Defaults — nicht automatisch die richtige Wahl.

Responsive Breakpoints für Web-App-Frontends.

## Tailwind Default Breakpoints

| Name | CSS | Width | Verwendung |
|------|-----|-------|------------|
| `sm` | `@media (min-width: 640px)` | 640px | Large Phones |
| `md` | `@media (min-width: 768px)` | 768px | Tablets |
| `lg` | `@media (min-width: 1024px)` | 1024px | Small Laptops |
| `xl` | `@media (min-width: 1280px)` | 1280px | Desktops |
| `2xl` | `@media (min-width: 1536px)` | 1536px | Large Screens |

## Custom Breakpoints (empfohlen)

```javascript
// tailwind.config.js
module.exports = {
  theme: {
    screens: {
      'xs': '475px',      // Extra small devices
      'sm': '640px',      // Small tablets
      'md': '768px',      // Tablets
      'lg': '1024px',     // Small laptops
      'xl': '1280px',     // Desktops
      '2xl': '1536px',    // Large screens
    },
  },
};
```

## Breakpoint-Strategie

### Mobile-First Ansatz

```css
/* Base: Mobile (0px - 639px) */
.element {
  width: 100%;
  padding: 1rem;
}

/* sm: 640px+ */
@media (min-width: 640px) {
  .element {
    padding: 1.5rem;
  }
}

/* md: 768px+ */
@media (min-width: 768px) {
  .element {
    width: 50%;
  }
}
```

### Container Breakpoints

```css
/* Container mit max-width */
.container {
  width: 100%;
  margin-left: auto;
  margin-right: auto;
  padding-left: 1rem;
  padding-right: 1rem;
}

@media (min-width: 640px) {
  .container {
    max-width: 640px;
  }
}

@media (min-width: 768px) {
  .container {
    max-width: 768px;
  }
}

@media (min-width: 1024px) {
  .container {
    max-width: 1024px;
  }
}

@media (min-width: 1280px) {
  .container {
    max-width: 1280px;
  }
}
```

## Responsive Patterns

### 1. Sidebar Layout

```tsx
// Mobile: Stacked, Desktop: Sidebar + Content
<div className="flex flex-col lg:flex-row">
  <aside className="w-full lg:w-64 lg:shrink-0">Sidebar</aside>
  <main className="flex-1">Content</main>
</div>
```

### 2. Card Grid

```tsx
// 1 col mobile, 2 col tablet, 3 col desktop, 4 col wide
<div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
  {items.map(item => (
    <Card key={item.id} {...item} />
  ))}
</div>
```

### 3. Data Table

```tsx
// Mobile: Cards, Desktop: Table
function ResponsiveTable({ data }) {
  return (
    <>
      {/* Mobile Cards */}
      <div className="block md:hidden">
        {data.map(row => (
          <Card key={row.id}>
            <CardHeader>
              <CardTitle>{row.name}</CardTitle>
            </CardHeader>
            <CardContent>
              {Object.entries(row).map(([key, value]) => (
                <div key={key} className="flex justify-between py-2">
                  <span className="text-muted">{key}:</span>
                  <span>{value}</span>
                </div>
              ))}
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Desktop Table */}
      <table className="hidden md:table">
        <thead>...</thead>
        <tbody>...</tbody>
      </table>
    </>
  );
}
```

### 4. Navigation

```tsx
// Mobile: Hamburger Menu, Desktop: Horizontal
function Navigation() {
  const [isOpen, setIsOpen] = useState(false);

  return (
    <nav className="flex items-center justify-between">
      <Logo />

      {/* Desktop Navigation */}
      <ul className="hidden md:flex items-center gap-6">
        <li><a href="/">Home</a></li>
        <li><a href="/about">About</a></li>
        <li><a href="/contact">Contact</a></li>
      </ul>

      {/* Mobile Menu Button */}
      <button
        className="md:hidden"
        onClick={() => setIsOpen(!isOpen)}
        aria-expanded={isOpen}
        aria-controls="mobile-menu"
      >
        <MenuIcon />
      </button>

      {/* Mobile Menu */}
      {isOpen && (
        <ul id="mobile-menu" className="md:hidden absolute top-16 left-0 right-0 bg-white">
          <li><a href="/">Home</a></li>
          <li><a href="/about">About</a></li>
          <li><a href="/contact">Contact</a></li>
        </ul>
      )}
    </nav>
  );
}
```

### 5. Typography Scaling

```css
/* Responsive Type Scale */
.text-display {
  font-size: 2.25rem;  /* 36px mobile */
  line-height: 1.2;
}

@media (min-width: 640px) {
  .text-display {
    font-size: 3rem;     /* 48px sm */
  }
}

@media (min-width: 1024px) {
  .text-display {
    font-size: 3.75rem;  /* 60px lg */
  }
}
```

## Touch Target Sizes

| Element | Min Size | Notes |
|---------|----------|-------|
| Buttons | 44×44px | Apple HIG |
| Buttons (Google) | 48×48px | Material Design |
| Spacing between | 8px | Prevent accidental taps |
| Input Height | 44px | Comfortable typing |

```css
.touch-target {
  min-height: 44px;
  min-width: 44px;
}

/* For smaller visual elements */
.touch-target::after {
  content: '';
  position: absolute;
  inset: -8px;
}
```

## Breakpoint-Checkliste

Vor Launch:
- [ ] Mobile (320px) getestet
- [ ] Tablet (768px) getestet
- [ ] Desktop (1280px) getestet
- [ ] Large Screen (1536px+) getestet
- [ ] Landscape/Potrait Rotation
- [ ] Zoom 200%
- [ ] Keine horizontalen Scrollbars bis 320px
- [ ] Touch Targets ≥ 44px
- [ ] Lesbare Textgrößen auf allen Geräten
- [ ] Navigation bedienbar auf Touch
