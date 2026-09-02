# PR108: Versioniertes Strategiezuordnungs-Entwurfsformat

Stand: 2026-09-02

## Ziel

PR108 fuehrt ein kleines, versioniertes JSON-Entwurfsformat fuer konkrete
Strategiezuordnungen und die zugehoerigen Parameterwerte ein. Entwuerfe werden
nur strukturell und gegen die vorhandenen Katalog-, Ziel- und
Parameterschemavertraege geprueft.

Der Schritt speichert keinen Entwurf, erzeugt keine Regel-Snapshots und fuehrt
keine Strategie aus.

## Historische und technische Grundlage

- `IMSDATA.C`: `ACTION.st`, `vkrvu` und `vkrvn` als historische Bindung einer
  Regel an ein einzelnes VU oder VN;
- `IMS.E`: `Vuauini`, `Vnauini` und `Vdefmd6` als belegte Population mit
  Aktivierungsangaben und zwei historischen Sektorpositionen;
- `ims.strategy-catalog.v1`: stabile Strategie-IDs;
- `ims.strategy-assignment-contract.v1`: zulaessige Akteurstypen,
  Parameterschemata und vorhandene Loadergrenzen.

## Formatentscheidungen

1. Ein Entwurf bezieht sich in Version 1 auf die bekannte `Vdefmd6`-Population
   mit 25 VU und 200 VN.
2. Der Entwurf darf eine Teilmenge von Akteuren enthalten. Er beschreibt noch
   keine Ueberschreibungs- oder Zusammenfuehrungssemantik.
3. Derselbe Akteur darf innerhalb eines Entwurfs nur einmal vorkommen.
4. Strategie-ID und Akteurstyp muessen zum Katalog passen.
5. Parametrisierte Strategien muessen genau ihr vorhandenes Parameterschema
   und alle dort belegten Felder liefern.
6. Parameterfelder bestehen aus exakt zwei Zahlen fuer die historischen,
   weiterhin unbenannten Sektorpositionen.
7. `Vrvn01` besitzt weiterhin keinen Strategieparameterblock.
8. Aktivierungsperiode, Laufgrenze und logische Zeit werden nur als positive
   Ganzzahlen validiert. Neue fachliche Wertebereiche oder Defaults entstehen
   nicht.

## Lieferumfang

- Entwurfsschema `ims.strategy-assignment-draft.v1`;
- Validierungsbericht `ims.strategy-assignment-draft-validation.v1`;
- rein lesender Formatvertrag unter
  `GET /api/strategies/assignment-draft-contract`;
- zustandslose Pruefung unter
  `POST /api/strategies/assignment-draft-validation`;
- synthetischer, ausschliesslich struktureller Beispielentwurf;
- positive und negative Modul-, API- und Dokumentationstests.

## Geschlossene Grenzen

- keine Speicherung und kein Metadatenbankzugriff;
- keine Workbench-Bearbeitung;
- keine Gruppen- oder sektorweise Zuordnung;
- keine geplanten Strategiewechsel;
- keine Uebersetzung in vorhandene Regel-Snapshots;
- kein Runner- oder Simulationsstart;
- keine historische Vollgleichheitsbehauptung.

## Validierung

- Schema- und Vertragsversionen strikt pruefen;
- Zielgrenzen, doppelte Akteure und Akteur-/Strategiefehler pruefen;
- Parameterfelder, Zweiervektoren, Zahltypen und vorhandene Loadergrenzen
  pruefen;
- fehlende Parameter fuer parametrisierte Strategien und unzulaessige
  Parameter fuer `Vrvn01` abweisen;
- API-Berichte auf explizit geschlossene Schreib-, Snapshot- und
  Ausfuehrungsgrenzen testen;
- vollstaendige Python-Regression ohne Simulationsstart ausfuehren.

## Anschlussplanung

PR109 kann einen gueltigen Entwurf in der Workbench erfassbar und pruefbar
machen, weiterhin ohne Speicherung oder Ausfuehrung. Eine deterministische
Uebersetzung in bestehende Regel-Snapshots benoetigt danach einen eigenen PR
mit explizitem Mapping und eigenen Regressionstests.
