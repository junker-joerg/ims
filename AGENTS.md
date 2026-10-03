# AGENTS.md

## Zweck des Repos

Dieses Repository dient der kontrollierten, wissenschaftlich nachvollziehbaren Migration des historischen IMS/ESS-Codes in eine moderne Python-Codebasis.

Primäres Ziel:
- fachliche Semantik des Altmodells erhalten
- technische Altlasten nicht 1:1 übernehmen
- Migration in zusammenhängenden, reviewbaren Arbeitspaketen durchführen
- jederzeit nachvollziehbar machen, welche C-Logik in welche Python-Komponente überführt wurde

Nicht-Ziel:
- keine komplette kreative Neuschreibung ohne Referenz auf das Altmodell
- keine Modernisierung der historischen Terminal-UI
- keine kosmetischen Großumbauten ohne fachlichen Nutzen

---

## Aktuelle Lieferplanung

AP1–AP3 der modernen Workbench sind nach main übernommen. Der Plan vom
30.09.2026 in `docs/plans/ims_ai_sprint_2026_09.md` und
`docs/plans/ims_ai_sprint_plan.json` bleibt ihr Abnahme- und Herkunftsnachweis.
Die alten PR179–192 einschließlich PR187a–k bleiben Anforderungs-IDs;
sie bedeuten nicht jeweils einen eigenen GitHub-PR.

Für die Folgearbeit gilt die am 01.10.2026 vom Auftraggeber geprüfte und zum
Merge freigegebene Planung in `docs/plans/ims_explainable_market_2026_10.md`
und `docs/plans/ims_explainable_market_plan.json`. Mit Übernahme von PR #291
nach main ist die Lieferreihenfolge AP4 → AP5 → AP6 → AP7 → AP8 → AP9 angenommen.
AP4 ist nach Anwenderabnahme am 02.10.2026 über PR #293 nach main übernommen
(`9b0d45a22be4314eda8e9ab1db61c506a44160f7`). AP5 ist im Branch
`codex/ims-market-strategy-groups` beauftragt und begonnen. Paketplan und
Fachvertragsvorschlag: `docs/plans/ims_ap5_implementation.md` und
`docs/plans/ims_ap5_market_contract.md`. Der Auftraggeber nahm den konkreten
Vertrag in Draft-PR #294 am 02.10.2026 mit „Vertrag annehmen und umsetzen“ an;
Beleg `docs/reports/ims_ap5_contract_acceptance.md`. Umsetzung im selben PR.
AP5 ist technisch fertig (`done`) und am 02.10.2026 vom Auftraggeber abgenommen;
`docs/reports/ims_ap5_abschlussbericht.md` und `ims_ap5_verification.json`
enthalten die Nachweise. `docs/reports/ims_ap5_user_acceptance.md` dokumentiert
die ausdrücklich erteilte Anwenderabnahme und Mergefreigabe. PR #294 wurde am
02.10.2026 tatsächlich nach main übernommen
(`03f87662e85e6081998bab79e32ee12baac52da1`); Beleg
`docs/reports/ims_ap5_merge.md`. Alle vier Checks am Abnahmekommitt 525916c
bestanden, Merge-Tree identisch. Danach ist AP6 gemäß Fortsetzungsauftrag in
dieser Sitzung im Branch `codex/ims-german-market-top40` begonnen. Auftrag,
Methodenvorschlag, Quellen und Arbeitsstand: `docs/plans/ims_ap6_*` und
`docs/reports/ims_ap6_fortschritt.md`. Die vollständige deutsche Rangbasis,
das gemeinsame Datenjahr und Grenze 40/41 für den deutschen Direktmarkt sind
weiter offen. AP6 ist im später ausdrücklich angenommenen BaFin-Referenzumfang
technisch fertig (`done`); `docs/reports/ims_ap6_produktpruefung.md` und
`ims_ap6_verification.json` enthalten vier erfolgreiche Produkt-CI-Checks,
den echten alpha.6-Installer und installierte Browserprüfungen. Keine deutsche
Top-40-Abnahme; die ursprünglichen Daten-/Methodentore bleiben sichtbar offen.
Ein done-Status im Branch ersetzt keinen main-Abhängigkeitsbeleg.
AP4 liefert erklärbare Oberfläche, CEO-/CIO-/COO-/CSO-Vertriebssichten
und geführten Einstieg samt Einsteigeranleitung. Die Dokumentation wächst in
jedem Paket. Marktaggregate und Strategiefamilien werden in IMS ausgewertet,
Einzel-VU-Details in Excel. Der Deutschland-Fall umfasst 40 Versicherungsgruppen
nach deutschem Erstversicherungsgeschäft über alle Sparten, ohne doppelt
gezählte Töchter; fehlende Daten und nicht modellierte Sparten bleiben sichtbar.

Vor Folgearbeit den angenommenen Plan und sein Manifest lesen.
`scripts/planning/ims_sprint_plan.py` unterstützt die bisherigen AP1–AP3-Aufrufe
und mit `--plan` die Folgepläne AP4–AP9 sowie AP10–AP14. Sein Standardaufruf mit
dem alten Manifest kann „kein Auftrag“ liefern, obwohl AP4–AP9 noch offen sind.
Folgepläne standardmäßig nur als deutlich beschriftete Vorschau erzeugen;
`--mode authorized` benötigt den angenommenen Umfang und erledigte Abhängigkeiten
in aktuell gefetchtem `origin/main` sowie einen echten, paketbezogenen menschlichen
Umsetzungsauftrag mit `--authorization-file`. Freigabebelege niemals erfinden.
Format und Befehle: `docs/plans/ims_work_order_generator.md`. Planannahme,
Umsetzungsfreigabe, technische Fertigstellung und Merge bleiben getrennt.
Einen Folgeauftrag anhand des angenommenen Manifests und der in main erledigten
Abhängigkeiten ausführen; proposed/deferred bedeutet keine Ausführungsfreigabe.
Der Planungsmerge startet kein Umsetzungspaket. Die Entscheidungstore für
Mehr-VU-/Risiko-/Gruppenvertrag, Top-40-Datenbasis, Lebens-Nachfrage und
Markt-/ICT-Kopplung bleiben verbindlich; die AP3-Zustimmung ersetzt sie nicht.

Die am 02.10.2026 zum Merge freigegebene Wettbewerbs-/Vorstandsplanung in
`docs/plans/ims_board_strategy_2026_10.md` und
`docs/plans/ims_board_strategy_plan.json` gilt mit Übernahme von PR #292 nach
main als angenommen. AP4–AP9 bleiben die Lieferbasis; angenommene Ergänzungen
stehen mit Herkunft/Abnahmeauswirkung separat. AP10–AP14 und der minimale
Drei-VU-DORA-Fall benötigen weiterhin eigene Umsetzungs- und Vertragstore.
Historische Abnahmen niemals rückwirkend erweitern. Quellenmatrix, Referenzfall
und aktuelle Manifeste lesen; recherchierte Fähigkeiten, tatsächliche IMS-Läufe
und spezifizierte Modellkanäle unterscheiden.

Der erste Umsetzungsauftrag vom 02.10.2026 autorisierte ausschließlich AP4.
Der anschließende Auftrag desselben Tages bestätigt seine Anwenderabnahme,
erteilt den AP4-Mergeauftrag und beauftragt danach AP5. Abnahmebeleg:
`docs/reports/ims_ap4_user_acceptance.md`. AP5 beginnt erst nach dem tatsächlich
übernommenen AP4-Status in main; sein Mehr-VU-/Risiko-/Aggregat-/Gruppenvertrag
ist anhand kleiner Handfälle zu erklären und anzunehmen. Die angenommenen
Ergänzungen E05-01/E05-02 aus dem Boardplan sind mit eigener Herkunft einzubeziehen.
Der spätere Auftrag derselben Sitzung erteilt die AP5-Abnahme/Mergefreigabe
und setzt danach das nächste Paket AP6 fort; Beleg oben. Keine Freigabe für
AP6-Merge, Veröffentlichung oder Umsetzung von AP7–AP14.

Bei der AP6-Fortsetzung wurde die bereitgestellte BaFin-Top-40-Mappe 2024
vollständig nachgerechnet. Der Auftraggeber hat anschließend ausdrücklich
„Ja, AP6 als gekennzeichneten BaFin-Referenzfall weiterbauen“ bestätigt.
Umfang und Abnahmeauswirkung: `docs/reports/ims_ap6_scope_acceptance.md` und
`docs/plans/ims_ap6_bafin_reference_proposal.md`. Diese AP6-Lieferung heißt
„BaFin-Gruppenauswertung 2024 – Workshop“: verdiente Beiträge einschließlich
Ausland und übernommener Rückversicherung, redaktionelle Gruppensummen ohne
konzerninterne Eliminierung. Kein belegter deutscher Direktmarkt; Fakten,
ungeprüfte Gruppierungen und angenommener Spartenmix bleiben sichtbar getrennt.
Historische Planabnahmen nicht ändern. API/UI/Export/Tests/Anleitung/Installer
im selben PR #295 geliefert. Am 03.10.2026 hat der Auftraggeber ausdrücklich
„Gibst du AP6 zur Anwenderabnahme und zum Merge frei? Freigabe erteilt - fahre fort“
bestätigt; `docs/reports/ims_ap6_user_acceptance.md`. AP6 ist allgemein abgenommen
und am 03.10.2026 über PR #295 nach main übernommen
(`88841290113a37faa6bf117d4cd67dcd9ff0867c`); `docs/reports/ims_ap6_merge.md`.
Alle vier Checks am Abnahmekommitt a2787a9 bestanden, Merge-Tree identisch.
Danach begann AP7 in `codex/ims-market-shock-demos`; Arbeitsauftrag,
Umsetzungsplan und konkreter Vertragsvorschlag stehen in `docs/plans/ims_ap7_*`,
Handproben und Fortschritt in `docs/reports/ims_ap7_*`; fortsetzen im selben
Draft-PR #296. M1 erklärt den neuen
Vertrag; dessen fachliche Annahme steht aus. Lebens-Nachfrage-/ICT-Zeit-/Buchungstore
und die angenommene Ergänzung E07-01 bleiben verbindlich. Keine AP7-Merge- oder
Veröffentlichungsfreigabe und keine AP8–AP14-Umsetzung. Die früheren
Freigabegrenzen oben dokumentieren die damaligen Aufträge.

Die DORA-Benchmark-PDF wurde inzwischen bereitgestellt. Ihre Quelle, Fragen,
Seiten und Bezugsgruppen sind im Register `docs/research/dora_benchmark_2026_06.json`
geprüft; die Einordnung steht in der gleichnamigen Markdown-Datei. Der ehemalige
Zugangsblocker G-BENCH entfällt mit dem Eingang; daraus folgt keine Kalibrierung
und keine Freigabe weiterer Modellkanäle. AP4 erklärt weiterhin vorhandene AP3-Fälle.

Ein Arbeitspaket umfasst Implementierung, API/UI-Anschluss, Tests und Anleitung
in einem Branch und Draft-PR. Mehrere Stunden oder Sitzungen sind zulässig.
Vor Sitzungspausen Fortschritt, Tests, Blocker und nächsten Schritt festhalten;
beim Fortsetzen denselben PR verwenden. Die fachlichen Entscheidungstore und
Modellgrenzen bleiben verbindlich. Erledigte Abnahmen im Manifest mit Belegen
dokumentieren; für abhängige Pakete zählt der nach main übernommene Status.

Unter Windows Python explizit über `.venv\Scripts\python.exe` und npm über
`npm.cmd` im jeweiligen Checkout aufrufen. Jeder neue Worktree braucht eine
eigene Umgebung einschließlich editable install; keine Umgebung eines anderen
Checkouts übernehmen.

## Arbeitsprinzipien

1. **Semantik vor Syntax**
   Portiere Verhalten, Zustandsübergänge, Aggregatbildung, Scheduling und stochastische Logik.
   Portiere nicht blind C-Idiome, Pointer-Muster, Freilisten, ANSI-Terminalcode oder K&R-Stil.

2. **Zusammenhängende, reviewbare Lieferungen**
   Ein klar abgegrenztes Paket darf einen größeren PR über mehrere Sitzungen bilden.
   Halte Commits und interne Meilensteine nachvollziehbar; prüfe die vereinbarten
   Abnahmen. Keine sachfremden Änderungen in das Paket aufnehmen.

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

### Eindeutige Anwender-Releases

Für jede neue an Anwender ausgelieferte Produktfassung eine höhere, bisher
nicht vergebene Release-Nummer verwenden. Die gemeinsame Quelle ist
`python_port/ims/release.py`; Spiegel in Python-/npm-Metadaten werden über
`.venv\Scripts\python.exe scripts\installer\release_metadata.py --set-version VERSION`
aktualisiert. Build und CI prüfen die Übereinstimmung. Installerdateiname,
Windows-Dateiversion, Backend und Anzeige unten links müssen zusammenpassen.
Reine Wiederholungen desselben Produkt-Releases bleiben über Commit und
SHA-256 nachvollziehbar. Schema-/Modellversionen nicht dafür verändern.

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
