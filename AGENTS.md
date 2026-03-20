# AGENTS.md

## Zweck des Repos

Dieses Repository dient der kontrollierten, wissenschaftlich nachvollziehbaren Migration des historischen IMS/ESS-Codes in eine moderne Python-Codebasis.

Primäres Ziel:
- fachliche Semantik des Altmodells erhalten
- technische Altlasten nicht 1:1 übernehmen
- Migration in kleinen, reviewbaren Pull Requests durchführen
- jederzeit nachvollziehbar machen, welche C-Logik in welche Python-Komponente überführt wurde

Nicht-Ziel:
- keine komplette kreative Neuschreibung ohne Referenz auf das Altmodell
- keine Modernisierung der historischen Terminal-UI
- keine kosmetischen Großumbauten ohne fachlichen Nutzen

---

## Arbeitsprinzipien

1. **Semantik vor Syntax**
   Portiere Verhalten, Zustandsübergänge, Aggregatbildung, Scheduling und stochastische Logik.
   Portiere nicht blind C-Idiome, Pointer-Muster, Freilisten, ANSI-Terminalcode oder K&R-Stil.

2. **Kleine, reviewbare Änderungen**
   Arbeite in kleinen Pull Requests mit klar abgegrenztem Zweck.
   Keine riesigen Sammel-PRs.

3. **Erst verstehen, dann ändern**
   Vor jeder größeren Änderung:
   - relevante C-Dateien lesen
   - betroffene Datenstrukturen und Abläufe benennen
   - Migrationsannahmen explizit machen
   - Risiken kurz notieren

4. **Keine stille Semantikänderung**
   Wenn ein Verhalten unklar ist:
   - Altverhalten dokumentieren
   - konservative Annahme treffen
   - Unsicherheit im PR-Text festhalten
   - keine „Verbesserung“ als stillen Nebeneffekt einführen

5. **Reproduzierbarkeit**
   Zufallslogik, Seeds, Aggregatausgaben und Simulationsabläufe müssen reproduzierbar sein.

---

## Zielarchitektur

Bevorzugte Python-Zielstruktur:

- `legacy_c/`
  - unveränderte oder minimal annotierte historische C-Quellen
- `docs/`
  - Migrationsnotizen
  - fachliche Mapping-Dokumente
  - Verifikationsnotizen
- `python_port/`
  - neue Python-Implementierung
- `tests/`
  - Regressionstests
  - Scheduler-Tests
  - Regeltests
  - Referenzszenarien

Wenn die Struktur noch nicht existiert, schlage sie vor und erstelle sie in kleinen Schritten.

---

## Python-Zielstil

Bevorzugt:
- Python 3.12+
- `dataclasses` für Zustandsobjekte
- Typannotationen überall dort, wo sie Lesbarkeit und Sicherheit erhöhen
- klare Modulgrenzen
- kleine, testbare Funktionen
- explizite Zustandsübergänge
- explizite RNG-Übergabe statt versteckter Globalzustände

Bevorzugte Komponenten:
- `dataclasses` für Entitäten und Zustandscontainer
- `heapq` oder äquivalente Priority-Queue für Scheduler/Ereignisse
- `pathlib`
- `pytest`
- `json` und/oder `yaml` für Szenarien
- tabellarische Ergebnisexporte, z. B. CSV

Vermeiden:
- versteckte Globals
- monolithische Dateien
- massive Seiteneffekte beim Import
- implizite I/O im Simulationskern
- UI-Kopplung im Kernmodell

---

## Fachliche Migrationsregeln

### 1. Altlogik kartieren
Vor jeder Portierung identifiziere:
- beteiligte Subjektklassen
- relevante Zustandsvektoren/Strukturen
- Aktionen und deren Ausführungszeitpunkte
- Aggregatdefinitionen
- Abhängigkeiten zu Vorperioden
- Zufallsverwendungen

### 2. C -> Python Mapping dokumentieren
Für jede portierte Komponente dokumentiere kurz:
- Ursprung im Altcode
- neue Python-Datei
- fachliche Entsprechung
- bekannte Abweichungen

Bevorzugtes Format:
- kurze Tabelle oder Liste im PR-Text
- bei größeren Umbauten zusätzlich Datei in `docs/migration/`

### 3. Reihenfolge der Migration
Bevorzugte Portierreihenfolge:
1. Datenstrukturen und Zustandscontainer
2. Scheduler / Zeitlogik
3. RNG / Zufallsverteilungen
4. BAV-/Zentralfunktionen / Aggregatbildung
5. VU-Regeln
6. VN-Regeln
7. Szenarioeinlesung
8. Ergebnisexport
9. optionale CLI

### 4. UI nicht mitportieren
Historische Terminaldialoge, Bildschirmmasken und ANSI-Ausgaben nicht nach Python übertragen, außer ausdrücklich angefordert.
Fokus ist der Simulationskern.

---

## Validierung und Tests

Jede nichttriviale Änderung soll mindestens eine der folgenden Validierungen enthalten:

- Unit-Tests für neue Python-Komponenten
- Regressionstest gegen erwartete Referenzwerte
- Vergleich kleiner Referenzszenarien zwischen Alt- und Neuverhalten
- deterministischer Test mit festem Seed
- Dokumentation offener Unterschiede

Wenn exakte 1:1-Ergebnisse wegen RNG-Unterschieden noch nicht erreichbar sind:
- Zwischenzustände vergleichen
- Abweichung transparent dokumentieren
- keine unbegründeten Gleichheitsbehauptungen machen

---

## Pull-Request-Regeln

Jeder PR soll enthalten:

1. **Ziel**
   Was wird migriert oder refaktoriert?

2. **Ursprung im Altcode**
   Welche historischen Dateien/Funktionen sind betroffen?

3. **Umsetzung**
   Welche neuen Python-Module/Klassen/Funktionen wurden ergänzt oder geändert?

4. **Validierung**
   Welche Tests wurden hinzugefügt oder ausgeführt?

5. **Offene Punkte**
   Welche Unsicherheiten oder fachlichen Restfragen bleiben?

PRs sollen bevorzugt nur **ein** klar abgegrenztes Thema behandeln.

---

## Arbeitsmodus für Codex

Bei jeder Aufgabe:

1. zuerst relevanten Kontext lesen
2. dann einen knappen Arbeitsplan intern ableiten
3. danach Änderungen in kleinen, zusammenhängenden Schritten vornehmen
4. anschließend Tests oder Plausibilitätsprüfungen ausführen
5. Diff sauber halten
6. PR-Beschreibung fachlich nachvollziehbar formulieren

Bei größeren Änderungen:
- zuerst ein kurzes Plan-Dokument in `docs/plans/` oder einen PR-Entwurf anlegen
- dann schrittweise umsetzen

---

## Was Codex nicht tun soll

- keine komplette Repo-Neuschreibung in einem Schritt
- keine Umbenennungsorgien ohne funktionalen Nutzen
- keine Einführung unnötiger Frameworks
- keine Vermischung von Simulationskern, CLI und Analysecode
- keine stillschweigende Änderung fachlicher Kennzahlen
- keine Löschung historischer Referenzquellen ohne Begründung
- keine Behauptung fachlicher Gleichwertigkeit ohne Testbasis

---

## Bevorzugte erste Aufgaben

Wenn keine genauere Aufgabe vorliegt, arbeite in dieser Reihenfolge:

1. Repo-Struktur für Migration anlegen
2. zentrale Altquellen kartieren
3. Migrations-Mapping in `docs/` anlegen
4. Python-Grundgerüst für `context`, `entities`, `scheduler` anlegen
5. erste Tests für Scheduler und Seed-Reproduzierbarkeit erstellen
6. danach BAV-/Aggregatlogik portieren

---

## Definition von „fertig“

Eine Migrationsaufgabe ist erst dann als fertig anzusehen, wenn:
- der Code konsistent eingeordnet ist
- Tests vorhanden oder die Testlücke explizit dokumentiert ist
- die Verbindung zum Altcode benannt ist
- die PR-Beschreibung fachlich verständlich ist
- keine unnötigen Nebenänderungen enthalten sind

---

## Stil für Commit- und PR-Texte

Bevorzugte Commit-/PR-Sprache: Deutsch.
Technische Begriffe können englisch bleiben, wenn sie in Python/Softwareentwicklung üblich sind.

PR-Titel möglichst im Stil:
- `Portiere Scheduler-Grundgerüst aus ESS nach Python`
- `Füge dataclass-Strukturen für VU/VN/BAV hinzu`
- `Ergänze Regressionstest für periodische Aggregatbildung`

---

## Eskalationsregel bei Unklarheit

Wenn historische Logik widersprüchlich oder unklar erscheint:
- konservative Interpretation wählen
- Stelle im Code kommentieren
- im PR offen benennen
- keine spekulative „Verbesserung“ als Tatsache darstellen