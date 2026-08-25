# Kontrollierter Vdefmd6-Vertrag fuer die erste VN-Regelgruppe

## Ziel

Der Vertrag `pr83-v1` erzeugt aus dem kontrollierten 100-Perioden-Zustand von
PR 82 zusaetzlich `imsvnr01.dat` bis `imsvnr03.dat`. Alle drei Tabellen
entstehen vollstaendig im Speicher. Die historischen Dateien werden erst
danach fuer die Abweichungsklassifikation gelesen.

## Ursprung und Mapping

| Moderne Tabelle | Legacy-Referenz | Stufe | Selektor | Fenster |
| --- | --- | --- | --- | --- |
| `imsvnr01.dat` | `IMSVNR01.DAT` | II | `rule = 1` | `1-100` |
| `imsvnr02.dat` | `IMSVNR02.DAT` | II | `rule = 2` | `1-100` |
| `imsvnr03.dat` | `IMSVNR03.DAT` | II | `rule = 3` | `1-100` |

Die vorhandenen Referenzen reichen mindestens bis Periode 300. PR 83
vergleicht nur das gemeinsame Fenster 1-100 des kontrollierten Zustands.

## Kontrollierter Befund

| Ziel | Feldtreffer | Volle Zeilen | Erste Vollabweichung |
| --- | ---: | --- | ---: |
| `imsvnr01.dat` | 316/1300 | keine | 1 |
| `imsvnr02.dat` | 241/1300 | keine | 1 |
| `imsvnr03.dat` | 389/1300 | keine | 1 |

Insgesamt treffen 946 von 3.900 verglichenen Feldern. Header und Periodenindex
treffen fuer jede Datei in allen 100 Perioden. Keine der 300 verglichenen
Zeilen ist dagegen im gesamten VN-Zustand gleich.

## Historischer VN-Regelakkumulator

Der historische `Agrsich`-Block setzt Summen und Haeufigkeitstabellen nur vor
der Schleife ueber die sechs VN-Regeln zurueck. Regel 2 erbt daher den bereits
dividierten Zustand von Regel 1, Regel 3 wiederum den Zustand von Regel 2. Die
Moduszaehler fuer die gewaehlten Versicherer werden ebenfalls fortgetragen.
Die Initialisierung schreibt zudem zweimal auf `sh1`, waehrend `sh2` an dieser
Stelle nicht gesetzt wird.

Der moderne Aggregatdienst bildet jede Regel als unabhaengige Gruppe. PR 83
setzt deshalb
`historical_vn_rule_accumulator_compatibility_applied = false`. Eine
Kompatibilitaetsentscheidung bleibt ein eigener fachlicher Schritt.

## Offene Feldgrenze

Die historischen Kommentare bezeichnen `Ev1` und `Ev2` als
eigenversicherten Schaden. Der aktuelle Exportpfad belegt diese Spalten aus dem
modernen Vermoegenszustand. PR 83 klassifiziert die Differenzen, aendert das
gemeinsam genutzte Mapping aber nicht ohne separaten Herkunftsnachweis.

Ein moderner fehlender Versicherermodus wird als explizite Abweichung
protokolliert. Er wird nicht still als historische Versicherernummer `0`
interpretiert.

## Grenzen

- keine Legacy-Zeile als Erzeugungsinput;
- keine Datei geschrieben;
- kein Scheduler und keine allgemeine Simulation gestartet;
- keine historische RNG-, Same-Slot- oder Vollgleichheitsbehauptung;
- keine Produktionsfreigabe aus den Teiltreffern;
- offene VU- und VN-Akkumulatorsemantiken bleiben unveraendert;
- die offene Ableitung des historischen Versicherungsgrads bleibt bestehen.

## Restplanung

Nach PR 83 bleiben drei geplante Schritte bis PR 86:

1. PR 84: Regeln 4-6 aus demselben Zustand vergleichen;
2. PR 85: VN-Klassen und VN-SK1/all vergleichen;
3. PR 86: alle 15 Kernexporte gemeinsam klassifizieren und die fachliche
   Freigabe menschlich neu bewerten.
