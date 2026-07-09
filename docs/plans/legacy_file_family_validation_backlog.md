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
  ausgefuehrten engen Carryover-Probe read-only in den Kernvalidierungsblick
  einordnen. `VU014PR1.DAT` bleibt weiterhin geparkt; keine Simulation, keine
  automatische historische Regelwahl und keine Vollgleichheitsbehauptung.

## Aktuelle PR-Zaehlung

Nach PR 21 bleiben bis zu einer demo-nahen, weiterhin read-only
Carryover/Kern-Sicht noch 4 klar planbare PRs:

- PR 22: Carryover-Probe im Kernvalidierungsueberblick als Ergebnisvertrag
  einordnen, ohne Probe aus dem Overview heraus zu starten.
- PR 23: Read-only API-Vertrag fuer bereits berechnete Carryover-Probe-Ergebnisse
  vorbereiten, ohne Schreibpfad und ohne Runner-Start.
- PR 24: UI-Karte fuer die bereits berechnete Carryover-Probe-Sicht vorbereiten,
  ohne Startbutton oder Ausfuehrungsadapter.
- PR 25: Demo-/Doku-Smoke fuer die read-only Carryover/Kern-Sicht ergaenzen.

Danach bleiben mindestens 3 weitere fachliche Validierungs-PRs offen:

- ein schmaler VU- oder VN-Regel-Slice aus vorhandenen Planfixtures;
- ein gezielter Abgleich dieses Slices mit vorhandenen Legacy-Referenzfenstern;
- ein separater Plan fuer einen spaeteren kontrollierten Ausfuehrungsadapter.

Zaehlschnitt: 4 PRs bis zur demo-nahen read-only Carryover/Kern-Sicht; 7+
PRs bis zu einem breiteren fachlichen Anschluss. Diese Zahl ist kein
Vollgleichheits- oder Gesamtabschlussversprechen.

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
  aufnehmen, aber keinen Probe-Start aus dem Overview heraus einfuehren.
- PR 23: Read-only API-Vertrag fuer bereits berechnete Probe-Ergebnisse
  vorbereiten.
- PR 24: UI-Karte fuer die bereits berechnete Carryover-Probe-Sicht
  vorbereiten.
- PR 25: Demo-/Doku-Smoke fuer die read-only Carryover/Kern-Sicht ergaenzen.
- PR 26+: Eine spaetere Run-Control-Anbindung oder breitere fachliche
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
