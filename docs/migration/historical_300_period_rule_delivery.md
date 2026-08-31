# Historische VN-Regeldiagnostik ueber drei Wiederholungen

Stand: 2026-08-31
Vertrag: `pr98-v1`

## Korrigierte Bedeutung

`IMSVNR01.DAT` und `IMSVNR02.DAT` enthalten je 300 fortlaufend nummerierte
Ergebniszeilen. Nach Altcode und Dissertation sind dies drei getrennte
100-Perioden-Laeufe, kein historischer 300-Perioden-Lauf.

Die Ergebnisnummern werden deshalb so gelesen:

| Ergebniszeilen | Lauf | Lokale Perioden |
| --- | ---: | --- |
| 1-100 | 1 | 1-100 |
| 101-200 | 2 | 1-100 |
| 201-300 | 3 | 1-100 |

Der moderne Diagnosekorpus erzeugt drei voneinander getrennt initialisierte
100-Perioden-Laeufe mit den expliziten Seeds `20260001`, `20260002` und
`20260003`. Diese Seedfolge ist eine moderne Reproduzierbarkeitspolitik und
keine behauptete historische RNG-Folge.

## Referenzen

| Referenz | Export | Identitaet | Ergebniszeilen | Schicht |
| --- | --- | --- | ---: | --- |
| `IMSVNR01.DAT` | `imsvnr01.dat` | VN / II / Regel 1 | 300 | `zins000_archive` |
| `IMSVNR02.DAT` | `imsvnr02.dat` | VN / II / Regel 2 | 300 | `zins000_archive` |

ZINS000 ist eine eigene Parameterschicht. Andere Archive duerfen nicht als
Fortsetzung oder derselbe Lauf behandelt werden.

## Diagnostischer Befund

| Export | Zeilen gleich | Zeilen abweichend | Exakt | Toleriert | Numerisch abweichend | Offene nichtnumerische Felder |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `imsvnr01.dat` | 0 | 300 | 946 | 1 | 2.947 | 6 |
| `imsvnr02.dat` | 0 | 300 | 615 | 127 | 2.600 | 558 |

Diese Zahlen frieren den aktuellen Diagnosezustand ein. Sie sind kein
Freigabekriterium und kein Nachweis falscher Fachlogik, weil Parameter,
historische Seeds, C-Library und konkrete Laufidentitaet nicht vollstaendig
bekannt sind.

Kumulativ sind weiterhin vier Tabellen und 800 von 6.300 Ergebniszeilen
technisch an den Korpusbericht angeschlossen. Diese Kennzahl beschreibt
Anschlussabdeckung, nicht fachliche Gleichheit.

## Grenzen

- keine Legacy-Zeile als Erzeugungsinput;
- keine historische RNG-Reproduktion;
- keine Gleichsetzung der drei Wiederholungen mit einem langen Lauf;
- keine historische Vollgleichheit;
- keine Produktionsfreigabe;
- keine Datei- oder Datenbankschreibvorgaenge;
- kein Schedulerstart und keine Simulation.

## Aufruf

```powershell
$env:PYTHONPATH = "python_port"
python -m ims.api.historical_300_period_rule_delivery --root .
```

PR99 uebertraegt dieselbe korrigierte Lesart auf die VN-Regeln 3-6 mit je
fuenf getrennten 100-Perioden-Laeufen.
