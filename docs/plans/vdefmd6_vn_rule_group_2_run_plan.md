# Plan: zweite Vdefmd6-VN-Regelgruppe fuer PR 84

## Ziel

PR 84 verbreitert den kontrollierten `Vdefmd6`-Zustand aus PR 83 auf die
VN-Regelaggregate `imsvnr04.dat` bis `imsvnr06.dat`. Die Tabellen werden fuer
Perioden 1-100 vollstaendig im Speicher erzeugt und erst danach mit den
versionierten Legacy-Referenzen verglichen.

## Historischer Ursprung

- `IMSDATA.C` ordnet die VN den Regeln `Vrvn01` bis `Vrvn06` zu;
- `IMS.E`, `Agrsich`, bildet in der Schleife `j = 1` bis `6` die
  Regelaggregate der Stufe II;
- `IMSVNR04.DAT` bis `IMSVNR06.DAT` enthalten jeweils die Perioden `1-500`;
- die drei Referenzen wurden gezielt aus `WVEMOD1.ZIP` uebernommen;
- PR 84 nutzt ausschliesslich das Fenster `1-100`.

| Moderne Tabelle | Legacy-Referenz | Regel | Stufe | Fenster |
| --- | --- | ---: | --- | --- |
| `imsvnr04.dat` | `IMSVNR04.DAT` | 4 | II | `1-100` |
| `imsvnr05.dat` | `IMSVNR05.DAT` | 5 | II | `1-100` |
| `imsvnr06.dat` | `IMSVNR06.DAT` | 6 | II | `1-100` |

## Kontrollierter Vertrag

1. Derselbe moderne Zustand und Seed wie in PR 83 werden verwendet.
2. Nach jeder Periode werden die vorhandenen Agrsich-Records fuer die drei
   VN-Regeln ausgewaehlt.
3. Die Tabellen werden im Speicher zu jeweils 100 Perioden zusammengefuehrt.
4. Historische Zeilen werden erst nach der Erzeugung gelesen.
5. Der Bericht klassifiziert Feldtreffer und erste Abweichungen je Ziel.

## Provenienz- und Akkumulatorgrenze

Die Referenzen stammen aus `WVEMOD1.ZIP`. Anders als `VDEFMD5A.ZIP` enthaelt
dieses Archiv keinen `IMSREPOR.DAT`, der Seed und konkrete Laufparameter
belegen wuerde. Der historische Laufseed der verglichenen Tabellen wird daher
nicht behauptet.

Der historische Regelblock initialisiert Summen und Haeufigkeitstabellen nur
vor der Schleife ueber alle sechs VN-Regeln. Regeln 4 bis 6 erben damit noch
mehr bereits dividierten Zustand und Moduszaehler ihrer Vorgaenger. Der moderne
Agrsich-Dienst gruppiert jede VN-Regel unabhaengig. PR 84 misst diese
Abweichung, aktiviert aber keine Legacy-Kompatibilitaet.

## Grenzen

- keine Legacy-Zeile als Erzeugungsinput;
- keine Datei wird geschrieben;
- kein Scheduler und keine allgemeine Simulation werden gestartet;
- keine Gleichsetzung verschiedener Archiv- oder Modellvarianten;
- keine Behauptung eines historischen Seeds fuer `WVEMOD1.ZIP`;
- keine historische RNG-, Same-Slot- oder Vollgleichheitsbehauptung;
- keine automatische Uebernahme des historischen VN-Regelakkumulators;
- die Feldbedeutung von `Ev1` und `Ev2` bleibt offen;
- der offene Versicherungsgrad `BAV.Dg` bleibt unveraendert.

## Restplanung

Nach PR 84 bleiben zwei geplante Schritte bis PR 86:

1. PR 85: VN-Klassen und VN-SK1/all aus demselben Zustand vergleichen;
2. PR 86: alle 15 Kernexporte gemeinsam klassifizieren und die fachliche
   Freigabe menschlich neu bewerten.
