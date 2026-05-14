# Legacy-Agrsich-Validierungsschritt für Versichererexporte

Dieser PR führt einen ersten echten Alt-/Neu-Vergleich für den Versicherer-Agrsich-Slice ein.
Validiert werden gezielt die historischen Versichererdateien `VU14L1.DAT` und `VUSK1L4.DAT`
gegen kleine, bewusst ausgerichtete Python-Validierungsfixtures.

## Was jetzt mit echten Legacy-Dateien validiert wird

- Parserpfad für historische Versicherer-Agrsich-Dateien mit Header und Datenzeilen
- Zeilenebener Vergleich eines Python-Exports gegen echte Legacy-Zeilen
- globale Periode sowie alle zwölf Versicherer-Metriken
- Stufe I für `VU14L1.DAT` und Stufe IV für `VUSK1L4.DAT`

## Welche Modellkorrektur daraus folgt

Die validierten Legacy-Dateien widersprechen einer skalar modellierten Reservegröße.
Für den Versicherer-Agrsich-Export werden aktuelle Reserven daher nun sektorgetrennt als
`reserves_current[0] -> Rs1` und `reserves_current[1] -> Rs2` geführt und aggregiert.

## Was dieser PR noch nicht leistet

- kein VN-Legacy-Vergleich
- kein vollständiger historischer Mehrperioden-Neulauf aus Altinitialdaten
- keine Vollvalidierung der kompletten Zeitreihe aller Versichererdateien
- keine Ausweitung auf weitere Altdateifamilien
- keine Behauptung historischer Vollgleichheit des gesamten Modells

## Sinnvoller Anschluss für PR 28

PR 28 sollte den gleichen Referenzpfad für VN-Dateien aufbauen, weitere echte Legacy-Dateien
aufnehmen und den Alt-/Neu-Vergleich über mehr Perioden und mehr Dateifamilien verbreitern,
ohne vorschnell eine vollständige Historienportierung zu behaupten.
