# Historische 500-Zeilen-VU-Klassenlieferung

## Zweck

PR101 bindet `imsvuvk1.dat` bis `imsvuvk3.dat` als die letzten drei
berechneten Tabellen an den gesperrten Produktionskorpusbericht. Der Vergleich
ist eine diagnostische Regression gegen versionierte Referenzen, keine
historische Vollgleichheitspruefung und keine neue Fachlogik.

## Historischer Ursprung und Python-Ziel

| Historischer Bezug | Python-Komponente | Fachliche Entsprechung |
| --- | --- | --- |
| `IMSDATA.C:241,286`, Feld `Vk` | `ims.api.historical_500_period_vu_class_delivery` | Regelklasse 1, 2 oder 3 fuer die Aggregatbildung |
| `IMS.E:510-562`, `Agrsich` | dieselbe Komponente | VU-Aggregation nach `Vk` auf Stufe III |
| `IMS.E:1123-2010`, `Vuag3[Vk]` | kontrollierter `Vdefmd6`-Zustandspfad | Aktivitaetszaehler der VU-Regelklasse |
| `ims.model.agrsich_export` | Ergebnisexport | `insurer / III / rule_class = 1-3` |
| `IMSDATA.C`, `SIMLAENGE = 100` | `ims.engine.vdefmd6_repeat_corpus` | hoechstens 100 Perioden je Lauf |

Die Referenzen `IMSVUVK1.DAT` bis `IMSVUVK3.DAT` sind bytegenau an
`WVEMOD1.ZIP` gebunden. Jede Datei enthaelt 500 Ergebniszeilen. Diese werden
als fuenf getrennte 100-Perioden-Laeufe gelesen, jeweils mit lokalen Perioden
1-100. Daraus folgt kein historischer 500-Perioden-Lauf.

## Kontrollierter Vergleich

Der moderne Korpus verwendet explizite Seeds `20260001` bis `20260005`.
Diese Seeds sichern nur die Wiederholbarkeit des heutigen Diagnosepfads. Eine
historische RNG-Folge, gleiche Zinssaetze, gleiche Parametervarianten oder die
Identitaet eines damaligen Laufs werden nicht behauptet.

| Tabelle | Klasse | Zeilen | Volltreffer | Exakt | Toleriert | Blockierend | Offen |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `imsvuvk1.dat` | 1 | 500 | 5 | 1.146 | 29 | 5.825 | 0 |
| `imsvuvk2.dat` | 2 | 500 | 0 | 1.105 | 12 | 5.883 | 0 |
| `imsvuvk3.dat` | 3 | 500 | 0 | 1.079 | 0 | 5.921 | 0 |
| **Summe** |  | **1.500** | **5** | **3.330** | **41** | **17.629** | **0** |

Fuenf der 1.500 Gesamtzeilen stimmen in allen Feldern ueberein. Zugleich
treffen 3.330/21.000 Felder exakt und 41 weitere innerhalb der bestehenden
numerischen Toleranz. Dieser Befund friert die heutige Beobachtung ein. Die
fuenf Volltreffer belegen weder einen gemeinsamen historischen Lauf noch
historische Parameter-, RNG- oder Modellgleichheit.

## Vollstaendige Tabellenlieferung

Mit den bereits gelieferten Tabellen aus PR93, PR95/98, PR97/98, PR99 und
PR100 umfasst der Produktionskorpusbericht nun 15/15 Tabellen und
6.300/6.300 Ergebniszeilen. Es fehlt keine vereinbarte Tabelle und keine
vereinbarte Ergebniszeile mehr.

Die Freigabe bleibt trotzdem `blocked_calculated_core_validation`, weil die
berechneten Werte blockierende Abweichungen und offene historische
Laufbedingungen enthalten. Vollstaendige Lieferung bedeutet Vollstaendigkeit
des Vergleichsinputs, nicht Feldgleichheit oder Produktionsfreigabe.

## Validierungsgrenzen

- Referenzpfade und SHA-256-Hashes sind fest gebunden.
- Identitaet bleibt `insurer / III / rule_class = 1-3`.
- Jede berechnete Tabelle muss genau 500 fortlaufend nummerierte
  Ergebniszeilen enthalten.
- Die Nummerierung bildet fuenf Laeufe ab und keinen langen Lauf.
- Historische Referenzzeilen werden nicht als Eingabe verwendet.
- Es wird keine Simulation, kein Server und kein Scheduler gestartet.
- Die im Altcode sichtbare klassenuebergreifende Akkumulatorbehandlung bleibt
  eine dokumentierte offene Semantikfrage; PR101 aendert sie nicht.
- Unterschiedliche historische Parameter- und Zufallskonfigurationen bleiben
  offen; daraus wird keine Vollgleichheitsforderung abgeleitet.

## Naechster Schritt

PR102 erstellt und bewertet den gemeinsamen read-only Vollkorpusbericht fuer
alle 19 Referenzziele, 15 berechneten Tabellen und 6.300 Ergebniszeilen. Die
menschliche Freigabeentscheidung bleibt von der Tabellenvollstaendigkeit
getrennt.
