# PR113: Snapshot-Kontexte lokal in der Workbench pruefen

Stand: 2026-09-07

## Ziel

PR113 macht den in PR112 versionierten Einperiodenkontext als sechsten Tab
`Kontext` im Strategiearbeitsbereich bedienbar. Ein Anwender kann fuer einen
gueltigen Strategieentwurf und dessen vollstaendige Snapshot-Bauplaene die
noch offenen Laufzeitwerte lokal erfassen und serverseitig pruefen.

Die Workbench speichert oder verwendet diese Werte nicht. Sie erzeugt keine
Snapshots und startet weder Regelkern noch Simulation.

## Historische und technische Grundlage

- `IMSDATA.C`: `ACTION.st` und die explizite VU-/VN-Regelbindung;
- `IMS.E`: periodische Aufrufe von `Vrvu01` bis `Vrvu10` und `Vrvn01` bis
  `Vrvn06` mit Ziehungen, Zins, Schock-, Markt- und Vorperiodenzustaenden;
- PR108/109: lokaler, serverseitig validierter Strategieentwurf;
- PR110/111: vollstaendige Bauplanvorschau mit exakt offenen Snapshotfeldern;
- PR112: versionierter Kontextvertrag und zustandslose Validierungs-API.

## Bedienpfad

1. Strategieentwurf im Tab `Entwurf` erfolgreich pruefen.
2. Im Tab `Bauplaene` die vollstaendige Vorschau anzeigen.
3. Im Tab `Kontext` den lokalen Kontext ausdruecklich anlegen.
4. Eine positive IMS-Periode angeben.
5. Offene Werte je VU/VN und Herkunftsgruppe erfassen.
6. Nullable Felder nur bewusst als `null` offen markieren.
7. Den gesamten Entwurf und Kontext atomar serverseitig pruefen.

Aenderungen am Strategieentwurf oder eine erneute Bauplanuebersetzung
verwerfen den lokalen Kontext. Ein Browser-Neuladen verwirft ihn ebenfalls.

## Darstellung

Die 18 Feldarten werden nach den PR112-Quellen gruppiert:

- Ziehungen;
- Zins und Periodenkosten;
- Schockstatus;
- Strategieschwellen;
- Marktwerte;
- Vorperiodenwerte.

Boolesche Werte verwenden eine explizite Auswahl ohne Vorbelegung. Zahlen
verwenden numerische Felder. Listen und verschachtelte Objekte werden als
JSON erfasst, weil ihre regelabhaengige Fachsemantik in PR112 bewusst offen
blieb. Ungueltiges JSON wird nicht still korrigiert, sondern durch den Server
als falsche Wertform gemeldet. Fehler erscheinen am betroffenen Feld und im
vollstaendigen Pruefbericht.

## Lieferumfang

- sechster Strategie-Tab `Kontext`;
- Laden des read-only PR112-Kontextvertrags;
- lokale, leere Kontexteintraege aus den offenen Bauplanfeldern;
- Eingaben fuer Periode und die sechs Herkunftsgruppen;
- explizite `null`-Markierung ausschliesslich fuer nullable Felder;
- POST gegen
  `/api/strategies/assignment-snapshot-context-validation`;
- kompakter Status, feldbezogene Fehler und atomarer Gesamtbericht;
- responsive Desktop- und kleine Ansicht;
- Frontend-, Dokumentations-, Build- und Browsertests.

## Geschlossene Grenzen

- keine vorbelegten Beispiel-, Default- oder abgeleiteten Laufzeitwerte;
- keine Datei-, `localStorage`-, Session- oder Datenbankspeicherung;
- keine Erzeugung von Zufallsziehungen;
- keine automatische Auswahl von Markt- oder Vorperiodenquellen;
- keine Verwendung der gelieferten Kontextwerte;
- kein Aufruf eines Snapshot-Loaders;
- keine Snapshot-Materialisierung;
- keine Run-Control-, Runner- oder Simulationskopplung;
- keine historische RNG- oder Vollgleichheitsbehauptung.

## Validierung

- Kontext erst nach gueltigem Entwurf und vollstaendigen Bauplaenen anlegen;
- alle offenen Felder exakt und ohne zusaetzliche UI-Felder uebernehmen;
- fehlende, nullable und formal ungueltige Werte sichtbar unterscheiden;
- API- und Vertragsfehler ohne Teilfreigabe anzeigen;
- Entwurfsaenderungen und erneute Uebersetzung verwerfen den Kontext;
- lange JSON-Werte und Fehlermeldungen ohne Layoutueberlauf darstellen;
- Desktop- und kleine Ansicht visuell pruefen;
- vollstaendige Regression und Windows-Release-Gate ohne Simulationsstart.

## Anschlussplanung

PR114 kann einen versionierten, deterministischen Materialisierungsvertrag
fuer vollstaendig gueltige Entwurfs- und Kontextpaare vorbereiten. Vor der
eigentlichen Materialisierung muss insbesondere die fachliche Struktur der
regelabhaengigen VN-Ziehungs-, Markt- und Historienwerte explizit belegt
werden. Run-Control, Runner und Simulation bleiben weitere, getrennte
Freigaben.
