# VN-Snapshot-Zielintegritaet

Dieser Slice haertet den expliziten VN-Periodenpfad gegen doppelte
Zieladressierung. Ein Versicherungsnehmer darf in einer Periode nicht zugleich
ueber `vn_damage_settlement_snapshots` und `vn_settlement_snapshots`
angesprochen werden.

## Ursprung im Altcode

- `IMS.E`, `act Vrvn01`
- `IMS.E`, `act Vrvn02`
- `IMS.E`, `act Vrvn03`
- periodische VN-Aktionen im historischen PlanVN-Umfeld

Die historischen VN-Aktionen schreiben den Zustand eines VN fuer die laufende
Periode einmal fort. Der Python-Pfad bietet inzwischen zwei explizite
Eingabeformen: Schaden plus Abrechnung oder direkte Abrechnung. Diese Formen
duerfen fuer denselben VN nicht kombiniert werden, weil beide Pfade VN- und
VU-Zustand mutieren.

## Python-Abbildung

Die erste Schutzlinie liegt im Szenario-Loader
`python_port/ims/io/scenario_loader.py`. Dort werden ueberlappende
`policyholder_id`-Werte zwischen `vn_damage_settlement_snapshots` und
`vn_settlement_snapshots` vor der Konstruktion des geladenen Szenarios
abgelehnt.

Die zweite Schutzlinie bleibt im Runner
`python_port/ims/engine/vn_rule_runner.py`. Damit werden auch programmatische
Aufrufer geschuetzt, die bereits konstruierte Snapshot-Objekte direkt an den
Runner uebergeben.

## Annahmen und Grenzen

- Diese Validierung klaert nur die Integritaet expliziter Snapshot-Eingaben.
- Keine Portierung der historischen Versichererwahl, Praeferenzbildung oder
  Pflichtversicherungslogik.
- Keine automatische Zustandsfortschreibung zwischen Perioden.
- Keine Vollsimulation und keine Behauptung historischer Vollgleichheit.
