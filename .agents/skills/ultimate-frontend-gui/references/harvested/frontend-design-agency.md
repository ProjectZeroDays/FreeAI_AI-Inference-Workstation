# Harvested: frontend-design-agency

Source: `/root/.codex/skills/frontend-design-agency`

---
name: frontend-design-agency
description: Use when building, redesigning, or extending web-app frontends that must look production-ready, visually distinctive, and systemically designed instead of like generic AI-generated UI
---

# Frontend Design Agency

## Wann verwenden

- Komplette Seiten, App-Shells, Dashboards, Landingpages, Form-Flows
- Settings-Bereiche, Onboarding, Tabellen-/Listenansichten, Detailansichten, Admin-Oberflächen
- Wenn UI hochwertig/marktreif wirken muss, nicht nach Demo-Template
- Wenn bestehende UI zu generisch/technisch/austauschbar wirkt
- Wenn Design und Code als zusammenhängendes System gebaut werden sollen

## Wann NICHT verwenden

- Einzelne Komponenten-Fixes (Buttonfarbe, Spacing-Korrektur)
- Rein technische Refactorings ohne visuelle Änderung
- Backend-/API-Arbeit ohne UI-Bezug
- Prototypen, bei denen Geschwindigkeit wichtiger ist als Qualität

## Eingaben

Erwarte und extrahiere, soweit vorhanden:
- Produkttyp & Ziel der Oberfläche
- Primäre Nutzerrolle & Hauptaufgaben
- Nutzungsszenario (Kontext, Häufigkeit, Gerät)
- Wichtigste Aktion oder Conversion
- Inhalte, Datenarten und Informationsdichte
- Notwendige Ansichten oder Komponenten
- Markenrahmen/visuelle Vorgaben
- Tech-Stack & bestehende UI-Bibliotheken oder Designsysteme
- Anforderungen (Accessibility, Responsive, Performance)

**Fallback bei minimalen Inputs:**
1. Triff belastbare Annahmen basierend auf Produkttyp
2. Dokumentiere sie knapp (1-2 Sätze)
3. Entscheide bewusst, nicht neutral

## Output (Deliverables)

Standardmäßig produziert dieser Workflow:
1. **Visuelle These** — 1-2 Sätze, konkret benennbar
2. **Design Tokens** — Colors, Spacing, Radius, Typography als CSS-Variablen oder Tailwind-Config
3. **Komponentencode** — React/TSX (oder passendes Framework), mit States, Responsive, Accessibility
4. **Kurzdokumentation** — Annahmen, Referenzen, Prinzipien (inline oder als Kommentar)
5. **Informationsarchitektur-Notiz** — Hauptbereiche, Prioritäten, primäre/sekundäre Zonen
6. **State-Check** — Zentrale Komponenten inkl. Hover, Focus, Active, Disabled, Empty, Loading, Error
7. **Responsive-Notiz** — Welche Struktur sich auf Mobile/Tablet/Desktop wie verändert

Der User kann den Scope einschränken (z.B. nur Tokens, nur eine View).

## Verhaltensregeln

1. Baue niemals einfach direkt eine UI.
2. Verstehe vor jeder Umsetzung: Produkttyp, Nutzerrolle, Nutzungsszenario, primäre Nutzeraufgabe, Informationspriorität, wichtigste Aktion oder Conversion.
3. Definiere vor dem Coden immer eine visuelle Richtung.
4. Arbeite mit einer klaren gestalterischen These, nicht mit beliebigen Komponenten.
5. Begründe die zentrale Stilentscheidung knapp und konkret.
6. Reduziere Komplexität sichtbar durch Hierarchie, Gruppierung und Führung.
7. Liefere kein loses Set schöner Blöcke, sondern ein zusammenhängendes Produktsystem.
8. Verbessere generische Entwürfe aktiv, bevor du sie ausgibst.
9. Denke Desktop und Mobile zusammen.
10. Implementiere nur Lösungen, deren visuelle und funktionale Logik du benennen kannst.

## Core-Prinzipien

### 1. Visuelle These VOR Code
Jede UI braucht genau eine klar benennbare Hauptthese. Beispiele:

| These | Merkmale |
|-------|----------|
| "Reduziertes B2B-Terminal" | Monospace Headers, technische Grids, keine Rounded-Corners, Accent nur auf Actions |
| "Editorial Precision" | Starke Typografie-Hierarchie, viel Weißraum, feine Linien, dezentrale Akzente |
| "Warmes SaaS" | Abgerundete Surfaces, warme Grays, weiche Schatten, humane Microcopy |
| "Technical Density" | Kompakte Layouts, hohe Informationsdichte, funktionale Farben, klare States |

Definiere die Hauptthese und halte sie über Layout, Typografie, Farbe, Komponenten und Motion konsistent.

**Ohne These = generische KI-Optik.**

### 2. Produktdesign statt Deko
- Prioritäten sofort sichtbar machen
- Wichtige Aktionen dominant führen
- Sekundäre Informationen sauber staffeln
- Dichte Informationen lesbar halten
- Orientierung ohne unnötige Deko
- Glaubwürdige Produktästhetik aufbauen

### 3. Systemisches UI
- Design Tokens für Colors, Spacing, Radius, Shadow, Motion
- Farbrollen statt Einzelwerten
- Typo-Skalen und Spacing-Skalen
- Komponenten mit konsistenten States (Hover, Focus, Active, Disabled, Empty, Loading, Error)
- Responsive mit klaren Breakpoint-Entscheidungen
- Wiederverwendbare Muster, nicht Einzelstücke

### 4. Typografie und Raum
- Starke visuelle Hierarchie
- Hochwertige Weißraum-Nutzung
- Wenige, präzise Akzente
- Klare Leselinien
- Differenzierte Flächen statt Kartenfriedhof

### 5. Research-basiert, nicht geraten
Bei Web-Zugriff: 3-5 hochwertige Referenzen suchen.

**Suchqueries nach UI-Typ:**
- Dashboard: `"SaaS dashboard" UI pattern` + `linear.com` `vercel.com` `raycast.com`
- Forms: `"B2B form design" best practices` + `stripe.com` `shopify.com`
- Tables: `"data table UI" SaaS` + `airtable.com` `notion.com`
- Onboarding: `"product onboarding flow" SaaS` + `intercom.com` `linear.com`
- Admin: `"admin panel design" enterprise` + `palantir.com` `grafana.com`

**Quellen priorisieren:** Reale SaaS-Produkte > Designsysteme > Showcase. Keine Dribbble-Optik ohne Produktlogik.

**Referenznutzung:** Nutze Referenzen nur, um Prinzipien abzuleiten, nicht um Oberflächen nachzubauen. Dokumentiere pro Referenz kurz:
- was übernommen wird
- was bewusst nicht übernommen wird
- warum die Entscheidung zur Produktlogik passt

**Ohne Webzugriff:** Arbeite mit bekannten Produktmustern, definiere Stilrichtung trotzdem explizit, rate nicht planlos.

## Tech-Stack

**Bevorzugt:** Next.js, React, TypeScript, Tailwind, shadcn/ui
**Andere Stacks** (Vue, Svelte, Admin-Template, bestehendes Design-System) nur wenn User oder Projekt es vorgibt.

**Icons:** Lucide-react wenn passend, sonst konsistentes alternatives System. Mische nicht mehrere Icon-Stile ohne Begründung.

**Implementierungsregeln:**
1. Semantische HTML-Struktur
2. Tastaturbedienbarkeit und Fokuszustände
3. Tokens oder CSS-Variablen für zentrale Stilwerte
4. Wiederkehrende Muster in Komponenten extrahieren
5. Tailwind systemisch statt chaotisch nutzen
6. shadcn/ui-Komponenten sichtbar an die definierte Designsprache anpassen
7. Default-Styling nie unreflektiert stehen lassen
8. Unnötige DOM-Komplexität vermeiden
9. Keine dekorativen Effekte mit hoher Renderlast
10. Bei Tabellen/Listen auf Skalierbarkeit achten

**Accessibility-Pflicht:**
- Sichtbare Focus-Zustände (nicht nur `:focus`, sondern `:focus-visible`)
- Ausreichende Kontraste (Text ≥ 4.5:1, UI-Elemente ≥ 3:1)
- Sinnvolle Tastaturbedienbarkeit und logische Tab-Reihenfolge
- Labels und verständliche Fehlermeldungen
- `prefers-reduced-motion` respektieren bei Animationen

## Umgang mit References

Behandle nicht alle Referenzen als gleichrangig.

### Autoritativ — steuern den Denkprozess
- `references/product-requirements-checklist.md`
- `references/research-workflow.md`
- `references/quality-gate.md`
- `references/accessibility-checklist.md`

### Leitend — helfen bei Richtung und Prüfung
- `references/visual-direction-canvas.md`
- `references/generic-vs-distinctive-examples.md`
- `references/design-system-rules.md`
- `references/motion-system-guide.md`

### Vorlagen — optionale Umsetzungshilfen
- `references/component-template.tsx`
- `references/layout-patterns-library.md`
- `references/grid-system-template.md`
- `references/color-palette-examples.md`
- `references/typography-scale-template.md`
- `references/breakpoint-definition.md`
- `references/focus-states-template.md`
- `references/user-persona-template.md`

**Regeln:**
- Autoritative Referenzen steuern die Entscheidung. Sie werden immer konsultiert.
- Leitende Referenzen helfen bei Richtung und Prüfung. Sie unterstützen den Denkprozess.
- Vorlagen dienen nur als optionale Umsetzungshilfe nach getroffenen Entscheidungen.
- Vorlagen dürfen niemals die visuelle These oder Produktlogik ersetzen.
- Wenn eine Vorlage der definierten Stilrichtung widerspricht, hat die Stilrichtung Vorrang.

## Ablauf (operativ)

### Phase 1: Discovery
1. **Kontext extrahieren** — Produkt, Nutzer, Aufgabe, Prioritäten
   → Konsultiere immer `references/product-requirements-checklist.md`
   → Nutze `references/user-persona-template.md` nur, wenn Zielnutzer, Kontext oder Nutzungsmuster unklar sind
2. **Nutzungsszenario ableiten** — Primäre Nutzeraufgabe und Informationsprioritäten festlegen

### Phase 2: Design Direction
3. **Visuelle These definieren** — 1-2 Sätze, konkret benennbar
   → Konsultiere `references/visual-direction-canvas.md`
4. **Referenzen** — Web-Recherche oder belastbare Annahmen
   → Konsultiere `references/research-workflow.md`
5. **Design-Prinzipien** — 3-5 Regeln aus Referenzen/These
   → Prüfe gegen `references/generic-vs-distinctive-examples.md`

### Phase 3: Design System
6. **Informationsarchitektur festlegen** — Primäre/sekundäre Informationszonen bestimmen, Komponenten priorisiert anordnen
7. **Tokens definieren** — Colors, Spacing, Radius, Typography-Scale
   → Konsultiere `references/design-system-rules.md`
   → Nutze `references/color-palette-examples.md` und `references/typography-scale-template.md` bei Bedarf als nicht-normative Umsetzungshilfe
8. **Komponentenplan** — Welche Views/Components nötig? Layoutsystem festlegen.
   → Nutze `references/grid-system-template.md` und `references/layout-patterns-library.md` nur, wenn Layout- und Komponentenlogik bereits definiert ist

### Phase 4: Implementation
9. **Implementieren** — Semantisch, States, Responsive, Motion
   → Konsultiere `references/component-template.tsx`, `references/breakpoint-definition.md`, `references/motion-system-guide.md`, `references/focus-states-template.md`
10. **Anti-Generic Review** — Prüfe jede View gegen die Checkliste in `references/generic-vs-distinctive-examples.md`. Überarbeite generische Stellen aktiv.

### Phase 5: Quality Gate
11. **Qualitätsprüfung** — Vor Abschluss Pflicht.
    → Konsultiere `references/quality-gate.md` und `references/accessibility-checklist.md`

## Explizit vermeiden

- Austauschbare Kartenraster ohne Priorisierung
- Generische Dashboard-Kompositionen
- Sterile Standard-Blöcke
- Accent-Farben ohne semantische Rolle
- Default-shadcn-Look ohne Anpassung
- Dekorative Glows und Gradients ohne funktionalen Zweck
- Badge-, Pill- und Shadow-Overuse
- UI, die wie ein zusammengesetztes Komponenten-Demo wirkt
- Zufällige Farbentscheidungen
- Unklare visuelle Hierarchie
- Desktop-only-Denken
- Fehlende Zustände (Hover, Focus, Empty, Loading, Error)
- Komponenten ohne Systemlogik
- 1:1-Kopien aus Referenzen
- Beliebige Icon-Mischung
- Rein technische Implementierung ohne Produktlogik

## Qualitätsprüfung (Pflicht)

Prüfe vor Abschluss immer:

### Produktqualität
- Wirkt die Oberfläche wie ein reales Produkt statt wie ein Demo-Template?
- Hat die UI eine erkennbare Identität (These)?
- Ist die Hauptaktion klar geführt?
- Sind Informationsdichte und Lesbarkeit ausbalanciert?

### Visuelle Qualität
- Gibt es eine saubere Hierarchie?
- Sind Abstände konsistent?
- Sind Farben rollenbasiert und nachvollziehbar?
- Sind Radius, Border und Shadow systemisch?
- Wirkt die Oberfläche hochwertig, aber nicht dekorativ überladen?

### Systemqualität
- Gibt es wiederverwendbare Komponenten?
- Sind Zustände vollständig abgedeckt?
- Ist das responsive Verhalten konsistent?
- Sind Tokens oder zentrale Stilregeln erkennbar?

### Codequalität
- Ist der Code sauber strukturiert?
- Sind Komponenten sinnvoll geschnitten?
- Ist unnötige Komplexität vermieden?
- Ist die Lösung barrierearm und produktionsnah?

**Wenn eine dieser Fragen mit nein beantwortet wird, ist die Arbeit nicht fertig.**

## Eskalation und Abbruch

Frage nach, bevor du weiterarbeitest, wenn:
- Produkttyp und Zielnutzer völlig unklar sind und keine sinnvolle Annahme möglich ist
- Widersprüchliche Anforderungen vorliegen (z.B. "minimalistisch" + "alle Features auf einen Screen")
- Der Tech-Stack nicht mit den visuellen Anforderungen vereinbar ist
- Der User explizit auf Qualitätsschritte verzichten will — weise auf Konsequenzen hin

## Definition of Done

Der Task ist erst abgeschlossen, wenn:
1. Produkttyp, Nutzerrolle und Nutzungsszenario klar benannt wurden
2. Eine visuelle Richtung explizit definiert wurde
3. Referenzen recherchiert oder eine belastbare Stilannahme dokumentiert wurden
4. Informationsarchitektur und Komponentenplan festgelegt wurden
5. Design Tokens oder klare Stilregeln erkennbar sind
6. Die UI eine erkennbare Produktidentität hat und die Hauptaktion visuell dominant ist
7. Alle relevanten Zustände ergänzt wurden
8. Die Oberfläche responsive und barrierearm ist
9. Der Code modular und produktionsnah ist
10. Das Ergebnis nicht wie generische KI-UI oder ein Default-Template wirkt

## Beispiel-Prompt

Nutze `frontend-design-agency`, um eine B2B-SaaS-Oberfläche für ein Incident-Management-Produkt zu entwerfen und in Next.js mit TypeScript, Tailwind und shadcn/ui umzusetzen. Recherchiere visuelle Referenzen, definiere zuerst eine klare Designrichtung, leite daraus Tokens und Komponentenregeln ab und baue anschließend eine hochwertige, responsive App-Shell mit Dashboard, Vorfallsliste und Detailansicht. Vermeide generische KI-Dashboard-Optik und begründe die gestalterische These kurz vor der Implementierung.
