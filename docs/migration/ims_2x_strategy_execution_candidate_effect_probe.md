# PR130: Strategie-Kandidaten einmalig im Backend ausfuehren

Stand: 2026-09-09

## Einordnung

PR129 prueft die Identitaet und Speicherintegritaet eines gemeinsamen VU-/VN-
Ausfuehrungskandidaten, erteilt aber keine Starterlaubnis. PR130 ergaenzt eine
zweite ausdrueckliche Freigabe fuer genau eine fluechtige Backend-
Wirkungsprobe.

## C-zu-Python-Mapping

| Historischer Bezug | Python-Ziel | Fachliche Entsprechung |
| --- | --- | --- |
| gemeinsamer Periodenzustand fuer `Vrvu01` bis `Vrvu10` und `Vrvn01` bis `Vrvn06` in `IMS.E` | `ims.api.strategy_execution_candidate_effect_probe` | kontrolliertes Laden einer isolierten Kopie des bereits belegten gemeinsamen Zustands |
| historische Aktionsreihenfolge innerhalb einer Periode | `ims.engine.explicit_period_runner.run_loaded_explicit_period` | vorhandener expliziter VU-/VN-/Schaden-/Abrechnungsschritt fuer genau eine Periode |
| implizit sichtbare Zustandsaenderungen | fluechtige `state_before`- und `state_after`-Projektion | technische Beobachtung bereits portierter Wirkungen ohne neue Regelableitung |

## Umsetzung

Der PR130-Request verschachtelt den vollstaendigen PR129-Freigaberequest und
verlangt zusaetzlich `explicit_effect_probe_execution = true`. Nach dem
erneuten ID-, Digest- und Speichercheck wird aus dem Kandidaten ein tief
kopiertes Szenariomapping aufgebaut und als neuer `LoadedScenario`-
Objektgraph geladen.

Der Runner wird genau einmal mit `output_dir=None` aufgerufen. Danach werden
die erwartete Periode, die leere Liste geschriebener Dateien und die
Unveraendertheit des gespeicherten Kandidaten geprueft.

## Beobachtbares Ergebnis

Die Antwort zeigt Anwendungshaeufigkeiten, fokussierte VU-/VN-Zustaende vor
und nach der Periode, geaenderte Akteurs-IDs sowie rein im Speicher gebildete
Exporttabellen und -zeilen. Sie enthaelt weder freie Pfade noch einen
veraenderbaren Kandidatenpayload.

`execution_performed = true` bezeichnet ausschliesslich diesen expliziten
Einperiodenschritt. `simulation_performed` bleibt `false`, weil weder der
historische Scheduler noch ein Mehrperioden- oder Carryover-Ablauf gestartet
wird.

## Technische Kompatibilitaetsgrenze

Ein in PR126 kanonisierter VN-Schaden-Snapshot kann
`insurance_decisions: null` enthalten, wenn die Entscheidung erst aus der
VN-Regelanwendung derselben Periode eingesetzt wird. Fuer den erneuten Loader
wird nur dieses `null`-Feld aus der tiefen Kopie entfernt. Es werden keine
Entscheidungswerte erzeugt; Ablage und Digest bleiben unveraendert.

## API

- `GET /api/run-control/strategy-candidate-effect-probe-contract`
- `POST /api/run-control/strategy-candidate-effect-probe`

Ein unbekannter Kandidat ergibt `404`, ein Digest- oder Integritaetskonflikt
`409` und ein ungueltiger oder nicht ausdruecklich freigegebener Request
`400`. Ein Runnerfehler wird ohne Ergebnis- oder Freigabepersistenz als `409`
gemeldet.

## Grenzen und offene Punkte

- kein Workbench-Start und keine UI-Ergebnisansicht in PR130;
- keine dauerhafte Idempotenz, Versuchshistorie oder Ergebnisablage;
- keine Queue, kein Preflight und kein Fixture-Adapter;
- kein Carryover, Mehrperiodenlauf, Scheduler oder Export;
- kein Legacy-Vergleich und keine historische Gleichheitsbehauptung;
- PR131 schliesst Bedienung, Idempotenz und Verlauf fuer diesen eng benannten
  Einperiodenpfad an.
