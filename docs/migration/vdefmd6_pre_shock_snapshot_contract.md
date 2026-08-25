# Vdefmd6-Vorschock-Snapshotvertrag

## Ziel und Mapping

Der Vertrag `pr78-v1` schliesst die in PR 77 markierte automatische
Snapshotableitung fuer einen einzelnen Vorschockzeitpunkt. Der neue Builder
`build_vdefmd6_pre_shock_snapshot_batch` liest die typisierte
`Vdefmd6Population` und bildet die 16 VN-Parameter auf die vorhandenen
`VNInsuranceRuleSnapshot`- und `VNDamageSettlementSnapshot`-Typen ab.

| Historischer Ursprung | Python-Ziel | Entsprechung |
| --- | --- | --- |
| `Vdefmd6`, `Vnauini` | `vdefmd6_population.py` | VN-Gruppen, Aktivierung und 16 Parameter |
| `Myinitvn`, `Sw` | `damage_thresholds` | zwei explizite moderne Schwellen je VN und Periode |
| `Vrvn01` bis `Vrvn06` | `VNInsuranceRuleSnapshot` | sechs vorhandene Regelarten und ihre Inputs |
| gemeinsame Schadenformel | `VNDamageSettlementSnapshot` | vier explizite Normalwerte und Vorschockparameter |
| `Bavauin(..., 0.8, ...)` | Informationskostenfelder | Kostenwert als Input; Vermoegensanwendung noch offen |

## Moderne Draw-Policy

`vdefmd6-modern-period-major-v1` ordnet die VN nach ID. Je VN werden erzeugt:

1. `Sw` fuer Sparte 1 und 2;
2. Schaden-Trigger und -Hoehe fuer Sparte 1;
3. Schaden-Trigger und -Hoehe fuer Sparte 2;
4. regelabhaengige Versicherungsdraws.

Der Vertragsfall Periode 2 erzeugt 990 uniforme Werte und 600 Normalwerte.
Die historischen Schwellen entstehen dagegen in `Myinitvn` vorab fuer alle
Perioden. Zudem bleibt die Operandenreihenfolge der zwei historischen
`normal()`-Aufrufe innerhalb einer C-Multiplikation offen. Der moderne Vertrag
ist daher reproduzierbar, aber nicht historisch RNG-identisch.

## Geschlossene und offene Punkte

Geschlossen sind die typisierte Ableitung fuer 150 aktive Vorschock-VN, die
Parameterabbildung, die moderne Reihenfolge und die Seed-Reproduzierbarkeit.
PR 79 hat die VU-Snapshots ergaenzt. PR 80 hat Informationskosten und die
kontrollierte Mehrperiodenanwendung fuer 2-49 geschlossen. Offen bleiben die
historische RNG- und Same-Slot-Reihenfolge sowie der Schockpfad 50-100.

Damit sind `independent_periods_2_49_ready` und
`full_state_projection_ready` im PR-80-Bericht wahr; `generation_ready` bleibt
falsch. Der PR-78-Bericht zieht
RNG-Werte nur zur Snapshotmaterialisierung; er startet keinen Runner und keine
Simulation. Historische Referenzzeilen werden nicht als Erzeugungsinput
verwendet. Es gibt keine historische Vollgleichheitsbehauptung.
