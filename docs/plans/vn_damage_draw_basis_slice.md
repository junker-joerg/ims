# VN-Schadendraw-Basis

## Ziel

Dieser Slice ergaenzt den expliziten VN-Schaden-/Abrechnungspfad um eine
reproduzierbare Python-Draw-Basis. `vn_damage_settlement_snapshots` duerfen
weiterhin explizite Normalziehungen enthalten, koennen sie im Runner aber auch
weglassen.

## Ursprung im Altcode

- `IMS.E`, `act Vrvn01`
- `IMS.E`, `act Vrvn02`
- `IMS.E`, `act Vrvn03`

Die historischen VN-Regeln ziehen je Sparte zuerst den Trigger fuer den
Schadeneintritt und danach die Schadenhoehe.

## Umsetzung

- `VNDamageSettlementSnapshot.draws` wird optional.
- Der direkte Abrechnungskern verlangt bei fehlenden Draws weiterhin eine
  explizite Draw-Quelle.
- `run_vn_settlement_period` erzeugt fehlende Draws aus dem
  `SimulationContext`-RNG in der Reihenfolge Trigger 1, Hoehe 1, Trigger 2,
  Hoehe 2.

## Annahmen und Grenzen

- Die Python-Draws sind reproduzierbar ueber `rng_seed`.
- Dieser Slice behauptet keine historische RNG-Gleichheit.
- Versichererwahl, Praeferenzlogik und Pflichtversicherung bleiben ausserhalb
  dieses Schritts.
