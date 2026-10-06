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
Draft-PR #296. Der Auftraggeber nahm den konkreten Lebens-/ICT-Vertrag am
03.10.2026 ausdrücklich an; `docs/reports/ims_ap7_contract_acceptance.md`.
M1–M4 sind im selben PR technisch fertig (`done`), Produkt alpha.7.
`docs/reports/ims_ap7_abschlussbericht.md`, `ims_ap7_produktpruefung.md` und
`ims_ap7_verification.json` belegen vier grüne Produktchecks an 37fe791,
2.755 Python-Tests/14 Subtests, 70 Browserfälle, echten Installer mit
14 Lifecycle-/70 installierten Browserprüfungen und gleiche vier 100er-Digests
im Checkout und installierten Produkt. ICT zeigt Ereignis, Abhängigkeit,
Kapazität/Queue, Vertrag und Buchung für beide Vergleichsseiten; Anleitung
und zwölf echte Browserbilder sind offline geliefert. Am 03.10.2026 erteilte
der Auftraggeber ausdrücklich die Anwenderabnahme und den AP7-Mergeauftrag;
`docs/reports/ims_ap7_user_acceptance.md`. Nach tatsächlichem AP7-Merge ist
AP8 beauftragt. Die Abschluss-/Abnahmedokumentation ändert keine Produktressource.
Lebens-Nachfrage-/ICT-Zeit-/Buchungsgrenzen
und die angenommene Ergänzung E07-01 bleiben verbindlich. AP8 übernimmt die
angenommene Ergänzung E08-01 mit eigener Herkunft und unterscheidet Addition,
Wechselwirkungen und Korrelation. Kein AP8-Merge, öffentliches Release oder
AP9–AP14-Auftrag. Die früheren
Freigabegrenzen oben dokumentieren die damaligen Aufträge.

AP7 wurde am 03.10.2026 tatsächlich über PR #296 nach main übernommen
(`32ba3112d994f57f33e64e1bc318e7d095223cd0`); `docs/reports/ims_ap7_merge.md`.
Alle vier Checks an f440f4c bestanden, main-Tree identisch, 372 Ressourcen
unverändert und vier vollständige Ergebnisdigests gleich zur gelieferten Fassung.
Danach begann AP8 im Branch `codex/ims-market-visualizations` nach erfolgreich
erzeugtem authorized-Auftrag gegen tatsächliches origin/main. Paketplan und
Darstellungsvertrag: `docs/plans/ims_ap8_implementation.md`,
`docs/plans/ims_ap8_view_contract.md`; Stand `docs/reports/ims_ap8_fortschritt.md`.
AP8 liefert sechs verknüpfte Ansichten und die separat angenommene E08-01 mit
eigener Herkunft. Bestehende Rechnungen bleiben unverändert; Filter verändern
keinen Lauf. Nenner/Gewichte/Zeitpunkte und Addition/Kanal/Wechselwirkung/
Korrelation explizit erklären. Ein Paket-PR einschließlich API/UI/Tests/
Anleitung/Installer; keine zusätzliche Vertragsannahme erfinden. Kein AP8-Merge,
öffentliches Release oder AP9–AP14-Auftrag.
AP8 ist im angenommenen Umfang technisch fertig (`done`) im Paket-PR #297.
Produktpunkt `17cbf5e631233ff5e5f5153a673a2eb6adaa7375`: vier echte Produktchecks
erfolgreich, 2.764 Python-Tests/14 Subtests, 83 Browserfälle, 14 Installer-Lifecycle-
und 83 installierte Browserprüfungen. Alle vier 100er-/25er-Prefixfälle erhalten
die AP7-Modell-Digests; Checkout und installierte Anwendung stimmen überein.
Sechs verknüpfte Ansichten, E08-01 Fokus/Rivalen/Modellmarkt, sichtbare ICT-Pfade,
Nenner/Gewichte/Buchungsbrücke und frische JSON-/Einzel-VU-Exporte geliefert.
Alpha.8 / Windows 2.0.0.8, Offline-Anleitung mit zwölf echten Bildern und
387 an den Git-Tree gebundene Ressourcen. Unversicherter Schaden bleibt
ausdrücklich außerhalb der VU-Bücher. Belege `docs/reports/ims_ap8_abschlussbericht.md`,
`ims_ap8_produktpruefung.md` und `ims_ap8_verification.json`.
Anwenderabnahme/Merge für AP8 weiter offen; kein öffentlicher Release/AP9–AP14.
Ein done-Status im Branch ersetzt keinen nach main übernommenen Abhängigkeitsbeleg.

Am 03.10.2026 meldete der Auftraggeber zunehmende Orientierungsprobleme und
hielt die Oberfläche für nicht vorzeigbar. AP8 ist deshalb im selben Paket-PR
#297 erneut in Arbeit: `docs/plans/ims_ap8_usability_correction.md`.
Direkte Markt-Navigation, getrennte Arbeitsbereiche, jeweils eine von sechs
Ansichten, klarer Lade-/Rechenablauf und erhaltene Zustände werden überprüft.
Die neue Produktfassung alpha.9 bezeichnet die AP8-Bedienkorrektur, kein AP9.
Frühere alpha.8-Abschlussbelege bleiben historisch; neue Produktprüfungen sind
separat erforderlich. Damaliges AP8-Manifest in_progress/technically_complete
false. Anwenderabnahme und Merge bleiben offen, AP9–AP14 nicht beauftragt.

Am vom Client ausgewiesenen 04.10.2026 beauftragte der Anwender die gesamte
Benutzerführung anhand vier Cockpitbildern erneut: Vorstandsstrategien endogen,
Marktänderungen durch Schocks/Regulierung/Entwicklungen exogen. AP8 wird im
selben PR #297 als gemeinsames Marktexperiment weitergeführt; Plan
`docs/plans/ims_ap8_experiment_cockpit.md`. Produkt alpha.10 bezeichnet diese
Bedien-/Gestaltungskorrektur, kein AP9. Bestehende AP5-/AP7-Eingabekanäle werden
verbunden, der Simulationskern bleibt unverändert. Neue Produkt-, Browser- und
Installerbelege sind erforderlich; frühere Fassungen bleiben historisch.
Anwenderabnahme/Merge und AP9–AP14 bleiben offen beziehungsweise nicht beauftragt.

AP8-Cockpitkorrektur alpha.10 ist am 04.10.2026 technisch fertig (`done`) im selben
PR #297. Produktpunkt `11384cf69f14f52d3c0f0ae72537986a94484e57`: vier erfolgreiche
Produktchecks, 2764 Python-Tests/14 Subtests, 91 Browserfälle und 14 Lifecycle-/
91 installierte Browserprüfungen. 409 Ressourcen am Git-Tree gebunden;
authentischer Windows-Installer 2.0.0.10 geliefert. Gemeinsames Marktexperiment
mit endogenen Vorstands-/VN-Eingaben, exogenen Ereignissen, tatsächlichem ICT-Netz,
frischen Exporten und aktueller Offline-Anleitung. Vier AP7-Modell-Digests und
Kernverträge unverändert. Belege `docs/reports/ims_ap8_cockpit_abschlussbericht.md`,
`ims_ap8_cockpit_produktpruefung.md`, `ims_ap8_cockpit_verification.json`.
Aktuelles Manifest done/technically_complete true; frühere alpha.8/alpha.9-
Stände oben bleiben historisch. Anwenderabnahme pending, Merge nicht autorisiert,
kein öffentlicher Release/AP9–AP14-Auftrag. Der spätere Dokumentationshead ist
vom geprüften Produktpunkt zu unterscheiden; keine Produktressource verändert.

Am 06.10.2026 beauftragte der Anwender vier weitere UI-Designreferenzen,
ein notwendiges Eingabeinventar, Grafiken des Rechenkerns mit fachlichen
Abweichungen zum ursprünglichen IMS und einen Dokumentationsaudit. AP8 bleibt
im selben PR #297; Plan `docs/plans/ims_ap8_modelworld_documentation.md`.
Alpha.11 bezeichnet Modellwelt, Unternehmensportfolio und Wiedergabe bereits
vollständig berechneter Perioden, keinen pausierbaren Kernzustand und kein AP9.
Die AP5-/AP7-Rechnungen bleiben unverändert. Frühere alpha.10-Belege bleiben
historisch. Alpha.11 ist technisch fertig am Produktpunkt 6117b72eb48a05d93b73e354099e5528a8b0ba6b:
2764 Python-Tests/14 Subtests, 99 Checkout-/99 installierte Browserfälle,
14 Lifecycle-Prüfungen und 424 Git-Tree-gebundene Ressourcen. Belege
`docs/reports/ims_ap8_modelworld_produktpruefung.md` und
`ims_ap8_modelworld_verification.json`. Marktkerne und vier AP7-Digests unverändert. Anwenderabnahme
und Merge weiter offen, kein öffentliches Release oder AP9–AP14-Auftrag.

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
