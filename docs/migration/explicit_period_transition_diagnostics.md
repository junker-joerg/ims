# Explizite Periodenuebergangsdiagnose

## Ziel

`ims.engine.explicit_period_transition_diagnostics` beschreibt benachbarte
Periodenuebergaenge aus vorhandenen expliziten Periodenplaenen. Der Schnitt ist
rein lesend: Er baut nur die bereits kontrolliert erzeugbaren Periodensnapshots
aus dem Plan und startet keinen expliziten Periodenrunner.

Beispiel:

```powershell
python -m ims.engine.explicit_period_transition_diagnostics tests/fixtures/replay_vu14_period_plan.json
python -m ims.engine.explicit_period_transition_diagnostics tests/fixtures/replay_vusk1_period_plan.json
```

Die stabile JSON-Antwort nutzt
`mode = "explicit_period_transition_diagnostics"` und enthaelt unter anderem:

- `transition_count`;
- `global_periods`;
- je Uebergang `from_period`, `to_period`, `from_global_period`,
  `to_global_period`;
- `insurer_ids` und `policyholder_ids`;
- explizite Update-Ziele und Update-Felder;
- `vu_carryover_planned` und `vn_carryover_planned`;
- Carryover-Kandidatenlisten fuer gemeinsam vorhandene Versicherer und VN;
- `carryover_source_fields` als Feldgrenze der bereits portierten
  Carryover-Bausteine;
- `writes_performed = false`;
- `execution_performed = false`;
- `simulation_performed = false`;
- `automatic_historical_rule_selection_performed = false`.

## Ursprung und Mapping

Die Altcode-Spur bleibt konservativ:

- `legacy_c/` enthaelt in diesem Stand keine lesbare historische C-Quelle.
- Die fachliche Spur laeuft ueber die bereits dokumentierten
  Periodenplan-Schnitte fuer Agrsich-Exports, Kontext-Overrides und den
  expliziten VU/VN-Periodenrunner.
- Die ersten Eingaben sind `replay_vu14_period_plan.json` fuer `VU14L1.DAT`
  und `replay_vusk1_period_plan.json` fuer `VUSK1L4.DAT`.

Dieser Schnitt portiert keine neue `Vrvu*`- oder `Vrvn*`-Regel. Er macht nur
sichtbar, welche benachbarten Periodenachsen und Subjektmengen fuer einen
spaeteren, engeren Carryover- oder Regel-Slice belegbar sind.

## Aktuelle Befunde

- `VU14L1.DAT`: 4 Perioden, 3 Uebergaenge, globale Perioden `1, 2, 3, 4`,
  Versicherer `14`, keine VN-Policyholder.
- `VUSK1L4.DAT`: 4 Perioden, 3 Uebergaenge, globale Perioden
  `101, 102, 103, 104`, Versicherer `77`, keine VN-Policyholder.
- Beide aktuellen Planfixtures melden deshalb den Hinweis
  `explicit_period_transition_no_policyholders`. Das ist keine Fehlerkorrektur,
  sondern eine offene VN-Abdeckungsgrenze.
- `replay_vn_policyholder_transition_plan.json`: 2 Perioden, 1 Uebergang,
  globale Perioden `21, 22`, Versicherer `11`, VN-Policyholder `21` und
  `vn_carryover_planned = true`. Dieses Anschlussfixture startet ebenfalls
  keinen Runner, loest den `explicit_period_transition_no_policyholders`-Hinweis
  aber gezielt fuer eine minimale VN-Subjektmenge auf.
- Die Diagnose meldet dafuer
  `vn_carryover_candidate_policyholder_ids = [21]` und
  `vn_carryover_candidate_insurer_ids = [11]`. Diese Kandidatenlisten sind nur
  Lesesignale; `vn_carryover_executed` bleibt `false`.

## Grenzen

- kein Runner-Start;
- keine Simulation;
- keine neue Fachlogik;
- keine automatische historische Regelwahl;
- kein HTTP- oder UI-Schreibpfad;
- keine Uebernahme von `VU014PR1.DAT`;
- keine historische Vollgleichheitsbehauptung.
