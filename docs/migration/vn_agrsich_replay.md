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

- `VNAgrsichReplayPeriodResult`
- `VNAgrsichReplayRunResult`
- `run_vn_agrsich_replay_from_mappings`
- `run_vn_agrsich_replay_from_fixture`

Der Ablauf pro Periode ist:

1. Szenario laden und validieren.
2. Explizite VN-Schaden-/Settlement-Snapshots anwenden.
3. Agrsich-Records aus dem mutierten Python-Zustand sammeln.
4. Agrsich-Exporttabellen schreiben.

## Validierungen

- Die globalen Perioden muessen nichtleer, eindeutig und streng steigend sein.
- Die bestehenden Szenario- und VN-Snapshot-Validierungen bleiben vorgeschaltet.
- Tests pruefen, dass exportierte VU-/VN-Zeilen aus dem nach Regelanwendung
  veraenderten Zustand stammen.

## Annahmen und Grenzen

- Keine automatische Zustandsfortschreibung zwischen Perioden.
- Keine Portierung der historischen Versichererwahl, Praeferenzbildung oder
  Pflichtversicherungslogik.
- Keine versteckte RNG-Nutzung.
- Keine Legacy-Gleichheitsbehauptung und keine Vollsimulation.
