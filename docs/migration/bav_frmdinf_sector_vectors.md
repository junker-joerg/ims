# BAV-Frmdinf: Sparten- und Risikovektoren

Dieser Schritt korrigiert den portierten BAV-Frmdinf-Zustand dort, wo der
historische Code bereits eindeutig ist: Die zentralen Fremdinformationen sind
keine Skalarwerte.

## Historische Grundlage

`IMS.E` fuehrt im `Frmdinf`-Block die VU-bezogenen Fremdinformationen
spartengetrennt:

- `Dp[0..1]`
- `Dw[0..1]`
- `Pm[0..1]`
- `Wm[0..1]`
- `Mp[0..1]`
- `Mw[0..1]`

Die VN-bezogene Fremdinformation `Dg[0..1]` ist risikogetrennt.

## Was dieser Schritt leistet

- der Python-BAV-Servicezustand fuehrt diese Felder als Zweiervektoren
- `scenario_loader` kann sektor- bzw. risikospezifische Vorperiodenwerte laden
- vorhandene Skalar-Fixtures bleiben konservativ lesbar, indem Skalarwerte auf
  beide Sektoren gespiegelt werden
- die bisherige Aktivitaetsbasis des portierten Frmdinf-Slices bleibt unveraendert

## Bewusst nicht enthalten

- keine vollstaendige Aktivierungsschock-Semantik
- keine vollstaendige `akvu`-/`akvn`-Rekonstruktion aus dem Altcode
- keine VU-/VN-Verhaltensregelportierung
- keine historische Vollsimulation

## Naechster sinnvoller Schritt

Ein folgender fachlicher PR kann auf dieser Struktur aufsetzen und einen klar
abgegrenzten VU- oder VN-Regelausschnitt lesen, der diese Fremdinformationen
tatsaechlich verwendet.
