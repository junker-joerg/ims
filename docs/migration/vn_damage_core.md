# VN-Schadenerzeugung aus Vrvn01 bis Vrvn03

Dieser Slice portiert den gemeinsamen Schadenerzeugungskern der historischen
VN-Regeln `Vrvn01`, `Vrvn02` und `Vrvn03`. Er bleibt bewusst eine pure
Berechnung mit explizit uebergebenen Normalziehungen.

## Ursprung im Altcode

- `IMS.E`, `act Vrvn01`
- `IMS.E`, `act Vrvn02`
- `IMS.E`, `act Vrvn03`

In allen drei Regeln wird je Sparte dieselbe Form genutzt:

- `s1 = (sw1 > normal()) * (a + b * normal())`
- `s2 = (sw2 > normal()) * (c + d * normal())`

Im Aenderungsschockfall werden die alternativen Parameterpaare verwendet.

## Python-Abbildung

Der Kern liegt in `python_port/ims/model/vn_damage_rules.py`.

Wichtige Typen und Funktionen:

- `VNDamageRuleParameters`
- `VNDamageRuleDraws`
- `VNDamageRuleResult`
- `apply_vn_damage_rule`
- `vn_damage_rule_parameters_from_mapping`
- `vn_damage_rule_draws_from_mapping`

Die Funktion erwartet:

- Schadenwahrscheinlichkeits-Schwellen je Sparte, historisch `Sw`
- explizite Trigger-Normalziehungen je Sparte
- explizite Hoehen-Normalziehungen je Sparte
- Normal- und Schockparameter

Das Ergebnis liefert die berechneten Schaeden, die Eintrittsflags und die
verwendeten Draws zurueck.

## Annahmen und Grenzen

- Keine versteckte RNG-Nutzung; alle Zufallsziehungen werden explizit uebergeben.
- Keine Versichererwahl, keine Praeferenzlogik, keine Pflichtversicherungslogik.
- Keine automatische Kopplung an den VN-Settlement-Runner aus dem vorherigen Slice.
- Negative Schadenhoehen werden nicht still gekappt, weil der Altcode die Formel
  ebenfalls direkt schreibt.
- Keine Vollsimulation und keine Behauptung historischer Vollgleichheit.
