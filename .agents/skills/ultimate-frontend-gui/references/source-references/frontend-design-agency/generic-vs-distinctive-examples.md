# Generic vs Distinctive Examples

Visuelle Vergleiche: Was macht UI generisch vs. unterscheidbar?

## 1. Dashboard Cards

### ❌ Generic: Card Friedhof
```
┌─────────────────────────────────────────┐
│  ┌─────────┐  ┌─────────┐  ┌─────────┐ │
│  │  📊    │  │  💰    │  │  👥    │ │
│  │  1,234 │  │  €45k  │  │   89   │ │
│  │  Views │  │ Revenue│  │  Users │ │
│  └─────────┘  └─────────┘  └─────────┘ │
│         Purple Gradient BG              │
└─────────────────────────────────────────┘
```
**Probleme:**
- Alle Cards gleiche Wichtigkeit
- Keine Priorisierung
- Beliebiger Purple Gradient
- Icons ohne Bedeutung
- Standard Shadow überall

### ✅ Distinctive: Hierarchische KPIs
```
┌─────────────────────────────────────────┐
│                                         │
│  REVENUE THIS MONTH          ▲ +12%   │
│  €45,230.00                             │
│  ═══════════════════════════            │
│                                         │
│  ┌─────────────┐  ┌─────────────┐        │
│  │ CONVERSION  │  │ NEW USERS   │        │
│  │ 3.2%        │  │ 234         │        │
│  │ ▲ 0.4%      │  │ ▼ 12        │        │
│  └─────────────┘  └─────────────┘        │
│                                         │
└─────────────────────────────────────────┘
```
**Lösungen:**
- Primäre Metric prominent
- Untere Metrics klar untergeordnet
- Minimaler Einsatz von Farbe
- Keine unnötigen Icons
- Datengesteuerte Hierarchie

---

## 2. Navigation

### ❌ Generic: Standard Header
```
┌─────────────────────────────────────────┐
│  Logo    Home  Features  Pricing   [Login] [Signup] │
└─────────────────────────────────────────┘
```
**Probleme:**
- Austauschbar
- Keine Produktidentität
- Gleiche Links wie jede andere Seite
- Buttons ohne Unterscheidung

### ✅ Distinctive: Charakterstarker Header
```
┌─────────────────────────────────────────┐
│  ◆ BRAND                    Products ▼  │
│                             Solutions ▼ │
│                             ──────────  │
│                    [Log in]  [Get Demo]   │
└─────────────────────────────────────────┘
```
**Lösungen:**
- Markantes Logo/Symbol
- Produktkategorien statt generischer Links
- CTA klar priorisiert
- Visuelle Trennung durch Linie

---

## 3. Tables

### ❌ Generic: Standard Table
```
┌────┬──────────┬──────────┬────────┬──────────┐
│ ID │ Name     │ Email    │ Status │ Actions  │
├────┼──────────┼──────────┼────────┼──────────┤
│ 01 │ Max M.   │ m@...    │ Active │ ⚙️ 🗑️    │
│ 02 │ Lisa S.  │ l@...    │ Active │ ⚙️ 🗑️    │
└────┴──────────┴──────────┴────────┴──────────┘
```
**Probleme:**
- Alles sieht gleich wichtig aus
- Grid zu dominant
- Actions nicht erkennbar
- Keine Priorisierung

### ✅ Distinctive: Datenfokussierte Tabelle
```
┌────────────────────────────────────────────┐
│ Name              │ Status │ Role     │    │
├───────────────────┼────────┼──────────┼────┤
│ ○ Lisa Schmidt    │ Admin  │ Engineer │ ▼  │
│   lisa@company.io │        │          │    │
├───────────────────┼────────┼──────────┼────┤
│ ○ Max Mustermann  │ User   │ Designer │ ▼  │
│   max@company.io  │        │          │    │
└───────────────────┴────────┴──────────┴────┘
```
**Lösungen:**
- Avatar + Name verbunden
- Secondary Info (Email) subtil
- Keine Grid-Lines, stattdessen ruhige Trennung
- Dropdown statt sichtbare Icons
- Status durch Badge-Style unterschieden

---

## 4. Buttons

### ❌ Generic: Standard Buttons
```
[    Primary    ] [Secondary] [Ghost]
```
**Probleme:**
- Gleiche Größe
- Secondary und Ghost kaum unterscheidbar
- Keine klare Hierarchie

### ✅ Distinctive: Hierarchische Actions
```
[ Save Changes ]  [ Cancel ]  Delete
```
**Lösungen:**
- Primary: Filled, höchste Priorität
- Secondary: Text-only, geringe Priorität
- Danger: Text-only, rot, destruktiv
- Unterschiedliche visuelle Gewichtung

---

## 5. Form Layout

### ❌ Generic: Form Stack
```
Email:    [_______________]
Password: [_______________]
          [ ] Remember me
          [    Submit    ]
```
**Probleme:**
- Keine Gruppierung
- Label links = schmale Inputs
- Checkbox verloren
- Button zu breit

### ✅ Distinctive: Klare Form-Gruppierung
```
┌─────────────────────────────┐
│                             │
│  Sign in to your account    │
│                             │
│  Work Email                 │
│  [________________]         │
│                             │
│  Password                   │
│  [________________] [👁]     │
│  Forgot password?           │
│                             │
│  [ ] Stay signed in         │
│                             │
│  [    Continue    ]         │
│                             │
│  ───── Or continue with ───│
│                             │
│  [G] [GitHub]               │
│                             │
└─────────────────────────────┘
```
**Lösungen:**
- Card-Container für Fokus
- Überschrift mit Kontext
- Password Toggle integriert
- Secondary Action (Forgot) verlinkt
- Social Login separat gruppiert

---

## 6. Empty States

### ❌ Generic: Leere Seite
```
No data found.
```
**Probleme:**
- Keine Hilfe
- Keine nächsten Schritte
- Deprimierend

### ✅ Distinctive: Helfender Empty State
```
┌─────────────────────────────┐
│                             │
│        [📁 Illustration]    │
│                             │
│     No projects yet         │
│                             │
│     Create your first       │
│     project to get started  │
│                             │
│     [+ New Project]         │
│                             │
│     Or import from:         │
│     [CSV] [Notion] [Trello] │
│                             │
└─────────────────────────────┘
```
**Lösungen:**
- Illustration als visueller Anker
- Klare Headline
- Erklärung warum leer
- Primäre CTA prominent
- Alternative Optionen

---

## 7. Loading States

### ❌ Generic: Spinner
```
[Spinning Circle] Loading...
```
**Probleme:**
- Keine Info was passiert
- Keine Fortschrittsanzeige
- Frustrierend bei langem Load

### ✅ Distinctive: Informatives Loading
```
┌─────────────────────────────┐
│                             │
│  [████░░░░░░░░░░] 35%       │
│                             │
│  Uploading file...          │
│  document_backup_v2.zip     │
│                             │
│  About 2 minutes remaining  │
│                             │
│  [ Cancel Upload ]          │
│                             │
└─────────────────────────────┘
```
**Lösungen:**
- Progress Bar zeigt Fortschritt
- Konkrete Beschreibung
- Dateiname sichtbar
- Zeit-ETA
- Cancel-Option

---

## Checkliste: Anti-Generic

- [ ] Habe ich eine klare Hierarchie?
- [ ] Sind die wichtigsten Actions dominant?
- [ ] Gibt es ein erkennbares Marken-Element?
- [ ] Sind Farben bewusst eingesetzt (nicht überall)?
- [ ] Gibt es genug White Space?
- [ ] Sind Labels konkret (nicht "Submit")?
- [ ] Gibt es hilfreiche Empty States?
- [ ] Sind Loading States informativ?
- [ ] Unterscheidet sich das Layout von Standard-Templates?
- [ ] Würde ich das als echtes Produkt erkennen?

---

## Pattern Library

### Gute Beispiele (Inspiration)

| Produkt | Stil | Besonderheit |
|---------|------|--------------|
| Linear  | Minimal, dunkel | Geschwindigkeit durch UI |
| Notion  | Clean, whitespace | Modularität |
| Figma   | Kollaborativ | Echtzeit-Indikatoren |
| Stripe  | Professionell | Datenvisualisierung |
| Apple   | Refined, Licht | Subtile Animationen |
| Airbnb  | Warm, einladend | Bilder zentral |

---

## Merke

> Generic = Keine Entscheidungen getroffen
> Distinctive = Klare, bewusste Entscheidungen

**Jedes Element sollte eine Funktion haben.**
**Wenn etwas nur "schön" ist, aber nicht hilft → weglassen.**
