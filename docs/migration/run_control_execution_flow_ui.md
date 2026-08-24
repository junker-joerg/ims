# Run-Control-Ausfuehrungsflow in der Workbench

## Zweck

PR 46 zeigt den geplanten Run-Control-Ablauf in der Workbench als reine
Statussicht:

`Preflight -> explizite Freigabe -> Ausfuehren`

Der Schnitt verbindet vorhandene UI-Signale aus Preflight, Queue-Aktionsplan,
Adapter-Startvertrag und Ergebnisstatus. Er startet keinen Adapter, erzeugt
keinen Queue-Worker, schreibt keine Metadaten und startet keine Simulation.

## Ursprung

Der UI-Schritt baut auf diesen vorhandenen Bausteinen auf:

- `GET /api/run-control/preflight/{run_id}` fuer den lokalen Preflight;
- `GET /api/run-control/queue/action-plan` fuer den naechsten sicheren
  Queue-Schritt;
- `GET /api/run-control/adapter-start-contract` fuer den hart gegateten
  Startvertrag;
- Queue-Status `result_persisted` und Aktionshinweis
  `inspect_persisted_result` aus dem lokalen Ergebnisstore.

## Umsetzung

Die Workbench laedt den Adapter-Startvertrag beim Start der Metadatenansicht
und zeigt eine neue Karte `Run-Control-Ausfuehrungsflow`.

Die Karte zeigt:

- den dreistufigen Ablauf `Preflight`, `Explizite Freigabe`, `Ausfuehren`;
- den geplanten Startendpunkt nur als Vertragsfeld;
- ob Start-Payload, Payload-Validierung, Adapterstart, UI-Start und
  Queue-Worker aktiv oder gesperrt sind;
- ob fuer den ausgewaehlten Queue-Eintrag bereits `result_persisted` vorliegt;
- den naechsten Queue-Aktionsschritt, einschliesslich
  `inspect_persisted_result`.

## Grenzen

- Kein `POST /api/run-control/adapter-start`.
- Kein UI-Startbutton.
- Kein Browser-Upload und keine freie Pfadauswahl.
- Kein Queue-Worker.
- Kein Adapterstart.
- Keine Simulation.
- Keine neue Fachlogik.
- Keine historische Vollgleichheitsbehauptung.

## Validierung

Die Frontend-Quelltests pruefen, dass die neue Karte, der Startvertrag und
`inspect_persisted_result` sichtbar sind. Der Workbench-Smoke prueft den
read-only Startvertrag zusammen mit den bestehenden API-Grenzen.

Nach PR 47 ist die read-only Ergebnisanzeige umgesetzt. Es bleiben grob
0 bis 2 reviewbare PRs bis zu einer benutzbaren, kontrollierten
Demo-Simulation: Demo-Smoke/Doku und optional Packaging-/Startskript-
Anpassungen.

## Erweiterung in PR 64

PR 64 erweitert die bisherige Statussicht um den kontrollierten UI-Startpfad.
Die Karte verlangt `Freigegeben von`, `Begruendung` und eine explizite
Bestaetigung. Erst `POST /api/run-control/adapter-release-check` erzeugt und
prueft den vollstaendigen Payload mit UTC-Zeitpunkt und stabilem
`idempotency_key`. Nur ein positives Ergebnis schaltet den getrennten Button
`Adapter starten` frei; dieser sendet denselben Payload unveraendert an
`POST /api/run-control/adapter-start`.

Die UI bietet die Freigabe nur fuer Queue-Status `validated` an. Nach Erfolg
oder Fehler werden Queue, Detail, Aktionsplan, Kernbruecke und Ergebnisanzeige
neu geladen. `starting`, `failed` und `result_persisted` werden sichtbar
eingeordnet. Es gibt keinen automatischen Start und keine automatische
Wiederholung.

Fixture- und Ausgabepfade bleiben ausserhalb des Browsers. Das Profil
`vu14-calculated-diagnostic` ist fest serverseitig bekannt; VU-/VN-Carryover
bleibt im UI-Payload `false`. Queue-Worker, Browser-Upload, Simulation,
automatische historische Regelwahl und historische Vollgleichheitsbehauptung
bleiben ausgeschlossen.
