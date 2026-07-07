# Backlog weiterer Legacy-Dateifamilien

Diese Liste verhindert, dass einzelne grüne Agrsich-Slices als
Gesamtgleichheit des Modells missverstanden werden.

## Bereits angebunden

- Versicherer-Agrsich: `VU14L1.DAT`, `VUSK1L1.DAT` bis `VUSK1L5.DAT` als
  SK1-Zeitfenster auf derselben unterstuetzten Aggregatstufe
- VN-Agrsich: `IMSVNR01.DAT` bis `IMSVNR05.DAT`, `IMSVNSK1.DAT`

## Naheliegende nächste Kandidaten

- Weitere VN-Regeldatei `IMSVNR06.DAT`.
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

- `IMSVNR06.DAT` und Abgleich der vollstaendigen IMSVNR-Familie;
- danach `IMSVNVK*.DAT` und `IMSVUVK*.DAT` aus den ZIP-Archiven.

## Rest-PR-Planung

- PR 1: `IMSVNR01.DAT` und `IMSVNR02.DAT` uebernehmen und validieren
  (erledigt).
- PR 2: `IMSVNR03.DAT` und `IMSVNR04.DAT` uebernehmen und validieren
  (dieser Schnitt).
- PR 3: `IMSVNR06.DAT` uebernehmen; `IMSVNR05.DAT` mit der Gesamtfamilie
  abgleichen.
- PR 4: Coverage-/Next-Family-Plan so aktualisieren, dass `policyholder_rule`
  nach vollstaendiger IMSVNR-Abdeckung als covered erscheint.
- PR 5: VN-Klassenaggregate `IMSVNVK*.DAT` vorbereiten, aber erst nach
  separater Header-/Feldpruefung.
- PR 6: Versicherer-Klassenaggregate `IMSVUVK*.DAT` vorbereiten.
- PR 7: Parameterausgaben wie `VU014PR1.DAT` nur nach eigener Feldklaerung
  vorbereiten.
- PR 8+: Schmale fachliche VU-/VN-Regel- oder Carryover-Slices aus vorhandenen
  Planfixtures, weiterhin ohne Vollgleichheitsbehauptung.

## Validierungsregel

Jede Dateifamilie bekommt:

- echte Referenzdatei im Testbestand,
- Parser mit whitespace-robustem Headervergleich,
- mindestens eine positive Alignment-Zeile,
- mindestens einen Negativtest,
- Dokumentation der noch nicht validierten Bereiche.
