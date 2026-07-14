# Plans

Dieses Verzeichnis ist für kleine, nachvollziehbare Arbeitspläne der IMS-Migration reserviert.
Hier sollen spätere PR-Schritte, offene Entscheidungen und Reihenfolgen dokumentiert werden.

- `ims_core_fachlogik_resume_plan.md`: IMS-Kern-Fachlogik nach Workbench-v1,
  mit konservativem Anschluss an vorhandene VU/VN-Periodenplaene und ohne
  neue Ausfuehrung.
- `run_control_core_diagnostics_bridge_plan.md`: Read-only Plan fuer eine
  spaetere Verbindung von Run-Control-Aktionsplan und Kernlauf-Diagnosen, ohne
  neuen Schreib- oder Ausfuehrungspfad.
- `explicit_period_transition_slice.md`: PR-16-Plan fuer den naechsten
  schmalen fachlichen Slice aus vorhandenen VU-Periodenfixtures, zunaechst nur
  als Periodenuebergangs- und Carryover-Grenze ohne neue Fachlogik.
- `explicit_transition_carryover_code_slice.md`: PR-20-Plan fuer den engen
  Carryover-Code-Slice aus vorhandenen expliziten Periodenfixtures, nur mit
  bestehenden portierten Carryover-Bausteinen und ohne historische
  Regelableitung.
- `first_fachlicher_slice_test_plan.md`: PR-26-Plan fuer den ersten fachlichen VN-Carryover-Slice-Test aus dem vorhandenen
  `replay_vn_policyholder_transition_plan.json`, weiterhin ohne Simulation und
  ohne Vollgleichheitsbehauptung.
- `second_fachlicher_slice_test_plan.md`: PR-29-Plan fuer den zweiten
  fachlichen Slice als VN-Regelwirkung ueber explizite `best_info`-Snapshots,
  weiterhin ohne Simulation und ohne Vollgleichheitsbehauptung.
- `third_fachlicher_slice_test_plan.md`: PR-31-Plan fuer den dritten
  fachlichen Slice als VU-Carryover-Fixture, weiterhin ohne Simulation und ohne
  Vollgleichheitsbehauptung.
- `controlled_execution_adapter_plan.md`: PR-33 bis PR-35-Plan fuer Vertrag
  und lokalen schmalen Ausfuehrungsadapter nach drei fachlichen
  Regressionstests, weiterhin ohne API-/UI-Startpfad, Queue-Worker oder
  Vollgleichheitsbehauptung.
- `run_control_adapter_result_plan.md`: PR-36-Entscheidung fuer ein
  read-only Adapter-Resultat in Run-Control und PR-37-Vertrag, weiterhin ohne
  Adapterstart, Browser-Upload, Queue-Worker oder UI-Startpfad.
- `run_control_adapter_result_view_plan.md`: Vorschlag fuer PR 38 als
  read-only API-/UI-Anzeigeplanung fuer bereits lokal erzeugte
  Adapterresultate, weiterhin ohne Upload, Startbutton oder Adapterstart.
- `../migration/run_control_adapter_result_api_contract.md`: PR-39-API-Vertrag
  fuer `GET /api/run-control/adapter-result-contract`, weiterhin ohne
  Payload-Upload, HTTP-Validierung, Startbutton oder Adapterstart.
- `../migration/fourth_fachlicher_regressionstest.md`: PR-41-Einordnung des
  vierten fachlichen VN-Slices fuer `best_info`-Wirkung plus VN-State-Carryover,
  weiterhin ohne Simulation und ohne Vollgleichheitsbehauptung.
- `../migration/fifth_fachlicher_regressionstest.md`: PR-42-Einordnung des
  fuenften fachlichen VN-Slices fuer `sample_search` / Vrvn05 plus
  Schaden-/Settlement-Runner-Grenze, weiterhin ohne Simulation.
- `run_control_execution_release_plan.md`: PR-43-Plan fuer die explizite
  Run-Control-Ausfuehrungsfreigabe vor einem spaeter benutzbaren Startpfad,
  weiterhin ohne UI-Startbutton, Queue-Worker oder Simulation.
