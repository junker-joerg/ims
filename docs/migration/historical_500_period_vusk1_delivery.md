# Historische VU-SK1-Zeitfenster bis Periode 500

Stand: 2026-08-31
Vertrag: `pr97-v1`

## Ziel

PR97 bindet die eine kontrolliert berechnete Tabelle `imsvusk1.dat` fuer die
Perioden 1-500 an fuenf getrennte historische Referenztests. Die berechnete
Tabelle stammt aus dem modernen Zustandsvertrag `pr96-v1`; die historischen
Zeilen werden erst nach ihrer Erzeugung gelesen und verglichen.

Der Lieferbericht
`ims.api.historical_500_period_vusk1_delivery` uebergibt damit kumulativ 5/15
Tabellen und 1.300/6.300 Zielperioden an den weiterhin gesperrten
Produktionskorpusbericht.

## Historischer Ursprung

Alle fuenf Referenzen beschreiben dieselbe Exportidentitaet
`IMSVUSK1.DAT`, dasselbe SK1/all-Aggregat und dieselbe Aggregatstufe IV:

| Referenz | Fenster | Schicht | Beleggrenze |
| --- | --- | --- | --- |
| `VUSK1L5.DAT` | 1-100 | `wvemod2_archive` | `archive_content_match_only` |
| `VUSK1L4.DAT` | 101-200 | `vusk1l4_direct_04410ef` | `versioned_fixture_regression_only` |
| `VUSK1L3.DAT` | 201-300 | `wvemod2_archive` | `archive_content_match_only` |
| `VUSK1L2.DAT` | 301-400 | `wvemod2_archive` | `archive_content_match_only` |
| `VUSK1L1.DAT` | 401-500 | `wvemod2_archive` | `archive_content_match_only` |

`VUSK1L5.DAT`, `VUSK1L3.DAT`, `VUSK1L2.DAT` und `VUSK1L1.DAT` sind
tokennormalisierte Zeitfenster von `WVEMOD2.ZIP/IMSVUSK1.DAT`.
`VUSK1L4.DAT` stimmt dagegen mit keinem bekannten Archiveintrag ueberein und
bleibt deshalb in seiner isolierten direkten Referenzschicht. Die fuenf
Fenster werden weder als unterschiedliche Aggregatebenen noch als eine
koharente historische 500-Perioden-Laufdatei behandelt.

## Kontrollierter Vergleich

Der moderne Zustand wird mit Basis-Seed `20260001` getrennt fuer die
Horizonte 100, 300 und 500 erzeugt. Der generische Horizontpruefer bestaetigt:

- drei eindeutige Snapshots fuer `imsvusk1.dat`;
- exakte Prefixe 1-100 und 1-300;
- drei Prefixvergleiche ueber insgesamt 500 Zeilen;
- lueckenlose berechnete Perioden 1-500;
- exakte Level-IV-Identitaet `all = SK1`.

Danach wird jede berechnete 100-Perioden-Scheibe nur gegen ihre eigene
versionierte Referenz und deren eigene Schicht verglichen.

## Beobachteter Befund

| Referenz | Zeilen gleich | Zeilen abweichend | Exakte Felder | Toleriert | Blockierend |
| --- | ---: | ---: | ---: | ---: | ---: |
| `VUSK1L5.DAT` | 1 | 99 | 215 | 17 | 1.168 |
| `VUSK1L4.DAT` | 0 | 100 | 201 | 2 | 1.197 |
| `VUSK1L3.DAT` | 0 | 100 | 200 | 1 | 1.199 |
| `VUSK1L2.DAT` | 0 | 100 | 202 | 5 | 1.193 |
| `VUSK1L1.DAT` | 0 | 100 | 203 | 4 | 1.193 |
| Gesamt | 1 | 499 | 1.021 | 29 | 5.950 |

Damit unterscheiden sich 499 von 500 Zeilen in mindestens einem Fachfeld.
Von 7.000 Feldvergleichen sind 1.021 exakt, 29 liegen innerhalb der bereits
bestehenden numerischen Toleranz und 5.950 sind blockierende numerische
Abweichungen. Es gibt keine offenen nichtnumerischen Feldfragen.

Der eine vollstaendige Zeilentreffer ist Periode 1 in `VUSK1L5.DAT`. Er
belegt keine Gleichheit der uebrigen Perioden oder des historischen Modells.

## Kumulative Lieferung

Der Produktionskorpusbericht erhaelt read-only:

- `imsvu014.dat`, Perioden 1-100;
- `imsvnsk1.dat`, Perioden 1-100;
- `imsvnr01.dat` und `imsvnr02.dat`, Perioden 1-300;
- `imsvusk1.dat`, Perioden 1-500.

Damit sind 5/15 Tabellen und 1.300/6.300 Zielperioden geliefert. Zehn Tabellen
und 5.000 Perioden bleiben offen. Der Korpusstatus bleibt `blocked` und die
Entscheidung `blocked_calculated_core_validation`.

## Grenzen

- keine Legacy-Zeile als Erzeugungsinput;
- keine neue Fachlogik oder historische Regelwahl;
- keine Zusammenfuehrung der beiden Referenzschichten;
- keine gemeinsame historische Laufidentitaet;
- keine historische Scheduler- oder RNG-Gleichheit;
- keine historische Vollgleichheit;
- keine Datei- oder Datenbankschreibvorgaenge;
- kein Schedulerstart und keine Simulation;
- keine Produktionsfreigabe.

## Reproduzierbarer Aufruf

```powershell
$env:PYTHONPATH = "python_port"
python -m ims.api.historical_500_period_vusk1_delivery --root .
```

Der Aufruf erzeugt kontrollierte Tabellen im Speicher, liest nur versionierte
Referenzen und schreibt keine Ergebnisdateien.

## Naechster Schritt

PR98 bindet als Naechstes `IMSVNR03.DAT` bis `IMSVNR06.DAT` als vier
getrennte 500-Perioden-Regeltabellen aus der Schicht `wvemod1_archive` an.
Auch dort bleibt ein vollstaendiger Vergleich eine Abweichungsbeobachtung und
keine historische Vollgleichheits- oder Produktionsfreigabebehauptung.
