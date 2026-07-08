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

## Bisheriger groesserer Kernblock

Der erste fachliche Block nach der Workbench hat die vorhandenen expliziten
VU/VN-Periodenlaeufe in Richtung validierbarer Kernlauf verdichtet:

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

Dieser Block ist umgesetzt. Der aktuelle Stand trennt weiterhin:

- read-only Plan- und Bundle-Diagnosen, die keine Runner starten;
- echte explizite Mehrperiodenlaeufe, die nur ueber explizite Snapshots und
  Tests/gezielte Aufrufe laufen;
- `build_explicit_multi_period_execution_summary` als stabile Beschreibung eines
  bereits ausgefuehrten expliziten Mehrperiodenergebnisses.

## Aktueller groesserer Kernblock

Der aktuelle groessere Schritt ordnet die Execution-Summary-Vertraege und die
vorhandenen expliziten VU/VN-Periodenplaene in den IMS-Kernvalidierungsueberblick
und die lokale Demo-Grenze ein, ohne dort einen Lauf zu starten. Ziel ist eine
gemeinsame, read-only Sprache fuer:

1. geplante Periodenstruktur aus `explicit_period_diagnostics`;
2. historische Referenzabdeckung aus `legacy_validation_overview` und Coverage;
3. vorhandene Execution-Summary-Felder als erwarteter Ergebnisvertrag fuer
   spaetere kontrollierte Ausfuehrungsadapter;
4. klare Blocker, wenn nur Plan-Diagnosen vorliegen und keine ausgefuehrte
   Summary vorhanden ist;
5. weiterhin keine Simulation, keine automatische historische Regelwahl und
   keine Vollgleichheitsbehauptung.

Der erste UI-/Demo-Anschluss ist umgesetzt: `/api/core-validation/overview` und
die Workbench-Karte `Kernvalidierungsueberblick` zeigen Plananzahl,
Periodenachsen, Legacy-Abdeckung und Execution-Summary-Vertrag lesend. Die
lokale Demo-Checkliste dokumentiert den aktuellen Diagnosebefund:
2 Planfixtures, 8 Perioden, globale Perioden `1, 2, 3, 4, 101, 102, 103, 104`,
19 Legacy-Referenzen, 6300 abgedeckte Zeilen und `execution_performed = false`.

Der passende PR-Titel waere:

`Plane Execution-Summary-Vertrag im IMS-Kernvalidierungsueberblick`

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
   Plan-Dateien auswaehlen und mit explizitem Ursprung dokumentieren. Der erste
   Anschluss ist umgesetzt: `build_explicit_multi_period_execution_summary`
   beschreibt ausgefuehrte explizite VU/VN-Mehrperiodenlaeufe mit
   Periodenachsen, Anwendungszaehlungen, Carryover- und Legacy-Report-Status,
   ohne Simulation oder automatische historische Regelwahl zu behaupten.
6. Execution-Summary-Vertrag im `ims_core_validation_overview` planen
   (dieser Schnitt): read-only, ohne Runner-Start und ohne Ausfuehrung aus dem
   Overview heraus, aber mit expliziter Kennzeichnung, welche Ergebnisfelder ein
   spaeter kontrollierter Ausfuehrungsadapter liefern muss.
   Kurzgrenze: keine Ausfuehrung aus dem Overview heraus.
7. Read-only API-/UI-Anbindung fuer den Kernvalidierungsueberblick in die
   lokale Demo-Grenze einordnen, weiterhin ohne funktionalen Start. Dieser
   Anschluss ist umgesetzt: `/api/core-validation/overview`, die UI-Karte und
   `docs/migration/workbench_demo_checklist.md` zeigen die vorhandenen
   VU/VN-Periodenplaene diagnostisch.
8. Erst danach eine echte Run-Control-Anbindung an Kernlauf-Diagnosen planen.

## Aktualisierte PR-Restplanung

Nach dem lokalen Inventar der historischen Testdaten unter `incomming/` ist der
Referenzblocker fuer mehrere Dateifamilien nicht mehr grundsaetzlich offen. Die
Versicherer-SK1-Zeitfenster `VUSK1L1.DAT` bis `VUSK1L5.DAT` sind nun als
versionierte Legacy-Referenzfenster im Bundle abgedeckt; weitere lokale
Kandidaten bleiben noch nicht versionierte Referenzen.

Aktualisierte grobe Restplanung:

- 0-1 PRs fuer weitere Inventar-/Akzeptanzgrenzen der neuen lokalen Kandidaten;
- 2-4 PRs fuer `IMSVNR01.DAT` bis `IMSVNR06.DAT`;
- 2-5 PRs fuer Klassenaggregate `IMSVNVK*.DAT` und `IMSVUVK*.DAT`;
- 2-4 PRs fuer schmale VU-/VN-Regel- oder Carryover-Slices aus vorhandenen
  Planfixtures;
- 1 PR fuer einen read-only Execution-Summary-Vertrag im
  Kernvalidierungsueberblick;
- 1-2 PRs fuer eine spaetere read-only Run-Control-Anbindung an diese
  Kernvalidierungsdiagnosen und Summary-Vertraege.

Damit bleiben grob ca. 8-18+ reviewbare PRs bis zu einem deutlich breiteren
historischen Validierungsstand. Diese Schaetzung ersetzt keine
Vollgleichheitspruefung.

## Grenzen

- keine Fachlogikaenderung in diesem Plan-PR;
- keine Simulation starten;
- kein neuer HTTP-Endpunkt;
- kein HTTP- oder UI-Schreibpfad;
- kein Browser-Upload oder Browser-Download;
- kein funktionaler Run-Start;
- kein Start eines expliziten Periodenrunners aus dem Kernvalidierungsueberblick;
- kein Szenario-Editor;
- keine SQLite-Migration;
- keine historische Vollgleichheitsbehauptung;
- keine Behauptung, dass nicht vorhandene `legacy_c/`-Quellen gelesen wurden.

## Validierung fuer diesen Plan

Dieser Plan wird durch Dokumentationstests abgesichert. Sie pruefen, dass der
Uebergang zur Fachlogik die vorhandenen Kernmodule benennt, den naechsten
Kernblock klar begrenzt und die Nicht-Ziele beibehaelt.
