# Plan: VU-Periodenplan mit Carryover

## Ziel

Der deterministische Versicherer-Agrsich-Periodenplan erzeugt Replay-Snapshots
aus Startzustand und expliziten Updates. Dieser Slice reicht das kontrollierte
VU-Carryover-Flag aus dem Plan bis in den Agrsich-Replay weiter.

Damit koennen kleine Plan-Fenster portierte VU-Regel-Snapshots und den bereits
validierten Versicherer-State-Carryover kombinieren, ohne automatische
Regelauswahl oder Schedulerlogik einzufuehren.

## Ursprung im Altmodell

- `IMS.E`, `act Vrvu01` bis `Vrvu10`
- historische Versicherer-Agrsich-Ausgaben wie `VU14L1.DAT` und `VUSK1L4.DAT`
- vorhandener deterministischer Agrsich-Periodenplan und VU-Mehrperiodenrunner

## Umsetzungsschritte

1. Plan-Feld `carry_forward_insurer_state` strikt als Boolean validieren.
2. Das Feld in das erzeugte Replay-Fixture uebernehmen.
3. Der bestehende Agrsich-Replay nutzt danach unveraendert seine Carryover-
   und Periodenfolgevalidierung.
4. Tests fuer Plan-Erzeugung, Replay-Wirkung und falsche Feldtypen ergaenzen.

## Grenzen

- Keine neue VU-Regel und keine automatische historische Regelauswahl.
- Keine Vollsimulation und kein Scheduler-Anschluss.
- Periodenupdates und Regel-Snapshots bleiben explizite Eingaben.
