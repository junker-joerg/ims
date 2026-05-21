# VN-Agrsich-Replay

Dieser Slice verbindet den expliziten VN-Periodenrunner mit dem bestehenden
Agrsich-Exportpfad. Mehrere explizite VN-Periodenszenarien werden geladen,
ueber die portierten VN-Schaden-/Abrechnungskerne ausgefuehrt und danach als
Agrsich-Tabellen geschrieben.

## Ursprung im Altcode

- `IMS.E`, `act Vrvn01`
- `IMS.E`, `act Vrvn02`
- `IMS.E`, `act Vrvn03`
- historische VN-Agrsich-Ausgaben wie `IMSVNR*.DAT` und `IMSVNSK1.DAT`

Die historischen VN-Aktionen erzeugen Periodenzustaende, die in Agrsich-Dateien
sichtbar werden. Der Python-Pfad erzeugt solche Exportzeilen aus explizit
gelieferten Periodenszenarien und portierten VN-Kernen.

## Python-Abbildung

Der neue Runner liegt in `python_port/ims/engine/vn_agrsich_replay.py`.

Wichtige Typen und Funktionen:

- `VNAgrsichLegacyTarget`
- `VNAgrsichReplayPeriodResult`
- `VNAgrsichReplayRunResult`
- `run_vn_agrsich_replay_from_mappings`
- `run_vn_agrsich_replay_from_fixture`

Das Laufergebnis trennt lokale und globale Periodendiagnosen:
`processed_local_periods` enthaelt die lokalen `context.period`-Werte,
`processed_global_periods` enthaelt die validierte globale Zeitachse.

Der Ablauf pro Periode ist:

1. Szenario laden und validieren.
2. Explizite VN-Schaden-/Settlement-Snapshots anwenden.
3. Agrsich-Records aus dem mutierten Python-Zustand sammeln.
4. Agrsich-Exporttabellen schreiben.

## Validierungen

- Die globalen Perioden muessen nichtleer, eindeutig und streng steigend sein.
- Lokale Perioden duerfen in unterschiedlichen Runs erneut auftreten, solange
  die globale Periodenfolge eindeutig und steigend bleibt.
- Die bestehenden Szenario- und VN-Snapshot-Validierungen bleiben vorgeschaltet.
- Tests pruefen, dass exportierte VU-/VN-Zeilen aus dem nach Regelanwendung
  veraenderten Zustand stammen.
- Optional kann `carry_forward_vn_state=True` gesetzt werden. Dann wird derselbe
  kontrollierte VN-State-Carryover wie im expliziten VN-Mehrperiodenrunner vor
  dem Folgeperiodenlauf angewendet und als `VNAgrsichReplayRunResult.carryovers`
  diagnostiziert.
- Das Fixture-Feld `carry_forward_vn_state` muss ein JSON-Boolean sein.
- Optional angegebene Legacy-Ziele werden gegen die ueber alle Perioden
  zusammengefuehrten Exporttabellen verglichen.

## Annahmen und Grenzen

- Keine automatische Zustandsfortschreibung zwischen Perioden ohne explizites
  Carryover-Opt-in.
- Keine Portierung der historischen Versichererwahl, Praeferenzbildung oder
  Pflichtversicherungslogik.
- Keine versteckte RNG-Nutzung.
- Keine Legacy-Gleichheitsbehauptung und keine Vollsimulation.
