# Plan: Legacy-Ziele fuer VU-Agrsich-Replay

## Ziel

Dieser Slice erweitert den VU-Agrsich-Replay-Pfad von einem einzelnen
`legacy_window` auf mehrere explizite Legacy-Ziele. Periodenplaene koennen diese
Ziele und einen Reportnamen durchreichen.

## Begrenzung

- Keine neue VU-Regelentscheidung.
- Kein historischer Scheduler.
- Keine Vollsimulation.
- Keine Gleichheitsbehauptung ohne Vergleichsergebnis.

## Umsetzung

1. `ReplayLegacyTarget` und mehrzieligen Tabellenvergleich im Replay-Runner
   ergaenzen.
2. Alte `legacy_window`-Fixtures weiterhin unterstuetzen.
3. `legacy_targets` und `legacy_report_name` im Periodenplan erhalten.
4. JSON-/CSV-Reportdateien ueber den bestehenden Reportpfad schreiben.

## Validierung

- Tests fuer direkten Replay-Runner mit Legacy-Ziel.
- Tests fuer Fixture- und Periodenplan-Durchleitung.
- Volltestlauf des Python-Ports.
