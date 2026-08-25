# Plan: Vdefmd6-VU-Aggregate fuer PR 82

## Ziel

PR 82 verbreitert den kontrollierten `Vdefmd6`-Zustand aus PR 81 auf vier
Versicherer-Aggregate. Fuer Perioden 1-100 werden `imsvusk1.dat` sowie
`imsvuvk1.dat` bis `imsvuvk3.dat` vollstaendig im Speicher erzeugt und erst
danach mit den versionierten Legacy-Referenzen verglichen.

## Historischer Ursprung

- `IMSDATA.C:77` ordnet VU-Regeln `1-2` der Klasse 1, `3-6` der Klasse 2 und
  `7-9` der Klasse 3 zu;
- `IMS.E:502-556`, `Agrsich`, bildet die drei VU-Klassenaggregate;
- `IMS.E:557-600`, `Agrsich`, bildet das gemeinsame VU-Aggregat der Stufe IV;
- `VUSK1L5.DAT` ist das belegte SK1-/all-Zeitfenster fuer Perioden 1-100;
- `IMSVUVK1.DAT` bis `IMSVUVK3.DAT` enthalten die Klassenreferenzen fuer das
  Vergleichsfenster 1-100 innerhalb ihrer Dateien mit Perioden 1-500.

Die Dateien `VUSK1L1.DAT` bis `VUSK1L5.DAT` bleiben Zeitfenster desselben
Aggregats auf Stufe IV. PR 82 behandelt insbesondere `VUSK1L5.DAT` nicht als
eigene Aggregatebene.

## Kontrollierter Vertrag

1. Derselbe moderne Zustand und derselbe Seed wie in PR 81 werden verwendet.
2. Nach jeder Periode werden die bereits vorhandenen Agrsich-Records fuer die
   drei VU-Regelklassen und fuer alle aktiven VU ausgewaehlt.
3. Die vier Tabellen werden fuer Perioden 1-100 im Speicher gesammelt.
4. Erst nach Abschluss der Erzeugung werden die historischen Tabellen gelesen.
5. Der Bericht klassifiziert Feldtreffer und erste Abweichungen je Ziel.

## Historische Akkumulatorgrenze

Der ausfuehrbare Klassenblock in `Agrsich` setzt seine Hilfsvariablen nur vor
der Schleife ueber die drei Klassen auf null; zwischen den Klassen werden sie
nicht zurueckgesetzt. Nach der Division fuer eine
Klasse verbleibt deren Mittelwert im Akkumulator und geht in die folgende
Klasse ein. Der vorhandene Python-Agrsich-Dienst bildet dagegen jede Klasse
als eigenstaendige Menge.

PR 82 dokumentiert und misst diese Abweichung. Er fuehrt den historischen
klassenuebergreifenden Akkumulator nicht als stille Aenderung in den gemeinsam
genutzten Aggregatdienst ein. Eine bewusste Kompatibilitaetsentscheidung waere
ein eigener fachlicher Schnitt.

## Grenzen

- keine Legacy-Zeile als Erzeugungsinput;
- keine Datei wird geschrieben;
- kein Scheduler und keine allgemeine Simulation werden gestartet;
- keine historische RNG- oder Same-Slot-Gleichheitsbehauptung;
- keine historische Vollgleichheitsbehauptung;
- keine automatische Uebernahme des historischen Klassenakkumulatorverhaltens;
- der offene Versicherungsgrad `BAV.Dg` bleibt unveraendert.

## Restplanung

Nach PR 82 bleiben vier geplante Schritte bis PR 86:

1. PR 83 und PR 84: VN-Regelzustand in zwei kleinen Gruppen schliessen;
2. PR 85: VN-Klassen- und SK1/all-Exporte aus demselben Zustand vergleichen;
3. PR 86: alle 15 Kernexporte gemeinsam vergleichen und die fachliche
   Freigabe menschlich neu bewerten.
