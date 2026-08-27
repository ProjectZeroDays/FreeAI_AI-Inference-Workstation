# Accessibility Checklist

WCAG 2.1 Level AA Compliance für Web-App-Frontends.

## Perceivable (Wahrnehmbar)

### Text Alternatives
- [ ] Bilder haben sinnvolle `alt`-Texte
- [ ] Dekorative Bilder haben `alt=""` oder `aria-hidden="true"`
- [ ] Icons haben `aria-label` oder sind mit Text verbunden
- [ ] Complex charts haben textuelle Alternativen

### Adaptable
- [ ] Keine Information nur durch Farbe vermittelt
- [ ] Inhalte sind bei 200% Zoom noch nutzbar
- [ ] Inhalte bei 400% Zoom noch scrollbar (Reflow)
- [ ] Tabelle haben `<th>` mit Scope oder Headers

### Distinguishable
- [ ] Kontrast Text : Hintergrund ≥ 4.5:1 (Normal)
- [ ] Kontrast Text : Hintergrund ≥ 3:1 (Large 18px+/Bold 14px+)
- [ ] Kontrast UI-Elemente : Hintergrund ≥ 3:1
- [ ] Links erkennbar ohne Farbe (Unterstreichung/Fett)
- [ ] Text kann auf 200% vergrößert werden
- [ ] Keine horizontalen Scrollbars bis 320px Breite

## Operable (Bedienbar)

### Keyboard Accessible
- [ ] Alle Funktionen per Tastatur erreichbar
- [ ] Keine Tastaturfallen (keyboard traps)
- [ ] `Tab`-Reihenfolge logisch
- [ ] Fokus ist sichtbar (Outline nicht entfernt)
- [ ] Skip-Links für wiederholende Inhalte

### Enough Time
- [ ] Automatisch ablaufende Inhalte können pausiert werden
- [ ] Formular-Timeouts sind konfigurierbar
- [ ] Keine unerwarteten automatischen Aktualisierungen

### Seizures
- [ ] Keine Inhalte blinken mehr als 3x pro Sekunde

### Navigable
- [ ] Seite hat einen beschreibenden `<title>`
- [ ] Überschriften-Hierarchie ist logisch (h1 → h2 → h3)
- [ ] Links haben beschreibenden Text (kein "Hier klicken")
- [ ] Fokus-Reihenfolge ist logisch
- [ ] Mehrere Wege zu Inhalten verfügbar (nicht nur Menü)

## Understandable (Verständlich)

### Readable
- [ ] Sprache der Seite mit `lang`-Attribut definiert
- [ ] Fremdsprachige Wörter markiert mit `lang`

### Predictable
- [ ] Navigation konsistent auf allen Seiten
- [ ] Komponente verhalten sich konsistent
- [ ] Formular-Validierung zeigt Fehler klar an

### Input Assistance
- [ ] Formular-Felder haben Labels (`<label for="...">`)
- [ ] Erforderliche Felder sind markiert
- [ ] Fehler werden neben dem Feld angezeigt
- [ ] Fehlermeldungen beschreiben das Problem + Lösung
- [ ] Suggestions für Fehlerkorrektur verfügbar

## Robust (Robust)

### Compatible
- [ ] Valides HTML
- [ ] ARIA-Attribute korrekt verwendet
- [ ] Keine veralteten ARIA-Attribute
- [ ] Status-Meldungen mit `role="status"` oder `aria-live`

## Komponenten-spezifisch

### Buttons
- [ ] Haben beschreibenden Text oder `aria-label`
- [ ] Disabled-Status ist für Screenreader erkennbar
- [ ] Loading-Status wird angekündigt

### Links
- [ ] Unterscheidbar von Buttons
- [ ] Beschreiben das Ziel
- [ ] Externe Links markieren Ziel

### Forms
- [ ] Jedes Input hat ein `<label>`
- [ ] Placeholder nicht als einzige Beschriftung
- [ ] `aria-describedby` für Hilfstexte
- [ ] Fehler mit `aria-invalid="true"` und `aria-describedby`
- [ ] Fieldsets für Gruppen (Radio, Checkbox)

### Modals/Dialogs
- [ ] Fokus wird in Modal verschoben
- [ ] Fokus bleibt im Modal (trap)
- [ ] ESC schließt Modal
- [ ] Fokus zurück zum Trigger nach Schließen
- [ ] `role="dialog"` und `aria-modal="true"`
- [ ] `aria-labelledby` für Titel

### Navigation
- [ ] `<nav>` oder `role="navigation"`
- [ ] Aktiver Link markiert mit `aria-current="page"`
- [ ] Mobile Menu: Toggle-Button mit `aria-expanded`
- [ ] Dropdowns: `aria-expanded`, `aria-haspopup`

### Tables
- [ ] `<caption>` für Tabellen-Titel
- [ ] `<th>` mit `scope="col"` oder `scope="row"`
- [ ] Komplexe Tabellen: `headers` Attribute

### Tabs
- [ ] `role="tablist"`, `role="tab"`, `role="tabpanel"`
- [ ] `aria-selected` für aktiven Tab
- [ ] `aria-controls` verbindet Tab mit Panel
- [ ] Pfeiltasten für Tab-Navigation

### Accordions
- [ ] `aria-expanded` für Toggle-Status
- [ ] `aria-controls` für Verbindung zum Content

## Testing

### Automatisierte Tests
- [ ] axe-core oder Lighthouse keine Errors
- [ ] Keine Kontrast-Fehler
- [ ] Semantisches HTML validiert

### Manuelle Tests
- [ ] Tab-Navigation durch gesamte Seite
- [ ] Screenreader-Test (VoiceOver/NVDA)
- [ ] Zoom 200% und 400%
- [ ] Mobile Screenreader (VoiceOver iOS/TalkBack)

### Tools
- **Kontrast**: WebAIM Contrast Checker
- **Test**: axe DevTools
- **Screenreader**: NVDA (Windows), VoiceOver (Mac)
- **Validierung**: W3C HTML Validator

## Prioritäten

### P0 - Kritisch (Blocker)
- Bilder ohne Alt-Text
- Formulare ohne Labels
- Keine Tastaturbedienbarkeit
- Tastaturfallen

### P1 - Hoch
- Fehlende Fokus-Indikatoren
- Unzureichender Kontrast
- Fehlende Überschriften-Hierarchie

### P2 - Mittel
- Skip-Links
- Sprachattribute
- Status-Ankündigungen

### P3 - Niedrig
- Verfeinerungen
- Erweiterte ARIA-Patterns
