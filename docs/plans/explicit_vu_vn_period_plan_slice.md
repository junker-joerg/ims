# Plan: Expliziter VU/VN-Periodenplan

## Ziel

Dieser Slice verbindet den expliziten VU/VN-Periodenrunner mit einem
deterministischen Periodenplan. Ein gemeinsamer Basissnapshot kann dadurch mit
periodischen Entity-Updates und expliziten VU/VN-Snapshotlisten zu ausfuehrbaren
Periodenszenarien erweitert werden.

## Begrenzung

- Kein historischer Scheduler.
- Keine neue VU-/VN-Entscheidungslogik.
- Keine versteckte RNG-Nutzung.
- Keine Legacy-Gleichheitsbehauptung.

## Umsetzung

1. Plan-Dataclasses fuer Basissnapshot, Carryover-Flags und Periodenupdates.
2. Explizite Snapshotlisten fuer bereits portierte VU-Regeln und VN-Settlement
   pro Periode erlauben.
3. Entity-Updates nur fuer vorhandene `entity_id`-Werte akzeptieren.
4. Erzeugte Perioden an den bestehenden expliziten VU/VN-Mehrperiodenrunner
   uebergeben.

## Validierung

- Tests fuer Fixture-Aufbau, kombinierten VU/VN-Lauf mit Carryover,
  Entity-Updates, Flag-Typisierung und Snapshot-Validierung.
