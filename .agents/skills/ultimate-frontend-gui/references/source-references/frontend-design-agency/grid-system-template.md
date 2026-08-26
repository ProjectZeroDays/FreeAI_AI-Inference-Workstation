# Grid System Template

> **Umsetzungshilfe, keine Standardlösung.**
> Diese Datei ist nicht normativ. Sie darf keine Produktentscheidung vorwegnehmen und keine definierte visuelle These überschreiben.
> Grid-Struktur, Spaltenanzahl und Gap-Werte erst nach Informationsarchitektur und visueller These festlegen. Diese Vorlage zeigt gängige Muster — übernimm nur, was zur Produktlogik passt.

12-Spalten Grid-System für Web-Apps.

## CSS-Variablen

```css
:root {
  /* Grid Configuration */
  --grid-columns: 12;
  --grid-gap: 1.5rem;        /* 24px */
  --grid-gap-sm: 1rem;       /* 16px */
  --grid-gap-lg: 2rem;       /* 32px */

  /* Container */
  --container-max: 1280px;
  --container-padding: 1rem; /* Mobile */
  --container-padding-md: 2rem;
  --container-padding-lg: 3rem;
}
```

## Tailwind Config

```javascript
// tailwind.config.js
module.exports = {
  theme: {
    extend: {
      gridTemplateColumns: {
        '12': 'repeat(12, minmax(0, 1fr))',
      },
      gap: {
        '4.5': '1.125rem',  /* 18px */
      },
    },
  },
};
```

## Grid-Klassen

```css
/* Container */
.container {
  width: 100%;
  max-width: var(--container-max);
  margin-left: auto;
  margin-right: auto;
  padding-left: var(--container-padding);
  padding-right: var(--container-padding);
}

@media (min-width: 768px) {
  .container {
    padding-left: var(--container-padding-md);
    padding-right: var(--container-padding-md);
  }
}

@media (min-width: 1024px) {
  .container {
    padding-left: var(--container-padding-lg);
    padding-right: var(--container-padding-lg);
  }
}

/* Grid */
.grid-12 {
  display: grid;
  grid-template-columns: repeat(12, minmax(0, 1fr));
  gap: var(--grid-gap);
}

/* Spans */
.col-span-1 { grid-column: span 1 / span 1; }
.col-span-2 { grid-column: span 2 / span 2; }
.col-span-3 { grid-column: span 3 / span 3; }
.col-span-4 { grid-column: span 4 / span 4; }
.col-span-5 { grid-column: span 5 / span 5; }
.col-span-6 { grid-column: span 6 / span 6; }
.col-span-7 { grid-column: span 7 / span 7; }
.col-span-8 { grid-column: span 8 / span 8; }
.col-span-9 { grid-column: span 9 / span 9; }
.col-span-10 { grid-column: span 10 / span 10; }
.col-span-11 { grid-column: span 11 / span 11; }
.col-span-12 { grid-column: span 12 / span 12; }

/* Responsive Spans */
@media (min-width: 640px) {
  .sm\:col-span-1 { grid-column: span 1 / span 1; }
  .sm\:col-span-2 { grid-column: span 2 / span 2; }
  .sm\:col-span-3 { grid-column: span 3 / span 3; }
  .sm\:col-span-4 { grid-column: span 4 / span 4; }
  .sm\:col-span-6 { grid-column: span 6 / span 6; }
  .sm\:col-span-8 { grid-column: span 8 / span 8; }
  .sm\:col-span-12 { grid-column: span 12 / span 12; }
}

@media (min-width: 768px) {
  .md\:col-span-1 { grid-column: span 1 / span 1; }
  .md\:col-span-2 { grid-column: span 2 / span 2; }
  .md\:col-span-3 { grid-column: span 3 / span 3; }
  .md\:col-span-4 { grid-column: span 4 / span 4; }
  .md\:col-span-6 { grid-column: span 6 / span 6; }
  .md\:col-span-8 { grid-column: span 8 / span 8; }
  .md\:col-span-9 { grid-column: span 9 / span 9; }
  .md\:col-span-12 { grid-column: span 12 / span 12; }
}

@media (min-width: 1024px) {
  .lg\:col-span-1 { grid-column: span 1 / span 1; }
  .lg\:col-span-2 { grid-column: span 2 / span 2; }
  .lg\:col-span-3 { grid-column: span 3 / span 3; }
  .lg\:col-span-4 { grid-column: span 4 / span 4; }
  .lg\:col-span-6 { grid-column: span 6 / span 6; }
  .lg\:col-span-8 { grid-column: span 8 / span 8; }
  .lg\:col-span-9 { grid-column: span 9 / span 9; }
}
```

## Häufige Layout-Patterns

### 1. Sidebar + Content

```html
<!-- Desktop: Sidebar 3 Spalten, Content 9 Spalten -->
<!-- Mobile: Stacked -->
<div class="grid-12">
  <aside class="col-span-12 lg:col-span-3">
    Sidebar
  </aside>
  <main class="col-span-12 lg:col-span-9">
    Content
  </main>
</div>
```

### 2. Equal Columns

```html
<!-- 3 equal columns -->
<div class="grid grid-cols-1 md:grid-cols-3 gap-6">
  <div>Column 1</div>
  <div>Column 2</div>
  <div>Column 3</div>
</div>

<!-- 4 equal columns -->
<div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
  <div>Column 1</div>
  <div>Column 2</div>
  <div>Column 3</div>
  <div>Column 4</div>
</div>
```

### 3. Asymmetric Layout

```html
<!-- 1/3 + 2/3 split -->
<div class="grid-12">
  <div class="col-span-12 md:col-span-4">
    <!-- Narrow column -->
  </div>
  <div class="col-span-12 md:col-span-8">
    <!-- Wide column -->
  </div>
</div>

<!-- Golden Ratio (38% + 62%) -->
<div class="grid-12">
  <div class="col-span-12 lg:col-span-5">
    Left
  </div>
  <div class="col-span-12 lg:col-span-7">
    Right
  </div>
</div>
```

### 4. Dashboard Grid

```html
<!-- KPI Cards row -->
<div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6 mb-6">
  <KpiCard />
  <KpiCard />
  <KpiCard />
  <KpiCard />
</div>

<!-- Charts + Lists -->
<div class="grid-12">
  <div class="col-span-12 lg:col-span-8">
    <Chart />
  </div>
  <div class="col-span-12 lg:col-span-4">
    <RecentActivity />
  </div>
</div>
```

### 5. Card Grid

```html
<!-- Auto-fit responsive -->
<div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
  <Card />
  <Card />
  <Card />
  <Card />
  <Card />
  <Card />
</div>

/* Oder mit CSS Grid */
.card-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 1.5rem;
}
```

### 6. Feature Sections

```html
<!-- Alternating image + text -->
<section class="grid-12 items-center">
  <div class="col-span-12 lg:col-span-6 order-2 lg:order-1">
    <h2>Feature Title</h2>
    <p>Description...</p>
  </div>
  <div class="col-span-12 lg:col-span-6 order-1 lg:order-2">
    <img src="..." />
  </div>
</section>
```

## Spacing-System

```css
/* Consistent Spacing Scale */
.space-0  { gap: 0; }
.space-1  { gap: 0.25rem; }   /* 4px */
.space-2  { gap: 0.5rem; }    /* 8px */
.space-3  { gap: 0.75rem; }  /* 12px */
.space-4  { gap: 1rem; }      /* 16px */
.space-6  { gap: 1.5rem; }    /* 24px */
.space-8  { gap: 2rem; }      /* 32px */
.space-12 { gap: 3rem; }      /* 48px */
.space-16 { gap: 4rem; }      /* 64px */
```

## Breakpoint-Zuordnung

| Breakpoint | Typisches Layout | Karten pro Reihe |
|------------|------------------|------------------|
| < 640px | Single column | 1 |
| 640px+ | 2 columns | 2 |
| 768px+ | Tablet | 2-3 |
| 1024px+ | Desktop | 3-4 |
| 1280px+ | Wide | 4-6 |

## Grid-Checkliste

- [ ] Container max-width definiert?
- [ ] Padding an Breakpoints angepasst?
- [ ] Gap-Konsistenz (nur Werte aus Scale)?
- [ ] Mobile-first Approach?
- [ ] Komplexe Layouts getestet?
- [ ] Keine horizontalen Scrollbars?
