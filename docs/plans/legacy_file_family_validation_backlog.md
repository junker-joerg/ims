# Backlog weiterer Legacy-Dateifamilien

Diese Liste verhindert, dass einzelne grüne Agrsich-Slices als
Gesamtgleichheit des Modells missverstanden werden.

## Bereits angebunden

- Versicherer-Agrsich: `VU14L1.DAT`, `VUSK1L4.DAT`
- VN-Agrsich: `IMSVNR05.DAT`, `IMSVNSK1.DAT`

## Naheliegende nächste Kandidaten

- Weitere Versicherer-Agrsich-Stufen aus `VUSK1L1.DAT` bis `VUSK1L5.DAT`.
- Weitere VN-Regeldateien aus `IMSVNR01.DAT` bis `IMSVNR06.DAT`.
- VN-Klassenaggregate `IMSVNVK*.DAT`.
- Versicherer-Klassenaggregate `IMSVUVK*.DAT`.
- Parameterausgaben wie `VU014PR1.DAT`, aber nur nach separater Feldklärung.

## Validierungsregel

Jede Dateifamilie bekommt:

- echte Referenzdatei im Testbestand,
- Parser mit whitespace-robustem Headervergleich,
- mindestens eine positive Alignment-Zeile,
- mindestens einen Negativtest,
- Dokumentation der noch nicht validierten Bereiche.
