# Migration IMS/ESS -> Python

Dieses Verzeichnis bündelt die fachliche und technische Dokumentation für die kontrollierte Migration des historischen IMS/ESS-Codes nach Python.

## Grundsätze

- Die Migration erfolgt schrittweise und PR-basiert.
- Fachliche Semantik hat Vorrang vor syntaktischer Nähe zum C-Code.
- Historische UI-/Terminallogik wird nicht priorisiert portiert.
- Jede nichttriviale Portierung soll auf den Altcode zurückgeführt werden können.
- Unsicherheiten werden ausdrücklich dokumentiert.

## Reihenfolge der Migration

1. Bestandsaufnahme des Altcodes
2. Zielarchitektur für Python
3. Technisches Grundgerüst
4. Scheduler- und Zeitlogik
5. Zustandscontainer / Entitäten
6. RNG / Reproduzierbarkeit
7. Erste fachliche Slices
8. Regressionstests gegen Referenzszenarien

## Dokumente in diesem Verzeichnis

- `ims_inventory.md`: Inventar und grobe Klassifikation der Altdateien
- `python_target_architecture.md`: geplante Zielstruktur des Python-Ports
- weitere Mapping- und Verifikationsnotizen folgen in späteren PRs
