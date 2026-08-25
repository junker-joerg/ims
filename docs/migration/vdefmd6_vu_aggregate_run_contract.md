# Kontrollierter Vdefmd6-Vertrag fuer VU-Aggregate

## Ziel

Der Vertrag `pr82-v1` erzeugt aus dem kontrollierten 100-Perioden-Zustand von
PR 81 zusaetzlich `imsvusk1.dat` und `imsvuvk1.dat` bis `imsvuvk3.dat`. Alle
vier Tabellen entstehen vollstaendig im Speicher. Die historischen Dateien
werden erst danach fuer die Abweichungsklassifikation gelesen.

## Ursprung und Mapping

| Moderne Tabelle | Legacy-Referenz | Stufe | Selektor | Fenster |
| --- | --- | --- | --- | --- |
| `imsvusk1.dat` | `VUSK1L5.DAT` | IV | `all` / kanonisch `SK1` | `1-100` |
| `imsvuvk1.dat` | `IMSVUVK1.DAT` | III | `rule_class = 1` | `1-100` |
| `imsvuvk2.dat` | `IMSVUVK2.DAT` | III | `rule_class = 2` | `1-100` |
| `imsvuvk3.dat` | `IMSVUVK3.DAT` | III | `rule_class = 3` | `1-100` |

`IMSDATA.C` ordnet die VU-Regeln `1-2`, `3-6` und `7-9` den drei Klassen zu.
Der moderne Agrsich-Dienst verwendet dieselbe Zuordnung und bildet jede Klasse
als eigenstaendige Menge. Stufe IV mittelt ueber alle 25 aktiven VU.

`VUSK1L1.DAT` bis `VUSK1L5.DAT` bleiben fuenf Zeitfenster desselben
SK1-/all-Aggregats. Nur `VUSK1L5.DAT` belegt das hier erzeugte Fenster 1-100;
die vier anderen Dateien werden weder umgedeutet noch in diesen Lauf gemischt.

## Kontrollierter Befund

| Ziel | Feldtreffer | Volle Zeilen | Erste Vollabweichung |
| --- | ---: | --- | ---: |
| `imsvusk1.dat` | 232/1400 | Periode 1 | 2 |
| `imsvuvk1.dat` | 229/1400 | Periode 1 | 2 |
| `imsvuvk2.dat` | 222/1400 | keine | 1 |
| `imsvuvk3.dat` | 215/1400 | keine | 1 |

Insgesamt treffen 898 von 5.600 verglichenen Feldern. Das SK1-/all-Aggregat
und Klasse 1 treffen ihre Initialzeile vollstaendig. Die Klassen 2 und 3
weichen bereits in Periode 1 ab.

## Historische Klassenakkumulatoren

Der historische `Agrsich`-Block setzt `pr1`, `wa1` und die weiteren
Hilfsvariablen nur vor der Schleife ueber die drei VU-Klassen auf null. Nach
der Division fuer Klasse 1 bleibt deren Mittelwert stehen und wird vor der
Division fuer Klasse 2 zu deren Summe addiert; Klasse 3 erbt entsprechend den
bereits dividierten Wert von Klasse 2. So entstehen in Periode 1 unter anderem
die Legacy-Werte `43.3` fuer Klasse 2 und `44.8` fuer Klasse 3, obwohl alle VU
mit Praemie `40.0` starten.

Der gemeinsam genutzte moderne Aggregatdienst bildet unabhaengige
Klassenmittelwerte. PR 82 aendert diese Semantik nicht stillschweigend und
setzt `historical_vu_class_accumulator_compatibility_applied = false`. Ob das
historische Akkumulatorverhalten als Kompatibilitaetsmodus erhalten werden
soll, bleibt eine explizite fachliche Entscheidung.

## Grenzen

- keine Legacy-Zeile als Erzeugungsinput;
- keine Datei geschrieben;
- kein Scheduler und keine allgemeine Simulation gestartet;
- keine historische RNG-, Same-Slot- oder Vollgleichheitsbehauptung;
- keine Produktionsfreigabe aus den Teiltreffern;
- die offene Ableitung des historischen Versicherungsgrads bleibt bestehen.

## Restplanung

Nach PR 82 bleiben vier geplante Schritte bis PR 86:

1. PR 83: erste Gruppe der VN-Regelaggregate aus demselben Zustand schliessen;
2. PR 84: zweite Gruppe der VN-Regelaggregate schliessen;
3. PR 85: VN-Klassen und VN-SK1/all vergleichen;
4. PR 86: alle 15 Kernexporte gemeinsam klassifizieren und die fachliche
   Freigabe menschlich neu bewerten.
