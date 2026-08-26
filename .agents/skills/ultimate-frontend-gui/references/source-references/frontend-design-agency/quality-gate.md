# Quality Gate

Diese Pruefung ist vor Abschluss Pflicht.

## 1. Produktlogik

- Ist die primaere Nutzeraufgabe sofort erkennbar?
- Ist die Hauptaktion deutlich priorisiert?
- Sind sekundaere Informationen klar nachrangig?
- Folgt die Struktur dem Anwendungsfall statt einer Template-Logik?

## 2. Visuelle Identitaet

- Hat die UI eine klare gestalterische These?
- Sind Farben, Typografie und Flachen erkennbar aufeinander abgestimmt?
- Wirkt die UI wie ein echtes Produkt?
- Gibt es mindestens ein klar wiedererkennbares Identitaetsmerkmal?

## 3. Anti-Generic Check

Wenn eine dieser Aussagen zutrifft, ueberarbeite den Entwurf:
- Sieht aus wie ein Standard-Admin-Template.
- Koennte aus jeder x-beliebigen AI-Demo stammen.
- Zu viele Karten ohne klare Aufgabe.
- Zu viele Effekte kompensieren fehlende Hierarchie.
- Standard-shadcn ohne erkennbare Anpassung.

## 4. Komponenten und Zustaende

- Sind wiederkehrende Muster konsistent?
- Haben interaktive Elemente saubere Hover- und Focus-States?
- Gibt es Loading, Empty und Error States fuer relevante Bereiche?
- Sind Formulare, Tabellen und Detailmodule systemisch abgestimmt?

## 5. Responsive Qualitaet

- Bleibt die Hauptaufgabe mobil klar?
- Brechen Layout und Abstaende kontrolliert um?
- Sind Header, Filter und Aktionszonen auch auf kleinen Screens nutzbar?
- Geht keine kritische Information durch unkontrolliertes Stacking verloren?

## 6. Code-Check

- Sind Tokens oder zentrale Stilregeln erkennbar?
- Sind Komponenten sinnvoll modularisiert?
- Ist das Markup semantisch?
- Ist die Tailwind-Nutzung lesbar statt chaotisch?

## 7. Abschlussfrage

Wenn diese UI auf der Website eines teuren SaaS-Produkts live waere:
- waere sie glaubwuerdig?
- waere sie unterscheidbar?
- waere sie sauber genug fuer Produktion?

Wenn nicht, ist die Arbeit nicht fertig.
