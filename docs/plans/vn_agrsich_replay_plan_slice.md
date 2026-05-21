# VN-Agrsich-Periodenplan-Slice

## Ziel

Dieser Slice ergaenzt einen deterministischen Periodenplan fuer VN-Agrsich-Replays.
Aus einem gemeinsamen Startzustand werden explizite Periodenszenarien erzeugt, indem
Kontextwerte, VN-/VU-Entitaetsupdates und VN-Snapshotlisten pro Periode ersetzt
werden.

## Begrenzung

- Kein historischer VN-Scheduler.
- Keine neue Versichererwahl, Praeferenzlogik oder Normalziehung.
- Keine Vollsimulation und keine Aussage historischer Vollgleichheit.
- Legacy-Zielvergleiche bleiben im bestehenden VN-Agrsich-Replay-Fixture-Pfad.

## Umsetzung

- Neuer Adapter `ims.engine.vn_agrsich_replay_plan`.
- Strikt typisiertes `carry_forward_vn_state`-Flag.
- Explizite Validierung unbekannter VN-/VU-Entitaetsupdates.
- Uebergabe an den vorhandenen VN-Agrsich-Replay-Runner inklusive optionalem
  VN-State-Carryover.

## Validierung

- Unit-Tests fuer Fixture-Aufbau, Carryover-Lauf, Entity-Updates und
  Fehlerfaelle.
- Importtest fuer die neue oeffentliche API.
