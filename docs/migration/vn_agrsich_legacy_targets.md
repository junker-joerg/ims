# VN-Agrsich-Legacy-Ziele

Dieser Slice erweitert den VN-Agrsich-Replay-Runner um optionale
Legacy-Ziele. Nach einem expliziten VN-Replay koennen die erzeugten
Agrsich-Exporttabellen gegen angegebene Referenzdateien verglichen werden.

## Ursprung im Altcode

- historische VN-Agrsich-Ausgaben wie `IMSVNR*.DAT` und `IMSVNSK1.DAT`
- `IMS.E`, `act Vrvn01` bis `Vrvn03` als fachlicher Ursprung der
  VN-Zustandsfortschreibung

## Python-Abbildung

Die Erweiterung liegt in `python_port/ims/engine/vn_agrsich_replay.py`.

Wichtige Typen und Funktionen:

- `VNAgrsichLegacyTarget`
- `VNAgrsichReplayRunResult.legacy_comparison`
- `run_vn_agrsich_replay_from_mappings(..., legacy_targets=...)`
- Fixture-Feld `legacy_targets`

Ein Legacy-Ziel beschreibt:

- `legacy_path`
- `export_filename`
- `subject_type` (`policyholder` oder `insurer`)
- optional `tolerance`

Relative `legacy_path`-Werte in Fixtures werden relativ zum Fixture-Verzeichnis
aufgeloest.

## Annahmen und Grenzen

- Der Runner waehlt keine Legacy-Dateien automatisch aus.
- Ein erfolgreicher Vergleich belegt nur das konkret angegebene explizite
  Replay-Fixture, keine historische Vollgleichheit.
- Keine neue VN-Wahl-, Praeferenz- oder RNG-Logik.
