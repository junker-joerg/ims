# Kontrollierter Vdefmd6-Vertrag fuer die zweite VN-Regelgruppe

## Ziel

Der Vertrag `pr84-v1` erzeugt aus dem kontrollierten 100-Perioden-Zustand von
PR 83 zusaetzlich `imsvnr04.dat` bis `imsvnr06.dat`. Alle drei Tabellen
entstehen vollstaendig im Speicher. Die historischen Dateien werden erst
danach fuer die Abweichungsklassifikation gelesen.

## Ursprung und Mapping

| Moderne Tabelle | Legacy-Referenz | Stufe | Selektor | Fenster |
| --- | --- | --- | --- | --- |
| `imsvnr04.dat` | `IMSVNR04.DAT` | II | `rule = 4` | `1-100` |
| `imsvnr05.dat` | `IMSVNR05.DAT` | II | `rule = 5` | `1-100` |
| `imsvnr06.dat` | `IMSVNR06.DAT` | II | `rule = 6` | `1-100` |

Die Referenzen reichen bis Periode 500. PR 84 vergleicht nur das Fenster
1-100 des kontrollierten Zustands.

## Kontrollierter Befund

| Ziel | Feldtreffer | Volle Zeilen | Erste Vollabweichung |
| --- | ---: | --- | ---: |
| `imsvnr04.dat` | 263/1300 | keine | 1 |
| `imsvnr05.dat` | 209/1300 | keine | 1 |
| `imsvnr06.dat` | 454/1300 | keine | 1 |

Insgesamt treffen 926 von 3.900 verglichenen Feldern. Davon sind 600 Treffer
Header und Periodenindex. Unter den eigentlichen Fachwerten treffen 326 von
3.300. Keine der 300 verglichenen Zeilen ist im gesamten VN-Zustand gleich.

Ueber beide PR-83-/PR-84-Regelgruppen treffen 1.872 von 7.800 Feldern. Nach
Abzug von Header und Periodenindex sind es 672 von 6.600 Fachwerten. Dieser
Befund beschreibt den aktuellen modernen Lauf, nicht die prinzipielle
Reproduzierbarkeit des historischen Modells.

## Provenienz und historischer Akkumulator

`IMSVNR04.DAT` bis `IMSVNR06.DAT` stammen aus `WVEMOD1.ZIP`. Das Archiv
enthaelt keinen zugeordneten `IMSREPOR.DAT`; Laufseed und genaue historische
Aufrufparameter werden daher nicht behauptet. Der Seed `5616` aus einem Report
in `VDEFMD5A.ZIP` wird nicht auf diese andere Archivfamilie uebertragen.

Der historische `Agrsich`-Block setzt Summen und Haeufigkeitstabellen nur vor
der Schleife ueber alle sechs VN-Regeln zurueck. Regeln 4 bis 6 erben damit
bereits dividierte Werte und Moduszaehler ihrer Vorgaenger. Der moderne
Aggregatdienst bildet jede Regel als unabhaengige Gruppe. PR 84 setzt deshalb
`historical_vn_rule_accumulator_compatibility_applied = false`.

## Offene Feldgrenze

Die historischen Kommentare bezeichnen `Ev1` und `Ev2` als
eigenversicherten Schaden. Der aktuelle Exportpfad belegt diese Spalten aus dem
modernen Vermoegenszustand. PR 84 klassifiziert die Differenzen, aendert das
Mapping aber nicht ohne separaten Herkunftsnachweis.

## Grenzen

- keine Legacy-Zeile als Erzeugungsinput;
- keine Datei geschrieben;
- kein Scheduler und keine allgemeine Simulation gestartet;
- keine Gleichsetzung verschiedener Archive oder Seeds;
- keine historische RNG-, Same-Slot- oder Vollgleichheitsbehauptung;
- keine Produktionsfreigabe aus den Teiltreffern;
- offene VU- und VN-Akkumulatorsemantiken bleiben unveraendert;
- die offene Ableitung des historischen Versicherungsgrads bleibt bestehen.

## Restplanung

Nach PR 84 bleiben zwei geplante Schritte bis PR 86:

1. PR 85: VN-Klassen und VN-SK1/all vergleichen;
2. PR 86: alle 15 Kernexporte gemeinsam klassifizieren und die fachliche
   Freigabe menschlich neu bewerten.
