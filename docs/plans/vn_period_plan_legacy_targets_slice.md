# Plan: Legacy-Ziele fuer VN-Agrsich-Periodenplaene

## Ziel

Dieser Slice schliesst die Luecke zwischen VN-Agrsich-Periodenplan und
VN-Agrsich-Replay-Validierung. Ein Plan kann Legacy-Ziele und einen
Reportnamen angeben; der erzeugte Lauf vergleicht seine Agrsich-Exports direkt
gegen die referenzierten historischen Tabellen.

## Begrenzung

- Keine neue VN-Wahl- oder Schadenslogik.
- Kein historischer Scheduler.
- Keine Vollsimulation.
- Keine Gleichheitsbehauptung ohne Vergleichsergebnis.

## Umsetzung

1. `legacy_targets` und `legacy_report_name` als optionale Plan-Felder laden.
2. Felder im erzeugten Replay-Fixture erhalten.
3. Relative Legacy-Pfade beim Planlauf am Planverzeichnis aufloesen.
4. Bestehenden VN-Agrsich-Runner inklusive Reportdateien wiederverwenden.

## Validierung

- Tests fuer Fixture-Durchleitung.
- Test fuer Planlauf mit Legacy-Ziel und geschriebenen Reportdateien.
- Test fuer kontrollierte Typvalidierung von `legacy_targets`.
