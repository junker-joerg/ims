# Erster fachlicher Slice: vereinfachte Aggregatbildung

## Ursprungsidee im Altmodell

Im historischen IMS/ESS-Modell sind periodische Kennzahlen und Auswertungen ein naheliegender fachlicher Schnitt zwischen Zustandsmodell und späterer Simulation.
Dieser Python-Slice greift diese Idee nur in stark vereinfachter Form auf und behauptet keine fachliche Gleichwertigkeit.

## Was dieser Slice leistet

- übernimmt einen geladenen Minimalzustand aus `SimulationContext`, `BAV`, `Insurer` und `Policyholder`
- bildet daraus wenige eindeutig ableitbare Kennzahlen
- liefert einen kleinen `AggregateSnapshot` für Tests und spätere Erweiterungen

## Was ausdrücklich noch nicht portiert wurde

- keine BAV-/VU-/VN-Regeln
- keine Aggregation über Beiträge, Produkte, Verträge oder Marktlogik
- keine Simulationsschleife, kein Scheduler-Ablauf, keine UI
- keine Behauptung historischer Kompatibilität oder fachlicher Vollständigkeit

## Warum dies nur ein erster vertikaler Slice ist

Dieser Slice verbindet erstmals Laden, Zustandscontainer und eine einfache fachnahe Auswertung.
Er bleibt absichtlich klein, weil nur Kennzahlen umgesetzt werden, die aus dem bisherigen Modellzustand ohne weitere Annahmen eindeutig ableitbar sind.
