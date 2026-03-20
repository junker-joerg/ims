# Vereinheitlichung des Ergebnisaufbaus

Dieses Dokument beschreibt einen kleinen Architektur-Schritt in `simulation.py`.
Wiederkehrender technischer Aufbau von Rückgabeobjekten wurde in kleine private Hilfsfunktionen gebündelt.

## Was vereinheitlicht wurde

- Aufbau von `SimulationStepResult`
- Aufbau von `ScheduledSequenceResult`
- Aufbau von `ControlledLoopResult`

## Was bewusst unverändert blieb

- öffentliche Dataclasses und öffentliche Funktionssignaturen
- Dispatch-, Scheduler-, RNG- und Eventreihenfolge-Logik
- bestehende Rückgabestrukturen und beobachtbare Metadaten
- bestehendes Fehlerverhalten

## Warum dies ein sinnvoller Architektur-Schritt ist

Der Rückgabeaufbau ist nun an weniger Stellen dupliziert und dadurch leichter wartbar.
Das hält `simulation.py` technischer und klarer, ohne neue Fachlogik einzuführen.

## Warum dies keine neue fachliche Semantik einführt

Die neuen Hilfsfunktionen setzen nur bestehende Ergebnisobjekte zusammen.
Sie verändern weder Ereignisse noch fachliche Regeln oder historische Semantik.
