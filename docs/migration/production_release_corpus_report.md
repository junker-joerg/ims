# Abschlussbericht: erster Produktionsfreigabekorpus

Stand: 2026-08-25  
Berichtsvertrag: `pr69-v1`

## Freigabeentscheidung

Der aktuelle IMS-Stand ist als lokale, reviewbare und technisch gehaertete
Workbench-Demo nutzbar. Eine fachliche Produktionsfreigabe fuer den
historischen Kernkorpus wird **nicht** erteilt.

Der Grund ist eindeutig: Alle 19 historischen Kernreferenzen sind vorhanden
und ihre 6.300 eingetragenen Perioden sind durch Parser-, Header-, Fenster- und
Coverage-Tests erfasst. Fuer einen unabhaengigen berechneten Alt-/Neu-Vergleich
fehlen jedoch weiterhin alle 15 erforderlichen Kernexporttabellen.

| Bereich | Befund | Entscheidung |
| --- | --- | --- |
| Historischer Kernkorpus | 19/19 Referenzen vorhanden und abgedeckt | abgegrenzter Referenzbestand belegt |
| Bundle-Perioden | 6.300/6.300 eingetragene Perioden ausgerichtet | Parser-/Mapping-Nachweis belegt |
| Berechnete Kernexporte | 0/15 vollstaendig geliefert | blockierend |
| Berechneter Kernvergleich | nicht ausgefuehrt | fachliche Produktionsfreigabe gesperrt |
| Lokale UI und Startpfad | gebaut, getestet und lokal bereitstellbar | reviewbare Demo belegt |
| Packaging und Recovery | ZIP/Staging/Start sowie Backup/Restore geprueft | technischer Betriebsnachweis belegt |
| Historische Vollgleichheit | nicht nachgewiesen | wird nicht behauptet |

## Korpusumfang

Der verbindliche Kernkorpus v1 bleibt unveraendert bei 19 Dateien und 6.300
eingetragenen Vergleichsperioden:

| Familie | Dateien | Perioden |
| --- | ---: | ---: |
| Versicherer einzeln | 1 | 100 |
| Versicherer SK1-Zeitfenster auf Stufe IV | 5 | 500 |
| VN SK1 | 1 | 100 |
| VN-Regeln | 6 | 2.600 |
| VN-Klassen | 3 | 1.500 |
| VU-Klassen | 3 | 1.500 |
| **Summe** | **19** | **6.300** |

Die Dateien `VUSK1L1.DAT` bis `VUSK1L5.DAT` bleiben Zeitfenster desselben
`SK1`-/`all`-Aggregats auf Aggregatstufe IV. Sie sind keine verschiedenen
Aggregatebenen.

Die physisch vorhandenen 6.700 Datenzeilen werden nicht pauschal als validiert
behandelt. Insbesondere bleibt das nicht eingetragene Restfenster von
`IMSVNSK1.DAT` ausserhalb der 6.300 belegten Perioden.

Das getrennte ZINS000-Paar `IMSVU014.DAT` und `IMSVUSK1.DAT` ist versioniert,
gehoert aber nicht zum 19-Dateien-Kernkorpus. `incomming/` bleibt lokaler,
unversionierter Kandidatenbestand und wurde in PR 69 nicht gelesen oder
erweitert.

## Belegte Teilnachweise

### Referenzen und Vergleichsrahmen

- Coverage-Matrix: 19 vorhandene und 19 abgedeckte Kernreferenzen, keine
  Dateiluecke, 6.300 abgedeckte Zeilen und Perioden.
- Fixturegetriebener Legacy-Report: 6.300 ausgerichtete Referenzzeilen.
- Strikter berechneter Vergleichsvertrag: 15 Exporttabellen, 19 Ziele und
  6.300 Zielperioden; Legacy-Zeilen duerfen nicht als berechnete Neu-Ausgabe
  zurueckgespiegelt werden.
- Read-only Abweichungsbericht: fehlende berechnete Exporte werden als
  `required_export_missing` blockiert.

### Schmale berechnete und fachliche Slices

- Zehn schmale VU-/VN-Regressionsslices pruefen vorhandene Carryover-, Regel-,
  Schaden-/Settlement- und explizite Draw-Grenzen.
- PR 60 bindet fuer VU14 die Perioden `1-4` als tatsaechlich berechneten
  Aggregat-/Export-Slice an: 4/4 Zeilen und 56/56 Felder.
- Dieser VU14-Slice verwendet weiterhin referenzausgerichtete explizite
  Zustandswerte. Er ist kein Nachweis unabhaengiger historischer
  Zustandsentwicklung und kein Ersatz fuer die 15 vollstaendigen Kernexporte.

### UI und lokaler Betrieb

- Die Workbench zeigt Szenarien, Queue, Freigabe, Startstatus, persistiertes
  Ergebnis und Ausfuehrungsverlauf.
- Der Browser-Smoke aus PR 66 nutzt bewusst einen injizierten Fake-Adapter und
  startet keinen Engine-Runner oder eine Simulation.
- PR 67 prueft Frontend-Build, ZIP, portables Staging, Produktionsskripte und
  normalen Loopback-Start getrennt vom Fake-Adapter.
- PR 68 prueft SQLite-Backup, Restore, Digestgleichheit und getrennte Repo-/
  Portable-Anwendungspfade fuer einen validierten Ergebnisstand.

`release_ready = true` im technischen PR-67-Smoke bedeutet deshalb nur, dass
die eingefrorenen Packaging-/Startskriptgates erfuellt sind. Es ist keine
fachliche Freigabe des historischen Modells.

## Aktuelle Blocker

Der maschinenlesbare Bericht meldet diese 15 fehlenden berechneten Exporte:

1. `imsvu014.dat` fuer Versicherer 14 auf Stufe I;
2. `imsvusk1.dat` fuer das Versicherer-`SK1`-/`all`-Aggregat auf Stufe IV;
3. `imsvnr01.dat` bis `imsvnr06.dat` fuer VN-Regeln 1 bis 6 auf Stufe II;
4. `imsvnsk1.dat` fuer das VN-`SK1`-/`all`-Aggregat auf Stufe IV;
5. `imsvnvk1.dat` bis `imsvnvk3.dat` fuer VN-Regelklassen auf Stufe III;
6. `imsvuvk1.dat` bis `imsvuvk3.dat` fuer VU-Regelklassen auf Stufe III.

Vor einer fachlichen Freigabe muessen alle 15 Tabellen aus einer belegten,
unabhaengig berechneten Quelle stammen, vollstaendig ueber die geforderten
Perioden vorliegen und den bestehenden Abweichungsbericht durchlaufen.
Treffer, tolerierte numerische Unterschiede, blockierende Unterschiede und
offene Feldfragen sind danach getrennt zu dokumentieren.

## Bedien- und Pruefpfad

Der Abschlussbericht selbst wird rein lesend erzeugt:

```powershell
python -m ims.api.production_release_corpus_report --repo-root .
```

Der erwartete aktuelle Kernbefund ist:

- `status = "blocked"`;
- `release_decision = "blocked_calculated_core_validation"`;
- `coverage_complete = true`;
- `missing_calculated_export_count = 15`;
- `production_release_approved = false`;
- `simulation_performed = false`;
- `historical_full_equality_claimed = false`.

Die lokale technische Workbench wird weiterhin ueber die dokumentierten
Check-/Startskripte geprueft und gestartet. Der Anwender darf den technischen
Demo-Status nicht als validierte historische Simulation interpretieren.

## Bekannte Grenzen

- kein unabhaengiger berechneter Gesamtvergleich des Kernkorpus;
- historische RNG-, Scheduler- und automatische Regelwahl nicht vollstaendig
  rekonstruiert;
- kein Beleg historischer Vollgleichheit;
- kein automatischer Updater und keine SQLite-Schemamigration;
- keine Aussage zu beliebiger versionsuebergreifender Datenkompatibilitaet;
- keine Produktionsfreigabe durch den read-only Bericht selbst.

## PR-69-Pruefnachweis

Am 2026-08-25 wurden fuer diesen Bericht ausgefuehrt:

- `python -m pytest -q`: 1.151 Tests bestanden;
- Frontend-Produktionsbuild: erfolgreich;
- read-only Korpusbericht: `status = "blocked"`, 19/19 Referenzen,
  6.300/6.300 Perioden und 0/15 berechnete Kernexporte;
- frischer ZIP-Build: 114 Eintraege einschliesslich Bericht und Berichtmodul;
- portables Staging und PR-67-Release-Smoke: `release_ready = true`, keine
  Produktionsskriptabweichung, kein PR-66-Fake-Adapter im Produktionspfad;
- `simulation_performed = false` in Bericht und Release-Smoke.

Der gruenen technischen Pruefkette steht damit weiterhin der fachliche
Exportblocker gegenueber. Beide Befunde sind gleichzeitig gueltig.

## Restplanung

Nach PR 69 bleiben grob `1-7` reviewbare PRs bis zu einer konservativen
Produktionsreife, **zuzueglich der externen Voraussetzung**, dass die 15
berechneten Kernexporte aus einer belegten Quelle bereitgestellt werden. Ohne
diese Daten bleibt die fachliche Freigabe unabhaengig von der PR-Anzahl
blockiert.

PR 70 haertet als naechstes den Abschlussstand als CI-/Windows-Freigabegate:
Python-Tests, Frontend-Build, read-only Korpusbericht und Release-Smoke sollen
in einer reproduzierbaren technischen Pruefkette zusammenlaufen. Dieser Schritt
erzeugt keine fehlenden Kernexporte und erweitert keine Gleichheitsaussage.
