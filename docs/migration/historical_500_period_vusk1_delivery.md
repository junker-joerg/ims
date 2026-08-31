# Historische VU-SK1-Diagnostik ueber fuenf Wiederholungen

Stand: 2026-08-31
Korrekturvertrag: `pr98-v1`

## Korrigierte Bedeutung

Die Ergebnisnummern 1-500 sind kein historischer 500-Perioden-Lauf. Sie
repraesentieren fuenf getrennte 100-Perioden-Laeufe. Der Altcode schreibt die
Nummer als `(rl-1)*sl+period`; `SIMLAENGE` ist auf 100 begrenzt.

`imsvusk1.dat` bleibt dabei eine Exportidentitaet auf Aggregatstufe IV mit
`all = SK1`. Die Dateien sind keine unterschiedlichen Aggregatebenen.

| Referenz | Ergebniszeilen | Lauf | Lokale Perioden | Schicht |
| --- | --- | ---: | --- | --- |
| `VUSK1L5.DAT` | 1-100 | 1 | 1-100 | `wvemod2_archive` |
| `VUSK1L4.DAT` | 101-200 | 2 | 1-100 | `vusk1l4_direct_04410ef` |
| `VUSK1L3.DAT` | 201-300 | 3 | 1-100 | `wvemod2_archive` |
| `VUSK1L2.DAT` | 301-400 | 4 | 1-100 | `wvemod2_archive` |
| `VUSK1L1.DAT` | 401-500 | 5 | 1-100 | `wvemod2_archive` |

Vier Bloecke sind tokennormalisierte Ausschnitte aus
`WVEMOD2.ZIP/IMSVUSK1.DAT`. `VUSK1L4.DAT` stimmt nicht mit dem entsprechenden
Archiveintrag ueberein und bleibt `versioned_fixture_regression_only`.

## Moderner Wiederholungskorpus

Die Diagnostik erzeugt fuenf getrennte 100-Perioden-Laeufe mit den modernen
Seeds `20260001` bis `20260005`. Jeder Lauf beginnt mit demselben
kontrollierten Anfangszustand. Die globale Ergebnisnummer wird erst fuer den
Dateivergleich aus Laufnummer und lokaler Periode gebildet.

Diese Seeds sichern heutige Reproduzierbarkeit. Sie behaupten keine
historische RNG-Folge und keine Gleichheit mit `rand()` aus DOS-, Linux- oder
Solaris-C-Libraries.

## Diagnostischer Befund

| Referenz | Zeilen gleich | Zeilen abweichend | Exakt | Toleriert | Numerisch abweichend |
| --- | ---: | ---: | ---: | ---: | ---: |
| `VUSK1L5.DAT` | 1 | 99 | 215 | 17 | 1.168 |
| `VUSK1L4.DAT` | 0 | 100 | 200 | 0 | 1.200 |
| `VUSK1L3.DAT` | 1 | 99 | 213 | 15 | 1.172 |
| `VUSK1L2.DAT` | 1 | 99 | 212 | 21 | 1.167 |
| `VUSK1L1.DAT` | 1 | 99 | 212 | 11 | 1.177 |
| **Gesamt** | **4** | **496** | **1.052** | **64** | **5.884** |

Die vier vollstaendigen Treffer sind die Anfangszustaende der vier belegten
WVEMOD2-Laeufe. Dass der isolierte L4-Block keinen solchen Treffer besitzt,
passt zu seiner ungeklaerten Herkunft. Die uebrigen Abweichungen bleiben
diagnostisch; sie sind wegen unbekannter Parameter- und RNG-Kontexte kein
Beweis gegen die portierte Fachlogik.

Kumulativ sind weiterhin 5/15 Tabellen und 1.300/6.300 Ergebniszeilen
technisch angeschlossen. Das ist Anschlussabdeckung, keine fachliche
Gleichheitsquote.

## Grenzen

- keine Legacy-Zeile als Erzeugungsinput;
- keine historische RNG-Reproduktion;
- keine Gleichsetzung der Wiederholungen mit einem langen Lauf;
- keine gemeinsame historische Laufidentitaet;
- keine historische Vollgleichheit;
- keine Produktionsfreigabe;
- keine Datei- oder Datenbankschreibvorgaenge;
- kein Schedulerstart und keine Simulation.

## Aufruf

```powershell
$env:PYTHONPATH = "python_port"
python -m ims.api.historical_500_period_vusk1_delivery --root .
```

PR99 bindet als Naechstes `imsvnr03.dat` bis `imsvnr06.dat` als je fuenf
getrennte 100-Perioden-Laeufe an.
