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
  anbinden, noch ohne UI-Button, Queue-Worker oder Adapterstart (dieser
  Schnitt).
- PR 46: UI-Flow `Preflight -> explizite Freigabe -> Ausfuehren` anzeigen,
  weiterhin ohne UI-Startbutton, Queue-Worker oder Adapterstart (dieser
  Schnitt).
- PR 47: Ergebnisanzeige fuer freigegebene Adapterlaeufe anbinden, weiterhin
  ohne Upload, UI-Startbutton, Queue-Worker oder Adapterstart (dieser
  Schnitt).
- PR 48: Demo-Smoke und Doku fuer den benutzbaren Ablauf (dieser Schnitt).
- PR 49: Packaging-/Startskript-Haertung fuer lokale Auslieferung (dieser
  Schnitt).

Damit bleiben nach PR 49 0 weitere Pflicht-PRs bis zu einer startbar
verpackten kontrollierten Demo. Diese Zahl ist kein historischer
Vollgleichheitsnachweis.

## Umsetzung in PR 45

PR 45 setzt die lokale Persistenzgrenze als expliziten SQLite-Schritt um:

- `python_port/ims/api/run_control_execution_result_store.py` legt
  `run_control_execution_results` an und speichert nur vorab validierte
  `controlled_execution_adapter`-Resultate;
- `--explicit-persistence-release` ist fuer den Schreibschritt Pflicht;
- Queue-Eintraege muessen `validated` sein und behalten
  `execution_performed = false`;
- nach erfolgreicher Persistenz wird der Queue-Status `result_persisted`;
- der Aktionsplan zeigt fuer diesen Status nur `inspect_persisted_result`;
- `adapter_started = false`, `execution_performed = false` und
  `simulation_performed = false` bleiben im Persistenzresultat.

## Umsetzung in PR 46

Run-Control-Ausfuehrungsflow in der Workbench anzeigen.

PR 46 zeigt den geplanten Ausfuehrungsflow in der Workbench als reine
Statussicht:

- `GET /api/run-control/adapter-start-contract` wird vom Frontend geladen;
- die neue Karte `Run-Control-Ausfuehrungsflow` zeigt
  `Preflight -> explizite Freigabe -> Ausfuehren`;
- der Status `result_persisted` wird als `Ergebnis pruefen` eingeordnet;
- der Aktionsplan-Schritt `inspect_persisted_result` bleibt sichtbar;
- Start-Payload, Startvalidierung, Adapterstart, UI-Start und Queue-Worker
  bleiben gesperrt.

Der vorgeschlagene naechste groessere Schritt ist PR 47:
Ergebnisanzeige fuer freigegebene Adapterlaeufe anbinden, weiterhin ohne
historische Vollgleichheitsbehauptung.

## Umsetzung in PR 47

PR 47 bindet die Ergebnisanzeige fuer persistierte Adapterresultate rein
lesend an:

- `GET /api/run-control/execution-result/{queue_id}` liest nur vorhandene
  Datensaetze aus `run_control_execution_results`;
- fehlende Ergebnisse liefern eine stabile read-only Fehlerform ohne Schreib-
  oder Startwirkung;
- die neue Workbench-Karte `Run-Control-Ergebnisanzeige` zeigt Queue, Run,
  Szenario, Resultatstatus, Summary-Modus, Persistenzzeitpunkt und Grenzflags;
- Upload, UI-Startbutton, Queue-Worker, Adapterstart, Simulation und
  historische Vollgleichheitsbehauptung bleiben gesperrt.

Der nach PR 47 vorgeschlagene naechste groessere Schritt war PR 48:
Demo-Smoke und Doku fuer den benutzbaren Ablauf, weiterhin ohne historische
Vollgleichheitsbehauptung.

## Umsetzung in PR 48

PR 48 sichert den benutzbaren lokalen Demo-Ablauf als API-/Doku-Smoke ab:

- `tests/test_workbench_demo_smoke.py` prueft Dry-Run, Queue-Vormerkung,
  Aktionsplan, hart gesperrten Adapter-Startvertrag, read-only
  Ergebnisanzeige, Run-Control-Kernblick-Bruecke, Carryover-Probe-Vertrag und
  Adapter-Resultat-Vertrag;
- `docs/migration/workbench_demo_checklist.md` beschreibt die UI-Reihenfolge,
  die erwarteten Demo-Signale und die Grenzen fuer Browser-/Screenshot-Smoke;
- `execution_performed = false`, `api_starts_adapter = false`,
  `ui_start_enabled = false`, `queue_worker_enabled = false` und
  `simulation_performed = false` bleiben die belegten Grenzen.

## Umsetzung in PR 49

PR 49 haertet die lokale Auslieferungsgrenze:

- Repo- und portable Start-/Check-Skripte setzen ueberschreibbare Defaults fuer
  `IMS_FRONTEND_DIST`, `IMS_METADATA_DB`, `IMS_WORKBENCH_HOST` und
  `IMS_WORKBENCH_PORT`;
- der portable Staging-Smoke prueft diese Startskriptgrenzen rein lesend;
- es gibt weiterhin keinen Adapterstart, keinen Queue-Worker, keine Simulation
  und keine historische Vollgleichheitsbehauptung.

PR 50 schreibt die Produktionsreife-Roadmap fest und waehlt wieder einen
schmalen fachlichen Validierungsslice: Vrvn04 / `search_history` als Plan fuer
PR 51. PR 51 setzt diesen sechsten fachlichen
VN-`search_history`-/Vrvn04-Regressionstest um. Der vorgeschlagene naechste
groessere Umsetzungsschritt war PR 52: Vrvn03 / `preference` als siebten
fachlichen Slice umsetzen. PR 52 ist erledigt; der naechste fachliche Schritt
war PR 53: Vrvn02 / `random` mit expliziten Draws und Seed-/Draw-Grenze. PR 53
ist erledigt; der naechste fachliche Schritt war PR 54:
VN-Schaden-/Settlement-Pfad aus `Vrvn01` bis `Vrvn03` breiter pruefen. PR 54 ist
erledigt; PR 55 prueft danach `Vrvu01` / Zufall I mit zwei expliziten
Draw-Vektoren und kontrollierter Carryover-Opt-in-Grenze (erledigt). Der
naechste Schritt ist PR 56: den Produktions-Altdatenkorpus als Plan fixieren.
PR 56 ist mit 19 Kernreferenzen, 6.300 Vergleichszeilen und einem getrennten
ZINS000-Aufnahmeentscheid erledigt. PR 57 hat ausschliesslich `IMSVU014.DAT`
und `IMSVUSK1.DAT` als separate historische Referenzschicht versioniert. PR 58
hat den berechneten Mehrperiodenvergleich fuer den unveraenderten Kernkorpus
als strikten externen Exporttabellenvertrag vorbereitet. PR 59 hat den
read-only Abweichungsbericht angebunden und weist 15 fehlende Kernexporte
blockierend aus. PR 60 hat einen ersten schmalen,
tatsaechlich berechneten VU14-Aggregat-/Export-Slice angebunden. PR 61 hat die
technische Level-IV-Selektorgrenze `all` gegen `SK1` eng kanonisiert. PR 62
hat den kontrollierten read-only Freigabecheck mit Auditfeldern, validierter
Queue, gruenem Preflight und serverseitigem Fixture-Profil umgesetzt. PR 63
schafft als naechstes die atomare Backend-Start-/Status- und Ergebnisgrenze
gegen Doppelstarts, weiterhin ohne UI-Startbutton oder freien Browser-Upload.

## Umsetzung in PR 62

- `POST /api/run-control/adapter-release-check` validiert nur die Freigabereife;
- Pflicht-Auditfelder sind `released_by`, `released_at` und `release_reason`;
- `release_profile_id` waehlt nur ein serverseitig bekanntes lokales Profil;
- Browser-Fixture- und Outputpfade werden als unbekannte Felder verworfen;
- Queue-Status `validated`, passende IDs und ein gruener Preflight sind Pflicht;
- `adapter_start_allowed = false`, `adapter_started = false`,
  `writes_performed = false`, `execution_performed = false` und
  `simulation_performed = false` bleiben erhalten;
- `POST /api/run-control/adapter-start` bleibt nicht vorhanden.

## Validierung dieses Planstands

Dieser Plan wird durch Dokumentationstests abgesichert. Sie pruefen, dass die
Freigabekette, die verbotenen Pfade, die PR-Roadmap und die Grenzen ohne
Simulation, UI-Startbutton und Queue-Worker benannt bleiben.
