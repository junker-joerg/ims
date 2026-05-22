# VN-Zufallsstrom und Vrvn02-Auswahlbasis

## Ziel

Dieser Slice haertet die gerade portierten VN-Zufallspfade, bevor weitere
VN-Wahlregeln darauf aufbauen:

- fehlende VN-Schadendraws laufen in Mehrperiodenlaeufen ueber einen gemeinsamen
  RNG-Strom weiter.
- Vrvn02 erzwingt die aktive VU-Auswahl fuer beide Sparten vor dem
  Versicherungsstatus-Zweig.

## Ursprung im Altcode

- `IMS.E`, `act Vrvn01` bis `Vrvn03`: VN-Schadenlogik mit Normalziehungen.
- `IMS.E`, `act Vrvn02`: Zufallsversicherung mit `myrndf()`-Statusziehung und
  aktiver VU-Auswahl je Sparte.

## Umsetzung

- `python_port/ims/engine/vn_rule_runner.py`
  - zieht fehlende VN-Schadendraws in Mehrperiodenlaeufen aus einem gemeinsamen
    RNG des ersten geladenen Periodenkontexts.
- `python_port/ims/model/vn_insurance_rules.py`
  - waehlt fuer jede Sparte einen aktiven Versicherer aus.
  - reicht den Versicherer nur bei versicherten Entscheidungen als
    `insurer_id` in den bestehenden Abrechnungspfad weiter.

## Validierung

- Regressionstest fuer fortlaufende Normalziehungen ueber zwei VN-Perioden.
- Regressionstest fuer Vrvn02 ohne aktive Versicherer, auch wenn beide Sparten
  unversichert bleiben.
- Regressionstest fuer sichtbare, aber nicht abgerechnete VU-Auswahl bei
  unversicherten Sparten.

## Grenzen

- Keine historische RNG-Folgen-Gleichheit.
- Keine automatische historische Scheduler- oder Regelwahl.
- Keine Vollsimulation.
