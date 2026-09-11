# PR138: Run-Control-Freigabecheck fuer Periodenketten

Stand: 2026-09-11

## Einordnung

PR137 speichert eine kanonische Periodenkette nur nach ausdruecklicher
Freigabe unveraenderlich. PR138 verbindet diese Ablage mit einer eigenen
read-only Run-Control-Pruefgrenze. Der Pfad bestaetigt die gespeicherte
Identitaet, erzeugt aber weder Laufauftrag noch Ergebnis.

## C-zu-Python-Mapping

| Historischer Bezug | Python-Ziel | Bedeutung |
| --- | --- | --- |
| `IMSDATA.C:14`, `SIMLAENGE = 100` | `StrategyExecutionPeriodChainRunControlResult.period_chain` | gepruefte Zusammenfassung des lokalen Horizonts bis maximal 100 Perioden |
| Periodenschleife in `ESS.C:71-75` | `period_chain_horizon_verified` | erneute Bestaetigung der bei Periode 1 beginnenden lueckenlosen Kette |
| implizite globale Laufzustandsgrenze | `StrategyExecutionPeriodChainRunControlRequest` | explizite moderne ID-, Digest- und Auditgrenze vor einer spaeteren Ausfuehrung |
| kein historischer Freigabedigest | `check_strategy_execution_period_chain_run_control_release` | technische Integritaetspruefung ohne historische Gleichheitsbehauptung |

PR138 portiert keine neue C-Funktion und aendert keine VU-/VN-Regel.

## Umsetzung

`ims.api.strategy_execution_period_chain_run_control` definiert:

- `ims.strategy-execution-period-chain-run-control-contract.v1`;
- `ims.strategy-execution-period-chain-run-control-request.v1`;
- `ims.strategy-execution-period-chain-run-control-check.v1`;
- einen exakten Parser fuer Ketten-ID, erwarteten Volldigest und
  Auditangaben;
- einen atomaren read-only Freigabecheck;
- eine knappe Kettenzusammenfassung ohne eingebettete Kandidaten- oder
  Kettenpayloads.

Der Check leitet die erwartete Ketten-ID aus dem Digest ab. Danach verwendet
er `get_strategy_execution_period_chain`, wodurch der gespeicherte Inhalt,
seine relationale Metadaten und sein Digest erneut geprueft werden. Zuletzt
vergleicht er den vollstaendigen erwarteten Digest, bestaetigt den Horizont
und kontrolliert die weiterhin geschlossenen Ausfuehrungsgrenzen.

Die in der Kette festgeschriebenen Kandidatenreferenzen werden in PR138 nicht
erneut aufgeloest. Ihre Integritaet wurde beim serverseitigen Kettenbau und
vor der PR137-Speicherung geprueft. Eine spaetere Wirkungsprobe muss die
benoetigten Kandidaten vor der Ausfuehrung erneut kontrolliert laden.

## API

- `GET /api/run-control/strategy-period-chain-contract`
- `POST /api/run-control/strategy-period-chain-release-check`

Ein unbekannter Datensatz ergibt `404`, ein Integritaets- oder
Volldigestkonflikt `409` und ein ungueltiger Request oder eine fehlende
SQLite-Konfiguration `400`. FastAPI und Starlette verwenden denselben
Handler.

## Ergebnisgrenze

`release_ready = true` belegt:

- eine konsistente Ketten-ID und den erwarteten SHA-256-Volldigest;
- einen vorhandenen, unveraenderten PR137-Datensatz;
- erneut bestaetigte Payload-, Digest- und Metadatenintegritaet;
- einen konsistenten Horizont;
- geschlossene Start-, Carryover-, Runner- und Ausgabegrenzen.

Der Wert belegt keine Benutzeridentitaet, speichert die Auditangaben nicht,
legt keine Queue an und ist keine Starterlaubnis.

## Validierung

Die Tests sichern:

- exakte Requestfelder, ID-/Digestformate, UTC-Zeit und Freigabeflag;
- einen positiven read-only Check einer gespeicherten Zwei-Perioden-Kette;
- unveraenderte Datenbankbytes vor und nach dem Check;
- Ablehnung eines abweichenden Volldigests trotz gleicher Ketten-ID;
- Fehler fuer unbekannte und beschaedigte Ketten;
- ausbleibende Kandidatenaufloesung, Carryover- und Runneraufrufe;
- Methoden- und Statuscodes beider API-Implementierungen.

## Bewusste Grenzen

PR138 erzeugt weder Queue-Eintrag noch dauerhafte Freigabeakte. Es gibt
keinen Preflight, keinen Start, kein Carryover, keinen Runner, keine
Ergebnisablage und keine Simulation. Der Check ist keine historische RNG-
oder Vollgleichheitsbehauptung. `incomming/` bleibt unversioniert.

## Naechster Schritt

PR139 soll aus einer erneut freigegebenen Kette genau zwei Perioden auf
isolierten Kandidatenkopien fluechtig ausfuehren. Kandidatenaufloesung,
Carryover-Flags und atomarer Fehlerstopp werden dort vor dem ersten
Runneraufruf separat abgesichert; eine Ergebnisablage bleibt noch gesperrt.
