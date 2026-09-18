# PR178: Kapital-Modellansicht und Export

Stand: 2026-09-18
Status: umgesetzt; PR178a Handbuch-Erstausgabe ebenfalls umgesetzt

## Ziel und Grenzen

Eine bereits gepruefte Vier-Sparten-Gesamtbilanz ist die einzige
Workbench-Quelle. Der Anwender waehlt eine Modellperiode und deklariert
Bewertungsdifferenzen, sechs disjunkte Teilpositionen, fuenf
Modulsaetze, einen Gegenparteisatz, einen operationellen Verlust,
Faktorladungen, einen unabhaengigen Modellpuffer und zwei
Workshop-Grenzen. Nichts wird aus der Bilanz stillschweigend als
regulatorischer Parameter abgeleitet. Nulleingaben sind explizite
Modellannahmen; die Eingaben bleiben fluechtig.

Die Workbench fordert PR172, PR175 und PR176 serverseitig an und
prueft die ETags sowie die Kette der Quellen-Digests bis zur
angezeigten Vier-Sparten-Bilanz. Sie trennt sichtbar Modellwirkung,
Workshop-Entscheidung und gesperrte regulatorische Werte. Eine
veraenderte Bilanz oder Annahme verwirft die bisherige Ansicht und
deaktiviert Exporte. Fehlereingaben liefern keine Teilwerte.

JSON exportiert den verifizierten Eingang und die drei zugehoerigen
Antworten zur Nachvollziehbarkeit. XLSX wird aus demselben Eingang
serverseitig erneut geprueft; Tabellen fuer Modellwirkung, Sparten,
Risiken, Annahmen, Regulatorik und Herkunft enthalten exakte
Dezimaltexte.
SCR, MCR, anrechenbare Eigenmittel und Bedeckungsquoten haben dort
keine Zahlenzellen. Beide Exporte sind in-memory und speichern
keinen Lauf.

## Historischer Bezug

| Ursprung | PR178-Entsprechung | Grenze |
| --- | --- | --- |
| `IMSDATA.C`, `LV`/`KV` mit `Pr`, `Rs`, `Sh` und `classVU.Sp` | Quelle des historischen Spartenbegriffs | historisch zwei Schaden-Sparten; kein Solvency-II-Kapitalwert |
| PR170 Vier-Sparten-Bilanz | sichtbarer, digestgebundener Ausgangspunkt | einfache Modellbilanz, keine gesetzliche Bilanz |
| PR172-176 | gepruefte Modellwerte und gesperrte Kapitalfelder | Szenarioannahmen, keine SCR-/MCR- oder Compliance-Berechnung |

## Abnahme

- Backend-Tests fuer XLSX-Werte, leere regulatorische Zahlenfelder,
  Herkunft und ungueltige Eingaben, jeweils mit FastAPI und
  Starlette-Fallback.
- Frontend-Build und Browser-Smoke fuer Eingabe, Bilanzbindung,
  Modell-/Regulatorik-Trennung, Downloads, Fehler und schmale Ansicht.
- Echte breite und schmale Screenshots unter `docs/handbook/images/`
  sind in die PR178a-Bedienungsanleitung eingeflossen.
- Gesamt-Pytest-Suite und Windows-Release-Gate.

Offen bleiben eine rechtlich freigegebene Kapitalformel und amtliche
Bewertungsdaten; es gibt keine historische Vollgleichheit. PR178a erklaert
nur den hier belegten Bedienpfad.
