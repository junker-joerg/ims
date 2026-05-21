# Plan: Kontext-Overrides fuer Periodenplaene

## Ziel

Dieser groessere Slice vereinheitlicht die Periodenplan-Adapter fuer VU-Replay,
VN-Agrsich-Replay und explizite VU/VN-Laeufe. Periodenupdates duerfen
`logtime` und `max_periods` explizit angeben, damit erzeugte Fixtures die
globalen Perioden- und Exportkontexte gezielt steuern koennen.

## Begrenzung

- Kein historischer Scheduler.
- Keine neue VU-/VN-Entscheidungslogik.
- Keine Vollsimulation.
- Keine Legacy-Gleichheitsbehauptung.

## Umsetzung

1. Optionale `logtime`- und `max_periods`-Felder in die drei
   Periodenupdate-Dataclasses aufnehmen.
2. Die Felder beim Fixture-Aufbau nur bei expliziter Angabe in den
   Periodenkontext schreiben.
3. Den Basissnapshot weiter als Default fuer nicht gesetzte Kontextwerte
   verwenden.

## Validierung

- Tests fuer VU-Replay-Plan, VN-Agrsich-Plan und expliziten VU/VN-Plan.
- Volltestlauf des Python-Ports.
