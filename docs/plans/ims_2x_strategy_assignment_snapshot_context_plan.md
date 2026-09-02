# PR112: Expliziten Snapshot-Kontextvertrag validieren

Stand: 2026-09-02

## Ziel

PR112 definiert einen versionierten Einperiodenkontext fuer die in PR110
offen gebliebenen Felder der vorhandenen VU-/VN-Regel-Snapshottypen. Ein
Kontext wird gemeinsam mit einem Strategieentwurf rein im Speicher geprueft.
Der Validator verwendet die Werte nicht und erzeugt keinen Snapshot.

## Historische und technische Grundlage

- `IMSDATA.C`: `ACTION.st` sowie die gebundenen VU-/VN-Regeln;
- `IMS.E`: periodische Aufrufe von `Vrvu01` bis `Vrvu10` und `Vrvn01` bis
  `Vrvn06` mit Laufzeit-, Markt- und Vorperiodenzustaenden;
- PR108: versionierter Strategieentwurf;
- PR110: exakte `unresolved_snapshot_fields` der vorhandenen Snapshottypen;
- `vu_rules.py` und `vn_insurance_rules.py`: aktuelle Python-Snapshotformen.

## Vertragsentscheidungen

1. Der Kontext gilt fuer genau eine explizit benannte positive Periode.
2. Jeder Kontexteintrag referenziert Akteur, Ziel-ID und Strategie eines
   vollstaendig gueltigen Strategieentwurfs.
3. Die Feldmenge muss exakt den offenen Feldern des zugehoerigen
   PR110-Bauplans entsprechen. Unbekannte Felder werden abgewiesen.
4. Die 18 offenen Feldnamen werden den Quellen `draw`, `period_finance`,
   `shock`, `strategy_state`, `market_state` und `previous_period`
   zugeordnet.
5. Eindeutige bestehende Wertformen werden geprueft: Boolesche Werte,
   endliche Zahlen, Ganzzahlen sowie bekannte Zwei- und Vierervektoren.
6. Regelabhaengige VN-Ziehungen und verschachtelte Markt-/Historienobjekte
   werden nur als JSON-Struktur geprueft. Ihre Fachsemantik bleibt offen.
7. Ein ausdrueckliches `null` ist nur fuer nullable Snapshotfelder erlaubt
   und haelt den Wert als offen sichtbar. Es wird durch keinen Default ersetzt.
8. Aktivierungsperiode, Laufgrenze und logische Zeit werden nicht still als
   Auswahlregel fuer den Kontext interpretiert.

## Lieferumfang

- Vertrag `ims.strategy-assignment-snapshot-context.v1`;
- Validierungsbericht
  `ims.strategy-assignment-snapshot-context-validation.v1`;
- Feldkatalog und Abdeckungspruefung fuer alle 18 offenen Snapshotfelder;
- zustandslose Validierung eines Anfragepaars aus `draft` und `context`;
- GET-Endpunkt
  `/api/strategies/assignment-snapshot-context-contract`;
- POST-Endpunkt
  `/api/strategies/assignment-snapshot-context-validation`;
- synthetisches Kontextfixture sowie Modul-, API- und Dokumentationstests.

## Geschlossene Grenzen

- keine Erzeugung oder Ableitung von Zufallsziehungen;
- keine Auswahl von Szenario-, Markt- oder Vorperiodenquellen;
- keine Anwendung technischer Defaults;
- keine Verwendung der gelieferten Kontextwerte;
- kein Aufruf eines Snapshot-Loaders;
- keine Snapshot-Materialisierung, Speicherung oder Ausfuehrung;
- kein Simulationsstart;
- keine historische RNG- oder Vollgleichheitsbehauptung.

## Validierung

- Feldkatalog gegen die Vereinigungsmenge aller offenen PR110-Felder pruefen;
- Entwurf vor jeder Kontextpruefung atomar validieren und uebersetzen;
- Kontextziele, Strategien und Feldmengen exakt gegen die Bauplaene pruefen;
- eindeutige Wertformen ohne Normalisierung oder Default pruefen;
- nullable Werte als weiterhin offen berichten;
- ungueltige Entwuerfe und Kontexte ohne Teilfreigabe abweisen;
- beide API-Endpunkte auf Schreib- und Ausfuehrungsfreiheit pruefen;
- vollstaendige Regression ohne Simulationsstart ausfuehren.

## Anschlussplanung

PR113 kann den Kontextvertrag und seine Validierung in der Workbench
zunaechst als lokalen Entwurfspfad anbieten. Eine spaetere Materialisierung
darf erst in einem eigenen PR erfolgen und muss zuvor insbesondere die
regelabhaengige Semantik verschachtelter VN-Werte klaeren. Runner und
Simulation bleiben davon getrennte Freigaben.
