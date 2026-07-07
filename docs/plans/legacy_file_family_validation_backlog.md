# Backlog weiterer Legacy-Dateifamilien

Diese Liste verhindert, dass einzelne grüne Agrsich-Slices als
Gesamtgleichheit des Modells missverstanden werden.

## Bereits angebunden

- Versicherer-Agrsich: `VU14L1.DAT`, `VUSK1L1.DAT` bis `VUSK1L5.DAT`
- VN-Agrsich: `IMSVNR05.DAT`, `IMSVNSK1.DAT`

## Naheliegende nächste Kandidaten

- Weitere VN-Regeldateien aus `IMSVNR01.DAT` bis `IMSVNR06.DAT`.
- VN-Klassenaggregate `IMSVNVK*.DAT`.
- Versicherer-Klassenaggregate `IMSVUVK*.DAT`.
- Parameterausgaben wie `VU014PR1.DAT`, aber nur nach separater Feldklärung.

## Neuer lokaler Kandidatenbestand

Unter `incomming/` liegt nun ein lokaler, nicht versionierter historischer
Kandidatenbestand. Details stehen in
`docs/plans/historical_testdata_inventory.md`. Der Bestand hebt mehrere bisherige
Referenzblocker fachlich auf, wird aber erst in separaten PRs gezielt nach
`tests/references/legacy_agrsich/` uebernommen.

Naechster bevorzugter Uebernahmeschnitt:

- `IMSVNR01.DAT` bis `IMSVNR06.DAT`;
- danach `IMSVNVK*.DAT` und `IMSVUVK*.DAT` aus den ZIP-Archiven.

## Validierungsregel

Jede Dateifamilie bekommt:

- echte Referenzdatei im Testbestand,
- Parser mit whitespace-robustem Headervergleich,
- mindestens eine positive Alignment-Zeile,
- mindestens einen Negativtest,
- Dokumentation der noch nicht validierten Bereiche.
