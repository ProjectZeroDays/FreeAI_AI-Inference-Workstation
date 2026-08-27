# Typography Scale Template

> **Umsetzungshilfe, keine Standardlösung.**
> Typografie-Entscheidungen ergeben sich aus der visuellen These und dem Produkttyp. Definiere zuerst die Rollen und die gewünschte Wirkung, dann wähle passende Schriften. Übernimm keine Fonts aus dieser Datei als Default.

## Schritt 1: Typografie-Rollen definieren

Jedes Projekt braucht mindestens drei Schrift-Rollen. Definiere die Rollen vor der Font-Wahl:

| Rolle | Zweck | Wirkung klären |
|-------|-------|----------------|
| **Display** | Headlines, Hero-Texte, große Statements | Welchen Charakter soll die Marke ausstrahlen? |
| **Body** | Fließtext, Labels, Navigation, UI-Text | Lesbarkeit und Neutralität oder Persönlichkeit? |
| **Mono** | Code, technische Werte, IDs, Daten | Braucht das Produkt überhaupt eine Monospace-Rolle? |

**Entscheidungsfragen:**
- Soll Display sich deutlich von Body unterscheiden (Kontrast-Pairing) oder harmonisch sein (gleiche Familie)?
- Serif, Sans-Serif oder etwas anderes — was passt zur visuellen These?
- Braucht das Produkt eine vierte Rolle (z.B. Accent, Handschrift, Condensed)?

## Schritt 2: Stilrichtung wählen

| Stilrichtung | Display-Typ | Body-Typ | Wirkung |
|-------------|-------------|----------|---------|
| Klassisch/Editorial | Display Serif | Neutral Sans | Autorität, Tiefe, Lesbarkeit |
| Modern/Technisch | Geometric Sans oder Grotesk | Neutral Sans | Klarheit, Präzision, Modernität |
| Freundlich/Warm | Rounded Serif oder Soft Sans | Humanist Sans | Nahbarkeit, Vertrauen |
| Mutig/Dramatisch | Condensed Sans oder Slab | Neutral Sans | Energie, Dichte, Aufmerksamkeit |
| Minimal/Swiss | Grotesk (eine Familie) | Gleiche Familie | Reduktion, System, Eleganz |

**Beispiel-Fonts pro Stilrichtung (optional, nicht normativ):**

| Stilrichtung | Display-Beispiele | Body-Beispiele |
|-------------|-------------------|----------------|
| Klassisch/Editorial | Playfair Display, Lora, Fraunces | Inter, Source Sans, Libre Franklin |
| Modern/Technisch | Space Grotesk, Outfit, Sora | Inter, IBM Plex Sans, Geist |
| Freundlich/Warm | DM Serif, Merriweather | DM Sans, Nunito, Public Sans |
| Mutig/Dramatisch | Oswald, Barlow Condensed | Source Sans Pro, Work Sans |
| Minimal/Swiss | Switzer, Satoshi, General Sans | Gleiche Familie wie Display |

## Schritt 3: Type Scale festlegen

### Skalen-Verhältnis wählen

Das Verhältnis bestimmt den visuellen Rhythmus:

| Verhältnis | Faktor | Wirkung | Geeignet für |
|-----------|--------|---------|--------------|
| Minor Second | 1.067 | Sehr eng, subtil | Kompakte Data-UIs |
| Major Second | 1.125 | Eng, funktional | Admin-Panels, Dense Layouts |
| Minor Third | 1.200 | Ausgewogen | SaaS-Apps, Standard-UIs |
| **Major Third** | **1.250** | **Gut lesbar, klar** | **Empfohlen als Ausgangspunkt** |
| Perfect Fourth | 1.333 | Deutliche Hierarchie | Editorial, Marketing |
| Golden Ratio | 1.618 | Dramatisch | Landing Pages, Hero-Bereiche |

### Größen-Definition

```css
:root {
  /* Rolle: Display → hier Font-Family einsetzen */
  --font-display: /* Projekt-spezifisch */;
  /* Rolle: Body → hier Font-Family einsetzen */
  --font-body: /* Projekt-spezifisch */;
  /* Rolle: Mono → hier Font-Family einsetzen (falls benötigt) */
  --font-mono: /* Projekt-spezifisch */;

  /* Type Scale — Verhältnis an Produkt anpassen */
  --text-2xs: 0.625rem;    /* 10px */
  --text-xs: 0.75rem;      /* 12px */
  --text-sm: 0.875rem;     /* 14px */
  --text-base: 1rem;       /* 16px */
  --text-lg: 1.125rem;     /* 18px */
  --text-xl: 1.25rem;      /* 20px */
  --text-2xl: 1.5rem;      /* 24px */
  --text-3xl: 1.875rem;    /* 30px */
  --text-4xl: 2.25rem;     /* 36px */
  --text-5xl: 3rem;        /* 48px */
  --text-6xl: 3.75rem;     /* 60px */

  /* Font Weights */
  --font-normal: 400;
  --font-medium: 500;
  --font-semibold: 600;
  --font-bold: 700;

  /* Line Heights */
  --leading-none: 1;
  --leading-tight: 1.25;
  --leading-snug: 1.375;
  --leading-normal: 1.5;
  --leading-relaxed: 1.625;
  --leading-loose: 2;

  /* Letter Spacing */
  --tracking-tighter: -0.05em;
  --tracking-tight: -0.025em;
  --tracking-normal: 0;
  --tracking-wide: 0.025em;
  --tracking-wider: 0.05em;
  --tracking-widest: 0.1em;
}
```

## Schritt 4: Elemente zuordnen

| Element | Größe | Gewicht | Zeilenhöhe | Tracking | Schrift-Rolle |
|---------|-------|---------|------------|----------|---------------|
| Display | 3.75rem (60px) | 700 | 1.1 | -0.02em | Display |
| H1 | 3rem (48px) | 700 | 1.2 | -0.02em | Display |
| H2 | 1.875rem (30px) | 600 | 1.3 | -0.01em | Display |
| H3 | 1.5rem (24px) | 600 | 1.4 | 0 | Body |
| H4 | 1.25rem (20px) | 600 | 1.4 | 0 | Body |
| H5 | 1.125rem (18px) | 600 | 1.5 | 0 | Body |
| H6 | 1rem (16px) | 600 | 1.5 | 0.025em | Body |
| Body Large | 1.125rem (18px) | 400 | 1.6 | 0 | Body |
| Body | 1rem (16px) | 400 | 1.6 | 0 | Body |
| Body Small | 0.875rem (14px) | 400 | 1.5 | 0 | Body |
| Caption | 0.75rem (12px) | 400 | 1.5 | 0.025em | Body |
| Overline | 0.75rem (12px) | 600 | 1.5 | 0.1em | Body |
| Label | 0.875rem (14px) | 500 | 1.25 | 0.025em | Body |
| Mono | 0.875rem (14px) | 400 | 1.5 | 0 | Mono |

## Schritt 5: Responsive Skalierung

Für mobile Geräte reduziere Display-Größen:

```css
@media (max-width: 768px) {
  :root {
    --text-6xl: 2.25rem;  /* 36px statt 60px */
    --text-5xl: 1.875rem; /* 30px statt 48px */
    --text-4xl: 1.5rem;   /* 24px statt 36px */
  }
}
```

## Tailwind Config (Muster)

```javascript
// tailwind.config.js — Fonts projekt-spezifisch einsetzen
module.exports = {
  theme: {
    fontFamily: {
      display: [/* Display-Rolle */],
      body: [/* Body-Rolle */],
      mono: [/* Mono-Rolle */],
    },
    fontSize: {
      '2xs': ['0.625rem', { lineHeight: '1.5' }],
      'xs': ['0.75rem', { lineHeight: '1.5' }],
      'sm': ['0.875rem', { lineHeight: '1.5' }],
      'base': ['1rem', { lineHeight: '1.6' }],
      'lg': ['1.125rem', { lineHeight: '1.6' }],
      'xl': ['1.25rem', { lineHeight: '1.4' }],
      '2xl': ['1.5rem', { lineHeight: '1.3' }],
      '3xl': ['1.875rem', { lineHeight: '1.2' }],
      '4xl': ['2.25rem', { lineHeight: '1.2' }],
      '5xl': ['3rem', { lineHeight: '1.1' }],
      '6xl': ['3.75rem', { lineHeight: '1.1' }],
    },
  },
};
```

## Checkliste

- [ ] Typografie-Rollen definiert (Display, Body, Mono)?
- [ ] Stilrichtung passt zur visuellen These?
- [ ] Type Scale Verhältnis bewusst gewählt?
- [ ] Font-Families ausgewählt und geladen?
- [ ] Line Heights angepasst?
- [ ] Font Weights konsistent?
- [ ] Responsive Breakpoints berücksichtigt?
- [ ] Font Loading optimiert (swap)?
- [ ] Rollen-Zuordnung dokumentiert?
