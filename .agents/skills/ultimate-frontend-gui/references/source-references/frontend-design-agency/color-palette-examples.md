# Color Palette — Entscheidungsrahmen

> **Umsetzungshilfe, keine Standardlösung.**
> Diese Datei ist nicht normativ. Sie darf keine Produktentscheidung vorwegnehmen und keine definierte visuelle These überschreiben.
> Farbentscheidungen ergeben sich aus Produkttyp, visueller These und Markenrahmen. Definiere zuerst Farbrollen und Kontrastlogik, dann wähle konkrete Werte. Übernimm keine Paletten aus dieser Datei als Default.

## Schritt 1: Farbrollen definieren

Jede Palette braucht klar definierte Rollen. Rollen vor Farben.

```css
/* 1. Canvas (Seiten-Hintergrund) */
--canvas

/* 2. Surfaces (Karten, Panels, erhöhte Flächen) */
--surface           /* Standard erhöht */
--surface-elevated  /* Höherer z-index */
--surface-subtle    /* Niedrigere Betonung */

/* 3. Text (Hierarchie durch Kontrast) */
--text-strong       /* Überschriften, primärer Text */
--text-default      /* Fließtext */
--text-muted        /* Sekundär, Meta-Informationen */
--text-placeholder  /* Leerzustände, Platzhalter */

/* 4. Actions (primäre Interaktion) */
--primary           /* Hauptaktion, CTA */
--primary-hover
--primary-active
--primary-subtle    /* Hintergrund-Tönung */
--primary-foreground /* Text auf Primary */

/* 5. Semantische States */
--success
--success-subtle
--warning
--warning-subtle
--danger
--danger-subtle

/* 6. Borders (Strukturierung) */
--border-default
--border-strong
--border-subtle
```

## Schritt 2: Farbtemperatur und Charakter wählen

| Charakter | Canvas-Tendenz | Grautöne | Primary-Tendenz | Wirkung |
|-----------|---------------|----------|-----------------|---------|
| Kühl/Professionell | Neutrales Weiß/Grau | Bläuliches Grau (Slate) | Blau-Spektrum | Vertrauen, Professionalität |
| Warm/Einladend | Leicht warmes Weiß | Warmes Grau (Stone) | Amber/Orange-Spektrum | Nahbarkeit, Wärme |
| Natürlich/Ruhig | Leicht grünliches Weiß | Olive/Sage Grau | Grün-Spektrum | Ruhe, Gesundheit |
| Mutig/Kreativ | Neutrales oder dunkles Canvas | Neutrales Grau | Violett/Pink-Spektrum | Innovation, Energie |
| Technisch/Fokussiert | Dunkles Canvas (Dark Mode first) | Bläuliches Dunkelgrau | Cyan/Electric Blue | Modernität, Fokus |

**Entscheidungsfragen:**
- Welche emotionale Wirkung soll das Produkt haben?
- Warm oder kühl? Hell oder dunkel? Satt oder gedeckt?
- Braucht das Produkt einen Dark Mode? Wenn ja: gleich mitdenken.

## Schritt 3: Kontrastlogik sicherstellen

| Kombination | Mindest-Kontrast | Level |
|-------------|-----------------|-------|
| `--text-strong` auf `--surface` | ≥ 7:1 | AAA |
| `--text-default` auf `--surface` | ≥ 4.5:1 | AA |
| `--text-muted` auf `--surface` | ≥ 4.5:1 | AA |
| `--primary` auf `--surface` | ≥ 3:1 | AA (UI) |
| `--primary-foreground` auf `--primary` | ≥ 4.5:1 | AA |

**Regel:** Prüfe Kontraste immer für Light und Dark Mode separat.

## Schritt 4: Einsatzregeln festlegen

Vor der Implementierung klären:

- **Primary:** Nur für die wichtigste Aktion pro View. Nicht inflationär einsetzen.
- **Success/Warning/Danger:** Nur semantisch, nie dekorativ.
- **Surface-Varianten:** Hierarchie durch subtile Helligkeitsunterschiede, nicht durch Farbe.
- **Borders:** So wenig wie möglich, so viel wie nötig. Flächen-Hierarchie bevorzugen.
- **Accent (optional):** Nur wenn das Produkt eine sekundäre Aktionsfarbe braucht.

## Beispiel-Richtungen (nicht normativ)

Diese drei Richtungen zeigen die Bandbreite. Sie sind Ausgangspunkte, keine Paletten zum Kopieren.

### Richtung A: Kühl/Professionell (B2B, Enterprise)
- Canvas: Neutrales Grau (#fafafa)
- Grau-Familie: Slate (bläulich)
- Primary: Blau-Spektrum (Trust Blue)
- Charakter: Sachlich, verlässlich, zurückhaltend

### Richtung B: Warm/Premium (Fintech, Lifestyle)
- Canvas: Warmes Weiß (#fdfcfb)
- Grau-Familie: Stone (warm)
- Primary: Amber/Gold-Spektrum
- Charakter: Exklusiv, einladend, wertig

### Richtung C: Natürlich/Ruhig (Health, Wellness)
- Canvas: Leicht grünliches Weiß (#f6f7f6)
- Grau-Familie: Sage/Olive
- Primary: Grün-Spektrum
- Charakter: Beruhigend, vertrauensvoll, organisch

## Dark Mode Hinweise

- Dark Mode ist keine Farb-Inversion. Surfaces werden dunkler, nicht invertiert.
- Primärfarben oft heller und entsättigter als im Light Mode.
- Borders subtiler (weniger Kontrast, mehr Flächen-Hierarchie).
- Schatten funktionieren anders — durch hellere Surfaces ersetzen oder Glow-Effekte.
- `prefers-color-scheme` respektieren, User-Präferenz speichern.

## Dark Mode Toggle (Referenz)

```javascript
function toggleTheme() {
  const current = document.documentElement.getAttribute('data-theme');
  const next = current === 'dark' ? 'light' : 'dark';
  document.documentElement.setAttribute('data-theme', next);
  localStorage.setItem('theme', next);
}

const saved = localStorage.getItem('theme');
const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
document.documentElement.setAttribute('data-theme', saved || (prefersDark ? 'dark' : 'light'));
```

## Checkliste

- [ ] Farbrollen definiert (Canvas, Surface, Text, Primary, States, Borders)?
- [ ] Farbtemperatur und Charakter bewusst gewählt?
- [ ] Kontraste geprüft (Text ≥ 4.5:1, UI ≥ 3:1)?
- [ ] Primary nur für Hauptaktion reserviert?
- [ ] Semantische Farben nur semantisch eingesetzt?
- [ ] Dark Mode mitgedacht (falls relevant)?
- [ ] Palette zur visuellen These passend?
