# User Persona Template

> **Umsetzungshilfe, keine Standardlösung.**
> Die Struktur ist ein Ausgangspunkt. Passe Felder und Tiefe an den konkreten Produkttyp an. Nicht jedes Feld ist immer relevant — fokussiere auf das, was echte Designentscheidungen informiert.

Nutze diese Vorlage, um deine Zielnutzer zu definieren.

## Template

```markdown
# Persona: [Name]

## Demografie
- **Name:** [Fiktiver Name]
- **Alter:** [Altersgruppe]
- **Beruf:** [Jobtitel]
- **Unternehmen:** [Unternehmensgröße/Branche]
- **Standort:** [Region/Remote]

## Kontext
- **Primäre Aufgabe:** [Was muss diese Person primär erledigen?]
- **Nutzungsfrequenz:** [Täglich/Wöchentlich/Sporadisch]
- **Nutungsdauer:** [Kurz <5min/Mittel 5-30min/Lang >30min]
- **Gerät:** [Desktop/Tablet/Mobile/Mixed]
- **Umgebung:** [Büro/Unterwegs/Homeoffice]

## Ziele
1. [Primäres Ziel - warum nutzt diese Person das Produkt?]
2. [Sekundäres Ziel]
3. [Langfristiges Ziel]

## Pain Points
- [Frustration 1 - was bereitet aktuell Stress?]
- [Frustration 2]
- [Frustration 3]

## Aktuelle Lösungen
- **Tools:** [Was nutzt die Person aktuell?]
- **Workarounds:** [Wie umgeht sie aktuelle Probleme?]
- **Mängel:** [Was stört an aktuellen Lösungen?]

## Technische Kompetenz
- **Level:** [Anfänger/Fortgeschritten/Experte]
- **Ähnliche Tools:** [Welche Software kennt sie schon?]
- **Lernbereitschaft:** [Hoch/Mittel/Gering]

## Entscheidungskriterien
Was ist beim Kauf/Wechsel wichtig:
1. [Kriterium 1 - z.B. Preis, Geschwindigkeit, Features]
2. [Kriterium 2]
3. [Kriterium 3]

## Zitat
> "[Typisches Zitat, das die Einstellung widerspiegelt]"
```

## Beispiele

### Persona 1: B2B SaaS Admin

```markdown
# Persona: Sarah

## Demografie
- **Name:** Sarah Müller
- **Alter:** 32
- **Beruf:** IT Operations Manager
- **Unternehmen:** Mittelständisches E-Commerce (150 MA)
- **Standort:** München, Hybrid

## Kontext
- **Primäre Aufgabe:** Systemüberwachung und Incident Response
- **Nutzungsfrequenz:** Täglich
- **Nutungsdauer:** Kurz (2-5 Minuten Checks), lang bei Incidents
- **Gerät:** Desktop (im Büro), Mobile (unterwegs/Alarm)
- **Umgebung:** Open Office, manchmal Homeoffice

## Ziele
1. Probleme sofort erkennen und eskalieren
2. Team-Kapazität effizient managen
3. Wochenberichte für Management erstellen

## Pain Points
- Zu viele Alerts → Alert Fatigue
- Unklare Priorisierung was zuerst
- Schlechte Mobile-Erfahrung bei Pager-Duty

## Aktuelle Lösungen
- **Tools:** PagerDuty, Slack, Excel-Listen
- **Workarounds:** Manuelle Filterung in Excel
- **Mängel:** Keine zentrale Übersicht

## Technische Kompetenz
- **Level:** Fortgeschritten
- **Ähnliche Tools:** Datadog, Grafana, Jira
- **Lernbereitschaft:** Mittel (hat wenig Zeit)

## Entscheidungskriterien
1. Schnelle Implementierung (<2 Wochen)
2. Gute Slack-Integration
3. Mobile App Qualität

## Zitat
> "Ich brauche in 10 Sekunden zu sehen, ob alles okay ist."
```

### Persona 2: Fintech End User

```markdown
# Persona: Markus

## Demografie
- **Name:** Markus Weber
- **Alter:** 45
- **Beruf:** Selbstständiger Steuerberater
- **Unternehmen:** Einzelunternehmen (5 MA)
- **Standort:** Homeoffice

## Kontext
- **Primäre Aufgabe:** Rechnungen erstellen und Zahlungen verfolgen
- **Nutzungsfrequenz:** Wöchentlich
- **Nutungsdauer:** Mittel (30-60 Minuten)
- **Gerät:** Laptop (Desktop)
- **Umgebung:** Homeoffice

## Ziele
1. Rechnungen schnell erstellen
2. Überfällige Zahlungen im Blick behalten
3. Steuerrelevante Daten exportieren

## Pain Points
- Unübersichtliche bisherige Buchhaltung
- Angst, etwas zu übersehen
- Zu komplexe Software früher

## Aktuelle Lösungen
- **Tools:** Excel, Dropbox, Email
- **Workarounds:** Erinnerungen im Kalender
- **Mängel:** Keine Automatisierung

## Technische Kompetenz
- **Level:** Anfänger-Fortgeschritten
- **Ähnliche Tools:** Word, Excel
- **Lernbereitschaft:** Mittel (braucht gute Guidance)

## Entscheidungskriterien
1. Einfache Bedienung
2. Steuerrechtlich konform (DACH)
3. Preis-Leistung

## Zitat
> "Ich will keine Schulung brauchen, um eine Rechnung zu schreiben."
```

## Nutzung

1. **Erstelle 2-3 Personas** für dein Produkt
2. **Priorisiere** die primäre Persona
3. **Hänge die Persona** neben deinem Monitor während des Designs
4. **Prüfe jede Entscheidung** gegen die Persona:
   - "Würde Sarah das verstehen?"
   - "Löst das Markus' Pain Point?"

## Anti-Patterns

- ❌ Zu viele Personas (mehr als 3)
- ❌ Unrealistische Details (Lieblingsfarbe, Haustier)
- ❌ Demografie ohne Kontext
- ❌ Keine Verbindung zu Produktentscheidungen
