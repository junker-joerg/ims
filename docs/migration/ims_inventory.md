# IMS-Migrationsinventar

Dieses Dokument beschreibt ein erstes, bewusst vorsichtiges Inventar der voraussichtlich zentralen Altdateien der IMS-C-Codebasis.
Aktuell liegen diese Dateien noch nicht in diesem Repository vor; die folgende Liste ist daher eine Arbeitsgrundlage für die spätere Einsortierung und muss beim Auftauchen der Originaldateien überprüft werden.

## Hinweise zum Status

- **Keine Altdatei wurde in diesem PR verschoben oder portiert.**
- **Unsicherheiten sind ausdrücklich markiert.**
- Die Zuordnungen dienen nur der Migrationsplanung und sind **noch keine belastbare Architekturentscheidung**.

## Vorläufige Liste zentraler Altdateien

| Altdatei (vorläufig) | Kurzbeschreibung | Grobe Zuordnung | Status / Unsicherheit |
| --- | --- | --- | --- |
| `inventory_main.c` | Vermuteter Prozess- oder Programmeinstieg. | Initialisierung, ggf. UI | **Unsicher**: Datei aktuell nicht im Repo vorhanden. |
| `inventory_context.c` | Vermutete Initialisierung gemeinsamer Laufzeitdaten. | Initialisierung, Aggregate | **Unsicher**: Name und Verantwortung müssen an Originalcode geprüft werden. |
| `inventory_scheduler.c` | Vermutete Steuerung der Abarbeitungsreihenfolge. | Scheduler | **Unsicher**: Schnittstellen und Nebenwirkungen noch unbekannt. |
| `inventory_rng.c` | Vermutete Zufallszahl- oder Seed-Verwaltung. | RNG | **Unsicher**: unklar, ob RNG isoliert oder verteilt implementiert ist. |
| `inventory_ui.c` | Vermutete Ausgabe- oder Bedienlogik. | UI | **Unsicher**: kann auch mit I/O oder CLI vermischt sein. |
| `inventory_aggregate.c` | Vermutete Berechnung aggregierter Bestände oder Kennzahlen. | Aggregate | **Unsicher**: Aggregatlogik kann über mehrere Dateien verteilt sein. |
| `inventory_domain.c` | Vermutete Kerndomäne rund um Bestände/Objekte. | Domäne | **Unsicher**: Domänengrenzen erst nach Sichtung belastbar. |

## Einsortierungsprinzip für spätere PRs

1. Historische C-Dateien bleiben zunächst an ihrem bisherigen Ort.
2. Jede Datei wird erst nach Sichtung des tatsächlichen Inhalts einer Ziel-Domäne zugeordnet.
3. Grenzfälle zwischen Domäne, Scheduler, RNG, UI, Aggregaten und Initialisierung werden separat dokumentiert.
4. Erst nach dieser Einordnung werden semantisch konservative Portierungs-PRs vorbereitet.
