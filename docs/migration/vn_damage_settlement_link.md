# VN-Schaden-Abrechnungs-Kopplung

Dieser Slice verbindet zwei bereits portierte Ausschnitte der historischen
VN-Regeln: den gemeinsamen Schadenerzeugungskern und den deterministischen
Abrechnungskern. Die Verbindung bleibt bewusst explizit und testbar.

## Ursprung im Altcode

- `IMS.E`, `act Vrvn01`
- `IMS.E`, `act Vrvn02`
- `IMS.E`, `act Vrvn03`

Die historischen Regeln ziehen je Sparte einen Schaden und schreiben danach,
abhaengig von der Versicherungsentscheidung, VN- und VU-Zustand fort. Die
Python-Abbildung haelt diese Schritte getrennt, fuehrt nun aber den belegten
Uebergang vom Schadenresultat zum Settlement-Snapshot ein.

## Python-Abbildung

Die Kopplung liegt in `python_port/ims/model/vn_rules.py`.

Wichtige Typen und Funktionen:

- `VNInsuranceDecision`
- `build_vn_settlement_snapshot_from_damage_result`
- `load_vn_insurance_decisions_from_mapping`
- `vn_insurance_decision_from_mapping`

`build_vn_settlement_snapshot_from_damage_result` uebernimmt die Schaeden aus
`VNDamageRuleResult` und kombiniert sie mit expliziten
Versicherungsentscheidungen. Daraus entsteht ein `VNSettlementSnapshot`, der
vom bestehenden Abrechnungskern verarbeitet werden kann.

## Zaehler-Fallback

Wenn ein Versicherer nur den skalaren `policyholders_current` besitzt und noch
kein `policyholders_current_sector` gesetzt ist, erhaelt das erste sektorielle
Settlement diesen vorhandenen Bestand. Dadurch wird ein Bestand von z. B. `5`
bei einer neuen versicherten Entscheidung zu `6` fortgeschrieben, statt durch
einen leeren Sektorvektor auf `1` zurueckzufallen.

Die konkrete Sektorverteilung eines rein skalaren Vorbestands ist historisch in
diesem Slice nicht weiter ableitbar. Konservativ wird der Skalar beim ersten
betroffenen Sektor eingetragen, damit der Gesamtzaehler erhalten bleibt.

## Annahmen und Grenzen

- Versichererwahl, Praeferenzwahl und Pflichtversicherungslogik bleiben
  ausserhalb dieses Slices.
- Die historischen Normalziehungen werden nicht versteckt erzeugt; sie muessen
  weiterhin explizit im `VNDamageRuleResult` vorliegen.
- Keine automatische Szenario- oder Scheduler-Kopplung.
- Keine Vollsimulation und keine Behauptung historischer Vollgleichheit.
