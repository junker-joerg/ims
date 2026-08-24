# Atomarer Run-Control-Adapterstart (PR 63)

## Ziel

PR 63 verbindet den in PR 62 eingefuehrten Freigabecheck mit dem vorhandenen
kontrollierten Adapter. Der neue Backend-Endpunkt startet hoechstens einen
Adapterlauf je Queue-Eintrag und Idempotenzschluessel und legt das validierte
Resultat gemeinsam mit dem abschliessenden Queue-Status ab.

## Mapping

| Ursprung / vorhandene Grenze | Python-Komponente | Rolle in PR 63 |
| --- | --- | --- |
| validierte Run-Control-Queue | `ims.api.run_control_queue` | atomarer Wechsel `validated -> starting -> result_persisted` oder `failed` |
| read-only Freigabecheck aus PR 62 | `ims.api.run_control_execution_release` | strikter Startpayload mit Audit- und Idempotenzfeldern |
| kontrollierter lokaler Adapter | `ims.api.controlled_execution_adapter` | ausschliesslich ueber ein serverseitiges Fixture-Profil aufrufbar |
| Adapter-Resultat-Vertrag | `ims.api.run_control_adapter_result_contract` | Ergebnispruefung vor der Persistenz |
| vorhandener Result-Store | `ims.api.run_control_execution_result_store` | gemeinsame Record-Erzeugung und atomare Ablage |
| neue Startgrenze | `ims.api.run_control_adapter_start` | Claim, Doppelstartschutz, Resultatabschluss und Fehlerstatus |
| Workbench-API | `ims.api.app` | `POST /api/run-control/adapter-start` mit injizierbarem Adapterrunner |

## Ablauf und Invarianten

Der Request muss den Freigabevertrag aus PR 62 erfuellen und zusaetzlich einen
nichtleeren `idempotency_key` enthalten. Fixture- und Ausgabepfade bleiben aus
dem Request ausgeschlossen. Das serverseitige Freigabeprofil bestimmt das
Fixture und den erlaubten Adaptermodus.

Ein `BEGIN IMMEDIATE` reserviert den Queue-Eintrag und schreibt den Versuch als
`starting`, bevor der Adapter aufgerufen wird. Ein zweiter gleichzeitiger Start
wird abgewiesen. Nach erfolgreicher Vertragspruefung werden Resultat,
Versuchsstatus und Queue-Status in einer Transaktion auf `result_persisted`
gesetzt. Derselbe unveraenderte Request kann danach unter demselben
Idempotenzschluessel nur das gespeicherte Resultat erneut lesen; der Adapter
wird nicht erneut aufgerufen. Derselbe Schluessel mit veraendertem Payload wird
abgewiesen.

Fehler werden als `failed` protokolliert. Es wird dabei kein Resultat erfunden
und `execution_performed` bleibt am Queue-Eintrag `false`, wenn kein gueltiges
Adapterresultat abgeschlossen wurde.

## Validierung

Die Tests verwenden ausschliesslich injizierte Adapterfunktionen. Sie pruefen:

- erfolgreiche atomare Ergebnisablage;
- idempotente Wiederholung ohne zweiten Adapteraufruf;
- Abweisung eines veraenderten Payloads unter demselben Schluessel;
- einen ueberlappenden Doppelstart mit genau einem Adapteraufruf;
- konservative Fehlerablage ohne Ergebnis oder Simulationsbehauptung.

Es wurde fuer diesen PR keine Simulation gestartet.

## Grenzen und offene Punkte

- kein UI-Startbutton;
- kein Queue-Worker und keine Hintergrundausfuehrung;
- kein freier Browser-Upload und keine freie Pfadauswahl;
- keine neue Fachlogik und keine automatische historische Regelwahl;
- keine historische Vollgleichheitsbehauptung;
- ein nach Prozessabbruch verbliebener `starting`- oder `failed`-Versuch wird
  nicht automatisch wiederholt; eine Wiederanlaufregel braucht einen eigenen
  reviewbaren Schritt.

PR 64 kann nun den bereits vorbereiteten UI-Flow an diesen eng gegateten
Backend-Endpunkt anbinden. Die explizite Freigabe und der Idempotenzschluessel
bleiben dabei Pflicht.

PR 64 hat diesen UI-Anschluss umgesetzt. Die atomaren Backend-Invarianten
bleiben unveraendert; die UI fuegt keine Wiederholungs- oder Workerlogik hinzu.
