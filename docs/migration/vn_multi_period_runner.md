# VN-Mehrperiodenrunner

Dieser Slice erweitert den expliziten VN-Periodenpfad um einen kleinen
deterministischen Mehrperiodenlauf. Er verarbeitet mehrere vollstaendig
ausformulierte Periodenszenarien, laedt sie ueber den bestehenden
Szenario-Loader und fuehrt pro Periode den VN-Schaden-/Settlement-Runner aus.

## Ursprung im Altcode

- `IMS.E`, `act Vrvn01`
- `IMS.E`, `act Vrvn02`
- `IMS.E`, `act Vrvn03`
- periodische VN-Aktionen im historischen PlanVN-Umfeld

Die historische Ablaufsteuerung wird nicht portiert. Der neue Runner bildet
nur den belegten, expliziten Schaden- und Abrechnungspfad ueber mehrere
Perioden ab.

## Python-Abbildung

Der Runner liegt in `python_port/ims/engine/vn_rule_runner.py`.

Wichtige Typen und Funktionen:

- `VNSettlementMultiPeriodRunResult`
- `run_loaded_vn_settlement_period`
- `run_vn_settlement_period_from_mapping`
- `run_vn_settlement_period_from_fixture`
- `run_vn_settlement_multi_period_from_mappings`
- `run_vn_settlement_multi_period_from_fixture`

Mehrperioden-Fixtures koennen entweder direkt eine Liste von
Periodenszenarien enthalten oder ein Objekt mit dem Feld `periods`.

## Validierungen

- Der Mehrperiodenlauf verlangt mindestens eine Periode.
- Globale Periodenpositionen muessen eindeutig und streng steigend sein. Die
  globale Position wird aus `run_index`, `max_periods` und `period` berechnet,
  damit mehrere Laeufe mit gleicher lokaler Periodennummer sauber auf einer
  gemeinsamen Zeitachse validiert werden koennen.
- `processed_periods` enthaelt weiterhin die lokalen Periodennummern der
  Eingabeszenarien; `processed_global_periods` enthaelt die validierte globale
  Reihenfolge.
- Innerhalb einer Periode darf ein VN nicht gleichzeitig ueber
  `vn_damage_settlement_snapshots` und `vn_settlement_snapshots` adressiert
  werden. Diese Regel gilt schon beim Laden eines Szenarios und nochmals beim
  direkten Runner-Aufruf mit bereits konstruierten Snapshots.
- Doppelte VN-Ziele innerhalb einer Snapshot-Liste werden vor Regelanwendung
  abgelehnt.

## Annahmen und Grenzen

- Keine automatische Zustandsfortschreibung zwischen Perioden.
- Keine Portierung der historischen Versichererwahl, Praeferenzbildung oder
  Pflichtversicherungslogik.
- Keine versteckte RNG-Nutzung; alle Zufallswerte bleiben explizite
  Snapshot-Eingaben.
- Keine Vollsimulation und keine Behauptung historischer Vollgleichheit.
