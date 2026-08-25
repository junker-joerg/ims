# Plan: Vdefmd6-Vorschock-Snapshots fuer PR 78

## Ziel

PR 78 materialisiert fuer genau eine Vorschockperiode 150 explizite
VN-Versicherungsregel-Snapshots und 150 Schaden-/Settlement-Snapshots. Die
moderne Ziehungsreihenfolge ist festgelegt und mit einem expliziten
`random.Random` reproduzierbar. Der Builder wendet keinen Snapshot an und
startet weder Runner noch Simulation.

## Quellen und Annahmen

- `IMS.E:2075-2104`, `Myinitvn`: historische `Sw`-Schwellen werden fuer beide
  Sparten vor den Regelperioden erzeugt;
- `IMS.E:4566-4669`, `Vdefmd6`: 25 VU, 150 Vorschock-VN und sechs VN-Regeln;
- `python_port/ims/model/vdefmd6_population.py`: typisierte Ausgangspopulation;
- `vn_insurance_rules.py` und `vn_rules.py`: vorhandene Snapshotoberflaechen;
- `python_port/ims/engine/rng.py`: moderne uniforme und normale RNG-APIs.

Die moderne Policy erzeugt pro VN in aufsteigender ID-Reihenfolge zuerst zwei
Schadenschwellen, dann Trigger und Hoehe je Sparte und zuletzt die
regelabhaengigen Versicherungsdraws. Fallbackdraws werden bewusst vorab
materialisiert. Diese Reihenfolge ist eine reproduzierbare Portierungswahl und
kein Nachweis der historischen RNG- oder Same-Slot-Reihenfolge.

## Umfang und Grenzen

Der Vertragsfall fuer Periode 2 und Seed `780001` umfasst:

- 25 aktive VU als lesende Praemien-/Werbeeingaenge;
- 150 VN-Regelsnapshots und 150 Schaden-Snapshots;
- 990 explizite uniforme Werte, davon 300 Schadenschwellen und 690
  Versicherungsdraws;
- 600 explizite Normalwerte;
- keine Anwendung der Snapshots und keine Legacy-Zeile als Erzeugungsinput.

Die Zaehler beziehen sich auf Werte der Python-RNG-API. Sie behaupten weder
eine Anzahl interner `random()`-Aufrufe noch Gleichheit mit den historischen
zwoelf `myrndf()`-Aufrufen je `normal()`.

## Restplanung

Nach PR 78 bleiben mindestens acht reviewbare PRs bis PR 86:

1. PR 79: Snapshotableitung fuer alle 25 VU-Regeln sowie BAV-Vorperiodeninputs
   und die offene Informationskostengrenze kartieren;
2. PR 80: den kontrollierten VU-/VN-/Schaden-/Settlement-Pfad fuer Perioden
   2-49 aus den expliziten Snapshots ausfuehren und VU14 klassifizieren;
3. PR 81: Schockgrenze und Perioden 50-100 schliessen;
4. PR 82: VU-Population auf SK1/all und VU-Klassenexporte verbreitern;
5. PR 83 und PR 84: VN-Regelzustand in zwei kleinen Gruppen schliessen;
6. PR 85: VN-Klassen- und SK1/all-Exporte aus demselben Zustand vergleichen;
7. PR 86: alle 15 Kernexporte gemeinsam vergleichen und die fachliche
   Freigabe menschlich neu bewerten.

Es gibt in PR 78 keine neue Fachregel, keine Simulation und keine historische
Vollgleichheitsbehauptung.
