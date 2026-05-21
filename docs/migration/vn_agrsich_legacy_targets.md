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
- `VNAgrsichReplayRunResult.legacy_report`
- `VNAgrsichReplayRunResult.written_legacy_report_files`
- `run_vn_agrsich_replay_from_mappings(..., legacy_targets=...)`
- Fixture-Feld `legacy_targets`
- optionales Fixture-Feld `legacy_report_name`

Ein Legacy-Ziel beschreibt:

- `legacy_path`
- `export_filename`
- `subject_type` (`policyholder` oder `insurer`)
- optional `tolerance`

Relative `legacy_path`-Werte in Fixtures werden relativ zum Fixture-Verzeichnis
aufgeloest.

Wenn Legacy-Ziele angegeben sind, baut der Runner zusaetzlich aus dem
mehrperiodigen Tabellenvergleich einen `LegacyValidationReport`. Dieser Report
nutzt denselben strukturierten Reportpfad wie die bestehenden Agrsich-
Validierungslaeufe: Datei-, Feld-, Gruppen-, Perioden- und Abweichungssummaries
werden nur aus den bereits berechneten Vergleichsobjekten abgeleitet.

Ein `legacy_report_name` schreibt die zugehoerigen JSON-/CSV-Dateien in das
Replay-Ausgabeverzeichnis. Ohne diesen Namen bleibt der Report bewusst nur im
Rueckgabeobjekt und erzeugt keine zusaetzlichen Dateien.

## Annahmen und Grenzen

- Der Runner waehlt keine Legacy-Dateien automatisch aus.
- Ein erfolgreicher Vergleich belegt nur das konkret angegebene explizite
  Replay-Fixture, keine historische Vollgleichheit.
- Keine neue VN-Wahl-, Praeferenz- oder RNG-Logik.
- Der Report berechnet keine neuen Fachwerte; er strukturiert nur vorhandene
  Legacy-Zielvergleiche.
