# PR107: Strategiezuordnungen und Parameterschemata read-only in der Workbench

Stand: 2026-09-02

## Ziel

PR107 stellt den in PR106 eingefuehrten Vertrag
`ims.strategy-assignment-contract.v1` in der bestehenden Strategieansicht der
Workbench dar. Ein Anwender soll zwischen Strategiekatalog, belegten
Vdefmd6-Zuordnungsprofilen und vorhandenen Parameterschemata wechseln koennen,
ohne Konfiguration oder Simulation auszulosen.

## Grundlage

- `IMSDATA.C`: `ACTION`, `vkrvu` und `vkrvn` als historische Regelbindung;
- `IMS.E`: `Vuauini`, `Vnauini` und `Vdefmd6` als Quelle der Gruppenprofile;
- `ims.strategies.assignment_contract`: zwei Zieltypen, dreizehn
  Parameterschemata und achtzehn Quellprofile;
- `GET /api/strategies/assignment-contract`: einziger Transportweg des
  Zuordnungsvertrags.

## Umsetzung

1. Die vorhandene Strategieoberflaeche erhaelt Tabs fuer Katalog,
   Zuordnungen und Parameterschemata.
2. Die Zuordnungsansicht zeigt Zielgrenzen, Akteursbereiche, Strategie,
   Aktivierungsperiode und nur die Identitaet des Parameterprofils.
3. Die Parameteransicht zeigt Dataclass-/Loaderformen und vorhandene
   Feldpruefungen in aufklappbaren Detailzeilen.
4. Die zwei historischen Sektorpositionen werden als solche bezeichnet. Es
   werden keine modernen Spartennamen vorweggenommen.
5. Lade- und Fehlerzustaende des neuen GET-Endpunkts bleiben vom Katalogpfad
   getrennt.

## Grenzen

- keine konkreten Parameterwerte;
- keine Auswahl, Zuordnungs- oder Parameterbearbeitung;
- keine Gruppenaktion und kein geplanter Strategiewechsel;
- kein Schreiben, kein Runner-Start und keine Simulation;
- keine historische Vollgleichheitsbehauptung.

## Validierung

- gezielter Frontend-Quelltest fuer GET-Pfad, Tabs, Quellprofile,
  Parameterschemata und gesperrte Grenzen;
- TypeScript- und Vite-Produktionsbuild;
- bestehende API- und Vertragsregressionen;
- visueller Desktop- und Mobil-Smoke der drei Tabs;
- vollstaendige Python-Regression ohne Simulationsstart.

## Anschluss

PR108 kann ein versioniertes Entwurfsformat fuer konkrete Strategiezuordnungen
und Parameterwerte samt reiner Validierung einfuehren. Der Entwurf bleibt von
Workbench-Schreiben, Snapshot-Uebersetzung und Ausfuehrung getrennt.
