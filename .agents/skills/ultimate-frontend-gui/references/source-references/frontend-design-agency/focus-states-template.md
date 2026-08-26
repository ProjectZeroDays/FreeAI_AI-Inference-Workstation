# Focus States Template

> **Umsetzungshilfe, keine Standardlösung.**
> Diese Datei ist nicht normativ. Sie darf keine Produktentscheidung vorwegnehmen und keine definierte visuelle These überschreiben.
> Focus-Styling an die definierten Design Tokens und die visuelle Sprache des Projekts anpassen. Die Patterns hier zeigen bewährte Techniken — Farben, Offsets und Stärken müssen zum Designsystem passen.

Barrierefreie und sichtbare Focus-Indikatoren.

## Warum Focus States wichtig sind

- **Tastatur-Navigation** ohne Focus-States unmöglich
- **Rechtlich** erforderlich (WCAG 2.1)
- **Nutzerfreundlich** für Power-User
- **Accessibility** für screen reader Nutzer

## Basis CSS

```css
/* Entferne niemals den Focus-Outline komplett */
:focus {
  outline: none; /* Nur wenn du einen Ersatz definierst! */
}

/* Standard Focus-Ring */
:focus-visible {
  outline: 2px solid var(--primary);
  outline-offset: 2px;
}

/* Für Form-Elemente */
input:focus-visible,
textarea:focus-visible,
select:focus-visible {
  outline: none;
  border-color: var(--primary);
  box-shadow: 0 0 0 3px rgba(var(--primary-rgb), 0.2);
}

/* Reduced Motion - Nutzer-Präferenz respektieren */
@media (prefers-reduced-motion: reduce) {
  :focus-visible {
    transition: none;
  }
}
```

## Komponenten-spezifisch

### Button Focus

```css
/* Primary Button */
.btn-primary:focus-visible {
  outline: 2px solid var(--primary);
  outline-offset: 2px;
  box-shadow: 0 0 0 4px rgba(var(--primary-rgb), 0.2);
}

/* Ghost Button */
.btn-ghost:focus-visible {
  background-color: var(--surface-subtle);
  outline: 2px solid var(--primary);
  outline-offset: 2px;
}

/* Icon Button */
.btn-icon:focus-visible {
  outline: 2px solid var(--primary);
  outline-offset: 2px;
  border-radius: var(--radius);
}
```

### Input Focus

```css
/* Text Input */
.input:focus-visible {
  border-color: var(--primary);
  box-shadow: 0 0 0 3px rgba(var(--primary-rgb), 0.15);
}

/* Error State + Focus */
.input-error:focus-visible {
  border-color: var(--danger);
  box-shadow: 0 0 0 3px rgba(var(--danger-rgb), 0.15);
}

/* Search Input */
.search-input:focus-visible {
  border-color: var(--primary);
  box-shadow: 0 0 0 3px rgba(var(--primary-rgb), 0.15),
              0 4px 12px rgba(0, 0, 0, 0.1);
}
```

### Link Focus

```css
/* Inline Links */
a:focus-visible {
  outline: 2px solid var(--primary);
  outline-offset: 2px;
  border-radius: 2px;
}

/* Navigation Links */
.nav-link:focus-visible {
  outline: 2px solid var(--primary);
  outline-offset: 4px;
  border-radius: var(--radius);
}

/* Skip Link */
.skip-link:focus-visible {
  position: fixed;
  top: 0;
  left: 0;
  z-index: 9999;
  padding: 0.5rem 1rem;
  background: var(--primary);
  color: var(--primary-foreground);
  outline: none;
}
```

### Card Focus

```css
/* Clickable Card */
.card-clickable:focus-visible {
  outline: 2px solid var(--primary);
  outline-offset: 2px;
  box-shadow: 0 0 0 4px rgba(var(--primary-rgb), 0.1);
}

/* Card mit Actions */
.card:focus-within {
  box-shadow: 0 0 0 2px var(--primary);
}

/* Focus-within für Form-Cards */
.form-card:focus-within {
  border-color: var(--primary);
}
```

### Custom Components

```css
/* Tabs */
.tab:focus-visible {
  outline: 2px solid var(--primary);
  outline-offset: -2px;
}

/* Accordion */
.accordion-trigger:focus-visible {
  outline: 2px solid var(--primary);
  outline-offset: -2px;
  border-radius: var(--radius);
}

/* Dropdown Menu Items */
.menu-item:focus-visible {
  background-color: var(--surface-subtle);
  outline: 2px solid var(--primary);
  outline-offset: -2px;
}

/* Toggle/Switch */
.switch:focus-visible {
  outline: 2px solid var(--primary);
  outline-offset: 2px;
}

/* Slider */
.slider-thumb:focus-visible {
  outline: 2px solid var(--primary);
  outline-offset: 2px;
  box-shadow: 0 0 0 4px rgba(var(--primary-rgb), 0.2);
}
```

## Tailwind Implementierung

```tsx
// Reusable Focus Utilities
const focusRing = "focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary focus-visible:ring-offset-2";
const focusRingInset = "focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary focus-visible:ring-inset";
const focusBorder = "focus-visible:border-primary focus-visible:ring-3 focus-visible:ring-primary/20";

// Button
<Button className={focusRing}>
  Click me
</Button>

// Input
<Input className={focusBorder} />

// Link
<a href="#" className={`${focusRing} rounded-sm`}>
  Link text
</a>

// Card
<div
  role="button"
  tabIndex={0}
  className={`${focusRing} cursor-pointer`}
>
  Clickable Card
</div>
```

## Skip Link

```tsx
// Am Anfang des Body
<a
  href="#main-content"
  className="sr-only focus:not-sr-only focus:fixed focus:top-4 focus:left-4
             focus:z-50 focus:bg-primary focus:text-white focus:px-4 focus:py-2
             focus:rounded-md"
>
  Zum Hauptinhalt springen
</a>

// Main content
<main id="main-content">
  {/* Content */}
</main>
```

## Focus Order (Tab-Reihenfolge)

```html
<!-- Logische Reihenfolge -->
<nav>
  <a href="#1">Link 1</a>
  <a href="#2">Link 2</a>
  <a href="#3">Link 3</a>
</nav>

<!-- Tabindex vermeiden wenn möglich -->
<!-- tabindex="0" - Fügt Element in Tab-Reihenfolge ein -->
<!-- tabindex="-1" - Nur programmatisch fokussierbar -->
<!-- tabindex=">0" - VERMEIDEN (bricht logische Reihenfolge) -->

<div role="button" tabIndex={0} onClick={...} onKeyDown={...}>
  Click me
</div>
```

## Focus Indikatoren - Best Practices

### Kontrast

```css
/* Focus-Outline muss gut sichtbar sein */
/* Mindestens 3:1 Kontrast zum Hintergrund */

/* Gut */
:focus-visible {
  outline: 2px solid #2563eb; /* Blau auf Weiß = 5.8:1 */
}

/* Schlecht */
:focus-visible {
  outline: 1px dashed #ccc; /* Zu schwach */
}
```

### Offset

```css
/* Mit Offset */
:focus-visible {
  outline: 2px solid var(--primary);
  outline-offset: 2px; /* Abstand zum Element */
}

/* Ohne Offset (für innere Elemente) */
.inset-focus:focus-visible {
  outline-offset: -2px; /* Innerhalb des Elements */
}
```

### Transition

```css
/* Sanfter Übergang */
.interactive-element {
  transition: outline-offset 0.15s ease-out;
}

.interactive-element:focus-visible {
  outline-offset: 2px;
  transition: outline-offset 0.15s ease-out;
}
```

## Testing

### Manuelle Tests

1. **Tab-Navigation:** Drücke Tab durch die ganze Seite
2. **Shift+Tab:** Rückwärts-Navigation
3. **Enter:** Aktiviere Links und Buttons
4. **Space:** Aktiviere Buttons, Checkboxes
5. **Arrow Keys:** Navigation in Menüs, Tabs, Radio Groups

### Was zu prüfen

- [ ] Jedes interaktive Element hat Focus-Indikator
- [ ] Focus-Reihenfolge ist logisch
- [ ] Focus-Indikator ist sichtbar
- [ ] Keine Focus-Fallen (kein Escape möglich)
- [ ] Modals trap Focus
- [ ] Skip Link funktioniert

## Common Mistakes

```css
/* ❌ Niemals */
:focus { outline: none; } /* Ohne Ersatz! */

/* ❌ Zu schwach */
:focus { outline: 1px dotted gray; }

/* ❌ Nur Farb-Änderung */
.btn:focus { background: blue; } /* Nicht ausreichend */

/* ✅ Richtig */
:focus-visible {
  outline: 2px solid var(--primary);
  outline-offset: 2px;
}
```

## Checkliste

- [ ] Alle interaktiven Elemente haben `:focus-visible`?
- [ ] Focus-Indikator hat ≥ 3:1 Kontrast?
- [ ] Focus-Reihenfolge ist logisch?
- [ ] Skip Link vorhanden?
- [ ] Modals trap Focus?
- [ ] Keine positiven tabindex Werte?
- [ ] Custom Controls haben Keyboard-Support?
- [ ] Reduced Motion berücksichtigt?
