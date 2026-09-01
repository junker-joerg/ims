# Historische 500-Zeilen-VN-Klassenlieferung

## Zweck

PR100 bindet `imsvnvk1.dat` bis `imsvnvk3.dat` als drei weitere berechnete
Tabellen an den gesperrten Produktionskorpusbericht. Der Vergleich ist eine
diagnostische Regression gegen versionierte Referenzen, keine historische
Vollgleichheitspruefung und keine neue Fachlogik.

## Historischer Ursprung und Python-Ziel

| Historischer Bezug | Python-Komponente | Fachliche Entsprechung |
| --- | --- | --- |
| `IMSDATA.C:241,286`, Feld `Vk` | `ims.api.historical_500_period_vn_class_delivery` | Regelklasse 1, 2 oder 3 fuer die Aggregatbildung |
| `IMS.E:758-811`, `Agrsich` | dieselbe Komponente | VN-Aggregation nach `Vk` auf Stufe III |
| `IMS.E:2205-3813`, `Vnag3[Vk]` | kontrollierter `Vdefmd6`-Zustandspfad | Aktivitaetszaehler der VN-Regelklasse |
| `ims.model.agrsich_export` | Ergebnisexport | `policyholder / III / rule_class = 1-3` |
| `IMSDATA.C`, `SIMLAENGE = 100` | `ims.engine.vdefmd6_repeat_corpus` | hoechstens 100 Perioden je Lauf |

Die Referenzen `IMSVNVK1.DAT` bis `IMSVNVK3.DAT` sind bytegenau an
`WVEMOD1.ZIP` gebunden. Jede Datei enthaelt 500 Ergebniszeilen. Diese werden
als fuenf getrennte 100-Perioden-Laeufe gelesen, jeweils mit lokalen Perioden
1-100. Daraus folgt kein historischer 500-Perioden-Lauf.

## Kontrollierter Vergleich

Der moderne Korpus verwendet explizite Seeds `20260001` bis `20260005`.
Diese Seeds sichern nur die Wiederholbarkeit des heutigen Diagnosepfads. Eine
historische RNG-Folge, gleiche Zinssaetze, gleiche Parametervarianten oder die
Identitaet eines damaligen Laufs werden nicht behauptet.

| Tabelle | Klasse | Zeilen | Exakt | Toleriert | Blockierend | Offen |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `imsvnvk1.dat` | 1 | 500 | 1.082 | 368 | 4.188 | 862 |
| `imsvnvk2.dat` | 2 | 500 | 1.425 | 491 | 4.121 | 463 |
| `imsvnvk3.dat` | 3 | 500 | 1.410 | 22 | 5.058 | 10 |
| **Summe** |  | **1.500** | **3.917** | **881** | **13.367** | **1.335** |

Keine der 1.500 Gesamtzeilen stimmt in allen Feldern ueberein. Zugleich treffen
3.917/19.500 Felder exakt und 881 weitere innerhalb der bestehenden
numerischen Toleranz. Dieser Befund friert die heutige Beobachtung ein. Er
belegt weder gleiche historische Eingaben noch fachliche Ungleichwertigkeit
des heutigen Kerns.

## Kumulierte Lieferung

Mit den bereits gelieferten Tabellen aus PR93, PR95/98, PR97/98 und PR99
umfasst der Produktionskorpusbericht nun 12/15 Tabellen und 4.800/6.300
Ergebniszeilen. Es fehlen drei Tabellen mit 1.500 Ergebniszeilen. Die Freigabe
bleibt daher `blocked_calculated_core_validation`; eine historische
Vollgleichheit und eine Produktionsfreigabe bleiben `false`.

## Validierungsgrenzen

- Referenzpfade und SHA-256-Hashes sind fest gebunden.
- Identitaet bleibt `policyholder / III / rule_class = 1-3`.
- Jede berechnete Tabelle muss genau 500 fortlaufend nummerierte
  Ergebniszeilen enthalten.
- Die Nummerierung bildet fuenf Laeufe ab und keinen langen Lauf.
- Historische Referenzzeilen werden nicht als Eingabe verwendet.
- Es wird keine Simulation, kein Server und kein Scheduler gestartet.
- Die im Altcode sichtbare klassenuebergreifende Akkumulatorbehandlung bleibt
  eine dokumentierte offene Semantikfrage; PR100 aendert sie nicht.
- Unterschiedliche historische Parameter- und Zufallskonfigurationen bleiben
  offen; daraus wird keine Vollgleichheitsforderung abgeleitet.

## Naechster Schritt

PR101 hat die drei VU-Klassenaggregate `imsvuvk1.dat` bis `imsvuvk3.dat`
nach demselben getrennten 5-mal-100-Vertrag angebunden. Der kumulierte Stand
liegt bei 15/15 Tabellen und 6.300/6.300 Ergebniszeilen. PR102 bewertet den
gemeinsamen Vollkorpus.
