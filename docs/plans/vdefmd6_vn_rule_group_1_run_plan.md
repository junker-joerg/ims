# Plan: erste Vdefmd6-VN-Regelgruppe fuer PR 83

## Ziel

PR 83 verbreitert den kontrollierten `Vdefmd6`-Zustand aus PR 82 auf die
VN-Regelaggregate `imsvnr01.dat` bis `imsvnr03.dat`. Die Tabellen werden fuer
Perioden 1-100 vollstaendig im Speicher erzeugt und erst danach mit den
versionierten Legacy-Referenzen verglichen.

## Historischer Ursprung

- `IMSDATA.C` ordnet die VN den Regeln `Vrvn01` bis `Vrvn06` zu;
- `IMS.E`, `Agrsich`, bildet in der Schleife `j = 1` bis `6` die
  Regelaggregate der Stufe II;
- `IMSVNR01.DAT` und `IMSVNR02.DAT` enthalten die Perioden `1-300`;
- `IMSVNR03.DAT` enthaelt die Perioden `1-500`;
- PR 83 nutzt aus allen drei Referenzen ausschliesslich das gemeinsame Fenster
  `1-100`.

| Moderne Tabelle | Legacy-Referenz | Regel | Stufe | Fenster |
| --- | --- | ---: | --- | --- |
| `imsvnr01.dat` | `IMSVNR01.DAT` | 1 | II | `1-100` |
| `imsvnr02.dat` | `IMSVNR02.DAT` | 2 | II | `1-100` |
| `imsvnr03.dat` | `IMSVNR03.DAT` | 3 | II | `1-100` |

## Kontrollierter Vertrag

1. Derselbe moderne Zustand und Seed wie in PR 82 werden verwendet.
2. Nach jeder Periode werden die vorhandenen Agrsich-Records fuer die drei
   VN-Regeln ausgewaehlt.
3. Die Tabellen werden im Speicher zu jeweils 100 Perioden zusammengefuehrt.
4. Historische Zeilen werden erst nach der Erzeugung gelesen.
5. Der Bericht klassifiziert Feldtreffer und erste Abweichungen je Ziel.

## Historische Akkumulatorgrenze

Der historische Regelblock initialisiert Summen und Haeufigkeitstabellen nur
vor der Schleife ueber alle sechs VN-Regeln. Nach der Division fuer eine Regel
bleiben die Werte erhalten und gehen in die folgende Regel ein. Auch die
Moduszaehler fuer die gewaehlten VU werden zwischen den Regeln nicht geleert.
Zudem setzt die Initialisierung `sh1` zweimal und `sh2` an dieser Stelle nicht
zurueck.

Der moderne Agrsich-Dienst gruppiert jede VN-Regel unabhaengig. PR 83
dokumentiert und misst die Abweichung, uebernimmt das historische
Akkumulatorverhalten aber nicht still in die gemeinsam genutzte Fachlogik.

## Grenzen

- keine Legacy-Zeile als Erzeugungsinput;
- keine Datei wird geschrieben;
- kein Scheduler und keine allgemeine Simulation werden gestartet;
- keine historische RNG- oder Same-Slot-Gleichheitsbehauptung;
- keine historische Vollgleichheitsbehauptung;
- keine automatische Uebernahme des historischen VN-Regelakkumulators;
- die Feldbedeutung von `Ev1` und `Ev2` bleibt gegen den modernen
  Vermoegenszustand offen;
- der offene Versicherungsgrad `BAV.Dg` bleibt unveraendert.

## Restplanung

Nach PR 83 bleiben drei geplante Schritte bis PR 86:

1. PR 84: `imsvnr04.dat` bis `imsvnr06.dat` aus demselben Zustand schliessen;
2. PR 85: VN-Klassen und VN-SK1/all vergleichen;
3. PR 86: alle 15 Kernexporte gemeinsam klassifizieren und die fachliche
   Freigabe menschlich neu bewerten.
