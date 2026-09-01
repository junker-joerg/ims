# Historische 500-Zeilen-VN-Regellieferung

## Zweck

PR99 bindet `imsvnr03.dat` bis `imsvnr06.dat` als vier weitere berechnete
Tabellen an den gesperrten Produktionskorpusbericht. Der Vergleich ist eine
diagnostische Regression gegen versionierte Referenzen, keine historische
Vollgleichheitspruefung und keine neue Fachlogik.

## Historischer Ursprung und Python-Ziel

| Historischer Bezug | Python-Komponente | Fachliche Entsprechung |
| --- | --- | --- |
| `IMS.E:2623-2941`, `Vrvn03` | `ims.api.historical_500_period_vn_rule_delivery` | VN-Regel 3 / Praeferenz |
| `IMS.E:2944-3222`, `Vrvn04` | dieselbe Komponente | VN-Regel 4 / totale Suche |
| `IMS.E:3225-3514`, `Vrvn05` | dieselbe Komponente | VN-Regel 5 / Stichprobensuche |
| `IMS.E:3517-3786`, `Vrvn06` | dieselbe Komponente | VN-Regel 6 / beste Information |
| `IMSDATA.C`, `SIMLAENGE = 100` | `ims.engine.vdefmd6_repeat_corpus` | hoechstens 100 Perioden je Lauf |
| `IMS.E`, `(rl-1)*sl+period` | Ergebniszeilenvertrag `pr98-v1` | fortlaufende Nummerierung mehrerer Laeufe |

Die Referenzen `IMSVNR03.DAT` bis `IMSVNR06.DAT` sind bytegenau an
`WVEMOD1.ZIP` gebunden. Jede Datei enthaelt 500 Ergebniszeilen. Diese werden
als fuenf getrennte 100-Perioden-Laeufe gelesen, jeweils mit lokalen Perioden
1-100. Daraus folgt kein historischer 500-Perioden-Lauf.

## Kontrollierter Vergleich

Der moderne Korpus verwendet explizite Seeds `20260001` bis `20260005`.
Diese Seeds sichern nur die Wiederholbarkeit des heutigen Diagnosepfads. Eine
historische RNG-Folge, gleiche Zinssaetze, gleiche Parametervarianten oder die
Identitaet eines damaligen Laufs werden nicht behauptet.

| Tabelle | Regel | Zeilen | Exakt | Toleriert | Blockierend | Offen |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `imsvnr03.dat` | 3 | 500 | 1.434 | 447 | 4.239 | 380 |
| `imsvnr04.dat` | 4 | 500 | 1.028 | 316 | 4.552 | 604 |
| `imsvnr05.dat` | 5 | 500 | 1.038 | 19 | 5.433 | 10 |
| `imsvnr06.dat` | 6 | 500 | 2.178 | 27 | 4.285 | 10 |
| **Summe** |  | **2.000** | **5.678** | **809** | **18.509** | **1.004** |

Keine der 2.000 Gesamtzeilen stimmt in allen Feldern ueberein. Zugleich treffen
5.678/26.000 Felder exakt und 809 weitere innerhalb der bestehenden numerischen
Toleranz. Dieser Befund wird als Beobachtungsfingerabdruck eingefroren. Er
belegt weder gleiche historische Eingaben noch fachliche Ungleichwertigkeit
des heutigen Kerns.

## Kumulierte Lieferung

Mit den bereits gelieferten Tabellen aus PR93, PR95/98 und PR97/98 umfasst der
Produktionskorpusbericht nun 9/15 Tabellen und 3.300/6.300 Ergebniszeilen. Es
fehlen sechs Tabellen mit 3.000 Ergebniszeilen. Die Freigabe bleibt daher
`blocked_calculated_core_validation`; eine historische Vollgleichheit und eine
Produktionsfreigabe bleiben `false`.

## Validierungsgrenzen

- Referenzpfade und SHA-256-Hashes sind fest gebunden.
- Identitaet bleibt `policyholder / II / rule = 3-6`.
- Jede berechnete Tabelle muss genau 500 fortlaufend nummerierte Ergebniszeilen
  enthalten.
- Die Nummerierung bildet fuenf Laeufe ab und keinen langen Lauf.
- Historische Referenzzeilen werden nicht als Eingabe verwendet.
- Es wird keine Simulation, kein Server und kein Scheduler gestartet.
- Unterschiedliche historische Parameter- und Zufallskonfigurationen bleiben
  offen; daraus wird keine Vollgleichheitsforderung abgeleitet.

## Naechster Schritt

PR100 hat die drei VN-Klassenaggregate `imsvnvk1.dat` bis `imsvnvk3.dat`
nach demselben getrennten 5-mal-100-Vertrag angebunden. Der kumulierte Stand
liegt bei 12/15 Tabellen und 4.800/6.300 Ergebniszeilen. PR101 fuehrt mit den
drei VU-Klassenaggregaten fort.
