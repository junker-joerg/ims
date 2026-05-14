# Vorbereitung Multi-Perioden-Neulauf

Dieser Plan bereitet den späteren Neulauf aus Altinitialdaten vor, ohne bereits
eine historische Vollgleichheit zu behaupten.

## Voraussetzungen

1. Geklärte Altinitialdaten pro kleinem Szenario-Slice.
2. Explizite Zuordnung von globaler Periode zu `run_index`, `max_periods` und
   `period`.
3. Festgelegte, reproduzierbare RNG-Initialisierung.
4. Validierte Writer-Formate für jede betrachtete Datei.
5. Pro Dateifamilie ein eigener Parser und Comparator.

## Empfohlene Reihenfolge

1. Versicherer-Agrsich-Slice auf mehrere Perioden erweitern.
2. VN-Agrsich-Slice auf mehrere Perioden erweitern.
3. Erst danach gemeinsame Altinitialdaten laden.
4. Abweichungen tabellarisch erfassen, nicht durch Toleranz verdecken.
5. Pro weiterer Dateiart einen separaten Validierungs-PR verwenden.

## Noch nicht umsetzen

- Kein monolithischer historischer Gesamtlauf.
- Keine implizite Umrechnung unbekannter C-Zustandsvektoren.
- Keine Gleichheitsbehauptung fuer nicht geparste Dateifamilien.

## Minimaler Harness-Zuschnitt

Ein erster Harness sollte nur:

- ein kuratiertes JSON-Szenario laden,
- mehrere Perioden deterministisch ausführen,
- Agrsich-Exporttabellen schreiben,
- ausgewählte Dateien gegen echte Legacy-Referenzen vergleichen,
- Differenzen pro Datei, Periode und Feld ausgeben.

Erst wenn dieser schmale Pfad grün ist, sollte der Harness auf weitere
Altinitialdaten und Dateifamilien erweitert werden.
