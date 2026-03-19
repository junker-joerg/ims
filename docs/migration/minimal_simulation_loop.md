# Minimale Simulationsschleife

Dieses Dokument beschreibt eine kleine technische Orchestrierung für genau einen BAV-nahen Update-Schritt.
Die Schleife ist bewusst minimal und noch keine historische IMS/ESS-Simulation.

## Was die Orchestrierung leistet

- lädt ein Szenario
- initialisiert optional ein RNG im Kontext
- führt genau einen `update_bav_central_state(...)` aus
- sammelt anschließend einfache Aggregatkennzahlen
- gibt alle aktualisierten Objekte in einem Ergebnisobjekt zurück

## Verwendete bestehende Bausteine

- `load_scenario`
- `ensure_context_rng` als kleine RNG-Initialisierung aus dem Kontext-Seed
- `update_bav_central_state`
- `collect_basic_aggregates`

## Was ausdrücklich noch nicht enthalten ist

- keine historische Vollsimulation
- keine Scheduler-gesteuerte Ablaufsteuerung
- keine UI
- keine komplexe Markt- oder Regelverarbeitung
- keine Behauptung fachlicher Gleichwertigkeit

## Warum dies noch keine historische Simulation ist

Die Orchestrierung verbindet nur bestehende technische Bausteine zu genau einem einzelnen Update-Schritt.
Mehrperiodige Abläufe, historische Reihenfolgen und fachliche Regeln müssen später separat validiert und portiert werden.
