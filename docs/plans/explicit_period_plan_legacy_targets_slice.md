# Plan: Legacy-Ziele im expliziten VU/VN-Periodenplan

## Ziel

Dieser Slice verbindet den expliziten VU/VN-Periodenplan mit den Legacy-Zielen
des kombinierten VU/VN-Runners. Plan-Fixtures koennen dadurch Perioden, Carryover
und Validierungsziele zusammen beschreiben.

## Begrenzung

- Keine neue VU-/VN-Fachlogik.
- Kein historischer Scheduler.
- Keine Vollsimulation und keine historische Gleichheitsbehauptung.
- Keine neue Reportstruktur; vorhandene Legacy-Reportbausteine werden genutzt.

## Umsetzung

1. `legacy_targets` und `legacy_report_name` als optionale Plan-Felder laden.
2. Beide Felder in das erzeugte Runner-Fixture uebernehmen.
3. Relative Legacy-Pfade am Plan-Fixture-Verzeichnis aufloesen.
4. Die Ziele an `run_explicit_multi_period_from_mappings` weiterreichen.

## Validierung

- Fixture-Aufbau erhaelt Legacy-Ziele und Reportnamen.
- Plan-Lauf vergleicht einen expliziten Versichererexport und schreibt die
  bestehenden Reportartefakte.
