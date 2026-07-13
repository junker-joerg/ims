# Backlog weiterer Legacy-Dateifamilien

Diese Liste verhindert, dass einzelne gruene Agrsich-Slices als
Gesamtgleichheit des Modells missverstanden werden.

## Bereits angebunden

- Versicherer-Agrsich: `VU14L1.DAT`, `VUSK1L1.DAT` bis `VUSK1L5.DAT` als
  SK1-Zeitfenster auf derselben unterstuetzten Aggregatstufe
- VN-Agrsich: `IMSVNR01.DAT` bis `IMSVNR06.DAT`, `IMSVNSK1.DAT`,
  `IMSVNVK1.DAT` bis `IMSVNVK3.DAT`
- Versicherer-Klassenaggregate: `IMSVUVK1.DAT` bis `IMSVUVK3.DAT`

## Naheliegende naechste Kandidaten

- Schmale fachliche VU-/VN-Regel- oder Carryover-Slices aus vorhandenen
  Planfixtures, weil die naheliegenden Agrsich-Dateifamilien inzwischen
  versioniert und validiert sind.
- Parameterausgaben wie `VU014PR1.DAT` bleiben geparkt, bis eine belastbare
  Feldklaerung und eigene Parserentscheidung vorliegt.

## Neuer lokaler Kandidatenbestand

Unter `incomming/` liegt nun ein lokaler, nicht versionierter historischer
Kandidatenbestand. Details stehen in
`docs/plans/historical_testdata_inventory.md`. Der Bestand hebt mehrere bisherige
Referenzblocker fachlich auf, wird aber erst in separaten PRs gezielt nach
`tests/references/legacy_agrsich/` uebernommen.

Naechster bevorzugter Arbeitsschnitt:

- Keine Uebernahme von `VU014PR1.DAT`; der naechste groessere Schritt soll den
  geplanten VN-Carryover-Slice als ersten fachlichen Regressionstest
  vorbereiten.
  `VU014PR1.DAT` bleibt weiterhin geparkt; keine Simulation, keine automatische
  historische Regelwahl und keine Vollgleichheitsbehauptung.

## Aktuelle PR-Zaehlung

Nach PR 25 ist die demo-nahe, weiterhin read-only Carryover/Kern-Sicht
vorbereitet:

- PR 22: Carryover-Probe im Kernvalidierungsueberblick als Ergebnisvertrag
  einordnen, ohne Probe aus dem Overview heraus zu starten (erledigt).
- PR 23: Read-only API-Vertrag fuer bereits berechnete Carryover-Probe-Ergebnisse
  vorbereiten, ohne Schreibpfad und ohne Runner-Start (erledigt).
- PR 24: UI-Karte fuer die bereits berechnete Carryover-Probe-Sicht vorbereiten,
  ohne Startbutton oder Ausfuehrungsadapter (erledigt).
- PR 25: Demo-/Doku-Smoke fuer die read-only Carryover/Kern-Sicht ergaenzen
  (erledigt).

Danach bleiben mindestens 3 weitere fachliche Validierungs-PRs offen:

- die Umsetzung des geplanten VN-Carryover-Slices als Regressionstest;
- die Schaerfung der fachlichen Assertions und Dokumentation dieses Slices;
- ein separater Plan fuer einen spaeteren kontrollierten Ausfuehrungsadapter.

Zaehlschnitt: 0 PRs bis zur demo-nahen read-only Carryover/Kern-Sicht; 3+
PRs bis zu einem breiteren fachlichen Anschluss. Diese Zahl ist kein
Vollgleichheits- oder Gesamtabschlussversprechen.

Der erste echte fachliche Regressionstest ist nach PR 28 ausgefuehrt und
eingeordnet:

- PR 27: VN-Carryover-Slice aus
  `replay_vn_policyholder_transition_plan.json` als gezielten Regressionstest
  ausfuehren (erledigt:
  `tests/test_first_fachlicher_vn_carryover_regression.py`).
- PR 28: Assertions und Dokumentation fuer diesen Slice schaerfen, weiterhin
  ohne historische Vollgleichheitsbehauptung (erledigt:
  `docs/migration/first_fachlicher_regressionstest.md`).

Bis zur geschaerften Einordnung dieses ersten fachlichen Regressionstests
bleiben nach PR 28 noch 0 PRs.

Naechster bevorzugter fachlicher Schnitt:

- PR 29: zweiten schmalen Slice waehlen (erledigt:
  `docs/plans/second_fachlicher_slice_test_plan.md`). Gewaehlt ist eine
  VN-Regelwirkung ueber explizite `best_info`-Snapshots fuer Policyholder `21`,
  Versicherer `11/12` und Periode `5`. Auch dieser Schnitt bleibt ohne
  Simulation und ohne historische Vollgleichheitsbehauptung.
- PR 30: geplanten VN-Regel-Snapshot-Slice als zweiten fachlichen
  Regressionstest umsetzen und dokumentieren (erledigt:
  `tests/test_second_fachlicher_vn_rule_snapshot_regression.py` und
  `docs/migration/second_fachlicher_regressionstest.md`).

Bis zum zweiten ausgefuehrten fachlichen Regressionstest bleiben nach PR 30
noch 0 PRs.

Der dritte fachliche Slice ist nach PR 31 geplant:

- PR 31: VU-Carryover-Fixture fuer Versicherer `10` von lokaler Periode `2`
  nach `3` als naechsten schmalen Regressionstest waehlen (erledigt:
  `docs/plans/third_fachlicher_slice_test_plan.md`).
- PR 32: geplanten VU-Carryover-Fixture-Slice als dritten fachlichen
  Regressionstest umsetzen und dokumentieren (erledigt:
  `tests/test_third_fachlicher_vu_carryover_regression.py` und
  `docs/migration/third_fachlicher_regressionstest.md`).

Bis zum dritten ausgefuehrten fachlichen Regressionstest bleiben nach PR 32
noch 0 PRs.

## Rest-PR-Planung

- PR 1: `IMSVNR01.DAT` und `IMSVNR02.DAT` uebernehmen und validieren
  (erledigt).
- PR 2: `IMSVNR03.DAT` und `IMSVNR04.DAT` uebernehmen und validieren
  (erledigt).
- PR 3: `IMSVNR06.DAT` uebernehmen; `IMSVNR05.DAT` mit der Gesamtfamilie
  abgleichen (erledigt).
- PR 4: Coverage-/Next-Family-Plan so aktualisieren, dass `policyholder_rule`
  nach vollstaendiger IMSVNR-Abdeckung als covered erscheint (erledigt).
- PR 5: VN-Klassenaggregate `IMSVNVK*.DAT` vorbereiten und validieren
  (erledigt; `policyholder_class` ist im Bundle belegt).
- PR 6: Versicherer-Klassenaggregate `IMSVUVK*.DAT` vorbereiten und validieren
  (erledigt; `insurer_class` ist im Bundle belegt).
- PR 7: Parameterausgaben wie `VU014PR1.DAT` nur nach eigener Feldklaerung
  vorbereiten (erledigt: Inventar, verwandte lokale Kandidaten und Altcode-Spur
  dokumentiert; Feldmapping bleibt offen, keine Referenzuebernahme).
- PR 8: `VU014PR1.DAT` nur wieder aufnehmen, wenn eine historische
  Schreibstelle oder ein belastbares Feldmapping fuer `Pr1L1` bis `Pr1L5`
  vorliegt; dann eigener Parser und gezielte Tests.
- PR 9: Naechsten Kernlogik-Schnitt aus den vorhandenen Planfixtures waehlen
  (erledigt: stabile Execution-Summary fuer ausgefuehrte explizite
  VU/VN-Mehrperiodenlaeufe, ohne Simulation und ohne automatische historische
  Regelwahl).
- PR 10: Execution-Summary-Vertrag im `ims_core_validation_overview` read-only
  planen und dokumentieren (erledigt; keine Ausfuehrung aus dem Overview
  heraus).
- PR 11: Read-only API-/UI-Anbindung fuer den Kernvalidierungsueberblick
  vorbereiten, damit die UI den Demo-Status ohne Laufstart anzeigen kann
  (erledigt).
- PR 12: Read-only Brueckenplan fuer Run-Control-Aktionsplan und
  Kernlauf-Diagnosen dokumentieren und als kleines Python-DTO vorbereiten,
  ohne neuen Endpunkt, Schreibpfad oder Runner-Start (erledigt).
- PR 13: Optional eine rein lesende API-Anbindung fuer das Bruecken-DTO
  vorbereiten; weiterhin ohne UI-Startpfad und ohne Ausfuehrungsadapter
  (erledigt).
- PR 14: Optional eine rein lesende UI-Karte fuer die Bruecken-Antwort
  vorbereiten; weiterhin ohne Startbutton, Upload oder Ausfuehrungsadapter
  (erledigt).
- PR 15: Bruecken-Demo-/Screenshot-Smoke optional aktualisieren, wenn ein
  visueller Beleg fuer die neue Karte gebraucht wird (erledigt).
- PR 16: Naechsten schmalen fachlichen VU-/VN-Regel- oder Carryover-Slice aus
  vorhandenen Planfixtures planen: Altcode-Spur, Fixture-Bezug, erwartete
  Zwischenzustaende und Testgrenzen unter
  `docs/plans/explicit_period_transition_slice.md` dokumentieren, noch ohne neue Fachlogik.
  Periodenuebergangs-/Carryover-Grenze fuer `VU14L1.DAT` und `VUSK1L4.DAT` (erledigt).
- PR 17: Explizite Periodenuebergangs-/Carryover-Diagnose aus dem Plan
  vorbereiten, weiterhin ohne Runner-Start, Simulation oder automatische
  historische Regelwahl (erledigt).
- PR 18: Kleines VN-Policyholder- oder Carryover-Anschlussfixture planen, damit
  `explicit_period_transition_no_policyholders` gezielt aufgeloest oder als
  weiterhin offene Grenze bestaetigt wird (dieser Schnitt:
  `replay_vn_policyholder_transition_plan.json`).
- PR 19: Engen Carryover-Code-Slice aus dem Anschlussfixture planen oder
  vorbereiten, weiterhin ohne historische Regelableitung und ohne
  Vollsimulation (dieser Schnitt: Carryover-Kandidatenlisten in der
  Uebergangsdiagnose, keine Carryover-Ausfuehrung).
- PR 20: Echten Carryover-Code-Slice separat planen oder vorbereiten, dabei
  weiterhin nur vorhandene portierte Carryover-Bausteine nutzen und keine
  historische Regelableitung einfuehren (dieser Schnitt:
  `docs/plans/explicit_transition_carryover_code_slice.md`, noch keine
  Carryover-Ausfuehrung).
- PR 21: Den geplanten engen Carryover-Probe als Code-/Test-Schritt umsetzen:
  nur explizites Opt-in, nur vorhandene portierte Carryover-Bausteine,
  Uebergangsdiagnose als Grenzpruefung, keine API-/UI-/Run-Control-Anbindung
  (dieser Schnitt: `ims.engine.explicit_transition_carryover_probe`, erledigt).
- PR 22: Carryover-Probe im Kernvalidierungsueberblick als read-only Vertrag
  aufnehmen, aber keinen Probe-Start aus dem Overview heraus einfuehren
  (dieser Schnitt: `explicit_transition_carryover_probe_contract`, erledigt).
- PR 23: Read-only API-Vertrag fuer bereits berechnete Probe-Ergebnisse
  vorbereiten (dieser Schnitt:
  `GET /api/core-validation/carryover-probe-contract`, erledigt).
- PR 24: UI-Karte fuer die bereits berechnete Carryover-Probe-Sicht
  vorbereiten (dieser Schnitt: `Carryover-Probe-Vertrag` in der Workbench,
  erledigt).
- PR 25: Demo-/Doku-Smoke fuer die read-only Carryover/Kern-Sicht ergaenzen
  (dieser Schnitt: `carryover-probe-contract` im Demo-Smoke, erledigt).
- PR 26: Ersten fachlichen VN-Carryover-Slice-Test planen
  (dieser Schnitt: `docs/plans/first_fachlicher_slice_test_plan.md`).
- PR 27: Den geplanten VN-Carryover-Slice als fachlichen Regressionstest
  ausfuehren, nur ueber vorhandene portierte Probe-/Carryover-Bausteine
  (dieser Schnitt: `tests/test_first_fachlicher_vn_carryover_regression.py`,
  erledigt).
- PR 28: Assertions und Dokumentation fuer den ersten fachlichen
  Regressionstest schaerfen, ohne Vollgleichheitsbehauptung (dieser Schnitt:
  `docs/migration/first_fachlicher_regressionstest.md`, erledigt).
- PR 29: Zweiten schmalen fachlichen Slice auswaehlen, vorzugsweise
  VU-Carryover oder VN-Regelwirkung ueber explizite Snapshots (dieser Schnitt:
  VN-Regelwirkung ueber explizite `best_info`-Snapshots, erledigt).
- PR 30: Geplanten VN-Regel-Snapshot-Slice als zweiten fachlichen
  Regressionstest umsetzen und dokumentieren (dieser Schnitt:
  `tests/test_second_fachlicher_vn_rule_snapshot_regression.py`, erledigt).
- PR 31: Optional weiteren VN-Regel-Snapshot oder VU-Carryover-Fixture planen,
  falls der Review mehr fachliche Breite vor einer Run-Control-Planung
  verlangt (dieser Schnitt: VU-Carryover-Fixture geplant, erledigt).
- PR 32: Geplanten VU-Carryover-Fixture-Slice als dritten fachlichen
  Regressionstest umsetzen und dokumentieren (dieser Schnitt:
  `tests/test_third_fachlicher_vu_carryover_regression.py`, erledigt).
- PR 33: Danach entscheiden, ob ein weiterer VN-/VU-Regel-Snapshot oder ein
  schmaler Ausfuehrungsadapterplan fachlich sinnvoller ist.
- PR 34+: Eine spaetere Run-Control-Anbindung oder breitere fachliche
  Regel-Slices erst nach separater Freigabe vorbereiten, weiterhin ohne
  Vollgleichheitsbehauptung.

Restgrenze fuer alle Folge-PRs: weiterhin ohne Vollgleichheitsbehauptung.

## Validierungsregel

Jede Dateifamilie bekommt:

- echte Referenzdatei im Testbestand,
- Parser mit whitespace-robustem Headervergleich,
- mindestens eine positive Alignment-Zeile,
- mindestens einen Negativtest,
- Dokumentation der noch nicht validierten Bereiche.
