# Vrvu05-Aktivzaehlerbasis

## Ziel

Dieser Slice verbindet den portierten Vrvu05-/Mark-Up-III-Kern mit dem aktuellen
BAV-Aktivitaetszaehler. Dadurch muss `akvn` nicht mehr in jedem Szenario-Snapshot
doppelt gepflegt werden, sofern der VU-Periodenrunner zuvor die BAV-Aktivitaet
berechnet.

## Ursprung im Altcode

Der fachliche Ursprung bleibt `IMS.E`, `act Vrvu05`:

- Marktanteil je Sparte als `Vn / akvn`
- Nullschutz bei `akvn == 0`

## Python-Abbildung

- `python_port/ims/model/vu_rules.py`
  - `VUMarketShareMarkupRuleSnapshot.active_policyholder_count` ist optional.
  - `apply_vu_market_share_markup_rule_snapshots` nutzt den Snapshot-Wert oder einen
    expliziten Runner-Wert.
- `python_port/ims/engine/vu_rule_runner.py`
  - der Runner berechnet zuerst `compute_extended_foreign_info`
  - anschliessend wird
    `loaded.bav.service_state.activity_state.active_policyholder_count_current`
    an die Vrvu05-Snapshot-Anwendung uebergeben.

Explizite Snapshot-Werte bleiben moeglich und ueberschreiben die Runner-Basis fuer
gezielte Referenz- und Regressionstests.

## Grenzen

- Keine automatische historische Regelwahl.
- Keine Parameterherleitung aus historischen Initialdaten.
- Keine Aussage ueber historische Vollgleichheit.
- Die staerkere Validierung gegen weitere historische Referenzfenster bleibt offen.
