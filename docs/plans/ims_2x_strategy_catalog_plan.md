# PR104: Versionierter Strategiekatalog und Taxonomie

Stand: 2026-09-02

## Ziel

PR104 fuehrt einen kleinen, versionierten und rein lesenden Vertrag fuer die
historischen VU- und VN-Strategien ein. Jede Regel erhaelt eine stabile ID,
einen Akteurstyp, ihre Altcode-Herkunft, die vorhandene Python-Implementierung,
ihre Parameterfaehigkeit und einen konservativen Teststatus.

Die Regeln werden zusaetzlich in moderne Familien gruppiert. Diese Taxonomie
soll spaeter Regelauswahl, Baseline-/Interventionsvergleich und
Ergebnisgliederung unterstuetzen. Sie aendert keine Regel und ersetzt die
historischen Regelklassen nicht.

## Historische Grundlage

- `IMS.E`, `Vrvu01` bis `Vrvu10`;
- `IMS.E`, `Vrvn01` bis `Vrvn06`;
- `Vdefmd6`, VU-Regelklassen `1/2`, `3-6` und `7-9`;
- `Vdefmd6`, VN-Regelklassen `1/2`, `3/4` und `5/6`.

`Vrvu10` ist historisch belegt, gehoert aber nicht zu den Vdefmd6-Gruppen.
Dieser Unterschied muss im Vertrag sichtbar bleiben.

## Umsetzung

1. Neues Zielpaket `ims.strategies` mit unveraenderlichen Katalogeintraegen.
2. Acht moderne Familien als ausdruecklich reine Taxonomie.
3. Sechzehn historische Regeln mit stabilen IDs und C-/Python-Ankern.
4. Serialisierbares read-only Payload fuer den spaeteren Anzeigeweg.
5. Integritaetspruefung fuer IDs, Familien, Parameter- und Testangaben.

## Nicht in PR104

- keine Strategieauswahl in API oder UI;
- keine Aenderung von VU-/VN-Zuordnungen;
- keine neue Parametrisierung oder Fachregel;
- kein Runner- oder Simulationsstart;
- keine historische Vollgleichheitsbehauptung.

## Validierung

- exakte Vdefmd6-Regelklassen und Vrvu10-Ausnahme pruefen;
- alle sechzehn Aktionen in `IMS.E` nachweisen;
- alle referenzierten Python-Einstiegspunkte und Parameterschemata importieren;
- vorhandene Testdateien fuer jeden Eintrag nachweisen;
- serialisierbaren Vertrag und negative Integritaetsfaelle testen.

## Risiken und offene Punkte

Die moderne Familienbildung ist eine Navigations- und Analysehilfe. Eine
spaetere parametrisierbare Strategie darf erst dann als fachlich neu gelten,
wenn Wirkungskanal, Parametergrenzen und Regressionstests in einem eigenen PR
belegt sind. Insbesondere wird die nicht parametrisierte Vrvn01-Portierung in
PR104 nur als solche ausgewiesen.

## Anschluss

PR105 kann den Katalog ueber eine read-only API und eine kompakte
Workbench-Ansicht sichtbar machen. Er darf noch keine Regelzuordnung speichern
und keinen Lauf starten.
