# Plan: VU-Agrsich-Replay-Periodenfolge

## Ziel

Der Versicherer-Agrsich-Replay nutzt optional den kontrollierten
VU-State-Carryover. Dieser Slice stellt sicher, dass Carryover nur ueber
strikt steigende Replay-Perioden laeuft.

## Ursprung im Altmodell

- `IMS.E`, `act Vrvu01` bis `Vrvu10`
- historische Versicherer-Agrsich-Ausgaben wie `VU14L1.DAT` und `VUSK1L4.DAT`
- portierter VU-Mehrperiodenrunner mit bereits vorhandener Periodenfolgepruefung

## Umsetzungsschritte

1. Replay-Perioden vor dem ersten VU-Schritt und vor Export-I/O validieren.
2. Doppelte Replay-Perioden bei aktivem Carryover ablehnen.
3. Rueckwaerts oder unsortiert angeordnete Replay-Perioden bei aktivem
   Carryover ablehnen.
4. Tests fuer programmatischen Override und Fixture-Flag ergaenzen.

## Grenzen

- Ohne aktivierten VU-Carryover bleibt der bestehende explizite Snapshot-Replay
  unveraendert.
- Keine neue VU-Regellogik, keine automatische Regelauswahl, kein Scheduler.
