# Product Requirements Checklist

Systematische Erfassung vor dem Design.

## Section 1: Kontext & Ziele

### Produktverständnis
- [ ] Produkttyp definiert (B2B SaaS, B2C App, internal Tool)?
- [ ] Kernfunktion des Produkts erklärt?
- [ ] Hauptnutzerrolle identifiziert?
- [ ] Sekundäre Nutzerrollen bekannt?
- [ ] Primäre Nutzeraufgabe dokumentiert?
- [ ] Erfolgskriterium für diese Aufgabe definiert?

### Geschäftsziele
- [ ] Was soll die UI bewirken?
- [ ] Primäre Conversion definiert?
- [ ] Metriken zur Erfolgsmessung?
- [ ] Timeline / Deadline?

## Section 2: Nutzer & Nutzung

### Nutzerprofil
- [ ] Altersgruppe?
- [ ] Technische Kompetenz?
- [ ] Häufigkeit der Nutzung?
- [ ] Nutzungsdauer pro Session?
- [ ] Primäres Gerät?
- [ ] Nutzungskontext (Büro, unterwegs, etc.)?

### Pain Points
- [ ] Aktuelle Probleme dokumentiert?
- [ ] Workarounds identifiziert?
- [ ] Wettbewerbslücken gefunden?
- [ ] Nutzerzitate gesammelt?

## Section 3: Inhalt & Funktion

### Daten & Inhalte
- [ ] Welche Daten werden angezeigt?
- [ ] Datenquellen bekannt?
- [ ] Datenaktualisierungsfrequenz?
- [ ] Beispieldaten verfügbar?
- [ ] Leer- und Fehlerfälle definiert?

### Funktionale Anforderungen
- [ ] Muss-Features (P0) gelistet?
- [ ] Soll-Features (P1) gelistet?
- [ ] Kann-Features (P2) gelistet?
- [ ] Nicht-Funktionale Anforderungen?
  - [ ] Performance-Requirements?
  - [ ] Browser-Support?
  - [ ] Device-Support?

## Section 4: Visuelle Anforderungen

### Markenrahmen
- [ ] Existierendes Branding?
- [ ] Logo, Farben, Fonts vorhanden?
- [ ] Brand Guidelines vorhanden?
- [ ] CI/CD Vorgaben?

### Design-Präferenzen
- [ ] Referenz-Websites identifiziert?
- [ ] Gewünschter Stil grob definiert?
- [ ] Light/Dark/Both?
- [ ] Spielraum für kreative Freiheit?

## Section 5: Technische Constraints

### Stack
- [ ] Framework definiert (Next.js, React, Vue)?
- [ ] UI Library (shadcn, Material, etc.)?
- [ ] Styling-Lösung (Tailwind, CSS Modules)?
- [ ] State Management?
- [ ] API / Datenhandling?

### Integrationen
- [ ] Existierende Design Systeme?
- [ ] Third-party Komponenten?
- [ ] Icon-Library?
- [ ] Analytics Requirements?

## Section 6: Architektur

### Seiten/Ansichten
- [ ] Liste aller Seiten?
- [ ] Seitenhierarchie?
- [ ] Navigation-Struktur?
- [ ] User Flows dokumentiert?

### Komponenten
- [ ] Wiederverwendbare Elemente identifiziert?
- [ ] Komplexe Komponenten spezifiziert?
- [ ] Interaktions-Muster definiert?

## Section 7: Qualitätsanforderungen

### Accessibility
- [ ] WCAG-Level definiert (AA/AAA)?
- [ ] Screenreader-Support gefordert?
- [ ] Tastatur-Navigation gefordert?
- [ ] Barrierefreiheit gesetzlich relevant?

### Responsiveness
- [ ] Mobile-First oder Desktop-First?
- [ ] Breakpoints definiert?
- [ ] Mobile-Prioritäten?
- [ ] Tablet-Optimierung nötig?

### Performance
- [ ] Ladezeit-Requirements?
- [ ] Time-to-Interactive Ziel?
- [ ] Bundle-Size-Limits?
- [ ] Animation-Performance?

## Section 8: Deliverables

### Output
- [ ] Code-Repository definiert?
- [ ] Deployment-Prozess bekannt?
- [ ] Review/Approval-Prozess?
- [ ] Dokumentations-Anforderungen?

### Testing
- [ ] Test-Devices verfügbar?
- [ ] Beta-Tester identifiziert?
- [ ] Feedback-Runden geplant?

## Final Review

### Vor Design-Start
- [ ] Alle P0-Anforderungen klar?
- [ ] User Persona verfügbar?
- [ ] Visuelle Richtung abgestimmt?
- [ ] Technische Machbarkeit geprüft?
- [ ] Timeline realistisch?

### Vor Implementierungs-Start
- [ ] Design approved?
- [ ] Assets (Bilder, Icons) bereit?
- [ ] API-Contracts final?
- [ ] Test-Daten verfügbar?

---

## Quick-Start Template

```markdown
# Project: [Name]

## 1. Basics
- **Type:** [B2B SaaS / B2C / Internal]
- **Primary User:** [Rolle]
- **Main Task:** [Aufgabe]
- **Success:** [Woran erkennen wir Erfolg?]

## 2. Must-Have Features
1. [Feature 1]
2. [Feature 2]
3. [Feature 3]

## 3. Tech Stack
- Framework: [Next.js / React / Vue]
- Styling: [Tailwind / CSS]
- UI Lib: [shadcn / Material]

## 4. Design Direction
- Style: [Minimal / Bold / Playful]
- References: [URL 1], [URL 2]
- Theme: [Light / Dark / Both]

## 5. Constraints
- Deadline: [Datum]
- Devices: [Desktop / Mobile / Both]
- Browser: [Chrome / Safari / IE11?]

## 6. Deliverables
- [ ] Design Mockups
- [ ] Working Prototype
- [ ] Production Code
- [ ] Documentation
```

## Anti-Patterns

- ❌ "Mache es schön"
- ❌ "Wie Airbnb, aber anders"
- ❌ "Responsive, aber keine Zeit für Mobile"
- ❌ "Accessibility später"
- ❌ "Alle Features auf einmal"

## Checkliste abgeschlossen?

- [ ] Alle relevanten Sections durchgegangen
- [ ] Unbekannte Aspekte als Annahmen dokumentiert
- [ ] Stakeholder haben reviewed
- [ ] GO für Design-Phase
