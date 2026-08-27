# Design System Rules

Nutze diese Regeln beim Umsetzen in Next.js, React, TypeScript und Tailwind CSS.

## 1. Tokens zuerst

Lege zentrale Werte als Tokens oder CSS-Variablen an fuer:
- Farben
- Typografie
- Radius
- Spacing
- Shadow
- Motion

Keine verstreuten Einzelwerte, wenn ein Wert mehrfach vorkommt.

## 2. Farbrollen statt Einzelwerte

Arbeite mit Rollen wie:
- background
- foreground
- surface
- surface-strong
- primary
- primary-foreground
- muted
- muted-foreground
- border
- danger
- success
- warning

Vermeide "hier noch schnell ein anderer Blauton".

## 3. Typo-Skala

Mindestens diese Ebenen sauber definieren:
- Display
- H1
- H2
- H3
- Body
- Small
- Label
- Mono oder Data

Jede Ebene braucht:
- Groesse
- Gewicht
- Laufweite wenn noetig
- Zeilenhoehe

## 4. Spacing-Skala

Nutze eine feste Skala, zum Beispiel:
- 4
- 8
- 12
- 16
- 24
- 32
- 48
- 64

Nutze nicht beliebige Mischwerte ohne Systemgrund.

## 5. Komponentenaufbau

Extrahiere wiederkehrende Muster in Komponenten, wenn mindestens zwei Bedingungen gelten:
- wiederholte Struktur
- wiederholte Interaktionslogik
- wiederholte Stilregeln

Typische Kandidaten:
- Page Header
- KPI Block
- Filter Bar
- Data Table Wrapper
- Empty State
- Detail Section
- Status Badge

## 6. Zustandsmodell

Wichtige Komponenten brauchen mindestens:
- default
- hover
- focus-visible
- active
- disabled
- loading
- error falls relevant
- empty falls relevant

## 7. Responsives Verhalten

Definiere nicht nur Breakpoints, sondern Umbruchslogik:
- Was wird gestapelt?
- Was wird gekuerzt?
- Was wird zu Tabs, Drawer oder Accordion?
- Welche Info bleibt mobil sichtbar?

Mobile darf nicht nur die Desktop-Version in schmal sein.

## 8. Accessibility

Pflicht:
- semantische Struktur
- Tastaturbedienbarkeit
- sichtbare Fokuszustaende
- ausreichender Kontrast
- Labels statt nur Placeholder
- sinnvolle aria-Attribute bei komplexen Controls

## 9. shadcn/ui

shadcn/ui ist Startpunkt, nicht Endzustand.

Pflicht:
- Komponenten sichtbar anpassen
- Defaults nur uebernehmen, wenn sie zur Stilthese passen
- Panels, Buttons, Inputs und Overlays in eine gemeinsame Designsprache bringen

## 10. Code-Qualitaet

Vermeide:
- ueberladene Utility-Ketten ohne Struktur
- Komponenten mit mehreren visuellen Konzepten
- zu fruehe Abstraktion
- zu spaete Abstraktion bei klarer Wiederholung

Ziel:
- klare Komponenten
- nachvollziehbare Props
- produktionsnahe Lesbarkeit
