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
