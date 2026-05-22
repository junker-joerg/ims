# Plan: VU-Zufallsdraw-Basis fuer Vrvu01/Vrvu02

## Ziel

Die bereits portierten Vrvu01-/Vrvu02-Formelkerne sollen im VU-Periodenrunner
reproduzierbare Draws aus dem vorhandenen Python-RNG beziehen koennen, wenn ein
Snapshot keine expliziten Draw-Vektoren enthaelt.

## Ursprung

- `IMS.E`, `act Vrvu01`
- `IMS.E`, `act Vrvu02`
- `Vrvu01` nutzt vier `myrndf()`-Ziehungen.
- `Vrvu02` nutzt vier `normal()`-Ziehungen.

## Umsetzung

- Explizite `random_draws` und `normal_draws` bleiben weiterhin moeglich.
- Fehlen die Draws, kann die Snapshot-Anwendung eine Runner-Draw-Quelle verwenden.
- Der VU-Periodenrunner erzeugt diese Draws aus `SimulationContext.rng_seed`.
- Der Regelkern bleibt deterministisch und erhaelt weiterhin konkrete Draw-Vektoren.

## Grenzen

- Keine Portierung des historischen IMS/ESS-RNG.
- Keine Behauptung historischer RNG-Gleichheit.
- Keine automatische historische Regelwahl.
