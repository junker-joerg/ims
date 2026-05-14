# Legacy-VN-Validierungsschritt

Dieser Schritt erweitert die echte Legacy-Validierung von Versichererdateien auf
einen ersten, eng begrenzten VN-Agrsich-Slice.

## Validierter Bestand

Aus dem historischen Archiv `WVEMOD1.ZIP` wurden zwei echte VN-Agrsich-Dateien
in den Testbestand übernommen:

- `tests/references/legacy_agrsich/IMSVNR05.DAT`
- `tests/references/legacy_agrsich/IMSVNSK1.DAT`

Der neue Parser liest Header, alle Datenzeilen, globale Periode und die elf
VN-Metriken:

`Vu1 Vs1 Vp1 Ev1 Sh1 Vu2 Vs2 Vp2 Ev2 Sh2 Vm`

Die Tests prüfen die Dateien mit 500 Datenzeilen sowie je eine gezielte
Alignment-Zeile für Regel- und Gesamtdatei. Das ist bewusst ein
Validierungsslice und noch kein vollständiger historischer Neulauf.

## Modellkorrektur

Die Legacy-VN-Dateien zeigen getrennte Werte für `Vu1`/`Vu2` und `Ev1`/`Ev2`.
Daher wird der bisherige kleine Policyholder-Agrsich-Ausschnitt konservativ
erweitert:

- `chosen_insurer_sector_current: list[int | None]` für `Vu1` und `Vu2`
- `end_wealth_sector_current: list[float]` für `Ev1` und `Ev2`
- `end_wealth_current` bleibt als skalarer `Vm`-Wert erhalten

Wenn keine sektorgetrennte Auswahl angegeben ist, fällt der Code auf den
bisherigen skalaren `chosen_insurer_current` zurück. Bestehende Szenarien bleiben
damit ladbar.

## Grenzen

- Keine Vollvalidierung aller VN-Dateien.
- Keine Aussage, dass alle historischen VN-Regeln fachlich portiert sind.
- Keine Ableitung neuer Fachsemantik über die belegten Spaltenpositionen hinaus.
- Kein Multi-Perioden-Neulauf aus Altinitialdaten.

## Anschluss

Der nächste PR sollte weitere VN-Dateifamilien nur dann hinzufügen, wenn die
jeweiligen Header, Periodenbereiche und Feldpositionen explizit geprüft werden.
Danach kann ein Multi-Perioden-Harness kleine Altinitialdaten-Slices gegen
mehrere echte Ausgabegruppen laufen lassen.
