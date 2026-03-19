# RNG-Strategie

Dieses Dokument beschreibt das minimale technische RNG-Grundgerüst des Python-Ports.
Es handelt sich bewusst noch nicht um eine historische IMS/ESS-RNG-Portierung.

## Ziel dieses Grundgerüsts

- deterministische RNG-Erzeugung auf Basis eines Seeds
- kleine Hilfsfunktionen für einfache Zufallszahlen
- optionale Führung eines RNG im `SimulationContext`

## Was dieses Grundgerüst noch nicht leistet

- keine historische RNG-Kompatibilität
- keine fachliche Nutzung in Regeln oder Simulationen
- keine Aussage über Gleichwertigkeit zum Altverhalten

## Spätere Prüfung

Eine mögliche Regression gegen historisches Altverhalten muss in späteren PRs separat geprüft und dokumentiert werden.
