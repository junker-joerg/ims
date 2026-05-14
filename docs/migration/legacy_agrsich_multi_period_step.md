# Mehrperiodiger Legacy-Vergleich fuer validierte Agrsich-Slices

## Ziel

Dieser Schritt baut einen schmalen Multi-Perioden-Rahmen um die bereits vorhandenen echten
Agrsich-Legacy-Vergleiche. Er vergleicht mehrere erzeugte Exportzeilen einer Tabelle gegen
die passenden Periodenzeilen aus den realen Referenzdateien.

Abgedeckt sind derzeit:

- Versicherer-Agrsich-Dateien ueber den bestehenden Parser fuer `VU14L1.DAT` und `VUSK1L4.DAT`
- VN-Agrsich-Dateien ueber den bestehenden Parser fuer `IMSVNR05.DAT` und `IMSVNSK1.DAT`
- positive Mehrperioden-Vergleiche
- gezielte Negativfaelle fuer abweichende Werte und fehlende Legacy-Perioden

## Umsetzung

Die neue Datei `python_port/ims/model/legacy_agrsich_multi_period.py` fuehrt keine neue
Fachsemantik ein. Sie kapselt vorhandene Einzelzeilenvergleiche in tabellenweite
Vergleichsergebnisse:

- `LegacyTableComparison`
- `MultiPeriodLegacyComparison`
- `compare_insurer_export_table_to_legacy(...)`
- `compare_policyholder_export_table_to_legacy(...)`
- `build_multi_period_legacy_comparison(...)`

Jede Exportzeile wird ueber ihre globale Periode einer Legacy-Zeile zugeordnet. Fehlt diese
Zeile in der Referenzdatei, wird dies als expliziter Vergleichsfehler dokumentiert.

## Grenzen

Dieser Schritt ist noch kein vollstaendiger Multi-Perioden-Neulauf aus Altinitialdaten.
Er erzeugt auch keine historische Vollsimulation und behauptet keine Vollgleichheit des
Modells. Die Tests verwenden bewusst bereits vorhandene Legacy-Dateien und konstruieren
Exporttabellen direkt aus belegten Referenzzeilen, um den Vergleichsrahmen selbst zu
validieren.

Noch offen bleiben:

- ein echter Neulauf aus Altinitialdaten ueber mehrere Perioden
- eine vollstaendige Erzeugung aller historischen Agrsich-Dateifamilien
- breitere Validierung weiterer echter Legacy-Dateien
- fachliche Bewertung von Abweichungen, sobald Python-Ausgaben nicht nur aus Referenzzeilen,
  sondern aus einer zusammenhaengenden Simulation stammen

## Anschluss

Der naechste sinnvolle Schritt ist, diesen Rahmen mit einer kleinen, reproduzierbaren
Multi-Perioden-Erzeugung aus Python-Domaenenzustand zu verbinden. Erst danach sollte eine
groessere Altinitialdaten-Pipeline aufgebaut werden.
