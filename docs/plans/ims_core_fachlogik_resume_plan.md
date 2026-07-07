# Plan: IMS-Kern-Fachlogik nach Workbench-v1

## Ziel

Dieser Plan markiert den Ruecksprung vom abgeschlossenen lokalen
Workbench-Ausbau in die eigentliche IMS-Fachlogik. Er beschreibt den naechsten
reviewbaren Kernblock, ohne bereits eine neue Simulation, einen Scheduler oder
eine historische Vollgleichheit zu behaupten.

## Ausgangsstand

Die Workbench-v1 stellt lokale Metadaten, Run-Control-Grenzen, Diagnose,
Readiness und eine rein lesende Browser-Oberflaeche bereit. Dieser Rahmen ist
nuetzlich, aber nicht der fachliche IMS-Kern.

Der portierte Kern enthaelt bereits belastbare Ausschnitte:

- `python_port/ims/model/entities.py` fuer kleine BAV-, VU- und VN-Zustandscontainer.
- `python_port/ims/engine/context.py` und `python_port/ims/engine/scheduler.py` fuer
  explizite Kontext- und Scheduling-Grundlagen.
- `python_port/ims/engine/rng.py` fuer kontrollierte Zufallsquellen.
- BAV-/Agrsich-Bausteine in `python_port/ims/model/bav_service.py`,
  `python_port/ims/model/agrsich_service.py`, `python_port/ims/model/agrsich_export.py`
  und `python_port/ims/model/agrsich_writer.py`.
- VU- und VN-Regel-Slices in `python_port/ims/model/vu_rules.py`,
  `python_port/ims/model/vn_rules.py`, `python_port/ims/model/vn_insurance_rules.py`
  und `python_port/ims/model/vn_damage_rules.py`.
- explizite Mehrperioden-Adapter in `python_port/ims/engine/explicit_period_runner.py`
  und `python_port/ims/engine/explicit_period_plan.py`.
- Legacy-orientierte Referenzen und Vergleichsfixtures unter `tests/fixtures/` und
  `tests/references/legacy_agrsich/`.

`legacy_c/` ist in diesem Stand nur ein Platzhalter. Der naechste Kernschritt
darf deshalb keine nicht vorhandene C-Quelle als gelesen behaupten. Belastbare
Referenzpunkte sind die vorhandenen Portierungsplaene, Python-Slices,
Legacy-DAT-Referenzen und Vergleichstests.

## Naechster groesserer Kernblock

Der naechste fachliche Block sollte die vorhandenen expliziten VU/VN-Periodenlaeufe
in Richtung validierbarer Kernlauf verdichten:

1. bestehenden expliziten Periodenplan und Runner inventarisieren;
2. die heute unterstuetzten Snapshot-Familien und Carryover-Flags als stabile
   Eingabegrenze dokumentieren;
3. eine kleine, deterministische Kernlauf-Diagnose aus vorhandenen Planfixtures
   ableiten;
4. die Ausgabe auf Periodenfolge, globale Perioden, VU-Regelanwendungen,
   VN-Versicherungsregeln, VN-Schaden-/Settlement-Anwendungen und Legacy-Targets
   beschraenken;
5. keine neuen Fachregeln einfuehren, bevor diese Diagnose die vorhandenen
   Referenzfenster nachvollziehbar beschreibt.

Der passende PR-Titel waere:

`Ergaenze IMS-Kernlauf-Diagnose fuer explizite Periodenplaene`

## Vorgeschlagene PR-Reihenfolge

1. Kernlauf-Diagnose fuer vorhandene explizite Periodenplaene, nur lesend und
   ohne neue Fachregel. Der Befehl
   `python -m ims.engine.explicit_period_diagnostics tests/fixtures/replay_vu14_period_plan.json`
   liest Planstruktur, Periodenfolge, globale Perioden, Snapshot-Familien,
   erwartete Regelanwendungsgrenzen und Legacy-Bezuege, startet aber keinen
   Runner und schreibt keine Ausgaben. Dieser Schritt ist umgesetzt.
2. Validierungsbericht fuer die vorhandenen Legacy-Agrsich-Referenzen
   vereinheitlichen, ohne Toleranzen still zu veraendern. Der lokale Befehl
   `python -m ims.model.legacy_validation_overview tests/fixtures/legacy_validation_bundle.json`
   fasst vorhandene Legacy-Agrsich-Validierungsfixtures als JSON zusammen,
   berichtet Tabellen, Perioden, Abweichungsachsen und die dokumentierte
   `legacy_compare_default`-Toleranz, startet aber keinen Runner und schreibt
   keine Reportartefakte. Dieser Schritt ist umgesetzt.
3. Diagnose-Buendel fuer mehrere vorhandene explizite Periodenplaene
   zusammenfassen. Der Befehl
   `python -m ims.engine.explicit_period_diagnostics_bundle tests/fixtures/replay_vu14_period_plan.json tests/fixtures/replay_vusk1_period_plan.json`
   aggregiert Planstatus, Perioden, globale Perioden, Snapshot-Familien und
   Legacy-Bezuege, ohne Runner oder Simulation zu starten. Dieser Schritt ist
   umgesetzt.
4. IMS-Kernvalidierungsueberblick aus Diagnose-Buendel,
   Legacy-Validierungsueberblick, Coverage-Matrix und Next-Family-Plan
   zusammenfuehren. Der Befehl
   `python -m ims.engine.core_validation_overview --legacy-fixture tests/fixtures/legacy_validation_bundle.json tests/fixtures/replay_vu14_period_plan.json tests/fixtures/replay_vusk1_period_plan.json`
   bleibt read-only und zeigt, welche weitere Validierung durch fehlende echte
   historische Referenzen blockiert ist.
5. Danach einen schmalen VU- oder VN-Regel-Slice aus den vorhandenen
   Plan-Dateien auswaehlen und mit explizitem Ursprung dokumentieren.
6. Erst danach eine echte Run-Control-Anbindung an Kernlauf-Diagnosen planen.

## Aktualisierte PR-Restplanung

Nach dem IMS-Kernvalidierungsueberblick bleiben ohne neue historische
Referenzdateien voraussichtlich:

- 2-4 PRs fuer weitere Kernlauf-Diagnosen und Akzeptanzgrenzen;
- 2-4 PRs fuer schmale VU-/VN-Regel- oder Carryover-Slices aus vorhandenen
  Planfixtures;
- 1-3 PRs fuer eine spaetere read-only Run-Control-Anbindung an diese
  Kernvalidierungsdiagnosen.

Mit neuen echten historischen Referenzen unter `tests/references/legacy_agrsich/`
kommen je Dateifamilie voraussichtlich 2-4 PRs hinzu: Parser-/Alignment-Test,
Fixture-Erweiterung, Coverage-/Overview-Anpassung und gegebenenfalls
Abweichungsanalyse.

In Summe bleiben damit ohne neue historische Dateien grob ca. 5-11 reviewbare
PRs. Mit weiterer historischer Validierung bleibt die konservative Groesse bei
ca. 12-25+ PRs. Diese Schaetzung ist keine historische
Vollgleichheitsbehauptung.

## Grenzen

- keine Fachlogikaenderung in diesem Plan-PR;
- keine Simulation starten;
- kein neuer HTTP-Endpunkt;
- kein HTTP- oder UI-Schreibpfad;
- kein Browser-Upload oder Browser-Download;
- kein funktionaler Run-Start;
- kein Szenario-Editor;
- keine SQLite-Migration;
- keine historische Vollgleichheitsbehauptung;
- keine Behauptung, dass nicht vorhandene `legacy_c/`-Quellen gelesen wurden.

## Validierung fuer diesen Plan

Dieser Plan wird durch Dokumentationstests abgesichert. Sie pruefen, dass der
Uebergang zur Fachlogik die vorhandenen Kernmodule benennt, den naechsten
Kernblock klar begrenzt und die Nicht-Ziele beibehaelt.
