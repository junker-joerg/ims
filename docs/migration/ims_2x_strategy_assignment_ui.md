# IMS 2.x: Strategiezuordnungen und Parameterschemata in der Workbench

Stand: 2026-09-02
Vertrag: `ims.strategy-assignment-contract.v1`
API: `GET /api/strategies/assignment-contract`

## Einordnung

PR107 transportiert den in PR106 festgelegten Zuordnungs- und
Parametrisierungsvertrag unveraendert in die Workbench. Die Ansicht erklaert,
welche historischen Akteursgruppen welche Strategie verwenden und welche
bereits implementierten Parameterfelder zu einer Strategie gehoeren. Sie ist
keine Szenariokonfiguration.

## C-zu-Workbench-Mapping

| Historischer Ursprung | Python-/API-Zwischenschicht | Workbench-Darstellung |
| --- | --- | --- |
| `IMSDATA.C`, `ACTION.st` | `assignment_targets` | eine optionale Katalogstrategie je einzelnem VU oder VN |
| `IMSDATA.C`, `vkrvu` und `vkrvn` | Regel-ID und Regelklasse im Quellprofil | Strategie und historische Klasse je Akteursbereich |
| `IMS.E`, `Vdefmd6` | `source_profiles` | achtzehn VU-/VN-Bereiche mit Aktivierungsperiode |
| vorhandene `*RuleParameters` | `parameter_schemas` | aufklappbare Schemata mit Feldnamen und Zweiervektorform |
| vorhandene Mapping-Loader | `existing_validation` | lesbare Beschreibung der bereits implementierten Pruefung |

## Bedienpfad

Der Bereich `Strategien` enthaelt drei Tabs:

1. `Katalog` behaelt die in PR105 eingefuehrte Regel- und Familienansicht.
2. `Zuordnungen` zeigt die belegten Vdefmd6-Quellprofile getrennt nach VU und
   VN. VU14 und VU15-16 bleiben wegen ihrer unterschiedlichen
   Parameterfingerabdruecke getrennte Profile.
3. `Parameterschemata` zeigt die dreizehn vorhandenen Dataclass-/Loaderformen.
   Einzelne Schemata lassen sich fuer die Feldansicht aufklappen.

`Vrvn01` wird ausdruecklich ohne Strategieschema dargestellt. Seine
Versichererwahl-Ziehungen bleiben Laufeingaben und werden nicht zu
Strategieparametern umgedeutet.

## Sichtbare Grenzen

Die Workbench benennt die zwei Vektoreintraege nur als historische
Sektorpositionen. Dieselbe Strategie gilt fuer beide Positionen. Kfz,
Sach-Haftpflicht, Leben und Kranken werden in diesem Schritt weder zugeordnet
noch modelliert.

Konkrete historische Parameterwerte bleiben verborgen. Angezeigt werden nur
Schema, Feldform und ein gekuerzter Fingerabdruck zur Unterscheidung der
quellgebundenen Profile. Der vollstaendige API-Vertrag bleibt read-only.

## Ausfuehrungsgrenze

Die neuen Tabs verwenden ausschliesslich GET. Sie enthalten keine Eingaben,
Speicheraktionen oder Ausfuehrungsaktionen. Der Schritt startet weder einen
Regelkern noch einen Runner oder eine Simulation und behauptet keine
historische Vollgleichheit.

## Anschluss

Ein spaeteres Entwurfsformat fuer konkrete Werte benoetigt eigene
Versionierung und Validierung. Erst danach koennen Uebersetzung in vorhandene
Regel-Snapshots, UI-Schreiben und Ausfuehrung in getrennten PRs entschieden
werden.
