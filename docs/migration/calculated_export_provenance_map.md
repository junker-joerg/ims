# Herkunfts- und Erzeugungswegkarte der Kernexporte

Stand: 2026-08-25
Berichtsvertrag: `pr71-v1`

## Ergebnis

PR 71 kartiert alle 15 berechneten Exportidentitaeten des ersten
Produktionsfreigabekorpus. Der Befund trennt drei Aussagen:

1. Die 19 historischen Referenzziele und 6.300 Vergleichsperioden sind
   vorhanden und auf 15 eindeutige Exportidentitaeten abgebildet.
2. Der Python-Port kann fuer explizit gelieferte Periodenzustaende alle 15
   Identitaeten aggregieren und als Tabellen darstellen.
3. Fuer keine Identitaet ist die unabhaengige Zustandsentstehung ueber das
   gesamte geforderte Fenster von 100 bis 500 Perioden belegt.

Der fehlende Teil ist damit kein Satz von 15 Dateiwritern. Es sind zwei
gemeinsame, noch nicht geschlossene Zustandswege fuer Versicherer und VN.

## Historischer Ursprung

`IMSDATA.C` definiert die Dateinamensfelder `agvu1nm`, `agvu3nm`, `agvu4nm`,
`agvn2nm`, `agvn3nm` und `agvn4nm`. `IMS.E`, `act Agrsich`, liest den jeweils
aktuellen VU-/VN-Zustand, bildet die Stufen I bis IV und schreibt die
Periodenzeilen.

| Bereich | Dateinamenanker | Aggregatanker |
| --- | --- | --- |
| Versicherer einzeln | `IMSDATA.C:94` | `IMS.E:408` |
| Versicherer-Regelklasse | `IMSDATA.C:112` | `IMS.E:504` |
| Versicherer SK1/all | `IMSDATA.C:116` | `IMS.E:559` |
| VN-Regel | `IMSDATA.C:181` | `IMS.E:657` |
| VN-Regelklasse | `IMSDATA.C:187` | `IMS.E:752` |
| VN SK1/all | `IMSDATA.C:191` | `IMS.E:848` |

Die historischen Quellen belegen die Ausgabeform und Aggregatbildung. Sie
belegen nicht, aus welchem konkreten historischen Lauf die versionierten
Referenzdateien stammen.

## Karte der 15 Identitaeten

| Export | Referenz | Fenster | Zustandsfamilie | Python-Anschluss | Vorhandener enger Nachweis |
| --- | --- | ---: | --- | --- | --- |
| `imsvu014.dat` | `VU14L1.DAT` | `1-100` | Versicherer | expliziter VU/VN-Periodenrunner, Stufe I | Perioden 1-4, referenzausgerichtete Zustaende |
| `imsvusk1.dat` | `VUSK1L1-5.DAT` | `1-500` | Versicherer | expliziter VU/VN-Periodenrunner, Stufe IV | Replay 101-104, referenzausgerichtete Zustaende |
| `imsvuvk1.dat` | `IMSVUVK1.DAT` | `1-500` | Versicherer | expliziter VU/VN-Periodenrunner, Stufe III | Writer-/Aggregatvertrag |
| `imsvuvk2.dat` | `IMSVUVK2.DAT` | `1-500` | Versicherer | expliziter VU/VN-Periodenrunner, Stufe III | Writer-/Aggregatvertrag |
| `imsvuvk3.dat` | `IMSVUVK3.DAT` | `1-500` | Versicherer | expliziter VU/VN-Periodenrunner, Stufe III | Writer-/Aggregatvertrag |
| `imsvnr01.dat` | `IMSVNR01.DAT` | `1-300` | VN | `Vrvn01/compulsory`-Snapshot plus Stufe II | Regelkern-/Writervertrag |
| `imsvnr02.dat` | `IMSVNR02.DAT` | `1-300` | VN | `Vrvn02/random`-Snapshot plus Stufe II | Regelkern-/Writervertrag |
| `imsvnr03.dat` | `IMSVNR03.DAT` | `1-500` | VN | `Vrvn03/preference`-Snapshot plus Stufe II | Regelkern-/Writervertrag |
| `imsvnr04.dat` | `IMSVNR04.DAT` | `1-500` | VN | `Vrvn04/search_history`-Snapshot plus Stufe II | Regelkern-/Writervertrag |
| `imsvnr05.dat` | `IMSVNR05.DAT` | `1-500` | VN | `Vrvn05/sample_search`-Snapshot plus Stufe II | Regelkern-/Writervertrag |
| `imsvnr06.dat` | `IMSVNR06.DAT` | `1-500` | VN | `Vrvn06/best_info`-Snapshot plus Stufe II | Regelkern-/Writervertrag |
| `imsvnsk1.dat` | `IMSVNSK1.DAT` | `1-100` | VN | expliziter VN-Runner, Stufe IV | Writer-/Aggregatvertrag |
| `imsvnvk1.dat` | `IMSVNVK1.DAT` | `1-500` | VN | expliziter VN-Runner, Stufe III | Writer-/Aggregatvertrag |
| `imsvnvk2.dat` | `IMSVNVK2.DAT` | `1-500` | VN | expliziter VN-Runner, Stufe III | Writer-/Aggregatvertrag |
| `imsvnvk3.dat` | `IMSVNVK3.DAT` | `1-500` | VN | expliziter VN-Runner, Stufe III | Writer-/Aggregatvertrag |

`VUSK1L1.DAT` bis `VUSK1L5.DAT` bleiben fuenf aufeinanderfolgende
Zeitfenster derselben Identitaet `imsvusk1.dat`: Versicherer, Stufe IV,
`selector_kind = "all"`, `selector_value = "SK1"`. Sie sind keine
unterschiedlichen Aggregatebenen.

## Python-Erzeugungsweg

Der vorhandene explizite Weg lautet:

1. `run_loaded_vu_foreign_info_period` wendet nur explizit geladene
   VU-Regelsnapshots an;
2. `run_loaded_vn_settlement_period` wendet nur explizit geladene
   VN-Regel-, Schaden- und Settlement-Snapshots an;
3. `run_loaded_explicit_period` verbindet beide Schritte;
4. `collect_extended_agrsich_records` gruppiert aktive Entitaeten nach
   Einzel-ID, Regel, Regelklasse und `all`;
5. `build_agrsich_export_tables` bildet Dateiname, Header und Periodenzeile.

Der Writer-Anschluss ist fuer alle 15 Identitaeten vorhanden. Der Runner ist
aber absichtlich snapshotgetrieben und ersetzt weder den historischen
PlanVU-/PlanVN-Dispatch noch eine vollstaendige historische Simulation.

## Gemeinsame Erzeugungsluecken

Alle 15 Identitaeten bleiben durch dieselben Kernpunkte blockiert:

- `complete_production_population_missing`: kein vollstaendig belegtes
  Produktionsfixture mit der gesamten VU-/VN-Population und allen Parametern;
- `automatic_historical_rule_dispatch_missing`: keine vollstaendige
  Rekonstruktion der historischen automatischen Regelwahl und Ablaufplanung;
- `historical_rng_alignment_unproven`: keine belegte Gleichheit des gesamten
  historischen Zufallsstroms;
- `full_window_state_evolution_unproven`: keine unabhaengige, durchgaengige
  Zustandsfortschreibung ueber 100 bis 500 Perioden;
- `independent_calculated_export_missing`: keine vollstaendige, unabhaengig
  berechnete Exporttabelle fuer den Kernvergleich.

Der VU14-Slice fuer Perioden 1-4 und der VUSK1-Replay fuer 101-104 beweisen
Aggregat-, Export- und Vergleichsgrenzen. Ihre Zustandswerte sind jedoch
referenzausgerichtete explizite Eingaben. Sie schliessen keine der genannten
Vollfensterluecken.

## Maschinenlesbarer Bericht

```powershell
python -m ims.api.calculated_export_provenance_report --repo-root .
```

Der erwartete PR-71-Befund lautet:

- `status = "mapped"`;
- `required_export_count = 15`;
- `legacy_reference_count = 19`;
- `required_period_count = 6300`;
- `writer_connected_count = 15`;
- `explicit_runner_connected_count = 15`;
- `independent_full_window_ready_count = 0`;
- `production_release_approved = false`;
- `execution_performed = false` und `simulation_performed = false`.

## Restplanung

Fuer eine interne, reviewbare Erzeugung ergibt sich ab PR 72 eine Mindestserie
von sieben PRs:

1. PR 72: vollstaendigen 100-Perioden-Erzeugungsvertrag fuer
   `imsvu014.dat` mit belegten Eingaben und Negativgrenzen vorbereiten;
2. PR 73: unabhaengigen VU14-Zustandsweg fuer `1-100` umsetzen und vergleichen;
3. PR 74: dieselbe Versicherer-Population auf `imsvusk1.dat` und
   `imsvuvk1-3.dat` fuer das geforderte Fenster verbreitern;
4. PR 75: VN-Regelzustand fuer `imsvnr01-03.dat` schliessen;
5. PR 76: VN-Regelzustand fuer `imsvnr04-06.dat` schliessen;
6. PR 77: VN-Klassen- und SK1/all-Exporte aus demselben Zustand vergleichen;
7. PR 78: alle 15 Tabellen gemeinsam durch den Abweichungsbericht fuehren und
   die fachliche Freigabe erneut menschlich bewerten.

Diese sieben PRs sind eine Mindestplanung. Funde zur Population, zum Scheduler,
zum RNG oder zur Zustandsfortschreibung duerfen eigene kleine Korrektur-PRs
erzwingen. Werden stattdessen unabhaengig berechnete Tabellen extern mit
belegter Herkunft geliefert, kann die interne Erzeugungsserie verkuerzt werden.

## PR-71-Pruefnachweis

Am 2026-08-25 wurden ausgefuehrt:

- read-only Herkunftsbericht: `status = "mapped"`, 15 Exporte, 19 Referenzen,
  6.300 Perioden, 15 Writer-/Runner-Anschluesse und 0 unabhaengige
  Vollfenster;
- gezielte Berichts-, Doku-, CLI- und Packaging-Tests: 129 bestanden;
- vollstaendiges Windows-Gate: 1.166 Python-Tests bestanden;
- Frontend-Produktionsbuild: 1.578 Module transformiert;
- Bundle-, Staging-, Readiness- und Release-Smoke: bestanden;
- `production_release_approved = false`, keine Ausfuehrung und keine
  Simulation.

## Grenzen

- kein Zugriff auf oder Import aus `incomming/`;
- keine Exporterzeugung in PR 71;
- kein Runner-, Adapter-, Scheduler-, Queue-, Server- oder Simulationsstart;
- keine neue Fachlogik und keine automatische historische Regelwahl;
- keine historische Vollgleichheitsbehauptung;
- keine fachliche Produktionsfreigabe.
