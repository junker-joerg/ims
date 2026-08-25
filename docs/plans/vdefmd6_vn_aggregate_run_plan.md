# Plan: Vdefmd6-VN-Klassen und SK1/all fuer PR 85

## Ziel

PR 85 verbreitert den kontrollierten `Vdefmd6`-Zustand aus PR 84 auf die drei
VN-Klassenaggregate `imsvnvk1.dat` bis `imsvnvk3.dat` und das gemeinsame
VN-SK1-/all-Aggregat `imsvnsk1.dat`. Die Tabellen werden fuer Perioden 1-100
vollstaendig im Speicher erzeugt und erst danach mit den versionierten
Legacy-Referenzen verglichen.

## Historischer Ursprung und Mapping

- `IMSDATA.C` ordnet Regeln 1-2 der VN-Klasse 1, Regeln 3-4 der Klasse 2 und
  Regeln 5-6 der Klasse 3 zu;
- `IMS.E`, `Agrsich`, bildet die Klassen in der Schleife `j = 1` bis `3` auf
  Stufe III und danach das gemeinsame Aggregat auf Stufe IV;
- alle vier Referenzen stammen aus `WVEMOD1.ZIP` und enthalten 500 Perioden;
- PR 85 nutzt ausschliesslich das Fenster `1-100`.

| Moderne Tabelle | Legacy-Referenz | Stufe | Selektor | Fenster |
| --- | --- | --- | --- | --- |
| `imsvnvk1.dat` | `IMSVNVK1.DAT` | III | `rule_class = 1` | `1-100` |
| `imsvnvk2.dat` | `IMSVNVK2.DAT` | III | `rule_class = 2` | `1-100` |
| `imsvnvk3.dat` | `IMSVNVK3.DAT` | III | `rule_class = 3` | `1-100` |
| `imsvnsk1.dat` | `IMSVNSK1.DAT` | IV | `all` / kanonisch `SK1` | `1-100` |

## Kontrollierter Vertrag

1. Derselbe moderne Zustand und Seed wie in PR 84 werden verwendet.
2. Nach jeder Periode werden die vorhandenen Agrsich-Records fuer die drei
   VN-Klassen und alle aktiven VN ausgewaehlt.
3. Die vier Tabellen werden im Speicher zu jeweils 100 Perioden
   zusammengefuehrt.
4. Historische Zeilen werden erst nach der Erzeugung gelesen.
5. Der Bericht trennt Struktur- und Fachwerttreffer je Ziel.

## Historische Aggregatgrenzen

Der historische Klassenblock initialisiert Summen und Haeufigkeitstabellen nur
vor der Schleife ueber alle drei VN-Klassen. Klasse 2 und Klasse 3 erben damit
bereits dividierten Zustand und Moduszaehler ihrer Vorgaenger. Der moderne
Agrsich-Dienst gruppiert jede Klasse unabhaengig.

Vor dem SK1-/all-Block werden Summen und Haeufigkeitstabellen neu
initialisiert. Das Gesamtaggregat traegt daher keinen Klassenakkumulator fort.
Beide historischen Bloecke schreiben bei der Initialisierung jedoch zweimal
auf `sh1`, waehrend `sh2` an dieser Stelle nicht gesetzt wird.

PR 85 misst diese Grenzen, aktiviert aber keine Legacy-Kompatibilitaet und
aendert keine gemeinsam genutzte Fachlogik.

## Provenienzgrenze

Die vier Referenzen sind derselben `WVEMOD1`-Archivfamilie zugeordnet. Das
Archiv enthaelt keinen Runreport mit Seed. Alternative Dateien aus
`WVEMOD2.ZIP`, `WVEMOD3.ZIP` und den VDEFMOD5-Varianten werden nicht vermischt.

## Grenzen

- keine Legacy-Zeile als Erzeugungsinput;
- keine Datei wird geschrieben;
- kein Scheduler und keine allgemeine Simulation werden gestartet;
- keine Behauptung eines historischen Seeds fuer `WVEMOD1.ZIP`;
- keine historische RNG-, Same-Slot- oder Vollgleichheitsbehauptung;
- keine automatische Uebernahme historischer Akkumulatorsemantik;
- die Feldbedeutung von `Ev1` und `Ev2` bleibt offen;
- der offene Versicherungsgrad `BAV.Dg` bleibt unveraendert.

## Restplanung

Nach PR 85 bleibt ein geplanter Schritt:

1. PR 86: alle 15 Kernexporte gemeinsam klassifizieren, Struktur- und
   Fachwerttreffer zusammenfassen und die fachliche Freigabe menschlich neu
   bewerten.
