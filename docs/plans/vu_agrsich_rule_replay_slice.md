# Plan: VU-Agrsich-Replay mit Regel- und Carryover-Schritt

## Ziel

Der bestehende Versicherer-Agrsich-Replay schreibt bislang explizit geladene
Perioden-Snapshots direkt in Agrsich-Exporttabellen. Dieser Slice bindet den
bereits portierten, kontrollierten VU-Periodenschritt vor der Exportbildung an.

Dadurch koennen explizite VU-Regel-Snapshots und optionaler VU-State-Carryover
in denselben Agrsich-Replay- und Validierungspfad einfliessen.

## Ursprung im Altmodell

- `IMS.E`, `act Vrvu01` bis `Vrvu10`
- historische Versicherer-Agrsich-Ausgaben wie `VU14L1.DAT` und `VUSK1L4.DAT`
- bereits portierte VU-Regelkerne und der kontrollierte VU-Mehrperiodenrunner

## Umsetzungsschritte

1. VU-State-Carryover aus `vu_rule_runner.py` wiederverwendbar machen.
2. `run_agrsich_replay_from_mapping` vor dem Export durch den portierten
   VU-Periodenschritt fuehren.
3. Optionales Fixture-Feld `carry_forward_insurer_state` streng als Boolean
   validieren.
4. Replay-Ergebnis um VU-Periodendiagnosen und Carryover-Diagnosen erweitern.
5. Tests fuer Exportwirkung, Fixture-Parsing und Importflaeche ergaenzen.

## Grenzen

- Keine automatische historische Regelauswahl.
- Keine neue RNG- oder Schedulerlogik.
- Keine Behauptung historischer Vollgleichheit.
- Periodenzustaende und Regel-Snapshots bleiben explizite Validierungseingaben.
