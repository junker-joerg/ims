# Entity-Mapping

Dieses Dokument beschreibt das minimale technische Grundgerüst für erste Entitäten und datengetriebene Initialisierung.
Es bereitet wenige Zustandscontainer und ein kleines JSON-Szenario vor, ohne bereits IMS-Fachlogik oder Regeln zu portieren.

## Dieses Grundgerüst bereitet vor

- eine kleine gemeinsame Entitätsbasis mit `BaseEntity`
- konservative Dataclasses für `BAV`, `Insurer` und `Policyholder`
- einen minimalen Szenario-Loader, der `SimulationContext` und wenige Entitäten erzeugt
- erste Tests für Instanziierung und grobe Szenario-Validierung

## Noch nicht enthalten

- BAV/VU/VN-Regeln oder fachliche Zustandsfortschreibung
- Aggregatbildung, UI oder Ergebnisverarbeitung
- umfangreiche Szenariovalidierung oder komplexe Relationen
- Ableitungen aus detaillierten historischen Datenstrukturen
