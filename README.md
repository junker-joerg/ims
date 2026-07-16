# ims

Dieses Repository enthält das Arbeitsgerüst für eine schrittweise, PR-basierte und semantisch konservative Migration von IMS.
Weitere Hinweise stehen unter `docs/migration/README.md`.

## Lokale Workbench

Die lokale Workbench-v1 ist unter `docs/migration/workbench_shell.md` beschrieben. Sie laeuft zuerst lokal im Browser und bleibt bewusst von der Fachlogik getrennt.

Kurzstart fuer die lokale Browser-Workbench:

```powershell
python -m pip install -e .\python_port[dev]
cd frontend
npm.cmd install
npm.cmd run build
cd ..
python -m ims.api.workbench_diagnostics --frontend-dist frontend/dist
python -m ims.api.workbench_readiness --frontend-dist frontend/dist
python -m ims.api.workbench_portable_readiness --root . --layout repo
python -m ims.api.workbench_build_snapshot --root . --frontend-dist frontend/dist
python -m ims.api.workbench_artifact_manifest --root . --frontend-dist frontend/dist
python -m ims.api.workbench_bundle_plan --root . --frontend-dist frontend/dist
python -m uvicorn ims.api.app:app --app-dir python_port --host 127.0.0.1 --port 8000
```

Danach ist die Workbench lokal unter `http://127.0.0.1:8000/` erreichbar. Die aktuelle Workbench ist weiterhin rein lesend: keine Simulation, kein Browser-Upload und keine HTTP-/UI-Schreibpfade.

Alternativ stehen erste lokale Windows-Skripte bereit:

```powershell
scripts\workbench\check-workbench.cmd
scripts\workbench\start-workbench.cmd
```

Die Skripte setzen ein gebautes `frontend/dist` voraus. Das Check-Skript fuehrt Diagnose und Readiness aus, startet aber keinen dauerhaften Server. Es nutzt `IMS_METADATA_DB` nur, wenn die Datei bereits existiert. Das Start-Skript startet nur den lokalen Backend-Server. Beide Skripte setzen bei Bedarf ueberschreibbare Defaults fuer `IMS_FRONTEND_DIST`, `IMS_METADATA_DB`, `IMS_WORKBENCH_HOST` und `IMS_WORKBENCH_PORT`.

Lokaler Workbench-v1 Abschlussstatus:

Die lokale Workbench-v1 ist als Modernisierungs-Meilenstein abgeschlossen. Dieser Abschluss ist kein Release-Tag, keine Fachvalidierung und keine historische Vollgleichheitsbehauptung.

- Backend-Health und Version sind lokal verfuegbar.
- Das gebaute Frontend wird statisch ausgeliefert.
- Szenario- und Run-Metadaten sind lesend als Listen, Details, Filter und Auswahlzusammenfassung verfuegbar.
- Betriebsdiagnose, Metadatenquelle, Konsistenzdiagnose, Readiness und lokale CLI-Grenzen sind dokumentiert und getestet.
- Lokale CLI-Adapter decken Diagnose, Import-Check, Preview, Dry-Run, Export, Roundtrip, Snapshot, expliziten Importbericht und Run-Control-Preflight ab.
- Keine Fachlogikaenderung, keine Simulation, keine HTTP-/UI-Schreibpfade und keine historische Vollgleichheitsbehauptung.

Die spaetere Run-Steuerung und Gesamtplanung bis zum vollstaendigen Abschluss sind unter `docs/migration/workbench_run_control_plan.md` beschrieben. Der separate Packaging- und Bereitstellungsblock ist unter `docs/migration/workbench_packaging_plan.md` als lokaler ZIP-/Staging-Abschlussstatus konsolidiert. Diese Plaene und Checks starten keine Simulation.

Die PR-Roadmap bis zu einer konservativen Produktionsreife steht unter
`docs/plans/production_readiness_pr_plan.md`. PR 50 waehlt als naechsten
fachlichen Slice Vrvn04 / `search_history` unter
`docs/plans/sixth_fachlicher_slice_test_plan.md`; die Testumsetzung ist in
PR 51 unter `tests/test_sixth_fachlicher_vn_search_history_regression.py`
erfolgt.

Die lokale Demo-Checkliste fuer eine kurze Vorfuehrung steht unter `docs/migration/workbench_demo_checklist.md`. Sie benennt Startbefehle, UI-Reihenfolge, erwartete Demo-Signale und klare Grenzen: Queue-Metadaten duerfen nur in eine explizite SQLite-Datei vorgemerkt werden; Simulation, Ausfuehrungsadapter und fachlicher Gleichheitsnachweis bleiben ausgeschlossen.

Der Anschluss zur eigentlichen IMS-Kern-Fachlogik nach Workbench-v1 ist unter
`docs/plans/ims_core_fachlogik_resume_plan.md` geplant. Dieser Plan benennt den
naechsten fachlichen Diagnoseblock fuer vorhandene explizite VU/VN-Periodenplaene,
ohne neue Fachlogik, HTTP-Schreibpfade oder Ausfuehrung freizuschalten.
Der konkrete naechste PR-16-Schnitt ist unter
`docs/plans/explicit_period_transition_slice.md` dokumentiert: Er kartiert die
Periodenuebergangs- und Carryover-Grenze der vorhandenen VU-Planfixtures
`replay_vu14_period_plan.json` und `replay_vusk1_period_plan.json`, noch ohne
neue Fachlogik und ohne Runner-Start.
Der PR-17-Code-Schnitt ist die lokale Diagnose
`python -m ims.engine.explicit_period_transition_diagnostics tests/fixtures/replay_vu14_period_plan.json`;
sie beschreibt Uebergaenge, Update-Felder und Carryover-Planung, bleibt aber
ohne Runner-Start und ohne Simulation.
Das Anschlussfixture `tests/fixtures/replay_vn_policyholder_transition_plan.json`
belegt dieselbe Diagnose fuer eine minimale VN-Policyholder-Subjektmenge.
Der naechste Carryover-Code-Schnitt ist unter
`docs/plans/explicit_transition_carryover_code_slice.md` abgegrenzt: Er verlangt
ein explizites Opt-in, darf nur die vorhandenen portierten
Carryover-Bausteine pruefen und bleibt ohne Simulation, API-/UI-Startpfad oder
historische Regelableitung.
Der lokale Probe-Befehl
`python -m ims.engine.explicit_transition_carryover_probe --apply-vn tests/fixtures/replay_vn_policyholder_transition_plan.json`
prueft diese Grenze in-memory. Der Kernvalidierungsueberblick enthaelt nun
einen read-only `explicit_transition_carryover_probe_contract`, startet den
Probe aber nicht. Die Workbench-API stellt den Vertrag ueber
`GET /api/core-validation/carryover-probe-contract` ebenfalls nur lesend bereit;
der Endpunkt akzeptiert keinen Probe-Payload und startet keinen Probe. Die
Workbench zeigt den Vertrag nun als eigene read-only Karte
`Carryover-Probe-Vertrag`, ebenfalls ohne Payload-Upload, Probe-Start oder
Ausfuehrungsadapter. Der Demo-/Doku-Smoke deckt diese read-only
Carryover/Kern-Sicht nun mit ab. Aktueller Zaehlschnitt: 0 PRs bis zur
demo-nahen read-only Carryover/Kern-Sicht, danach 3+ fachliche
Validierungs-PRs bis zu einem breiteren fachlichen Anschluss; keine dieser
Zahlen ist eine historische Vollgleichheitsbehauptung.
Der erste echte fachliche Test-Slice ist unter
`docs/plans/first_fachlicher_slice_test_plan.md` geplant: VN-Carryover fuer
Versicherer `11` und Policyholder `21` von globaler Periode `21` nach `22` aus
`replay_vn_policyholder_transition_plan.json`. Der Slice ist nun als eigener
fachlicher Regressionstest unter
`tests/test_first_fachlicher_vn_carryover_regression.py` ausgefuehrt. Er bleibt
ohne Simulation und ohne Vollgleichheitsbehauptung. Die Einordnung steht in
`docs/migration/first_fachlicher_regressionstest.md`; der naechste fachliche
Schritt ist unter `docs/plans/second_fachlicher_slice_test_plan.md` als zweiter
schmaler Slice geplant: VN-Regelwirkung ueber explizite `best_info`-Snapshots
fuer Policyholder `21`, Versicherer `11/12` und Periode `5`. Auch dieser
Anschluss bleibt ohne Simulation und ohne Vollgleichheitsbehauptung.
Der zweite fachliche Regressionstest ist unter
`tests/test_second_fachlicher_vn_rule_snapshot_regression.py` umgesetzt und in
`docs/migration/second_fachlicher_regressionstest.md` eingeordnet. Er prueft
die `best_info`-Snapshot-Wirkung und ihre Uebernahme in den VN-Periodenlauf,
ohne daraus einen historischen Vollgleichheitsnachweis abzuleiten.
Der dritte fachliche Slice ist unter
`docs/plans/third_fachlicher_slice_test_plan.md` geplant: VU-Carryover fuer
Versicherer `10` von lokaler Periode `2` nach `3`, mit erwarteter
weitergerollter Frmdinf-Basis und Vrvu04-Nettowechslerbasis. Auch dieser
Anschluss bleibt ohne Simulation, ohne neue Fachregel und ohne
Vollgleichheitsbehauptung.
Der dritte fachliche Regressionstest ist unter
`tests/test_third_fachlicher_vu_carryover_regression.py` umgesetzt und in
`docs/migration/third_fachlicher_regressionstest.md` eingeordnet. Er prueft
die VU-Carryover-Wirkung und die Vrvu04-Nettowechslerbasis, ohne daraus einen
historischen Vollgleichheitsnachweis abzuleiten.
Der vierte fachliche Regressionstest ist unter
`tests/test_fourth_fachlicher_vn_best_info_carryover_regression.py` umgesetzt
und in `docs/migration/fourth_fachlicher_regressionstest.md` eingeordnet. Er
prueft, dass die explizite VN-`best_info`-Entscheidung fuer Policyholder `21`
und Versicherer `11/12` von Periode `5` in den vorhandenen VN-State-Carryover
nach Periode `6` eingeht, ohne neue Snapshots in der Folgeperiode, ohne
Simulation und ohne historischen Vollgleichheitsnachweis.
Der fuenfte fachliche Regressionstest ist unter
`tests/test_fifth_fachlicher_vn_sample_search_regression.py` umgesetzt und in
`docs/migration/fifth_fachlicher_regressionstest.md` eingeordnet. Er prueft
die VN-`sample_search`-/Vrvn05-Entscheidung fuer Policyholder `21` und
Versicherer `11/12`, die Stichprobendiagnose und die Uebernahme in den
VN-Schaden-/Settlement-Runner, ohne Simulation und ohne historischen
Vollgleichheitsnachweis. Nach diesem PR-42-Schnitt bleiben fuer eine
reviewbare und stabile benutzbare Demo-Simulation grob noch 5 bis 7 PRs.
Der sechste fachliche Regressionstest ist unter
`tests/test_sixth_fachlicher_vn_search_history_regression.py` umgesetzt und in
`docs/migration/sixth_fachlicher_regressionstest.md` eingeordnet. Er prueft die
VN-`search_history`-/Vrvn04-Entscheidung fuer Policyholder `21`, Versicherer
`11/12`, die Historienauswahl aus Periode `4` und die Uebernahme in den
VN-Schaden-/Settlement-Runner, ohne Simulation und ohne historischen
Vollgleichheitsnachweis.
Der siebte fachliche Regressionstest ist unter
`tests/test_seventh_fachlicher_vn_preference_regression.py` umgesetzt und in
`docs/migration/seventh_fachlicher_regressionstest.md` eingeordnet. Er prueft
die VN-`preference`-/Vrvn03-Entscheidung fuer Policyholder `21`, Versicherer
`11/12`, die Praeferenzscores aus aktiver VU-Werbung und die Uebernahme in den
VN-Schaden-/Settlement-Runner, ohne Simulation und ohne historischen
Vollgleichheitsnachweis.
Der achte fachliche Regressionstest ist unter
`tests/test_eighth_fachlicher_vn_random_regression.py` umgesetzt und in
`docs/migration/eighth_fachlicher_regressionstest.md` eingeordnet. Er prueft
die VN-`random`-/Vrvn02-Entscheidung fuer Policyholder `21`, Versicherer
`11/12`, explizite Status- und Versicherer-Draws sowie die Uebernahme in den
VN-Schaden-/Settlement-Runner, ohne Simulation, ohne historische
RNG-Gleichheitsbehauptung und ohne historischen Vollgleichheitsnachweis.
Der neunte fachliche Regressionstest ist unter
`tests/test_ninth_fachlicher_vn_damage_settlement_breadth.py` umgesetzt und in
`docs/migration/ninth_fachlicher_regressionstest.md` eingeordnet. Er prueft den
VN-Schaden-/Settlement-Pfad fuer explizite Entscheidungen aus `Vrvn01` bis
`Vrvn03` mit drei Policyholdern, kumulierten Versichererfortschreibungen und
Sektorvermoegen, ohne Simulation und ohne historischen
Vollgleichheitsnachweis.
Der Run-Control-Ausfuehrungsfreigabeplan ist unter
`docs/plans/run_control_execution_release_plan.md` dokumentiert. Er beschreibt
die Freigabekette von Dry-Run, Queue, Action-Plan, expliziter
Ausfuehrungsfreigabe, spaeterem Adapterstart und Ergebnisablage. Dieser
PR-43-Schnitt baut noch keinen API-Startpfad, keinen UI-Startbutton und keinen
Queue-Worker. Nach diesem Plan bleiben grob noch 4 bis 6 reviewbare PRs bis zu
einer benutzbaren kontrollierten Demo-Simulation.
Der hart gegatete API-Startvertrag ist unter
`python_port/ims/api/run_control_adapter_start_contract.py` umgesetzt und in
`docs/migration/run_control_adapter_start_contract.md` dokumentiert.
`GET /api/run-control/adapter-start-contract` beschreibt nur die spaeteren
Request-Felder, Preconditions und verbotenen Grenzen fuer
`POST /api/run-control/adapter-start`; der POST-Startendpunkt existiert in
diesem PR-44-Schnitt nicht. `api_accepts_start_payload`,
`api_validates_start_payload`, `api_starts_adapter`, `ui_start_enabled`,
`queue_worker_enabled`, `writes_enabled` und `execution_enabled` bleiben
`false`. Nach PR 44 bleiben grob noch 3 bis 5 reviewbare PRs bis zu einer
benutzbaren kontrollierten Demo-Simulation.
Die lokale Ergebnis-Persistenzgrenze ist unter
`python_port/ims/api/run_control_execution_result_store.py` umgesetzt und in
`docs/migration/run_control_execution_result_store.md` dokumentiert. Sie
speichert nur ein vorab validiertes `controlled_execution_adapter`-JSON mit
explizitem `--explicit-persistence-release` in eine explizite SQLite-Quelle,
setzt den Queue-Status `result_persisted` und startet keinen Adapter. Nach
PR 45 bleiben grob noch 2 bis 4 reviewbare PRs bis zu einer benutzbaren
kontrollierten Demo-Simulation.
Der Workbench-UI-Flow fuer die kontrollierte Ausfuehrungsgrenze ist unter
`frontend/src/main.tsx` umgesetzt und in
`docs/migration/run_control_execution_flow_ui.md` dokumentiert. Die Karte
`Run-Control-Ausfuehrungsflow` zeigt
`Preflight -> explizite Freigabe -> Ausfuehren`, laedt
`GET /api/run-control/adapter-start-contract` nur lesend und ordnet
`result_persisted` als `Ergebnis pruefen` ein. Sie enthaelt keinen
UI-Startbutton, keinen Queue-Worker, keinen Adapterstart und keine Simulation.
Die read-only Ergebnisanzeige fuer persistierte Run-Control-Adapterresultate
ist unter `python_port/ims/api/app.py` angebunden und in
`docs/migration/run_control_execution_result_view.md` dokumentiert.
`GET /api/run-control/execution-result/{queue_id}` liest nur vorhandene
`run_control_execution_results`; die Workbench-Karte
`Run-Control-Ergebnisanzeige` zeigt Queue, Run, Szenario, Summary-Modus,
Persistenzzeitpunkt und Grenzflags. Nach PR 47 bleiben grob noch 0 bis 2 reviewbare PRs bis zu einer benutzbaren kontrollierten Demo-Simulation.
Der read-only Vertrag fuer einen spaeteren kontrollierten Ausfuehrungsadapter
ist unter `python_port/ims/api/controlled_execution_adapter_contract.py`
umgesetzt und in
`docs/migration/controlled_execution_adapter_contract.md` eingeordnet. Er bindet
einen spaeteren lokalen Adapter an den vorhandenen
`explicit_multi_period_execution_summary`-Vertrag, oeffnet aber keinen API-
oder UI-Start und laesst `runner_start_enabled`, `writes_enabled` und
`execution_performed` im Vertrag auf `false`. Der lokale Adapter selbst ist
unter `python_port/ims/api/controlled_execution_adapter.py` umgesetzt und in
`docs/migration/controlled_execution_adapter.md` dokumentiert. Er laeuft nur mit
explizitem `--explicit-execution-release`, akzeptiert keinen freien Output-Pfad
und bleibt von Run-Control, API, UI und Queue getrennt. Die Restplanung steht
weiter unter `docs/plans/controlled_execution_adapter_plan.md`; dieser
kontrollierte Ausfuehrungsadapter ist kein historischer Vollgleichheitsnachweis.
Er bleibt als kontrollierter Ausfuehrungsadapter-Vertrag die dokumentierte
Grenze fuer diese lokale Freigabe.
Der naechste Run-Control-Anschluss ist unter
`docs/plans/run_control_adapter_result_plan.md` geplant: Run-Control soll
zunaechst nur ein bereits lokal erzeugtes Adapterergebnis als read-only
Resultat einordnen duerfen. Der Plan oeffnet keinen Adapterstart, keinen
Browser-Upload, keinen Queue-Worker und keinen UI-Startpfad.
Der zugehoerige Vertrag ist unter
`python_port/ims/api/run_control_adapter_result_contract.py` umgesetzt und in
`docs/migration/run_control_adapter_result_contract.md` dokumentiert. Er kann
ein vorab erzeugtes `controlled_execution_adapter`-JSON lokal pruefen, startet
aber keinen Adapter und schreibt keine Metadaten.
Der vorgeschlagene naechste Schritt steht unter
`docs/plans/run_control_adapter_result_view_plan.md`: eine read-only
API-/UI-Anzeigeplanung fuer Adapter-Resultate, weiterhin ohne Browser-Upload,
Dateiauswahl, Startbutton oder Adapterstart.
Der erste API-Schnitt dafuer ist unter
`python_port/ims/api/run_control_adapter_result_api_contract.py` umgesetzt und
in `docs/migration/run_control_adapter_result_api_contract.md` dokumentiert.
`GET /api/run-control/adapter-result-contract` beschreibt nur die spaetere
Anzeigegrenze fuer vorab lokal gepruefte Adapter-Resultate; der Endpunkt nimmt
keinen Payload an, validiert kein Resultat ueber HTTP und startet keinen
Adapter.
Die spaetere rein lesende Verbindung zwischen Run-Control-Aktionsplan und
Kernlauf-Diagnosen ist unter
`docs/plans/run_control_core_diagnostics_bridge_plan.md` geplant. Der
read-only Endpunkt `GET /api/run-control/core-diagnostics-bridge` buendelt
Queue-Aktionsplan und Kernvalidierungsueberblick. Die UI-Karte
`Run-Control-Kernblick-Bruecke` zeigt diesen Vertrag nur lesend; sie bleibt ohne
Schreibpfad, ohne UI-Startpfad, ohne Runner-Start und ohne automatische
Fachlogik.
Als erster rein lesender Kernblick kann
`python -m ims.engine.explicit_period_diagnostics tests/fixtures/replay_vu14_period_plan.json`
die vorhandene Planstruktur diagnostizieren, ohne Simulation, Runner-Start oder
Ausgabedateien.

Start und Diagnose:

Optional kann die Diagnose eine explizite lokale Konfigurationsdatei lesen:

```powershell
python -m ims.api.workbench_diagnostics --config .\workbench.local.json
```

Ein rein beschreibender Startplan kann dieselben lokalen Werte als JSON zusammenfassen, ohne den Server zu starten:

```powershell
python -m ims.api.workbench_start_plan --config .\workbench.local.json
```

Eine lokale v1-Bereitschaftspruefung buendelt Diagnose, Metadatenquelle, CLI-Grenzen, Run-Control-Preflight und bei expliziter SQLite-Quelle die Run-Control-Queue-Diagnose, ohne den Server zu starten:

```powershell
python -m ims.api.workbench_readiness --frontend-dist frontend/dist
```

Eine lokale Strukturpruefung prueft die heutige Repo-Struktur oder eine spaetere portable Workbench-Ordnerstruktur, ohne Dateien zu erzeugen:

```powershell
python -m ims.api.workbench_portable_readiness --root . --layout repo
```

Die Strukturpruefung validiert dabei auch, ob erwartete Dateien und Ordner den richtigen Pfadtyp haben.

Ein lokaler Build-Snapshot fasst vorhandene Frontend-/Backend-Artefakte zusammen, ohne Dateien zu kopieren oder ein ZIP zu erzeugen:

```powershell
python -m ims.api.workbench_build_snapshot --root . --frontend-dist frontend/dist
```

Ein lokales Artefaktmanifest beschreibt Ein- und Ausschlusspfade fuer ein spaeteres portables Artefakt, erzeugt aber noch kein ZIP:

```powershell
python -m ims.api.workbench_artifact_manifest --root . --frontend-dist frontend/dist
```

Das Manifest enthaelt fuer eingeschlossene Dateien relative Pfade, Groesse und SHA-256-Pruefsummen.

Ein lokaler Bundle-Trockenlauf nutzt dieses Manifest und beschreibt ein spaeteres ZIP-Bundle, ohne Dateien zu kopieren oder ein Archiv zu erzeugen:

```powershell
python -m ims.api.workbench_bundle_plan --root . --frontend-dist frontend/dist
```

Ein expliziter lokaler ZIP-Build kann daraus ein ZIP in einen angegebenen Zielpfad schreiben. Der Ausgabeordner wird vorher explizit angelegt, weil der ZIP-Build fehlende Output-Parents nicht automatisch erzeugt:

```powershell
New-Item -ItemType Directory .\dist -Force
python -m ims.api.workbench_bundle_build --root . --frontend-dist frontend/dist --out .\dist\ims-workbench-local.zip
```

Dieses ZIP ist ein lokales Bereitstellungsartefakt, kein Installer, kein Release-Tag und kein fachlicher Gleichheitsnachweis.
Der ZIP-Zielpfad darf nicht unter eingeschlossenen Quellbaeumen wie `python_port` oder `frontend/dist` liegen. ZIP-Eintraege werden mit stabilen Metadaten geschrieben, damit die `zip_sha256`-Pruefsumme bei identischem Inhalt reproduzierbar bleibt.

Lokaler Release-Ablauf fuer ein ZIP-Artefakt:

```powershell
npm.cmd run build
New-Item -ItemType Directory .\dist -Force
python -m ims.api.workbench_bundle_build --root . --frontend-dist frontend/dist --out .\dist\ims-workbench-local.zip
python -m ims.api.workbench_bundle_smoke --zip-path .\dist\ims-workbench-local.zip
python -m ims.api.workbench_portable_staging --zip-path .\dist\ims-workbench-local.zip --out .\ims-workbench
python -m ims.api.workbench_portable_staging_smoke --root .\ims-workbench
python -m ims.api.workbench_portable_readiness --root .\ims-workbench --layout portable
```

Dieser Ablauf ist ein lokaler Bereitstellungscheck fuer den tatsaechlich erzeugten ZIP-Inhalt und eine daraus explizit gestagte portable Zielstruktur unter `.\ims-workbench`. Portable Readiness mit `app\frontend\dist` ist erst nach diesem Staging-Schritt sinnvoll. Der Ablauf startet keine Simulation, oeffnet keinen HTTP- oder UI-Schreibpfad, installiert nichts automatisch und migriert keine SQLite-Datenbank.
Der ZIP-Smoke prueft erwartete Eintraege, ausgeschlossene lokale Daten, stabile ZIP-Metadaten sowie die Lesbarkeit der ZIP-Payloads inklusive CRC-Pruefung.
Das portable Staging erwartet einen fehlenden oder leeren Zielordner und ueberschreibt keine lokalen Nutzerdaten wie `metadata.sqlite`, WAL-/SHM-Dateien oder Logs. Der Staging-Smoke prueft danach die gestagte Backend-/Frontend-Struktur, die Backend-Importfaehigkeit aus dem gestagten Workbench-Root fuer die Check-/Startskriptgrenze und die portablen Startskriptgrenzen rein lesend. Die generierten portablen Skripte setzen dieselben ueberschreibbaren Defaults fuer Frontend-Dist, lokale Metadatenablage, Host und Port.

Eine lokale CLI-Uebersicht listet die vorhandenen Befehle und ihre Grenzen, ohne Import, Snapshot oder Serverstart auszufuehren:

```powershell
python -m ims.api.workbench_cli_overview
```

Vertraege und Run-Control-Grenzen:

Ein lokaler Schreibvertrag beschreibt die vorbereiteten Metadaten-Schreibgrenzen, ohne einen Schreibpfad zu oeffnen:

```powershell
python -m ims.api.metadata_write_contracts
python -m ims.api.metadata_write_contracts check .\metadata_import.json
```

Ein lokaler Run-Control-Vertrag beschreibt die spaetere Steuerungsgrenze, ohne einen Lauf zu starten:

```powershell
python -m ims.api.run_control_contracts
python -m ims.api.run_control_dry_run_contract
python -m ims.api.core_validation_carryover_probe_contract
python -m ims.api.controlled_execution_adapter_contract
python -m ims.api.controlled_execution_adapter --fixture tests\fixtures\replay_vn_policyholder_transition_plan.json --explicit-execution-release
python -m ims.api.run_control_adapter_result_contract
python -m ims.api.run_control_adapter_result_contract check .\adapter_result.json
python -m ims.api.run_control_adapter_result_api_contract
python -m ims.api.run_control_adapter_start_contract
python -m ims.api.run_control_execution_result_store init --db .\.ims_workbench\metadata.sqlite
python -m ims.api.run_control_execution_result_store persist --db .\.ims_workbench\metadata.sqlite --queue-id baseline-python-tests --adapter-result .\adapter_result.json --persisted-at 2026-07-15T00:00:00Z --explicit-persistence-release
python -m ims.api.run_control_execution_result_store show --db .\.ims_workbench\metadata.sqlite --queue-id baseline-python-tests
```

Der Dry-Run-Vertrag beschreibt den kontrollierten HTTP-Pruefpfad. Die Workbench-API stellt ihn ueber `GET /api/run-control/dry-run-contract` bereit; `POST /api/run-control/dry-run` akzeptiert nur das Run-Control-Request-DTO mit `execution_enabled=false`, kombiniert es mit dem vorhandenen Preflight und schreibt keine Queue oder Metadaten. Es gibt keinen PUT, keinen Browser-Upload, keinen Schreibpfad und keine Simulation.

Der Carryover-Probe-Vertrag beschreibt den read-only API-Vertrag fuer bereits
berechnete Probe-Ergebnisse. Die Workbench-API stellt ihn ueber
`GET /api/core-validation/carryover-probe-contract` bereit. Er akzeptiert keinen
Probe-Payload, startet keinen Probe und schreibt keine Daten.

Der kontrollierte Ausfuehrungsadapter-Vertrag beschreibt nur die spaetere lokale
Adaptergrenze. Er hat in diesem Stand keinen HTTP-Endpunkt, keinen UI-Startpfad,
keinen Queue-Worker und startet keinen expliziten Periodenrunner.

Der lokale kontrollierte Ausfuehrungsadapter startet nur nach expliziter lokaler
Freigabe und gibt eine `explicit_multi_period_execution_summary` zurueck. Er
akzeptiert in diesem Stand keinen Output-Pfad, schreibt keine Metadaten und ist
nicht an die Browser-Workbench angebunden.

Der Run-Control-Adapter-Resultat-Vertrag beschreibt und prueft nur bereits lokal
erzeugte Adapter-JSONs. Er ist kein Startpfad, kein Upload und kein
Run-Control-Worker.
Die Workbench-API stellt diesen Anzeigevertrag jetzt lesend bereit:

```text
GET /api/run-control/adapter-result-contract
```

Die Antwort enthaelt `mode = "run_control_adapter_result_api_contract"`,
`api_accepts_result_payload = false`, `api_validates_result_payload = false`
und `api_starts_adapter = false`. Der Endpunkt akzeptiert keinen Request-Body,
liest keine Adapter-Datei, schreibt keine Metadaten und startet keine
Ausfuehrung.

Der Run-Control-Adapter-Startvertrag beschreibt nur den spaeteren
Startrequest. Die Workbench-API stellt ihn lesend bereit:

```text
GET /api/run-control/adapter-start-contract
```

Die Antwort enthaelt `mode = "run_control_adapter_start_contract"`,
`planned_start_endpoint = "/api/run-control/adapter-start"`,
`api_accepts_start_payload = false`, `api_validates_start_payload = false`,
`api_starts_adapter = false`, `ui_start_enabled = false` und
`queue_worker_enabled = false`. `POST /api/run-control/adapter-start` ist in
diesem Stand nicht vorhanden.

Der lokale Run-Control-Ergebnisstore speichert vorab validierte
Adapter-Resultate an einen validierten Queue-Eintrag:

```powershell
python -m ims.api.run_control_execution_result_store persist --db .\.ims_workbench\metadata.sqlite --queue-id baseline-python-tests --adapter-result .\adapter_result.json --persisted-at 2026-07-15T00:00:00Z --explicit-persistence-release
```

Der Store validiert das Adapter-Resultat gegen den
Run-Control-Adapter-Resultat-Vertrag, schreibt das Resultat und die Summary in
`run_control_execution_results` und setzt den Queue-Status auf
`result_persisted`. Er startet keinen Adapter und laesst
`execution_performed = false` fuer die Queue.

Ein lokaler Run-Control-Request-Check validiert eine spaetere Steuerungsanfrage als DTO, ohne sie zu speichern oder auszufuehren:

```powershell
python -m ims.api.run_control_requests check .\run_control_request.json
```

Die Workbench-API stellt denselben Request-Vertrag lesend bereit:

```text
GET /api/run-control/request-contract
```

Der Endpunkt gibt Pflichtfelder, optionale Felder, verbotene Felder und ein Beispiel-DTO zurueck. Er akzeptiert keinen Request-Body, validiert keinen Browser-Upload, schreibt keine Metadaten und startet keine Ausfuehrung.

Eine lokale Run-Control-Queue kann solche Requests in einer expliziten SQLite-Datei vormerken, ohne Ausfuehrung, Worker oder Scheduler zu starten:

```powershell
python -m ims.api.run_control_queue init --db .\.ims_workbench\metadata.sqlite
python -m ims.api.run_control_queue enqueue .\run_control_request.json --db .\.ims_workbench\metadata.sqlite
python -m ims.api.run_control_queue list --db .\.ims_workbench\metadata.sqlite
python -m ims.api.run_control_queue_diagnostics --db .\.ims_workbench\metadata.sqlite
python -m ims.api.run_control_queue_action_plan --db .\.ims_workbench\metadata.sqlite
```

`init` und `enqueue` sind die expliziten lokalen Queue-Schreibbefehle. `list`, `show`, `run_control_queue_diagnostics` und `run_control_queue_action_plan` lesen die Queue-Datenbank read-only. Die Diagnose prueft Queue-Schema, Statuswerte, Szenario-Referenzen und Ausfuehrungsflags, ohne Metadaten zu schreiben oder eine Simulation zu starten. Der Aktionsplan fuehrt diese Diagnose mit dem lokalen Preflight zusammen und empfiehlt pro Queue-Eintrag nur den naechsten sicheren lokalen Schritt: `run_preflight`, `await_execution_release`, `resolve_blockers`, `inspect_persisted_result` oder `inspect_queue_status`. Eine Queue-only-Datenbank aus `run_control_queue init --db` bleibt diagnostizierbar und planbar; fehlende Szenario-/Run-Metadatentabellen werden als Warnung gemeldet.

Die Workbench-Oberflaeche zeigt vorhandene Queue-Eintraege rein lesend, filtert sie clientseitig und blendet nur lokale Schrittlabels wie Preflight, Freigabe abwarten, Blocker klaeren oder Status pruefen ein. Daraus entsteht kein Start-, Upload-, Editor-, HTTP-Schreib- oder Ausfuehrungspfad.

Read-only SQLite-Zugriffe behandeln lokale WAL-Grenzen bewusst: Rollback-Journal-Datenbanken bleiben normale `mode=ro`-Reads, vollstaendige `-wal`/`-shm`-Sidecars werden beruecksichtigt und `immutable=1` wird nur fuer sidecar-freie WAL-Dateien genutzt, damit lesende Queue- und Metadatenbefehle keine neuen Sidecars erzeugen.

`workbench_readiness --db <metadata.sqlite>` bezieht diese Queue-Diagnose als eigenen Bereitschaftsbereich ein. Eine nicht initialisierte Queue bleibt ein zulaessiger Hinweis; unlesbare Queue-Schemas oder aktivierte Ausfuehrungsflags werden als Queue-Bereitschaftsproblem gemeldet.

Ein lokaler Run-Control-Preflight prueft vorhandene Run-Metadaten gegen diese gesperrte Steuerungsgrenze, ohne einen Lauf zu starten:

```powershell
python -m ims.api.run_control_preflight --run-id baseline-python-tests
```

Die Workbench-UI laedt denselben Preflight fuer den ausgewaehlten Run ueber `GET /api/run-control/preflight/{run_id}`. Die Dry-Run-Karte kann fuer die aktuelle Auswahl `POST /api/run-control/dry-run` als reine Pruefung ausloesen und nach einem erfolgreichen Dry-Run ueber `POST /api/run-control/queue` eine Queue-Vormerkung in einer expliziten SQLite-Quelle schreiben. `GET /api/run-control/queue/action-plan` zeigt danach nur den naechsten sicheren Schritt wie `run_preflight`, `await_execution_release`, `resolve_blockers`, `inspect_persisted_result` oder `inspect_queue_status`. Die Karten `Carryover-Probe-Vertrag` und `Adapter-Resultat-Vertrag` zeigen nur gesperrte read-only Vertraege fuer vorab berechnete bzw. lokal gepruefte Payloads. Die Karte `Run-Control-Ausfuehrungsflow` zeigt `Preflight -> explizite Freigabe -> Ausfuehren` nur als Statussicht auf Preflight, Aktionsplan, Startvertrag und Ergebnisstatus. Die Karte `Run-Control-Ergebnisanzeige` liest optional `GET /api/run-control/execution-result/{queue_id}` und zeigt nur bereits persistierte Ergebnis-Metadaten. Diese Schritte zeigen Run-/Szenario-Bezug, Hinweise und gesperrte Ausfuehrungsgrenzen, ohne PUT, Upload, Editor, UI-Startbutton oder Simulation. Ein kompaktes Run-Control-Statusband buendelt Queue, Preflight, Request-Vertrag, Dry-Run-Pruefung, Adapter-Resultat-Vertrag, Queue-Vormerkung und Aktionsplan.

Lokaler Demo-Smoke fuer die Browser-Workbench:

```text
Dry-Run pruefen -> Queue vormerken -> Run-Control-Aktionsplan ansehen -> Run-Control-Kernblick-Bruecke lesen -> Carryover-Probe-Vertrag lesen -> Adapter-Resultat-Vertrag lesen
```

Der Demo-Smoke nutzt den bekannten Run `baseline-python-tests` und das Szenario `agrsich-reference-window`. Er prueft den HTTP-Dry-Run, schreibt danach nur die Queue-Vormerkung in eine explizite SQLite-Metadatenquelle, liest den Aktionsplan wieder aus, prueft die read-only Run-Control-Ergebnisanzeige, prueft die read-only Run-Control-Kernblick-Bruecke und liest den Carryover-Probe-Vertrag sowie den Adapter-Resultat-Vertrag. Erwartet bleiben `execution_enabled=false`, `execution_performed=false`, als naechster Queue-Schritt `run_preflight`, als Brueckenhinweis `resolve_core_validation_blockers`, `api_starts_probe=false` und `api_starts_adapter=false`. Der Ablauf ist eine lokale Bedien- und Integrationsprobe, keine Simulation, kein Ausfuehrungsadapter, keine Fachvalidierung und keine historische Vollgleichheitsbehauptung.

Der zugehoerige Browser-/Screenshot-Smoke nutzt stabile UI-Anker fuer Dry-Run-Schaltflaeche, Queue-Schaltflaeche, Queue-Ergebnis, Aktionsplankarte, `run-control-execution-flow`, `run-control-execution-result`, `run-control-core-bridge`, `carryover-probe-contract` und `adapter-result-contract`. Der Screenshot soll belegen, dass die lokale UI den Demo-Pfad, die gesperrte Ausfuehrungsflow-Karte, die read-only Ergebnisanzeige, die gesperrte Brueckenkarte, den gesperrten Carryover-Probe-Vertrag und den gesperrten Adapter-Resultat-Vertrag sichtbar macht; er ist kein fachlicher Ergebnisnachweis.

Metadaten-CLI:

Ein lokaler Metadatenexport kann das bestehende Importformat reproduzierbar ausgeben. Ohne `--out` schreibt er nur nach stdout, mit `--out` nur in den expliziten Zielpfad:

```powershell
python -m ims.api.metadata_import_cli export
python -m ims.api.metadata_import_cli export --db .\.ims_workbench\metadata.sqlite --out .\metadata_export.json
```

Ein lokaler Roundtrip-Check prueft Export, Importformat und Schreibvertrag gemeinsam, ohne Dateien zu schreiben:

```powershell
python -m ims.api.metadata_import_cli roundtrip
python -m ims.api.metadata_import_cli roundtrip --db .\.ims_workbench\metadata.sqlite
```

Ein lokaler Import-Trockenlauf zeigt vor einem expliziten Import, welche Szenario- und Run-Metadaten neu waeren oder bestehende IDs ersetzen wuerden. Er schreibt nicht:

```powershell
python -m ims.api.metadata_import_cli dry-run .\metadata_import.json
python -m ims.api.metadata_import_cli dry-run .\metadata_import.json --db .\.ims_workbench\metadata.sqlite
```

Der explizite lokale Import schreibt nur in den angegebenen SQLite-Pfad und gibt danach einen kleinen Importbericht mit geschriebenen IDs und Konsistenzstatus aus:

```powershell
python -m ims.api.metadata_import_cli import .\metadata_import.json --db .\.ims_workbench\metadata.sqlite
```

Backup und Restore lokaler Workbench-Metadaten bleiben explizite Betriebsablaeufe. Die Doku beschreibt das Sichern von `.ims_workbench\metadata.sqlite`, den bewussten Umgang mit WAL-/SHM-Dateien sowie pruefende CLI-Kommandos wie `snapshot`, `roundtrip`, `export` und `workbench_readiness`. Es gibt keine automatische Backup-Funktion, keine SQLite-Migration und keine Simulation.

Update und Rollback lokaler Workbench-Versionen bleiben ebenfalls manuell. Eine neue Workbench-Version soll neben der bisherigen Version in einen eigenen Ordner gelegt werden. Die Checks sollen mit explizitem neuem Anwendungspfad und explizitem bestehendem Metadatenpfad laufen, etwa mit `workbench_portable_readiness`, `workbench_readiness --db <alter-metadata-pfad>` und optional `metadata_import_cli roundtrip --db <alter-metadata-pfad>`. Repo-Side-by-Side-Checks muessen ausserdem den Python-Kontext der neuen Version nutzen, etwa ueber `PYTHONPATH` auf den neuen `python_port`-Pfad oder eine explizite Installation aus dem neuen Checkout. Rollback heisst: neue Version stoppen, alte Version wieder starten und bei Bedarf die zuvor gesicherte Metadatenquelle zuruecklegen. Es gibt keinen automatischen Updater, keine In-place-Aktualisierung, keine automatische SQLite-Migration und keine historische Vollgleichheitsbehauptung.
