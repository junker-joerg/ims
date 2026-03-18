# Migrationsprinzipien

Die IMS-Migration erfolgt schrittweise, PR-basiert und semantisch konservativ.

## Leitlinien

- Kleine PRs mit klar abgegrenztem Scope.
- Zuerst Struktur, Inventar und Dokumentation.
- Fachliche Logik wird erst portiert, wenn die Altdateien gesichtet und eingeordnet sind.
- Historische C-Dateien bleiben vorerst an ihrem Ort, sofern keine zwingende strukturelle Maßnahme dagegen spricht.
- Jede spätere Portierung soll das vorhandene Verhalten möglichst unverändert abbilden, bevor Refactorings erfolgen.
