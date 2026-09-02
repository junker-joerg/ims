# IMS 2.x: Strategiekatalog in API und Workbench

Stand: 2026-09-02
Vertrag: `ims.strategy-catalog.v1`
API: `GET /api/strategies/catalog`

## Einordnung

PR105 transportiert den Strategiekatalog aus PR104 unveraendert bis in die
Workbench. Die API und die Anzeige sind Adapter des Metadatenvertrags. Sie
rufen keinen VU-/VN-Regelkern auf und veraendern keine Modellpopulation.

## Mapping

| Ursprung | Python-Vertrag | API | Workbench |
| --- | --- | --- | --- |
| `IMS.E`: `Vrvu01` bis `Vrvu10` | `ims.strategies.STRATEGY_DEFINITIONS` | `GET /api/strategies/catalog` | Gruppe `Versicherer (VU)` |
| `IMS.E`: `Vrvn01` bis `Vrvn06` | `ims.strategies.STRATEGY_DEFINITIONS` | `GET /api/strategies/catalog` | Gruppe `Versicherungsnehmer (VN)` |
| `Vdefmd6`: historische Regelklassen | `historical_rule_class` und `included_in_vdefmd6` | gleichnamige JSON-Felder | Herkunftsspalte je Regel |
| moderne Taxonomie aus PR104 | `ims.strategies.STRATEGY_FAMILIES` | `families` | acht Familienabschnitte |

`Vrvu10` wird in allen Schichten als historische Aktion ohne
Vdefmd6-Regelklasse ausgewiesen. Die drei VU-Fremdinformationsregeln bleiben
als Einzelregeln mit den Varianten `dumping`, `average` und `attack` erhalten.

## Read-only-Grenze

Das Payload weist folgende Grenzen explizit aus:

- `selection_enabled = false`;
- `parameter_editing_enabled = false`;
- `writes_enabled = false`;
- `execution_enabled = false`;
- `simulation_performed = false`;
- `historical_full_equality_claim = false`.

Der API-Pfad besitzt ausschliesslich eine GET-Route. `POST`, `PUT` und
`DELETE` werden abgewiesen. Die Workbench zeigt keine Eingabe, keine
Speicheraktion und keine Ausfuehrungsaktion im Strategiekatalog.

## Sichtbarer Informationsumfang

Die Workbench zeigt sechzehn historische Regeln in acht Familien. Pro Regel
werden stabile ID, Bezeichnung, Altaktion, Dissertationskapitel,
Vdefmd6-Einordnung, vorhandene Parameterdimensionen, Portierungsstand und
Teststatus dargestellt. Damit wird der vorhandene Modellbestand auffindbar;
eine fachliche Eignung fuer eine konkrete Regulierung wird daraus nicht
abgeleitet.

## Validierung und Grenzen

API- und UI-Vertrag werden automatisiert getestet. Der produktive
Frontend-Build sowie eine visuelle Desktop- und Mobilpruefung sichern die
Darstellung ab. Diese Pruefungen starten keine Simulation und belegen keine
vollstaendige Gleichheit mit historischen stochastischen Laeufen.

PR106 kann auf dieser Anzeige einen versionierten Zuordnungs- und
Parametrisierungsvertrag aufbauen. Eine editierbare Auswahl oder wirksame
Strategieaenderung bleibt danach weiterhin ein eigener, fachlich zu
validierender Schritt.
