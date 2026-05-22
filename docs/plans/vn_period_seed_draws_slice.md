# VN-Mehrperioden-Draws mit Perioden-Seeds

## Ziel

Dieser Slice klaert die RNG-Semantik fuer fehlende VN-Schadendraws in
Mehrperiodenlaeufen:

- gleiche Seeds in allen Perioden bedeuten einen fortlaufenden Draw-Strom.
- unterschiedliche Perioden-Seeds bleiben periodenspezifisch wirksam.

## Ursprung im Altcode

- `IMS.E`, `act Vrvn01` bis `Vrvn03`: VN-Schadenlogik mit Normalziehungen.

Die historische RNG-Folge wird weiterhin nicht als identisch behauptet. Der
Slice sichert die reproduzierbare Python-Abbildung fuer explizite
Mehrperiodenszenarien.

## Umsetzung

- `python_port/ims/engine/vn_rule_runner.py`
  - waehlt die Draw-Quelle anhand der geladenen Perioden-Seeds.
  - teilt einen RNG nur, wenn alle Perioden denselben Seed tragen.
  - verwendet bei abweichenden Seeds den jeweiligen Periodenkontext.

## Validierung

- Regressionstest fuer fortlaufende Draws bei gleichen Seeds.
- Regressionstest fuer periodenspezifische Draws bei unterschiedlichen Seeds.

## Grenzen

- Keine historische RNG-Kompatibilitaet.
- Keine automatische historische VN-Regelwahl.
- Keine Vollsimulation.
