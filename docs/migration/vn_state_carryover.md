# VN-State-Carryover

Dieser Slice erweitert den expliziten VN-Mehrperiodenrunner um einen
optionalen Zustandstransfer zwischen geladenen Periodenszenarien. Damit koennen
mehrere bereits portierte VN-Schaden-/Abrechnungsperioden auf den mutierten
VU- und VN-Aktuellwerten der Vorperiode aufbauen.

## Ursprung im Altcode

- `IMS.E`, `act Vrvn01`
- `IMS.E`, `act Vrvn02`
- `IMS.E`, `act Vrvn03`
- periodische VN-Aktionen im historischen PlanVN-Umfeld

Die historischen Aktionen schreiben aktuelle VN- und VU-Werte je Periode fort.
Der Python-Pfad bleibt enger: Er fuehrt nur explizit angegebene
Periodenszenarien aus und uebertraegt Zustandswerte nur, wenn der Aufrufer dies
ausdruecklich aktiviert.

## Python-Abbildung

Die Umsetzung liegt in `python_port/ims/engine/vn_rule_runner.py`.

Neue bzw. erweiterte Elemente:

- `VNStateCarryover`
- `VNSettlementPeriodRunResult.insurers`
- `VNSettlementPeriodRunResult.policyholders`
- `VNSettlementMultiPeriodRunResult.carryovers`
- `run_vn_settlement_multi_period_from_mappings(..., carry_forward_vn_state=True)`
- Fixture-Feld `carry_forward_vn_state`

Der Carryover uebertraegt fuer Folgeperioden nur Entitaeten mit gleicher ID.
Bei Versicherern werden aktuelle Praemien, Werbung, Reserven,
Versichertenzaehler und Schadenaggregate weitergereicht. Bei
Versicherungsnehmern werden die aktuellen Versicherungs-, Praemien-, Schaden-
und Vermoegensfelder sowie der zuletzt gewaehlte Versicherer weitergereicht.

## Annahmen und Grenzen

- Der Schalter ist standardmaessig aus; bestehende explizite Periodenszenarien
  behalten ohne Opt-in ihre eigenen Startwerte.
- Fehlende Folgeentitaeten werden nicht erzeugt.
- Snapshot-Inhalte wie Schadenrealisationen, Versicherungsentscheidungen und
  `previous_wealth` bleiben weiterhin explizit.
- Keine neue VN-Wahl-, Praeferenz-, RNG- oder Schedulerlogik.
- Keine Behauptung historischer Vollgleichheit.
