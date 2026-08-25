# Plan: Vdefmd6-Aktions- und Seed-Vertrag fuer PR 75

## Ziel

PR 75 bindet die in den historischen Quellen belegten logischen Aktionszeiten
der `Vdefmd6`-Population an einen typisierten, lesenden Plan. Zusaetzlich wird
eine moderne reproduzierbare Seed-Policy definiert. Der Schritt fuehrt weder
Aktionen noch Zufallsziehungen oder eine Simulation aus.

## Historische Belege

- `IMS.E:21-28`: BAV-Aktionen `Frmdinf` bei logischer Zeit 1 und `Agrsich`
  bei logischer Zeit 10;
- `imsvu.e`: VU-Koordinator `PlanVU` bei logischen Zeiten 1-10;
- `imsvn.e`: VN-Koordinator `PlanVN` bei logischen Zeiten 1-10;
- `IMS.E:1045-1063` und `IMS.E:2143-2161`: Regeln werden nur bei aktiver
  Aktion und passender logischer Zeit aufgerufen;
- `IMS.E:4137-4233`: die Initialisierung setzt die wirksame VU-/VN-Aktion auf
  logische Zeit 1;
- `IMS.E:6022-6044`: der historische Seed wurde aus der lokalen Uhrzeit
  abgeleitet und an `srand` uebergeben.

## Konservative Umsetzung

1. Pro Periode werden wirksame Regelaufrufe bei logischer Zeit 1 und der
   BAV-Export bei logischer Zeit 10 beschrieben.
2. Die Koordinatoraufrufe bei Zeiten 2-10 erzeugen wegen der leeren
   Aktionsvektoreintraege keine zusaetzlichen wirksamen Regelaufrufe.
3. VN 151-200 erscheinen wegen ihrer belegten Aktivierungsgrenze erst ab
   Periode 50 im wirksamen Plan.
4. Ein Slot wird stabil als BAV, danach VU nach ID und danach VN nach ID
   serialisiert. Das ist nur eine technische Darstellungsordnung und keine
   Behauptung ueber die historische Reihenfolge gleichzeitiger Aktionen.
5. Die moderne Seed-Policy verlangt einen expliziten Basis-Seed und leitet
   Run `n` als `base_seed + n - 1` ab.
6. Der unbekannte historische Lauf-Seed, der historische Generatoralgorithmus
   und die historische Draw-Reihenfolge bleiben offen.

## Risiken und Grenzen

- Die Quellen belegen die gemeinsamen logischen Zeiten, aber keine belastbare
  Reihenfolge innerhalb eines gemeinsamen Slots.
- Die moderne Seed-Policy schafft Reproduzierbarkeit, keine historische
  RNG-Gleichheit.
- Der Plan ruft keinen Scheduler und keine Regel auf, zieht keine Zufallszahl,
  schreibt nichts und startet keine Simulation.
- Es gibt keine historische Vollgleichheitsbehauptung.

## Danach

PR 76 hat den VU14-Regelpfad fuer Perioden 1-49 projiziert und die offene
VN-/Schaden-/Settlement-Grenze klassifiziert. PR 77 hat diesen Pfad fuer alle
sechs VN-Regeln kartiert. PR 78 leitet als naechstes explizite Vorschock-
Snapshots und eine moderne Drawfolge ab, bevor ein vollstaendiger Folgezustand
behauptet werden darf.
