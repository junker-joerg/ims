# Migration IMS/ESS -> Python

Dieses Verzeichnis buendelt die fachliche und technische Dokumentation fuer die kontrollierte Migration des historischen IMS/ESS-Codes nach Python.

## Grundsaetze

- Die Migration erfolgt schrittweise und PR-basiert.
- Fachliche Semantik hat Vorrang vor syntaktischer Naehe zum C-Code.
- Historische UI-/Terminallogik wird nicht priorisiert portiert.
- Jede nichttriviale Portierung soll auf den Altcode zurueckgefuehrt werden koennen.
- Unsicherheiten werden ausdruecklich dokumentiert.

## Reihenfolge der Migration

1. Bestandsaufnahme des Altcodes
2. Zielarchitektur fuer Python
3. Technisches Grundgeruest
4. Scheduler- und Zeitlogik
5. Zustandscontainer / Entitaeten
6. RNG / Reproduzierbarkeit
7. Erste fachliche Slices
8. Regressionstests gegen Referenzszenarien

## Dokumente in diesem Verzeichnis

- `ims_inventory.md`: Inventar und grobe Klassifikation der Altdateien
- `python_target_architecture.md`: geplante Zielstruktur des Python-Ports
- `legacy_agrsich_validation_step.md`: erster echter Versicherer-Agrsich-Vergleich
- `legacy_vn_validation_step.md`: erster echter VN-Agrsich-Vergleich
- `legacy_agrsich_multi_period_step.md`: mehrperiodiger Rahmen fuer validierte Agrsich-Legacy-Vergleiche
- `agrsich_replay_runner.md`: deterministischer Mehrperioden-Replay-Runner mit Legacy-Fenstervergleich
- `agrsich_replay_plan.md`: deterministische Replay-Snapshot-Erzeugung aus Startzustand plus expliziten Periodenupdates
- `agrsich_validation_report.md`: maschinenlesbarer Report fuer Agrsich-Legacy-Fenstervergleiche
- weitere Mapping- und Verifikationsnotizen folgen in spaeteren PRs
