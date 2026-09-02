# PR105: Strategiekatalog read-only in API und Workbench

Stand: 2026-09-02

## Ziel

PR105 macht den in PR104 versionierten Strategiekatalog ueber einen rein
lesenden API-Endpunkt und in der lokalen Workbench sichtbar. Der Anwender kann
die historischen VU- und VN-Regeln, ihre modernen Familien, Herkunft,
Parameterfaehigkeit und ihren Teststand ueberblicken.

Der Schritt fuehrt weder eine Strategieauswahl noch eine neue Fachregel ein.

## Grundlage

- `IMS.E`, Aktionen `Vrvu01` bis `Vrvu10` und `Vrvn01` bis `Vrvn06`;
- `Vdefmd6`, historische VU-/VN-Regelklassen;
- `ims.strategy-catalog.v1` aus PR104;
- vorhandene explizite Python-Regelkerne und ihre Testnachweise.

`Vrvu10` bleibt als historische Aktion ohne Zugehoerigkeit zu einer
Vdefmd6-Regelklasse sichtbar. Die acht modernen Familien bleiben als
`taxonomy_only` gekennzeichnete Navigations- und Analysehilfe.

## Umsetzung

1. `GET /api/strategies/catalog` liefert den unveraenderten Katalogvertrag.
2. Der Vertrag weist Auswahl, Parameterbearbeitung, Schreiben und Ausfuehrung
   ausdruecklich als gesperrt aus.
3. Die Workbench gruppiert sechzehn Regeln nach VU/VN und acht Familien.
4. Jede Regel zeigt Altaktion, Dissertationskapitel, Vdefmd6-Einordnung,
   Parameterfaehigkeit, vorhandene Parameterdimensionen und Teststatus.
5. Die Darstellung bleibt auf Desktop und Mobil lesbar und besitzt keine
   Eingabe-, Speicher- oder Ausfuehrungsaktion.

## Nicht in PR105

- keine Zuordnung einer Regel zu einem konkreten VU oder VN;
- keine Strategieauswahl und kein Strategiewechsel;
- keine Bearbeitung oder Erweiterung von Strategieparametern;
- kein Schreibpfad, kein Runner-Start und keine Simulation;
- keine historische Vollgleichheitsbehauptung.

## Validierung

- API-Vertrag, Version, Umfang und Sperrgrenzen testen;
- Schreibmethoden auf dem Katalogpfad als unzulaessig pruefen;
- Vrvu10- und Taxonomiegrenzen ueber den API-Pfad erhalten;
- Workbench-Quellvertrag und produktiven Frontend-Build pruefen;
- Desktop- und Mobilansicht auf Inhalt, Ueberlauf und fehlende Bedienelemente
  kontrollieren;
- vollstaendige Python-Regression ohne Simulationsstart ausfuehren.

## Anschluss und Restplanung

PR106 soll einen separaten, weiterhin rein beschreibenden
Strategiezuordnungs- und Parametrisierungsvertrag vorbereiten. Er soll klaeren,
welche Akteurs- oder Spartengruppe welche Katalogstrategie verwenden darf,
welche vorhandenen Parameter dazu gehoeren und welche Grenzen vor einer
spaeteren Bearbeitung gelten. Erst nach diesem Vertrag duerfen Schreib- oder
Ausfuehrungspfade in eigenen PRs geplant werden.
