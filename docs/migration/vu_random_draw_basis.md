# VU-Zufallsdraw-Basis fuer Vrvu01/Vrvu02

## Ziel

Dieser Slice verbindet die portierten Vrvu01-/Vrvu02-Formelkerne mit einer
reproduzierbaren Python-RNG-Basis im VU-Periodenrunner. Szenarien koennen weiterhin
explizite Draw-Vektoren angeben; fehlen sie, erzeugt der Runner die vier benoetigten
Draws aus dem `SimulationContext`.

## Ursprung im Altcode

- `IMS.E`, `act Vrvu01`
- `IMS.E`, `act Vrvu02`

`Vrvu01` verwendet vier `myrndf()`-Ziehungen fuer Praemien und Werbung. `Vrvu02`
verwendet vier `normal()`-Ziehungen fuer dieselben Zielgroessen.

## Python-Abbildung

- `python_port/ims/engine/rng.py`
  - ergaenzt einen Standardnormal-Draw auf Basis des vorhandenen Python-RNG.
- `python_port/ims/model/vu_rules.py`
  - `random_draws` und `normal_draws` sind auf Snapshot-Ebene optional.
  - direkte Snapshot-Anwendung benoetigt bei fehlenden Draws eine explizite
    Draw-Quelle.
- `python_port/ims/engine/vu_rule_runner.py`
  - erzeugt fehlende Vrvu01-Draws ueber `rand_uniform_0_1`.
  - erzeugt fehlende Vrvu02-Draws ueber `rand_normal_standard`.
  - verwendet den an `SimulationContext` gebundenen RNG, der aus `rng_seed`
    initialisiert wird.

## Grenzen

- Der historische IMS/ESS-RNG ist damit nicht portiert.
- Die Draw-Sequenz ist reproduzierbar innerhalb des Python-Ports, aber keine
  Aussage ueber historische Vollgleichheit.
- Die historische Regelwahl bleibt weiterhin explizit ueber Snapshots gesteuert.
