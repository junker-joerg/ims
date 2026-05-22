# VN-Pflichtversicherungsregel

## Ziel

Dieser Slice portiert den Versicherungsentscheidungsanteil von `Vrvn01` als
kleinen, wiederverwendbaren Python-Regelkern.

## Ursprung im Altcode

- `IMS.E`, `act Vrvn01`, etwa Zeilen 2185 bis 2263

Fachlich relevant sind:

- Startperiode: Uebernahme initialer Versicherungsstatus- und VU-Werte.
- Folgeperioden: Pflichtversicherung beider Sparten mit aktiver
  Versichererauswahl.

## Umsetzung

- `python_port/ims/model/vn_insurance_rules.py`
  - `VNCompulsoryInsuranceRuleDraws`
  - `VNCompulsoryInsuranceRuleResult`
  - `apply_vn_compulsory_insurance_rule`
  - `vn_compulsory_insurance_rule_draws_from_mapping`
- Die erzeugten Entscheidungen verwenden den bestehenden
  `VNInsuranceDecision`-Typ und koennen direkt in den vorhandenen
  Schaden-/Abrechnungspfad gegeben werden.

## Validierung

- Unit-Tests fuer Startperiode, Folgeperioden, Loader und Eingabevalidierung.
- Integrationstest gegen den bestehenden VN-Schaden-/Abrechnungspfad.

## Grenzen

- Keine historische RNG-Folgen-Gleichheit.
- Keine automatische Scheduler-Regelwahl.
- Keine Praeferenz- oder Suchregel.
- Keine Vollsimulation.
