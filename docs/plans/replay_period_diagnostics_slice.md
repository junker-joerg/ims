# Replay-Periodendiagnosen

## Ziel

Die Agrsich-Replay- und expliziten VU/VN-Runner berichten lokale und globale
Periodenachsen getrennt. Damit bleiben Fixtures mit mehreren Runs
nachvollziehbar, ohne lokale Periodennummern als globale Validierungs- oder
Exportzeit zu verwechseln.

## Umfang

- VU-Agrsich-Replay: lokale und globale Periodenlisten im Ergebnis.
- VN-Agrsich-Replay: lokale und globale Periodenlisten im Ergebnis.
- Expliziter VU/VN-Runner: lokale und globale Periodenlisten im Ergebnis.
- Tests fuer wiederholte lokale Perioden in unterschiedlichen Runs.

## Grenzen

- Keine neue Schedulerlogik.
- Keine automatische historische Regelauswahl.
- Keine Vollsimulation und keine Behauptung historischer Vollgleichheit.
