# Kontrollierter Vdefmd6-Vertrag fuer VN-Klassen und SK1/all

## Ziel

Der Vertrag `pr85-v1` erzeugt aus dem kontrollierten 100-Perioden-Zustand von
PR 84 zusaetzlich die drei VN-Klassenaggregate und das gemeinsame
VN-SK1-/all-Aggregat. Alle vier Tabellen entstehen vollstaendig im Speicher.
Die historischen Dateien werden erst danach fuer die Abweichungsklassifikation
gelesen.

## Ursprung und Mapping

| Moderne Tabelle | Legacy-Referenz | Stufe | Selektor | Fenster |
| --- | --- | --- | --- | --- |
| `imsvnsk1.dat` | `IMSVNSK1.DAT` | IV | `all` / kanonisch `SK1` | `1-100` |
| `imsvnvk1.dat` | `IMSVNVK1.DAT` | III | `rule_class = 1` | `1-100` |
| `imsvnvk2.dat` | `IMSVNVK2.DAT` | III | `rule_class = 2` | `1-100` |
| `imsvnvk3.dat` | `IMSVNVK3.DAT` | III | `rule_class = 3` | `1-100` |

Die Referenzen reichen bis Periode 500. PR 85 vergleicht nur das Fenster
1-100 des kontrollierten Zustands.

## Kontrollierter Befund

| Ziel | Feldtreffer | Volle Zeilen | Erste Vollabweichung |
| --- | ---: | --- | ---: |
| `imsvnsk1.dat` | 264/1300 | keine | 1 |
| `imsvnvk1.dat` | 289/1300 | keine | 1 |
| `imsvnvk2.dat` | 387/1300 | keine | 1 |
| `imsvnvk3.dat` | 294/1300 | keine | 1 |

Insgesamt treffen 1.234 von 5.200 verglichenen Feldern. Davon sind 800 Treffer
Header und Periodenindex. Unter den eigentlichen Fachwerten treffen 434 von 4.400.
Keine der 400 verglichenen Zeilen ist im gesamten VN-Zustand gleich.

Ueber alle sechs VN-Regeln und die vier VN-Aggregate treffen 3.106 von 13.000
Feldern. Nach Abzug von Header und Periodenindex sind es 1.106 von 11.000
Fachwerten. Dieser Befund beschreibt den aktuellen modernen Lauf, nicht die
prinzipielle Reproduzierbarkeit des historischen Modells.

## Provenienz und historischer Akkumulator

Alle vier Referenzen sind `WVEMOD1.ZIP` zugeordnet. Die versionierte
`IMSVNSK1.DAT` stimmt bytegenau mit dieser Archivvariante ueberein; die
Varianten anderer Archive unterscheiden sich. `WVEMOD1.ZIP` enthaelt keinen
zugeordneten Runreport. Laufseed und genaue historische Aufrufparameter werden
daher nicht behauptet.

Der historische Klassenblock setzt Summen und Haeufigkeitstabellen nur vor der
Schleife ueber alle drei VN-Klassen zurueck. Klassen 2 und 3 erben damit bereits
dividierte Werte und Moduszaehler ihrer Vorgaenger. Der moderne Aggregatdienst
bildet jede Klasse unabhaengig. Vor dem historischen SK1-/all-Block werden die
Akkumulatoren separat neu initialisiert; der moderne Gesamtaggregatpfad wird
dennoch nicht als historisch kompatibel behauptet. Beide historischen Bloecke
schreiben bei der Initialisierung zweimal auf `sh1`, waehrend `sh2` offen
bleibt.

## Offene Feldgrenze

Die historischen Kommentare bezeichnen `Ev1` und `Ev2` als
eigenversicherten Schaden. Der aktuelle Exportpfad belegt diese Spalten aus dem
modernen Vermoegenszustand. PR 85 klassifiziert die Differenzen, aendert das
Mapping aber nicht ohne separaten Herkunftsnachweis.

## Grenzen

- keine Legacy-Zeile als Erzeugungsinput;
- keine Datei geschrieben;
- kein Scheduler und keine allgemeine Simulation gestartet;
- keine Gleichsetzung verschiedener Archive oder Seeds;
- keine historische RNG-, Same-Slot- oder Vollgleichheitsbehauptung;
- keine Produktionsfreigabe aus den Teiltreffern;
- offene VU-, VN-Regel- und VN-Klassenakkumulatorsemantiken bleiben
  unveraendert;
- die offene Ableitung des historischen Versicherungsgrads bleibt bestehen.

## Restplanung

Nach PR 85 bleibt ein geplanter Schritt bis PR 86:

1. PR 86: alle 15 Kernexporte gemeinsam klassifizieren, Struktur- und
   Fachwerttreffer zusammenfassen und die fachliche Freigabe menschlich neu
   bewerten.
