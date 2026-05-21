# Expliziter VN-Schadenperiodenschritt

Dieser Slice fuehrt einen expliziten Periodenpfad fuer VN-Schaden und
VN-Abrechnung ein. Er nutzt die bereits portierten Kerne:

- `apply_vn_damage_rule` fuer die Schadenerzeugung
- `apply_vn_settlement_snapshot` fuer die deterministische Abrechnung

## Ursprung im Altcode

- `IMS.E`, `act Vrvn01`
- `IMS.E`, `act Vrvn02`
- `IMS.E`, `act Vrvn03`

Die historischen VN-Regeln berechnen Schaeden und schreiben danach, abhaengig
von der Versicherungsentscheidung, VN- und VU-Zustand fort. Der neue
Python-Pfad bildet nur diesen belegten Ablauf ab, wenn alle stochastischen und
wahlbezogenen Eingaben bereits explizit vorliegen.

## Python-Abbildung

Die fachlichen Typen liegen in `python_port/ims/model/vn_rules.py`.
Der Periodeneinstieg liegt in `python_port/ims/engine/vn_rule_runner.py`.

Wichtige Typen und Funktionen:

- `VNDamageSettlementSnapshot`
- `VNDamageSettlementApplication`
- `apply_vn_damage_settlement_snapshot`
- `apply_vn_damage_settlement_snapshots`
- `load_vn_damage_settlement_snapshots_from_mapping`
- `run_vn_settlement_period(..., damage_settlement_snapshots=...)`

Szenarien koennen optional `vn_damage_settlement_snapshots` enthalten. Der
Szenario-Loader prueft dabei frueh:

- unbekannte VN-Ziele
- unbekannte VU-Referenzen in versicherten Entscheidungen
- doppelte VN-Ziele innerhalb der expliziten Schaden-Abrechnungs-Snapshots
- Ueberlappungen mit direkten `vn_settlement_snapshots`

## Normalisierung

Der Adapter `build_vn_settlement_snapshot_from_damage_result` normalisiert
`previous_wealth_sector` nun wie der Mapping-Loader auf zwei Sparten. Damit
fuehrt ein einspaltiger Vorvermoegensvektor nicht erst spaeter im
Abrechnungskern zu einem `IndexError`.

## Annahmen und Grenzen

- Die historischen Normalziehungen werden nicht im Runner erzeugt.
- Versichererwahl, Praeferenzbildung und Pflichtversicherung bleiben
  ausserhalb dieses Slices.
- Explizite Settlement-Snapshots und explizite Schaden-Abrechnungs-Snapshots
  koennen im selben Periodenlauf genutzt werden, muessen aber disjunkte VN
  adressieren.
- Keine Vollsimulation und keine Behauptung historischer Vollgleichheit.
