# Plan: Periodenplan-Eingabevalidierung

## Ziel

Dieser Slice haertet die vorhandenen Periodenplan-Adapter gegen ungueltige
Entity-Update-Felder. `insurers` und `policyholders` muessen pro Periodenupdate
Listen sein; `null`, Objekte oder andere Werte werden kontrolliert mit
`ValueError` abgewiesen.

## Betroffene Pfade

- VU-Agrsich-Periodenplan
- VN-Agrsich-Periodenplan
- expliziter gemeinsamer VU/VN-Periodenplan

## Begrenzung

- Keine neue Fachlogik.
- Keine Aenderung der Periodenreihenfolge, Carryover-Semantik oder
  Regelanwendung.
- Keine historische Gleichheitsbehauptung.

## Validierung

- Fokustests fuer alle drei Plan-Adapter mit `insurers: null` und
  objektfoermigen `policyholders`.
