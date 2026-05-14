# Agrsich-Writer und Referenzvergleich: erste echte Dateiausgabe

Dieser PR erweitert den bisherigen Agrsich-Export-Slice substanziell um eine erste echte
Dateischreibstufe sowie einen ersten Referenzvergleich. Der Stand bleibt bewusst konservativ:
noch keine Behauptung historischer Vollgleichheit und noch kein Vergleich gegen echte Legacy-Originaldateien.

## Substanziell erweitert

- erste echte Dateischreibung für Agrsich-Exporttabellen
- historisch orientiertes Header- und Append-Verhalten ohne doppelte Kopfzeilen
- zeichenweiser Vergleich erzeugter Dateien gegen kuratierte Referenzangaben
- Vorbereitung einer späteren Alt-/Neu-Vergleichsinfrastruktur

## Historische Ausgabesemantik jetzt angenähert

- historisch orientierte Dateinamen und globale Periodennummer bleiben erhalten
- Header werden nur beim ersten Schreiben gesetzt, weitere Läufe hängen Datenzeilen an
- Exporttabellen werden in eine disk-nahe Repräsentation überführt

## Referenzvergleichsgrenze

Der aktuelle Referenzvergleich läuft bewusst gegen kuratierte Referenzdateien unter `tests/references/agrsich/`.
Diese Dateien basieren auf dem aktuellen Test-Setup und sind noch keine echten historischen Originaldateien.

## Was für einen späteren echten Legacy-Vergleich noch fehlt

- echte historische Referenzdateien im Repo oder anderweitig nachvollziehbar bereitgestellt
- breitere Abdeckung weiterer Agrsich-Dateien und Messgrößen
- zusätzliche Format- und Randfallprüfung gegen Altbestände
- spätere Einbindung in vollständiger ausgesteuerte Simulationsläufe
