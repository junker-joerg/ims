# IMS-Bestandsinventar

Dieses Inventar dokumentiert den aktuellen Bestand für die Migration.
Historische C-Dateien werden in diesem PR nicht verschoben, sondern nur beschrieben.

## Aktueller Repo-Bestand

| Datei | Zweck heute | Spätere Zielzuordnung | Hinweis |
| --- | --- | --- | --- |
| `legacy_c/` | vorgesehener Ablageort für historische C-Dateien | Referenzbestand für spätere Portierung | Aktuell liegen im Repository noch keine C-Dateien vor. |
| `docs/migration/README.md` | Migrationsleitfaden | Dokumentation | beschreibt das Vorgehen, nicht die Fachlogik |
| `docs/migration/ims_inventory.md` | Inventar und Zuordnung | Dokumentation | wird mit wachsendem Altbestand erweitert |
| `docs/migration/python_target_architecture.md` | erstes Zielbild | Dokumentation / Architekturplanung | bewusst vorläufig |
| `docs/plans/README.md` | Platz für Arbeitspläne | Planungsdokumentation | für spätere PR-Zerlegung gedacht |
| `python_port/` | künftiger Python-Zielbereich | Python-Port | in diesem PR noch ohne Business-Implementierung |
| `tests/` | künftige Testbasis | Regressionen / Referenztests | in diesem PR noch ohne fachliche Tests |

## Offene Punkte

- Sobald historische C-Dateien im Repository vorliegen, werden sie hier einzeln mit Zweck und Zielzuordnung ergänzt.
- Fachliche Priorisierung und Portierungsreihenfolge bleiben noch offen.
