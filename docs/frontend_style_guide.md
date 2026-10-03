# IMS: Leitlinien für die Weboberfläche

Stand 03.10.2026. Anwendung im bestehenden React-Frontend; keine neue UI-Bibliothek.
Diese Leitlinien beantworten den Anwenderbefund mangelnder Orientierung.

## Orientierung und Aufgaben

* Häufige Arbeitsbereiche stehen in der Hauptnavigation. Ihre Reihenfolge bleibt
  konstant; genau ein Eintrag bezeichnet den aktuellen Bereich.
* Die H1 benennt den aktuellen Ort. Menü, sichtbare Überschrift und Anleitung
  verwenden dieselben Begriffe. Ein interner Modulname ist kein Menüname.
* Eine Seite führt zu einer Hauptaufgabe. Mehrere unabhängige Fallformulare
  werden ausdrücklich ausgewählt und nicht hintereinander angehängt.
* Häufige Werkzeuge stehen direkt bereit; erweiterte Funktionen sind klar
  beschriftet und erreichbar. Nicht alle Funktionen bekommen denselben Vorrang.
* Fallwahl, Laden, Rechnung und Auswertung sind erkennbar. Die nächste Aktion
  und Zustände wie „geladen“, „läuft“, „ungültig“ und „veraltet“ bleiben sichtbar.
* Ergebnisansichten teilen ihre Filter. Ein Ansichtswechsel verändert keinen
  Modelllauf und verliert keine Eingaben, Ergebnisnachweise oder Freigaben.

## Gestaltung und Bedienung

* Farben, Kontrast, Abstände und Radien aus den bestehenden CSS-Tokens beziehen.
  Beschriftete Formulare, ruhige Flächen und eine abgestufte Überschriftenfolge.
* Eine führende Hauptaktion, zurückhaltende Nebenaktionen. Auswahl und Fehler
  mit Text und Form erklären; Farbe allein reicht nicht.
* Verwandte Auswahlfelder gruppieren. Buttons benennen ihre tatsächliche Aktion.
  Es werden keine internen Paket-/Transportdetails als Arbeitsschritte angezeigt.
* Eine Ergebnisansicht sichtbar; Reiter zeigen ihre Auswahl und behalten die
  gemeinsame Periode. Datentabellen bleiben als zugängliche Alternative erreichbar.
* Klickziele mindestens 44 × 44 CSS-Pixel, Textkontrast mindestens 4,5:1 auch
  bei großen Überschriften. Keine horizontal überlaufende ganze Seite.
* Reiter mit Tab sowie Links/Rechts/Pos1/Ende bedienen. Zugehörige Panels korrekt
  benennen; ausgeblendete Inhalte verlassen die Tastatur- und Lesereihenfolge.
* Kleine Bildschirme und beide Farbmodi anhand echter Browserbilder prüfen.

## Nachweise und Modellgrenzen

Quellenumfang, Einheiten und Workshop-Annahmen bleiben am Ergebnis sichtbar.
Details/Nachweise dürfen aufklappbar sein; unverzichtbare Warnungen bleiben
sichtbar. Technische Tests belegen konkrete Bedienfunktionen, keine menschliche
Verständlichkeit. Neue Produktfassungen brauchen eigene Versions-/Produktbelege.

Quellen, am 03.10.2026 gelesen:
[GOV.UK: Button](https://design-system.service.gov.uk/components/button/),
[NN/G: Progressive Disclosure](https://www.nngroup.com/articles/progressive-disclosure/),
[W3C: konsistente Navigation](https://www.w3.org/WAI/WCAG22/Understanding/consistent-navigation),
[W3C: Reiter](https://www.w3.org/WAI/ARIA/apg/patterns/tabs/).
Die Regeln sind IMS-Anforderungen und keine Behauptung einer Zertifizierung.
