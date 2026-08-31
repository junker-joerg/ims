# Historische 100-Perioden-Korpuslieferung

Stand: 2026-08-31
Vertrag: `pr93-v1`

## Ziel

Der Bericht `ims.api.historical_100_period_corpus_delivery` bindet die beiden
im Horizontvertrag `pr92-v1` vollstaendigen 100-Perioden-Ziele an den
Produktionskorpusbericht:

| Export | Identitaet | Perioden | Referenzschicht |
| --- | --- | ---: | --- |
| `imsvu014.dat` | Versicherer 14, Stufe I | 1-100 | `wvemod1_archive` |
| `imsvnsk1.dat` | VN `SK1/all`, Stufe IV | 1-100 | `wvemod1_archive` |

Damit sind 2 von 15 berechneten Kernexporten und 200 von 6.300 Zielperioden
als lueckenlose Tabellen geliefert. Die restlichen 13 Exporte und 6.100
Zielperioden bleiben explizit offen.

## Erzeugungs- und Identitaetsgrenze

Die Tabellen stammen aus dem bereits in `pr86-v1` eingefrorenen
kontrollierten Vdefmd6-Zustandspfad mit Basis-Seed `20260001` und State-Policy
`vdefmd6-modern-100-period-state-v1`. Legacy-Zeilen werden nicht als
Erzeugungsinput verwendet.

Die erzeugte `imsvnsk1.dat` traegt technisch den Level-IV-Selektorwert `all`.
Der gemeinsame kanonische Identitaetsvertrag ordnet `all` und `SK1` auf
Level IV derselben Exportidentitaet zu. Aggregatstufe, Selektorart und
fachliche Bedeutung werden dabei nicht geaendert.

Fuer beide Tabellen werden vor der Uebergabe geprueft:

- exakte Exportidentitaet nach kanonischer Level-IV-Regel;
- VU- beziehungsweise VN-Header;
- genau eine Tabelle je Ziel;
- lueckenlose Perioden 1 bis 100;
- die 100er-Pflichtgrenze aus `pr92-v1`;
- die Referenzschicht und zulaessige Aussage aus `pr91-v1`.

## Korpusstatus

Der Produktionskorpusbericht akzeptiert nun explizit uebergebene, gueltige
Teiltabellen. Sein Standardaufruf bleibt read-only und liefert weiterhin
keine Tabelle automatisch. Nur der PR93-Lieferbericht startet den bereits
vorhandenen kontrollierten 100-Perioden-Pfad und uebergibt genau die zwei
ausgewaehlten Tabellen.

Der PR93-Befund lautet:

- `supplied_calculated_export_count = 2`;
- `supplied_calculated_period_count = 200`;
- `missing_calculated_export_count = 13`;
- `missing_calculated_period_count = 6100`;
- `status = blocked`;
- `release_decision = blocked_calculated_core_validation`.

Die Teillieferung fuehrt noch keinen gemeinsamen 6.300-Zeilen-Vergleich aus.
Der Korpusbericht meldet deshalb weiterhin `calculated_comparison_performed =
false`. Der fruehere PR86-Abweichungsbericht bleibt als Befund erhalten:
`imsvu014.dat` traf 488/1.400 Felder, `imsvnsk1.dat` 264/1.300 Felder. Die
vollstaendige Periodenlieferung ist keine Feldgleichheit.

## Grenzen

- keine neue Fachlogik;
- keine Legacy-Zeilen als Erzeugungsinput;
- keine Dateischreibvorgaenge und kein Schedulerstart;
- keine Simulation;
- keine 300-/500-Perioden-Erweiterung;
- keine historische Laufidentitaet oder RNG-Gleichheit;
- keine historische Vollgleichheitsbehauptung;
- keine Produktionsfreigabe.

## Reproduzierbarer Aufruf

```powershell
$env:PYTHONPATH = "python_port"
python -m ims.api.historical_100_period_corpus_delivery --root .
```

Der Aufruf erzeugt die zwei Tabellen nur im Speicher und schreibt keine
Ergebnisdateien.

## Naechster Schritt

PR94 hat den kontrollierten Zustand deterministisch bis Periode 300 erweitert.
Die Perioden 1-100 bleiben fuer alle 15 Tabellen exakt unveraendert. PR95
bindet als naechstes nur die beiden belegten 300er-Regelfenster an; eine
historische Scheduler-, RNG- oder Akkumulatorsemantik wird nicht ergaenzt.
