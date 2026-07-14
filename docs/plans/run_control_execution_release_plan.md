# Plan: Run-Control-Ausfuehrungsfreigabe

## Zweck

Dieser PR 43 bereitet den naechsten groesseren Schritt zur benutzbaren,
kontrollierten Demo-Simulation vor. Er plant die explizite
Ausfuehrungsfreigabe zwischen Run-Control, Queue, lokalem
`controlled_execution_adapter` und spaeterer Ergebnisanzeige.

Der Schnitt ist nur ein Plan- und Dokumentations-PR. Er fuehrt keinen neuen
HTTP-Endpunkt ein, startet keinen Adapter, baut keinen UI-Startbutton, startet
keine Simulation, schreibt keine Queue-Ausfuehrung und behauptet keine
historische Vollgleichheit.

## Ausgangsstand

Vorhanden sind:

- lokaler Adapter `python_port/ims/api/controlled_execution_adapter.py` mit
  explizitem `--explicit-execution-release`;
- read-only Adapter-Vertrag
  `python_port/ims/api/controlled_execution_adapter_contract.py`;
- read-only Adapter-Resultat-Vertrag und API-Anzeigevertrag;
- Run-Control-Dry-Run, Queue-Vormerkung, Aktionsplan, Preflight und
  Kernblick-Bruecke;
- fuenf fachliche Regressionstests fuer VN-/VU-Zwischenzustaende.

Noch nicht vorhanden ist ein Run-Control-Pfad, der aus einer validierten Queue
und einer expliziten lokalen Freigabe heraus den Adapter kontrolliert startet.

## Entscheidung

Der naechste reviewbare Schritt bleibt eine harte Freigabegrenze:

1. Run-Control darf eine Ausfuehrung nur fuer bereits validierte Queue-Eintraege
   planen.
2. Die spaetere API darf den Adapter nur starten, wenn eine explizite
   Ausfuehrungsfreigabe uebergeben wird.
3. Die UI bekommt erst nach einem API-Vertrag und nach Persistenz-/Statusgrenzen
   einen sichtbaren Startflow.
4. Adapterresultate bleiben `explicit_multi_period_execution_summary` und kein
   fachlicher Vollgleichheitsnachweis.

## Geplante Freigabekette

| Schritt | Zweck | Status in PR 43 |
| --- | --- | --- |
| Dry-Run | Request und Preflight pruefen | vorhanden, bleibt ohne Ausfuehrung |
| Queue | validierten Request vormerken | vorhanden, bleibt ohne Worker |
| Action-Plan | naechsten sicheren Schritt anzeigen | vorhanden, bleibt lesend |
| Execution release | lokale Freigabe als separates DTO/API planen | nur geplant |
| Adapter start | kontrollierten Adapter hart gegated starten | nicht umgesetzt |
| Result persistence | Ergebnisstatus und Summary ablegen | nicht umgesetzt |
| UI flow | Preflight -> Freigabe -> Ausfuehren anzeigen | nicht umgesetzt |

## Preconditions fuer PR 44

Ein spaeterer API-Startpfad darf erst entstehen, wenn der Vertrag mindestens
folgende Bedingungen pruefbar macht:

- Queue-Eintrag existiert und gehoert zu einem bekannten Run/Szenario.
- Queue-Status ist `validated` oder ein spaeter explizit benannter
  Freigabestatus.
- Preflight ist gruen oder die blockierenden Issues sind explizit aufgeloest.
- `explicit_execution_release = true` wird im Request benoetigt.
- Fixture-Pfad oder Planfixture stammt aus einer bekannten, lokalen
  Metadatenquelle, nicht aus Browser-Upload.
- Output-Pfad bleibt verboten; Ergebnisablage erfolgt nur ueber den geplanten
  Resultat-/Statuspfad.
- `api_starts_adapter` darf nur im freigegebenen Startpfad `true` werden.

## Umsetzung in PR 44

PR 44 setzt diese Grenze als read-only Startvertrag um:

- `python_port/ims/api/run_control_adapter_start_contract.py` beschreibt die
  Request-Felder, Preconditions und verbotenen Grenzen;
- `GET /api/run-control/adapter-start-contract` liefert diesen Vertrag lesend
  aus;
- `planned_start_endpoint = "/api/run-control/adapter-start"` bleibt nur ein
  benannter Zukunftspfad;
- `api_accepts_start_payload = false`, `api_validates_start_payload = false`
  und `api_starts_adapter = false`;
- `ui_start_enabled = false`, `queue_worker_enabled = false`,
  `writes_enabled = false` und `execution_enabled = false`;
- der negative Test prueft, dass `POST /api/run-control/adapter-start` in
  diesem Schnitt nicht vorhanden ist.

## Verbotene Pfade

In PR 43, PR 44 und bis zur Umsetzung der naechsten Vertraege bleiben
verboten:

- kein sofortiger UI-Startbutton;
- kein Queue-Worker;
- kein Scheduler-Start;
- kein Browser-Upload;
- keine freie Fixture- oder Output-Pfadauswahl im Browser;
- keine automatische historische Regelwahl;
- keine neue Fachlogik;
- keine Simulation aus Preflight, Dry-Run, Queue-Aktionsplan, Kernblick-Bruecke
  oder Adapter-Resultat-Vertrag;
- keine historische Vollgleichheitsbehauptung.

## PR-Roadmap bis zur benutzbaren Demo-Simulation

- PR 43: diesen Ausfuehrungsfreigabeplan dokumentieren und testen.
- PR 44: API-Startvertrag fuer den kontrollierten Adapter hart gegated
  vorbereiten, noch ohne UI-Button oder POST-Startendpunkt (dieser Schnitt).
- PR 45: Queue-/Status-/Resultat-Persistenz fuer freigegebene Ausfuehrung
  anbinden.
- PR 46: UI-Flow `Preflight -> explizite Freigabe -> Ausfuehren` anzeigen.
- PR 47: Ergebnisanzeige fuer freigegebene Adapterlaeufe anbinden.
- PR 48: Demo-Smoke und Doku fuer den benutzbaren Ablauf.
- PR 49 optional: Packaging-/Startskript-Update fuer lokale Auslieferung.

Damit bleiben nach PR 44 grob 3 bis 5 reviewbare PRs bis zu einer benutzbaren
kontrollierten Demo-Simulation. Diese Zahl ist kein historischer
Vollgleichheitsnachweis.

## Validierung dieses Planstands

Dieser Plan wird durch Dokumentationstests abgesichert. Sie pruefen, dass die
Freigabekette, die verbotenen Pfade, die PR-Roadmap und die Grenzen ohne
Simulation, UI-Startbutton und Queue-Worker benannt bleiben.
