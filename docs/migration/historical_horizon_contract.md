# Historischer Ergebniszeilen- und Wiederholungsvertrag

Stand: 2026-08-31
Vertrag: `pr98-v1`

## Korrektur

Die bisher als historische Horizonte 100, 300 und 500 bezeichneten Werte sind
keine Lauflaengen. IMS 1995 begrenzt einen einzelnen Simulationslauf auf
maximal 100 Perioden:

- `IMSDATA.C` setzt `SIMLAENGE` auf 100;
- `IMS.E` fragt Perioden je Einzelsimulation und Anzahl der Wiederholungen
  getrennt ab;
- die Dissertation nennt maximal 100 Perioden je Lauf und fuer die
  Hauptauswertung 30 Laeufe mit jeweils 100 Perioden;
- `IMS.E` schreibt die Ergebnisnummer als `(rl-1)*sl+period`.

Bei `sl = 100` bezeichnen die Ergebnisnummern 101-200 daher den zweiten Lauf,
201-300 den dritten Lauf und 401-500 den fuenften Lauf. Sie sind keine
Perioden eines historischen 300- oder 500-Perioden-Laufs.

## Verbindliche Lesart

| Ergebniszeilen | Historische Laeufe | Lokale Perioden je Lauf | Exporte | Zielzeilen |
| ---: | ---: | --- | ---: | ---: |
| 100 | 1 | 1-100 | 2 | 200 |
| 300 | 3 | jeweils 1-100 | 2 | 600 |
| 500 | 5 | jeweils 1-100 | 11 | 5.500 |
| **Gesamt** | - | - | **15 Exportidentitaeten / 19 Referenzziele** | **6.300** |

Der bestehende Python-Feldname `required_horizon` bleibt intern vorerst als
Kompatibilitaetsname erhalten. Seine Bedeutung ist ab `pr98-v1`
`required_result_row_count`. Der Vertrag meldet zusaetzlich die Laufnummern
und die lokalen Periodengrenzen.

## VUSK1

`VUSK1L5.DAT` bis `VUSK1L1.DAT` bleiben dieselbe Exportidentitaet
`imsvusk1.dat`, Aggregatstufe IV, `selector_kind = all` und
`selector_value = SK1`. Sie sind keine unterschiedlichen Aggregate oder
Aggregatebenen.

| Referenz | Ergebniszeilen | Lauf | Lokale Perioden | Schicht |
| --- | --- | ---: | --- | --- |
| `VUSK1L5.DAT` | 1-100 | 1 | 1-100 | `wvemod2_archive` |
| `VUSK1L4.DAT` | 101-200 | 2 | 1-100 | `vusk1l4_direct_04410ef` |
| `VUSK1L3.DAT` | 201-300 | 3 | 1-100 | `wvemod2_archive` |
| `VUSK1L2.DAT` | 301-400 | 4 | 1-100 | `wvemod2_archive` |
| `VUSK1L1.DAT` | 401-500 | 5 | 1-100 | `wvemod2_archive` |

`VUSK1L4.DAT` bleibt wegen seiner abweichenden Herkunft
`versioned_fixture_regression_only`. Der Vertrag behauptet weder eine
gemeinsame historische Archivquelle noch identische Parameter der Laeufe.

## Moderne Langzeitpruefungen

Die vorhandenen modernen 300- und 500-Perioden-Runner bleiben als
deterministische Stresstests erhalten. Ihre exakten Prefixpruefungen sind
technisch sinnvoll, stellen aber keinen historischen Wiederholungsvergleich
dar. Ein moderner 500-Perioden-Zustand darf deshalb nicht mehr unmittelbar
gegen fuenf historische 100-Perioden-Laeufe bewertet werden.

## Zufallszahlen

Der historische Seed wurde aus Datum und Uhrzeit abgeleitet. Die Zahlenfolge
hing zusaetzlich vom plattformabhaengigen C-`rand()` ab. Der Vertrag verlangt
daher keine Reproduktion der historischen RNG-Folge. Verbindlich sind:

- reproduzierbare moderne Laeufe mit expliziten Seeds;
- korrekte Verteilungen und Ziehstellen der portierten Fachlogik;
- fachliche Invarianten, Zustandsuebergaenge und Aggregatdefinitionen;
- historische Zahlenvergleiche nur diagnostisch und mit bekannter
  Parameterschicht.

## Aussagegrenzen

`ready` bedeutet, dass 15 Exportidentitaeten, 19 Referenzziele und 6.300
Ergebniszeilen widerspruchsfrei auf 100-Perioden-Laeufe abgebildet sind. Es
bedeutet keine historische Vollgleichheit, keine historische RNG-Gleichheit,
keine gemeinsame Laufidentitaet und keine fachliche Produktionsfreigabe.

Der Aufruf ist read-only und startet keine Simulation:

```powershell
$env:PYTHONPATH = "python_port"
python -m ims.api.historical_horizon_contract --root .
```

## Naechster Schritt

PR99 hat `imsvnr03.dat` bis `imsvnr06.dat` und PR100 die drei
VN-Klassenaggregate als je fuenf getrennte 100-Perioden-Laeufe angebunden.
Einzelwertabweichungen bleiben diagnostisch. PR101 fuehrt den Vertrag fuer die
drei VU-Klassenaggregate fort.
