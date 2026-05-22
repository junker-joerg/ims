# VU/VN-Periodendiagnosen

## Ziel

Die direkten VU- und VN-Mehrperiodenrunner berichten lokale und globale
Periodenachsen konsistent. Das schliesst die Diagnose-Luecke zwischen den
primaeren Runnern und den Replay-/expliziten Periodenpfaden.

## Umfang

- `VUForeignInfoMultiPeriodRunResult` erhaelt `processed_local_periods` und
  `processed_global_periods`.
- `VNSettlementMultiPeriodRunResult` erhaelt `processed_local_periods`.
- Bestehende `processed_periods`-Bedeutungen bleiben kompatibel erhalten.
- Tests belegen die getrennte lokale und globale Achse.

## Grenzen

- Keine neue VU- oder VN-Regelentscheidung.
- Keine automatische Schedulerkopplung.
- Keine Vollsimulation und keine Behauptung historischer Vollgleichheit.
