# PR125: Gemeinsamen Kandidateneingang atomar validieren

Stand: 2026-09-08

## Ziel

PR125 fuehrt einen versionierten, zustandslosen Validator fuer die gemeinsam
benoetigten Quellen eines Einperioden-Ausfuehrungskandidaten ein. Der
Validator prueft Entwurf, Kontext, VU-Eingabepolicy, VU-Zustandsbeleg,
Szenarioprofil-Referenz und VN-Prozesseingang als eine atomare Einheit.

Ein gueltiger Bericht erzeugt noch keinen Kandidaten. Szenarioprofil,
Snapshotlisten und Digest werden nicht geladen oder materialisiert.

## Historische und heutige Grundlage

- `IMS.E`, Aktionen `Vrvu01` bis `Vrvu10` und `Vrvn01` bis `Vrvn06`:
  bereits dokumentierte Herkunft der Strategie- und Snapshotfelder;
- PR115: regel- und periodenabhaengige VN-Kontextpruefung;
- PR119: explizite VU-Felder und gesperrte Loader-/Runner-Fallbacks;
- PR120: VU-Zustands- und Herkunftsabgleich;
- PR124: Pflichtabschnitte und kanonische `LoadedScenario`-Sammlungen des
  spaeteren Kandidaten;
- `ims.engine.vn_rule_runner`: bestehende Verbindung von
  `VNInsuranceRuleSnapshot` zu `VNDamageSettlementSnapshot`.

## Eingabeentscheidung

Der PR125-Eingang enthaelt genau einen Strategieentwurf und genau einen
Snapshotkontext. Die VU-Policyfelder werden intern mit diesen beiden Quellen
zum vorhandenen PR119-Eingang zusammengesetzt. Dadurch gibt es keine zweite
Entwurfs- oder Kontextkopie, die unbemerkt abweichen koennte.

Die Szenarioprofil-Referenz enthaelt nur stabile ID, Periode und erwartete
BAV-/VU-/VN-IDs. Freie Fixture- oder Dateipfade sind nicht Teil des Schemas.
PR125 prueft die Referenz und ihre erwartete Population, loest das Profil
aber noch nicht auf.

## VN-Prozessgrenze

Fuer den ersten gemeinsamen Kandidatenpfad muss jedes zugeordnete VN genau
einen Eintrag in `damage_settlement_snapshots` besitzen. Parameter,
Schwellenwerte, Vorvermoegen, Schockstatus sowie alle Schaden-Normalziehungen
liegen explizit und zweispartig vor.

`insurance_decisions` und `information_cost` gehoeren nicht zum
Prozesseingang. Sie sollen spaeter aus den serverseitig neu materialisierten
VN-Regeln stammen. Reine `settlement_snapshots` bleiben gesperrt, weil sie
diese vorbereiteten VN-Entscheidungen im vorhandenen Runner nicht anbinden.

## Atomare Prueffolge

1. Exakte PR125-Form und feste Policywerte pruefen.
2. Gemeinsamen VN-Kontext mit PR115 pruefen.
3. Gemeinsamen VU-Eingang mit PR119 pruefen.
4. VU-Zustandsbeleg mit PR120 pruefen.
5. Entwurfs-ID, Periode, Schockstatus und erwartete Population quer abgleichen.
6. VN-Prozessform, explizite Ziehungen, Zielabdeckung und Schockstatus pruefen.
7. Nur bei vollstaendig fehlerfreiem Eingang `valid = true` melden.

Alle Fehlerpfade liefern `partial_candidate_returned = false`.

## API

- `GET /api/strategies/execution-candidate-validation-contract` beschreibt
  die Eingabe und die geschlossenen Grenzen.
- `POST /api/strategies/execution-candidate-validation` prueft genau einen
  Eingang in-memory.
- Andere Methoden sind nicht zugelassen.

## Schutzgrenzen

- keine neue oder geaenderte VU-/VN-Fachregel;
- keine Snapshotloader und keine Snapshot-Materialisierung;
- keine Szenarioprofil-Aufloesung;
- kein Kandidatenbau und keine Digestberechnung;
- keine Speicherung, Run-Control-, Runner- oder UI-Kopplung;
- kein Carryover, keine Ausgabedateien und kein Legacy-Vergleich;
- keine Simulation und keine historische RNG- oder Vollgleichheitsbehauptung;
- `incomming/` bleibt unversioniert.

Die bestehende PR115-Pruefung darf ihre verschachtelten Formloader weiterhin
kurzzeitig zur Strukturpruefung verwenden. Diese Ergebnisse werden nicht
behalten; Snapshotloader werden nicht aufgerufen.

## Validierung

- positiver deterministischer Gesamtfall mit je einer VU- und VN-Strategie;
- Querfehler fuer Entwurfs-ID, Periode, Profilpopulation und gemeinsamen
  Schockstatus;
- unvollstaendige und doppelte VN-Prozessziele;
- fehlende oder unvollstaendige explizite Schadenziehungen;
- Sperre fuer reine Settlement-Eingaenge und freie Felder;
- Grenztest gegen Snapshot-, Szenario- und Runneraufrufe;
- API-Methoden- und Invalid-JSON-Tests;
- Gesamtregression ohne Simulationsstart.

## Naechster Schritt

PR126 darf ausschliesslich einen vollstaendig gueltigen PR125-Eingang nehmen,
das referenzierte bekannte lokale Szenarioprofil serverseitig aufloesen, VN
und VU erneut materialisieren und daraus ein kanonisches `LoadedScenario`
samt stabilem Inhaltsdigest bauen. Runner, Speicherung und Run-Control bleiben
weiterhin gesperrt.
