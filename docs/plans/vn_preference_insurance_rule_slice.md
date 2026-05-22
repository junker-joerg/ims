# VN-Praeferenzversicherungsregel

## Ziel

Dieser Slice portiert den Versicherungsentscheidungsanteil von `Vrvn03` als
reviewbaren Python-Regelkern.

## Ursprung im Altcode

- `IMS.E`, `act Vrvn03`, etwa Zeilen 2627 bis 2805

Fachlich relevant sind:

- Startperiode: Uebernahme initialer Versicherungsstatus- und VU-Werte.
- Folgeperioden: Statusbildung aus subjektiver Schadenwahrscheinlichkeit und
  Schwellen.
- VU-Auswahl: maximale aktive Werbung je Sparte, Zufallsfallback bei
  Null-Werbung.

## Umsetzung

- `python_port/ims/model/vn_insurance_rules.py`
  - `VNPreferenceInsuranceRuleParameters`
  - `VNPreferenceInsuranceRuleDraws`
  - `VNPreferenceInsurerInput`
  - `VNPreferenceInsuranceRuleResult`
  - `apply_vn_preference_insurance_rule`
  - Mapping-Loader fuer Parameter, Draws und aktive VU-Werbebloecke
- Die erzeugten Entscheidungen verwenden den bestehenden
  `VNInsuranceDecision`-Typ und koennen direkt in den vorhandenen
  Schaden-/Abrechnungspfad gegeben werden.

## Validierung

- Unit-Tests fuer Startperiode, Statusschwellen, Praeferenzwahl,
  Zufallsfallback und Eingabevalidierung.
- Integrationstest gegen den bestehenden VN-Schaden-/Abrechnungspfad.

## Grenzen

- Keine historische RNG-Folgen-Gleichheit.
- Die diagnostischen Praeferenzscores normalisieren je Sparte; die historische
  Risiko-2-Nenner-Eigenheit wird nicht als Score-Diagnose nachgebildet, weil sie
  die Versichererauswahl nicht veraendert.
- Keine automatische Scheduler-Regelwahl.
- Keine Such- oder Beste-Regel.
- Keine Vollsimulation.
