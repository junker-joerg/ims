# Plan: Vdefmd6-VU-Snapshots fuer PR 79

## Ziel

PR 79 materialisiert fuer eine einzelne Vorschockperiode die expliziten
Snapshots aller 25 `Vdefmd6`-Versicherer. Zusaetzlich haelt der Batch die fuer
`Frmdinf` und die VU-Regeln benoetigten Vorperiodenflaechen von 25 VU und 150 VN
fest. Kein Snapshot wird angewendet; BAV-Service, Runner und Simulation bleiben
aus.

## Quellen und Mapping

- `IMS.E:1083-1969`: Regeln `Vrvu01` bis `Vrvu09`;
- `IMS.E:92-395`, `Frmdinf`: Vorperiodenpraemien, Werbung, Reserven,
  Aktivitaet und Versicherungsgrad;
- `IMS.E:4566-4628`, `Vdefmd6`: VU-Gruppen, Anspruchsniveaus und 16 Parameter;
- `Bavauin(50, 0, 0.8, 0.02, 1)`: Informationskosten und Zinssatz;
- vorhandene Snapshottypen in `python_port/ims/model/vu_rules.py`.

Die neun Regeln werden auf sieben bestehende Snapshotfamilien abgebildet.
`Vrvu07` bis `Vrvu09` teilen die Fremdinformationsfamilie und unterscheiden
sich nur durch `dumping`, `average` und `attack`.

## Vertragsumfang

Der Vertragsfall Periode 2 mit Seed `790001` erzeugt:

- 25 VU-Snapshots: `2/2/3/3/3/3/9` je Snapshotfamilie;
- 8 uniforme Werte fuer die zwei `Vrvu01`-VU;
- 8 Normalwerte fuer die zwei `Vrvu02`-VU;
- Vorperiodeninputs fuer 25 VU und 150 VN;
- Zinssatz `0.02` und Informationskosten `0.8` als belegte Eingaben.

Die moderne Drawfolge ordnet VU nach ID. Sie ist reproduzierbar, aber keine
Behauptung historischer Same-Slot- oder RNG-Gleichheit.

## Informationskostengrenze

Der historische Code zieht `ik` in `Vrvn05` und `Vrvn06` beim
Vermoegensupdate ab. Der Python-Port berechnet die Kosten bereits im
Regelergebnis, uebergibt sie aber noch nicht an
`VNDamageSettlementSnapshot`. PR 79 dokumentiert diese Luecke; er fuegt keine
stille Settlement-Aenderung ein.

## Restplanung

Nach PR 79 bleiben mindestens sieben reviewbare PRs bis PR 86:

1. PR 80: Informationskosten explizit an den Settlement-Zustand anbinden und
   den kontrollierten VU-/VN-Pfad fuer Perioden 2-49 ausfuehren;
2. PR 81: Schockgrenze und Perioden 50-100 schliessen;
3. PR 82: VU-Population auf SK1/all und VU-Klassenexporte verbreitern;
4. PR 83 und PR 84: VN-Regelzustand in zwei kleinen Gruppen schliessen;
5. PR 85: VN-Klassen- und SK1/all-Exporte vergleichen;
6. PR 86: alle 15 Kernexporte gemeinsam vergleichen und die fachliche
   Freigabe menschlich neu bewerten.

Es gibt in PR 79 keine Simulation, keine neue Fachregel und keine historische
Vollgleichheitsbehauptung.
