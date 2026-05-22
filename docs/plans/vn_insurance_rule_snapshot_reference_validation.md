# Slice-Plan: VN-Versicherungsregel-Snapshot-Referenzen

## Ziel

Explizite VN-Versicherungsregel-Snapshots sollen keine Entscheidungen oder
Diagnosen mit unbekannten VU-IDs erzeugen koennen.

## Umsetzung

- Scenario-Loader prueft VU-Referenzen in `active_insurer_ids`
- Scenario-Loader prueft VU-Referenzen in `initial_decisions`
- Scenario-Loader prueft VU-Referenzen in `insurer_inputs` fuer Praeferenz-,
  Stichproben- und Best-Info-Regeln
- Scenario-Loader prueft VU-Referenzen in Vrvn04-Suchhistorien

## Validierung

- Runner-Tests fuer unbekannte aktive VU-IDs
- Runner-Tests fuer unbekannte Startentscheidungs-VU-IDs
- Runner-Tests fuer unbekannte VU-Input-IDs
- Runner-Tests fuer unbekannte Suchhistorien-VU-IDs
