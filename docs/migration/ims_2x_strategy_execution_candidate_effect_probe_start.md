# PR131: Einperioden-Wirkungsprobe kontrolliert bedienen und nachweisen

Stand: 2026-09-09

## Einordnung

PR130 stellt den fachlich bereits portierten Einperiodenpfad als fluechtige
Backend-Probe bereit. PR131 ergaenzt die Bedien- und Nachweisschicht: Eine
manuelle Freigabe aus der Workbench fuehrt den Kandidaten hoechstens einmal
aus, speichert das Ergebnis unveraenderlich und zeigt den Versuchsverlauf
read-only an.

## C-zu-Python-Mapping

| Historischer Bezug | Python-Ziel | Fachliche Entsprechung |
| --- | --- | --- |
| gemeinsame Periodenwirkung der Aktionen `Vrvu01` bis `Vrvu10` und `Vrvn01` bis `Vrvn06` in `IMS.E` | `ims.api.strategy_execution_candidate_effect_probe` | unveraenderter PR130-Aufruf des vorhandenen expliziten Einperioden-Runners auf isolierter Kopie |
| historisch manueller Programmstart | `ims.api.strategy_execution_candidate_effect_probe_start` | ausdrueckliche, auditierte Freigabe mit atomarer Idempotenzreservierung |
| unmittelbar sichtbare Zustandsaenderungen | gespeichertes PR130-Ergebnis und Workbench-Ergebnisansicht | nachvollziehbarer Vorher/Nachher-Nachweis ohne neue Regelableitung |

PR131 portiert keine Fachlogik aus dem C-Code. Die neue Komponente steuert
ausschliesslich Freigabe, genau-einmal-Aufruf, Ergebnisablage und Beobachtung.

## Persistenter Start

Der neue Start-Endpunkt akzeptiert exakt den PR130-Request. Kandidaten-ID und
erwarteter SHA-256-Digest werden vor dem atomaren Claim und innerhalb des
PR130-Pfads unmittelbar vor dem Runner erneut geprueft.

Ein `BEGIN IMMEDIATE` reserviert Kandidat und Idempotenzschluessel, bevor der
Runner aufgerufen wird. Damit gelten folgende Regeln:

- derselbe Schluessel und identische Freigabe liefern ein vorhandenes
  Ergebnis ohne zweiten Runneraufruf;
- derselbe Schluessel mit veraenderter Freigabe wird abgewiesen;
- parallele Starts desselben Kandidaten werden blockiert;
- je Kandidat wird hoechstens ein erfolgreiches Ergebnis gespeichert;
- nach einem fehlgeschlagenen Versuch ist nur eine neue manuelle Freigabe mit
  neuem Idempotenzschluessel zulaessig;
- es gibt keinen automatischen Retry und keinen Queue-Worker.

## SQLite-Nachweis

`strategy_execution_candidate_effect_probe_attempts` speichert Freigabedaten,
Start- und Abschlusszeit, Status, Fehler und die Information, ob der Runner
erreicht wurde.

`strategy_execution_candidate_effect_probe_results` speichert genau ein
Ergebnis je Kandidat. Der Ergebnisinhalt erhaelt einen eigenen SHA-256-Digest,
der bei jedem read-only Zugriff erneut geprueft wird. Ein Ergebnis wird nicht
aktualisiert oder ueberschrieben.

Die Strategie-Tabellen sind bewusst von `run_control_execution_attempts` und
`run_control_execution_results` getrennt. Diese aelteren Tabellen gehoeren
zum Fixture-Adapter mit Queue-, Run- und Szenario-IDs; eine Gleichsetzung mit
dem kanonischen Strategie-Kandidaten waere fachlich und technisch falsch.

## API

- `GET /api/run-control/strategy-candidate-effect-probe-start-contract`;
- `POST /api/run-control/strategy-candidate-effect-probe-start`;
- `GET /api/run-control/strategy-candidate-effect-probe-result/{candidate_id}`;
- `GET /api/run-control/strategy-candidate-effect-probe-history/{candidate_id}`.

Der erste erfolgreiche Start antwortet mit `201`, eine idempotente
Wiederholung mit `200`. Unbekannte Kandidaten ergeben `404`; Integritaets-,
Idempotenz- und Laufkonflikte ergeben `409`. Reine Ergebnis- und
Verlaufsabfragen schreiben nichts und fuehren nichts aus.

## Workbench

Die Kandidatenansicht bietet Freigabeperson, Grund, eine ausdrueckliche
Einperiodenbestaetigung und den Startbefehl. Nach dem Start zeigt sie:

- lokale Periode und Zustandssaenderung;
- Anzahl der VU- und VN-Regelanwendungen;
- IDs geaenderter VU und VN;
- Anzahl nur im Speicher gebildeter Tabellen und Zeilen;
- Speicherzeit und Ergebnisdigest;
- alle Startversuche mit Freigabe, Status, Zeitpunkten und Fehlertext.

Nach gespeichertem Ergebnis wird der Start fuer diesen Kandidaten deaktiviert.
Der Server erzwingt dieselbe Grenze unabhaengig von der Browserdarstellung.

## Grenzen

- keine neue oder geaenderte VU-/VN-Fachlogik;
- genau eine Periode und eine isolierte Kandidatenkopie;
- keine freien Kandidaten-, Datenbank-, Fixture- oder Ausgabepfade;
- kein Carryover, Scheduler oder Mehrperiodenlauf;
- keine Ausgabedateien und kein Legacy-Vergleich;
- keine automatische Wiederholung;
- keine historische RNG- oder Vollgleichheitsbehauptung;
- `incomming/` bleibt unversioniert.

## Naechster Schritt

PR132 prueft den bedienbaren Pfad mit Browser-Smokes auf Desktop und schmalem
Viewport, vervollstaendigt die Fehlerdarstellung und uebernimmt die belegten
Bildschirmablaeufe in das Benutzerhandbuch.
